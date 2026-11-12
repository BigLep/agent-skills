# plannotator-auto-last

Automatically open [Plannotator](https://plannotator.ai) on Claude Code's reply when Claude asks you questions, so you can answer inline in the browser instead of typing in the terminal. It does what running `/plannotator-last` by hand does, but only when it's worth it.

It has two parts:

- **The hook** (`scripts/plannotator_if_questions.py`): a Claude Code `Stop` hook that decides whether to open Plannotator after each reply.
- **The skill** (`SKILL.md`): for "why didn't Plannotator open?". It diagnoses a turn, saves it as a test case and proposes rule changes, checking them against every saved case.

## Rules

Plannotator opens only when all of these hold:

| Rule | Why |
|---|---|
| Reply is at least 400 characters | Short replies are quick to answer in the terminal. |
| Contains at least one sentence-ending `?` | One is enough: a list of questions often has only one `?`. A `?` inside code (inline or fenced, including drafted messages for someone else), in a URL, or quoted as a literal `"?"` doesn't count; bold around it (`**date**?`, `**OK?**`) is fine. |
| The only question isn't a lone yes/no offer ("Want me to…?", "Should I…?", "OK to…?") | Those are faster to answer in the terminal. In a replay of past sessions they were about 40% of long replies with a question. |
| Claude didn't use the Plannotator Inbox this turn | If the questions went to the Inbox, you answer them there. |
| Not already continuing after Plannotator feedback (`stop_hook_active`) | Prevents loops. |
| You started the turn, by typing a prompt or sending Plannotator feedback | A turn started by anything else (another Claude session, a background task notification, a coordinator, an Orca orchestration wake) may have nobody watching, and waiting for you would hang the session until you notice. The reply stays in the terminal, and `/plannotator-last` opens it by hand. Prompts with no recorded sender count as yours. Orca's wake ("You have N orchestration message(s)...") is recognised by its text, because Orca types it into the terminal and Claude Code records it as human input. |

When it opens, `plannotator annotate-last --stdin --hook` waits for you. Sending annotations hands them to Claude and the turn continues; Approve or Close ends the turn normally.

## Install

Requires [uv](https://docs.astral.sh/uv/) and the `plannotator` CLI on PATH.

1. Install the skill (symlink on the authoring machine, see the repo README, or `npx skills add BigLep/agent-skills -g --skill plannotator-auto-last`).
2. Add the hook to `~/.claude/settings.json` (the `skills` CLI doesn't install hooks). Append to `hooks.Stop`:

   ```json
   {
     "hooks": [
       {
         "type": "command",
         "command": "~/.claude/skills/plannotator-auto-last/scripts/plannotator_if_questions.py",
         "timeout": 345600
       }
     ]
   }
   ```

   The long timeout (the value Plannotator's own hooks use) keeps the hook from giving up while you annotate.
3. Restart Claude Code, or review the change in `/hooks`.

## Testing

All scripts are uv scripts; run them directly from `scripts/`.

| Command | What it does |
|---|---|
| `./test_decide.py` | pytest: rule unit tests, hook stdin/stdout contract, Inbox detection, and every saved case. |
| `./run_cases.py` | Runs every saved case and lists mismatches; exits 1 on any failure. |
| `./replay.py turns` / `show --turn N` | Shows the hook's decision for each turn of a session (default: newest for the current directory). |
| `./replay.py add --turn N --expected open --note "..."` | Saves a real turn as a test case. |
| `./replay.py sample` | Replays recent sessions and summarizes decisions; `--seed N` saves N baseline cases per decision. |

`PLANNOTATOR_IF_QUESTIONS_DRY_RUN=1` makes the hook print its decision instead of opening Plannotator.

### Test cases

- `evals/examples.jsonl`: made-up cases, committed, so tests work on a fresh clone.
- `evals/cases.jsonl`: real turns from your sessions, **gitignored** because they contain private reply text. Grown with `replay.py add` whenever the hook gets a turn wrong.
