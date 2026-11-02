#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Claude Code Stop hook: open Plannotator on Claude's last reply when it asks me something.

Intent
    Answering a long reply full of questions is much nicer in Plannotator (inline comments next to
    each question) than typing into the terminal. This hook does automatically what running
    /plannotator-last by hand does, but only when it is worth it.

Opens Plannotator when ALL of these hold (see decide()):
    - The reply is at least MIN_CHARS characters ("decently long").
    - It contains at least one question mark followed by whitespace or the end of the text.
      One is enough: a list of questions often has only one "?" in it. A "?" inside code (inline or
      fenced, which includes drafted messages meant for someone else) doesn't count.
    - The only question is not a lone yes/no offer such as "Want me to commit this?" or
      "OK to force push?". Those are quicker to answer in the terminal. (In a replay of past
      sessions, about 40% of long replies with a question were just one of these offers.)
    - Claude did not use the Plannotator Inbox during this turn. If the questions went to the
      Inbox, I answer them there, so opening Plannotator as well would be redundant.
    - The hook is not already in a feedback loop (stop_hook_active), so it won't reopen while
      Claude is still addressing my annotations.

How it hooks in
    Configured as a "Stop" command hook in ~/.claude/settings.json with a very long timeout so it
    can wait while I annotate (see the skill README). It reads the Stop event JSON on stdin
    (last_assistant_message, transcript_path, stop_hook_active). When it opens Plannotator,
    `plannotator annotate-last --stdin --hook` blocks until I respond and its stdout is passed
    through unchanged:
    - Sending annotations prints {"decision":"block","reason":...}, which hands my feedback to
      Claude and keeps the turn going.
    - Approve or Close print nothing, and the turn ends normally.

Testing
    PLANNOTATOR_IF_QUESTIONS_DRY_RUN=1 prints the decision (open, or skip:<reason>) instead of
    opening Plannotator. replay.py, run_cases.py and test_decide.py import decide() and
    inbox_used_in_turn() from this file, so tests always exercise the real rules.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MIN_CHARS = 400

# A "?" that ends a sentence: right after a word or closing paren (bold/italic markers allowed in
# between, as in "**the date**?"), and followed by whitespace or end of text, optionally after
# closing markdown or quotes (as in "**OK to push?**" or "(which one?)"). Excludes URL query
# strings and a literal "?" mentioned in quotes.
QUESTION_RE = re.compile(r"[A-Za-z0-9)][*_]*\?[*_`'\")\]]*(\s|$)")

# A question sentence that starts with a yes/no offer phrase, either at the start of the line
# (after any markdown such as "- " or "**") or after the end of a previous sentence on that line.
YES_NO_OFFER_RE = re.compile(
    r"(^[^A-Za-z0-9]*|[.:!][^A-Za-z0-9]+)"
    r"(want me to|should i|shall i|ok to|okay to|do you want( me)? to|would you like( me)? to)\b"
    r"[^.!?]*\?",
    re.IGNORECASE,
)

# How a turn's tool calls reveal that Claude used the Plannotator Inbox.
INBOX_TOOL_NAME_RE = re.compile(r"plannotator_inbox")
# Bash only counts when it runs the command (start of the script or after ; & | ( or a newline,
# optionally with a path), not when the text merely appears, e.g. inside a grep pattern.
INBOX_BASH_RE = re.compile(r"(^|(?<!\\)[;&|(\n])\s*(\S*/)?(plannotator\s+inbox|inbox-send)\b")


@dataclass(frozen=True)
class Decision:
    decision: str  # "open" or "skip:<reason>"
    detail: str = ""  # human-readable evidence, e.g. the matching line

    @property
    def opens(self) -> bool:
        return self.decision == "open"


# Code is quoted material, not a question to me: fenced blocks are removed and `inline spans` are
# replaced by a placeholder word (so "delete `/tmp/x`?" still reads as a question) before looking
# for questions.
FENCED_CODE_RE = re.compile(r"^```.*?^```[^\n]*$", re.DOTALL | re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def question_lines(message: str) -> list[str]:
    prose = INLINE_CODE_RE.sub("code", FENCED_CODE_RE.sub("", message))
    return [line.strip() for line in prose.splitlines() if QUESTION_RE.search(line)]


def decide(message: str, *, inbox_used: bool = False, stop_hook_active: bool = False) -> Decision:
    """Pure decision function. Order matters: the first rule that fails is the reported reason."""
    if stop_hook_active:
        return Decision("skip:stop_hook_active", "already continuing after Plannotator feedback")
    if len(message) < MIN_CHARS:
        return Decision("skip:short", f"{len(message)} chars < {MIN_CHARS}")
    questions = question_lines(message)
    if not questions:
        return Decision("skip:no_question", "no line contains a sentence-ending '?'")
    if len(questions) == 1 and YES_NO_OFFER_RE.search(questions[0]):
        return Decision("skip:yes_no_offer", questions[0])
    if inbox_used:
        return Decision("skip:inbox", "this turn sent something to the Plannotator Inbox")
    return Decision("open", questions[-1])


# ---------------------------------------------------------------------------------------------
# Transcript helpers (Claude Code session JSONL), shared with replay.py.


def load_transcript(path: str | Path) -> list[dict]:
    entries = []
    for line in Path(path).read_text().splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def is_user_prompt(entry: dict) -> bool:
    """A prompt I typed (or a plugin/hook injected), as opposed to a tool result."""
    if entry.get("type") != "user":
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    return isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "text" for b in content
    )


def assistant_texts(entry: dict) -> list[str]:
    if entry.get("type") != "assistant":
        return []
    content = (entry.get("message") or {}).get("content")
    if not isinstance(content, list):
        return []
    return [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]


def is_inbox_tool_use(block: dict) -> bool:
    if block.get("type") != "tool_use":
        return False
    name = block.get("name", "")
    if INBOX_TOOL_NAME_RE.search(name):
        return True
    command = (block.get("input") or {}).get("command") or ""
    return name == "Bash" and bool(INBOX_BASH_RE.search(command))


def inbox_used_in_turn(entries: list[dict]) -> bool:
    """True if anything after the last user prompt called the Plannotator Inbox."""
    start = max((i for i, e in enumerate(entries) if is_user_prompt(e)), default=-1)
    for entry in entries[start + 1 :]:
        content = (entry.get("message") or {}).get("content") if entry.get("type") == "assistant" else None
        if isinstance(content, list) and any(isinstance(b, dict) and is_inbox_tool_use(b) for b in content):
            return True
    return False


# ---------------------------------------------------------------------------------------------
# Hook entry point.


def main() -> int:
    event = json.load(sys.stdin)
    message = event.get("last_assistant_message") or ""
    transcript = event.get("transcript_path")

    inbox_used = False
    if transcript and Path(transcript).is_file():
        try:
            inbox_used = inbox_used_in_turn(load_transcript(transcript))
        except OSError:
            pass

    result = decide(message, inbox_used=inbox_used, stop_hook_active=bool(event.get("stop_hook_active")))

    if os.environ.get("PLANNOTATOR_IF_QUESTIONS_DRY_RUN"):
        print(result.decision)
        return 0
    if not result.opens:
        return 0
    # stdout is inherited, so Plannotator's hook JSON goes straight back to Claude Code.
    return subprocess.run(["plannotator", "annotate-last", "--stdin", "--hook"], input=message, text=True).returncode


if __name__ == "__main__":
    sys.exit(main())
