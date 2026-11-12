# Idea: a local model to detect replies awaiting input (parked)

Status: parked on 2026-11-03, tried and left parked on 2026-11-12 (see below). Nothing here is in the hook.

## Why it came up

Some longer replies that were awaiting input did not open Plannotator. The regex heuristic only sees explicit `?` questions, so it can't notice an implicit ask such as a plan that ends "let me know if this looks right" or a list of proposed actions waiting for review. A language model could judge **awaiting input** (see `../GLOSSARY.md`) directly.

## What would unpark it

Evidence that the heuristic misses enough turns to matter. The way to get it: whenever a reply should have opened Plannotator and didn't (or the reverse), run the `plannotator-auto-last` skill and save the turn with `replay.py add`. When `evals/cases.jsonl` has a meaningful number of misses the regexes can't reasonably fix, revisit this.

At the time of parking: 22 real saved cases plus 7 examples, all passing. A replay sample of recent sessions decided 145 `no_question`, 81 `open`, 51 `short`, 32 `yes_no_offer`, 2 `inbox`.

## Tried on 2026-11-12: no better than the heuristic

A Foundation Models CLI (guided generation returning `awaitingInput: Bool`, reply trimmed to its last 6,000 characters) was run over 382 attended replies from 2026-11-03 to 2026-11-12. The labels came from what I did next: answered in Plannotator, opened it by hand with `/plannotator-last`, or just typed.

- **Latency:** fine. Median about 0.7s, 90th percentile about 1s, max 1.8s. One reply was refused as possibly sensitive.
- **Accuracy:** not useful. It said "awaiting input" for 93% of replies: all 110 the heuristic opens, and 165 of the 186 no-question replies I did not open. On the replies the heuristic skips, its "yes" matched what I wanted no better than the base rate (about 11%).
- **Why:** most remaining misses are long reports or drafts I wanted to comment on, not replies that ask something. Whether I want Plannotator there depends on me more than on the text, so a better prompt is unlikely to fix it.

## Decisions reached so far

- **What the model detects:** whether Claude is waiting on the user to respond or to review a set of actions. Answers are usually better in Plannotator because they can be given in context, so this is broader than "contains a question".
- **Scope:** keep the exact gates (`stop_hook_active`, Inbox used, under `MIN_CHARS`) in front, deterministic. The model only replaces the fuzzy judgment (is there a real ask, is it just a yes/no offer) for replies that pass the gates.
- **Optional, with fallback:** model mode is opt-in. The skill is published, and Foundation Models needs Apple Silicon, macOS 26+ and Apple Intelligence enabled. If the model is unavailable or errors, use the heuristic.
- **Latency:** target under about 1.5 seconds per decision; on timeout, use the heuristic's answer for that turn.
- **Two modes to compare:** support running with and without the model so their decisions can be compared, both against saved cases (`run_cases.py`) and across replayed sessions (`replay.py sample`), with a list of turns where they disagree.

## Technical notes (as of 2026-11-03)

- Apple's `FoundationModels.framework` (on-device model, about 3B parameters) is Swift-only. From this Python hook it would be called through a small compiled Swift CLI, using `@Generable` guided generation to return a structured verdict (for example `awaiting_input: bool`, `reason: String`).
- The on-device context window is small (about 4K tokens), so long replies need trimming, probably keeping the end of the reply where asks usually are.
- `decide()` is already pure and shared by `replay.py`, `run_cases.py` and `test_decide.py`, so a model-backed decider could plug in at the same seam.

## Open questions for when this resumes

- How is the mode chosen: an env var, the presence of the helper binary, or both?
- Should the comparison be offline only (replay and saved cases), or should the live hook also run a shadow mode that logs disagreements without acting on them?
- How should the helper binary be built and shipped for people installing the skill with `npx skills add`?
- What prompt and trimming strategy fit within the context window without losing the ask?
