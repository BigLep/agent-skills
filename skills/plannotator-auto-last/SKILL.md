---
name: plannotator-auto-last
description: Diagnose and tune the plannotator-auto-last Stop hook, which opens Plannotator on Claude's reply when it asks the user questions. Use when the user asks why Plannotator (or plannotator-last) did or didn't open for a turn, says it should have opened, says it opened when it shouldn't have, or wants to change when it opens.
---

# plannotator-auto-last

A Claude Code `Stop` hook (`scripts/plannotator_if_questions.py`) opens Plannotator on the last reply when it is long enough, asks a question that isn't just a lone yes/no offer, and the Inbox wasn't used that turn. The rules live in `decide()` in that file; its docstring explains the intent behind each one. See `README.md` for installation.

This skill handles the follow-up: "why didn't it open?" (or "why did it open?"). Diagnose the turn, record it as a test case, and propose the smallest rule change that gets the right result without breaking other cases.

All scripts are uv scripts in `scripts/` under this skill's directory; run them directly (for example `scripts/replay.py turns`). They need `uv` on PATH.

## Workflow

1. **Find the turn.** Run `scripts/replay.py turns` (defaults to the newest transcript for the current directory, which is normally this session; pass `--session <id or path>` for another). Each line shows a turn index, the hook's decision and the start of the reply. The turn the user means is usually the last completed one before their question, not the turn you are in now (your in-progress reply can show up as the final index). Confirm with the user if it's ambiguous.

2. **Explain the decision.** Run `scripts/replay.py show --turn N`. Report the decision and evidence in plain words: for example, "it skipped because the only question was the yes/no offer 'Want me to push it?'", or "it was 312 characters, under the 400 minimum". If the user expected a different result, ask what they expected only if it isn't already clear from what they said.

3. **Save the case.** Run `scripts/replay.py add --turn N --expected <open|skip:reason> --note "<why, in the user's terms>"`. That writes to `evals/cases.jsonl`, which is gitignored because it contains real reply text; never commit it or copy its contents into committed files. If the hook was right and the user agrees, save the case anyway with the current decision; it guards against regressions.

4. **Propose a fix.** Change `decide()` or its regexes in `scripts/plannotator_if_questions.py` as narrowly as possible. Then run:
   - `scripts/run_cases.py` to check every saved case, including the new one. It lists failures and exits 1 if any fail.
   - `scripts/test_decide.py` for the unit tests. Add a made-up unit test for the new behavior (never real reply text).
   - `scripts/replay.py sample` to see how the overall open/skip counts shift across recent sessions.
   
   Show the user the rule change, which cases flipped, and the change in counts. If a fix makes other saved cases fail, say which ones and why, and suggest alternatives rather than editing their expected values. Only change a case's expected value when the user says the old expectation was wrong.

5. **Update the docs.** If a rule changed, update the "Opens Plannotator when" list in the hook's docstring and the rules table in `README.md` to match.

6. **Commit only on request.** The skill lives in the user's `agent-skills` repo. Commit the script, tests and docs when the user asks; `evals/cases.jsonl` stays out because it is gitignored.

## Checking the live hook

- If nothing opens at all, check that the hook is registered (`jq '.hooks.Stop' ~/.claude/settings.json` should list the script path) and that Claude Code was restarted or `/hooks` reviewed after the change.
- To see what the hook decides for an event without opening Plannotator, pipe Stop-event JSON into the hook with `PLANNOTATOR_IF_QUESTIONS_DRY_RUN=1` set.
- `stop_hook_active` is true while Claude is continuing after Plannotator feedback. The hook ignores it and applies the normal rules, because each reopen waits for the user and Approve or Close ends the turn. `replay.py` treats those turns like any other.
