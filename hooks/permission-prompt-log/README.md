# permission-prompt-log

A Claude Code `PermissionRequest` hook that logs every tool call that wasn't auto-approved, with an inferred reason, so you can review the log and improve your permission rules.

The hook only observes. It prints nothing and exits 0, so the permission dialog still appears and you decide as usual. It also swallows its own errors, so a logging problem can't interfere with a prompt.

## What it logs

One JSON line per prompt, appended to `~/.claude/permission-prompts.jsonl` (override with `PERMISSION_PROMPT_LOG`):

```json
{"ts":"2026-11-04T18:02:11+00:00","session_id":"...","cwd":"/path/to/repo","tool":"Bash","command":"git fetch && make build","why":"unmatched_subcommand","unmatched_subcommands":["make build"],"signals":["mode:default","compound"],"permission_suggestions":[...]}
```

Claude Code doesn't say why it prompted, so `why` is inferred by re-checking the call against `permissions.allow` / `ask` in your user and project settings files (`settings.json` and `settings.local.json` in `~/.claude` and `<cwd>/.claude`):

| `why` | Meaning | Typical fix |
|---|---|---|
| `ask_rule` | A `permissions.ask` rule matched (see `matched_ask_rules`). | None; the rule is doing its job. Or narrow it if it's too broad. |
| `unmatched_subcommand` | A compound Bash command where some parts are allowed but others aren't (see `unmatched_subcommands`). Each part must be allowed on its own. | Allow the unmatched part. |
| `no_allow_rule` | Nothing in `permissions.allow` matches. | Add an allow rule if the command is safe and frequent. |
| `unknown` | The matcher thinks an allow rule matches, so the prompt came from something it can't see: a built-in safety check, a path outside the working directory, managed policy, or a matcher mismatch. | Inspect `signals` and the raw command. |

`signals` adds hints: `compound`, `command_substitution`, `redirect`, `outside_cwd_path`, and `mode:<permission_mode>`. `permission_suggestions` is the raw "always allow" suggestion list from the event, when Claude Code provides one.

The matcher approximates Claude Code's own (legacy `Bash(prefix:*)`, glob `*`, bare tool names; compound commands split on `&&`, `||`, `;`, `|`, `&`, newline). Treat `why` as a strong hint, not ground truth; the raw command is always logged.

## Install

Requires [uv](https://docs.astral.sh/uv/). Add to `hooks.PermissionRequest` in `~/.claude/settings.json` (use the absolute path to this checkout):

```json
{
  "matcher": "*",
  "hooks": [
    {
      "type": "command",
      "command": "/path/to/agent-skills/hooks/permission-prompt-log/scripts/log_permission_prompt.py",
      "timeout": 10
    }
  ]
}
```

Restart Claude Code, or review the change in `/hooks`.

## Reviewing the log

Examples with `jq`:

```sh
# Most frequent prompts by reason
jq -r .why ~/.claude/permission-prompts.jsonl | sort | uniq -c | sort -rn

# Most frequent commands with no allow rule (candidates for new allow rules)
jq -r 'select(.why=="no_allow_rule") | .command' ~/.claude/permission-prompts.jsonl | sort | uniq -c | sort -rn | head -30
```

## Testing

`./scripts/test_log_permission_prompt.py` (pytest via uv) covers command splitting, the `why` inference, and the stdin/stdout contract.
