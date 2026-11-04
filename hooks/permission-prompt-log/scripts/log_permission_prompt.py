#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Claude Code PermissionRequest hook: log every tool call that wasn't auto-approved.

Intent
    I want data on which commands interrupt me for approval, and why, so I can improve my
    permission rules (add allow rules for safe, frequent commands; spot rules that are too narrow).

How it hooks in
    Configured as a "PermissionRequest" command hook. That event fires only when Claude Code is
    about to show a permission dialog, i.e. when nothing auto-approved the call. This hook never
    makes a decision: it prints nothing and exits 0, so the dialog still appears as normal.

What it logs
    One JSON line per prompt, appended to ~/.claude/permission-prompts.jsonl (override with
    PERMISSION_PROMPT_LOG). Claude Code doesn't say why it prompted, so `why` is inferred by
    re-checking the call against the permission rules in the settings files:
    - ask_rule: a rule in permissions.ask matched (listed in matched_ask_rules).
    - unmatched_subcommand: a compound Bash command where some part has no allow rule
      (listed in unmatched_subcommands). Each part must be allowed on its own.
    - no_allow_rule: nothing in permissions.allow matches.
    - unknown: our matcher thinks an allow rule matches, so the prompt came from something it
      can't see (a built-in safety check, a path outside the working directory, a managed policy,
      or a matcher mismatch). Worth a look when it shows up.
    `signals` adds orthogonal hints: compound, command_substitution, redirect, outside_cwd_path,
    and the permission_mode.

Testing
    ./test_log_permission_prompt.py (pytest). The matcher is deliberately an approximation of
    Claude Code's own, which is why the raw tool_input and permission_suggestions are logged too.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG = Path.home() / ".claude" / "permission-prompts.jsonl"

# Operators that split a Bash command into independently-checked parts.
_SPLIT_OPS = ("&&", "||", ";", "|", "&", "\n")


def settings_files(cwd: str) -> list[Path]:
    home = Path.home() / ".claude"
    proj = Path(cwd) / ".claude"
    return [
        home / "settings.json",
        home / "settings.local.json",
        proj / "settings.json",
        proj / "settings.local.json",
    ]


def load_rules(cwd: str) -> dict[str, list[str]]:
    """Merge allow/ask/deny rule strings from every settings file that exists."""
    rules: dict[str, list[str]] = {"allow": [], "ask": [], "deny": []}
    for path in settings_files(cwd):
        try:
            perms = json.loads(path.read_text()).get("permissions", {})
        except (OSError, ValueError, AttributeError):
            continue
        for kind in rules:
            for rule in perms.get(kind, []) or []:
                if isinstance(rule, str) and rule not in rules[kind]:
                    rules[kind].append(rule)
    return rules


def split_command(command: str) -> list[str]:
    """Split a shell command on unquoted operators (&&, ||, ;, |, &, newline)."""
    parts: list[str] = []
    buf: list[str] = []
    quote = ""
    i = 0
    while i < len(command):
        ch = command[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(command):
                buf.append(command[i + 1])
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch == "\\" and i + 1 < len(command):
            buf.append(ch + command[i + 1])
            i += 1
        else:
            op = next((o for o in _SPLIT_OPS if command.startswith(o, i)), None)
            # `>&` / `2>&1` / `&>` redirects are not command separators.
            if op == "&" and (command[i - 1 : i] in (">", "<") or command[i + 1 : i + 2] == ">"):
                op = None
            if op:
                parts.append("".join(buf).strip())
                buf = []
                i += len(op)
                continue
            buf.append(ch)
        i += 1
    parts.append("".join(buf).strip())
    return [p for p in parts if p]


def _specifier(rule: str, tool: str) -> str | None:
    """Return the specifier of `Tool(spec)`, "" for a bare `Tool`, None if the rule is for another tool."""
    if rule == tool:
        return ""
    if rule.startswith(tool + "(") and rule.endswith(")"):
        return rule[len(tool) + 1 : -1]
    return None


def bash_rule_matches(spec: str, command: str) -> bool:
    if spec == "":
        return True
    if spec.endswith(":*"):  # legacy prefix form: Bash(git fetch:*)
        prefix = spec[:-2]
        return command == prefix or command.startswith(prefix + " ")
    return fnmatch.fnmatchcase(command, spec)


def matching_rules(rules: list[str], tool: str, tool_input: dict) -> list[str]:
    """Rules in `rules` that apply to this call (Bash is matched per sub-command by the caller)."""
    hits = []
    for rule in rules:
        spec = _specifier(rule, tool)
        if spec is None:
            continue
        if tool == "Bash":
            if bash_rule_matches(spec, tool_input.get("command", "")):
                hits.append(rule)
        elif spec == "":
            hits.append(rule)
        else:
            # File/URL-style specifiers: compare against the main string argument.
            target = next(
                (str(tool_input[k]) for k in ("file_path", "path", "url", "pattern") if k in tool_input),
                "",
            )
            if fnmatch.fnmatchcase(target, spec):
                hits.append(rule)
    return hits


def explain(tool: str, tool_input: dict, cwd: str, mode: str, rules: dict[str, list[str]]) -> dict:
    """Infer why a call wasn't auto-approved. Returns why, signals, and rule details."""
    signals: list[str] = []
    out: dict = {}
    if mode:
        signals.append(f"mode:{mode}")

    if tool == "Bash":
        command = tool_input.get("command", "")
        parts = split_command(command)
        if len(parts) > 1:
            signals.append("compound")
        if "$(" in command or "`" in command:
            signals.append("command_substitution")
        if re.search(r"(?<![0-9&<>])>>?(?!&)|<<|(?<![<])<(?![<(])", command):
            signals.append("redirect")
        if any(
            (tok.startswith("/") or tok.startswith("~")) and not tok.startswith(cwd.rstrip("/") + "/")
            for tok in re.findall(r"(?:^|\s)([/~][^\s;|&<>'\"]*)", command)
        ):
            signals.append("outside_cwd_path")

        ask_hits: list[str] = []
        unmatched: list[str] = []
        for part in parts or [command]:
            sub = {"command": part}
            ask_hits += [r for r in matching_rules(rules["ask"], tool, sub) if r not in ask_hits]
            if not matching_rules(rules["allow"], tool, sub):
                unmatched.append(part)
        if ask_hits:
            out["matched_ask_rules"] = ask_hits
            why = "ask_rule"
        elif unmatched and len(parts) > 1 and len(unmatched) < len(parts):
            out["unmatched_subcommands"] = unmatched
            why = "unmatched_subcommand"
        elif unmatched:
            why = "no_allow_rule"
        else:
            why = "unknown"
    else:
        ask_hits = matching_rules(rules["ask"], tool, tool_input)
        if ask_hits:
            out["matched_ask_rules"] = ask_hits
            why = "ask_rule"
        elif not matching_rules(rules["allow"], tool, tool_input):
            why = "no_allow_rule"
        else:
            why = "unknown"
    return {"why": why, "signals": signals, **out}


def build_entry(event: dict, rules: dict[str, list[str]]) -> dict:
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.getcwd()
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": event.get("session_id"),
        "cwd": cwd,
        "tool": tool,
        "command": tool_input.get("command") if tool == "Bash" else None,
        "tool_input": tool_input if tool != "Bash" else None,
        **explain(tool, tool_input, cwd, event.get("permission_mode", ""), rules),
        "permission_suggestions": event.get("permission_suggestions"),
    }
    return {k: v for k, v in entry.items() if v is not None}


def main() -> int:
    try:
        event = json.load(sys.stdin)
        entry = build_entry(event, load_rules(event.get("cwd") or os.getcwd()))
        log = Path(os.environ.get("PERMISSION_PROMPT_LOG") or DEFAULT_LOG)
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:  # Logging must never disturb the permission dialog.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
