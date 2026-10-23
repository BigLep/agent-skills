# Worked example: Lotus issue 13723 wrap-up comment

Context: the user asked an agent whether Lotus PR 13781 fully addressed issue 13723, then asked for a wrap-up comment to post on the issue. The agent had read the issue, the PR diff, the review thread, the merged file on the branch, and the builtin-actors source. The user had seen the diff and the review thread but had not read the actor source.

## Agent draft (author voice)

```markdown
Wrap-up now that #13781 has merged into `feat/solstice`.

**1. Post-upgrade removal is tracked in #13795.** Removing `--drop-claims`, the pre-nv29 branches, and the `lotus filplus` / `lotus-shed verifreg` write commands happens after nv29 has activated on mainnet, not in the nv29 release.

**2. Non-lotus-miner commands.** This issue was scoped to `lotus-miner` only (per the plan in the comment above). The `lotus filplus` and `lotus-shed verifreg` deprecation warnings are scoped in #13721 instead. See my comment there for the command list and the before/after-epoch behaviour.

**3. Gaps between what was asked for and what landed.** I compared the issue, the review thread, and the merged code. Two things to call out:

- **Faulted sectors and the review record.** The final review asked to switch from `ActiveSectors` to `LiveSectors` so faulted sectors are included, and the reply said this was done. The merged code still uses active sectors only. That is the correct behaviour: the actor rejects any non-active sector with `illegal_argument` and would fail the whole message. But the review thread now says the opposite of what shipped, and `upgrade-quality` silently skips faulted sectors with no hint to recover and re-run. Worth a short follow-up PR to print a note about skipped faulted sectors, and this comment serves as the correction to the review record.
- **No integration test drives the CLI.** Review asked for tests against the new command. What landed is unit tests for the message-packing helper (including the 12500-sector CBOR check). The itests exercise `UpgradeSectorQuality` through the test kit directly, not through `lotus-miner sectors upgrade-quality`. A CLI-level itest would close this.

Everything else in the issue is covered: `upgrade-quality` command, `--legacy-qa-power` list filter, `--drop-claims` rejected on nv29+, the deal-ID precommit guard, docs and changelog, and the bulk of the itest matrix from the review comments.
```

## What the user posted (reviewer voice, with links added afterwards)

```markdown
Wrap-up now that #13781 has merged into `feat/solstice`, which is sufficient for this issue since we are not waiting on the merge to master.

**1. Post-upgrade removal is tracked in #13795.** Removing `--drop-claims`, the pre-nv29 branches, and the `lotus filplus` / `lotus-shed verifreg` write commands happens after nv29 has activated on mainnet, not in the nv29 release.

**2. Non-lotus-miner commands.** This issue was scoped to `lotus-miner` only. The `lotus filplus` and `lotus-shed verifreg` deprecation warnings are scoped in #13721 instead. I [commented there](https://github.com/filecoin-project/lotus/issues/13721#issuecomment-5637915186) with my understanding for the command list and the before/after-epoch behaviour.

**3. Gaps between what was asked for and what landed.** with agent help, I compared the issue, the review thread, and the merged code. These are my finding:

- **Faulted sectors and the review record.** @LexLuthr's [final review points](https://github.com/filecoin-project/lotus/pull/13781#issuecomment-5631659769) asked to switch from `ActiveSectors` to `LiveSectors` so faulted sectors are included, and @snail8501's [reply](https://github.com/filecoin-project/lotus/pull/13781#issuecomment-5632174401) said this was done. The merged code still uses active sectors only. I believe this is the correct behavior: the actor rejects any non-active sector with `illegal_argument` and would fail the whole message. But I believe the review thread now says the opposite of what shipped, and `upgrade-quality` silently skips faulted sectors with no hint to recover and re-run. Is this worth a short follow-up PR to print a note about skipped faulted sectors?
- **No integration test drives the CLI.** @LexLuthr [asked for tests against the new command](https://github.com/filecoin-project/lotus/pull/13781#pullrequestreview-5164616407) and [for a test demonstrating message building](https://github.com/filecoin-project/lotus/pull/13781#discussion_r3977084583). I believe what landed is unit tests for the message-packing helper (including the 12500-sector CBOR check). The itests exercise `UpgradeSectorQuality` through the test kit directly, not through `lotus-miner sectors upgrade-quality`. Is a CLI-level itest required?
- **`--full-qa-power` was dropped without being called out.** The [plan](https://github.com/user-attachments/files/31631080/lotus-miner-nv29-cli-plan.en.md) and the earlier revision of the PR had both `--full-qa-power` and `--legacy-qa-power` filters on `sectors list`. It looks like only `--legacy-qa-power` shipped. I think that is fine since it is the one that identifies upgrade candidates, but the change was not noted in the PR description or review, so recording it here.

I believe everything else in the issue is covered. Once we close out on the above, I think we're good to close this issue.
```

## The edits, move by move

**Provenance.** "I compared" became "with agent help, I compared". One clause, placed where the analysis starts, not a banner at the top.

**Selective hedging.** These stayed plain because the user could see them in the diff or the thread: "The merged code still uses active sectors only", "asked to switch from ActiveSectors to LiveSectors", "the reply said this was done", the list of commands in item 1. These got hedged because they were the agent's reading of actor source or its interpretation: "I believe this is the correct behavior: the actor rejects...", "I believe the review thread now says the opposite", "I believe what landed is unit tests", "It looks like only --legacy-qa-power shipped", "I believe everything else in the issue is covered". About one clause in four.

**Citations.** "The final review" became "@LexLuthr's [final review points](link)". "The reply" became "@snail8501's [reply](link)". "Review asked for tests" became two linked phrases pointing at the specific review and the specific discussion thread. "The plan" got its attachment link. Roles were replaced by @mentions throughout.

**Recommendations to questions.** "Worth a short follow-up PR to print a note..." became "Is this worth a short follow-up PR to print a note...?" "A CLI-level itest would close this" became "Is a CLI-level itest required?" The reasoning before each question was kept so the question is informed.

**Removed.** "and this comment serves as the correction to the review record" was dropped: it pronounced on the record rather than asking the reviewers to confirm.

## A second, smaller example: scope the agent added on its own

On issue 13721 the agent drafted a scoping comment that said the CLI should "fail fast" after the upgrade epoch rather than let messages revert. That was the agent's idea, not something agreed in the thread; an earlier comment by the user had assumed the opposite. The user caught it only by asking "is this basically an expansion of what was already said?" The fix was to restate what was agreed (rely on actor rejection, wasting a little gas is fine) and open the comment with its purpose: restating the agreement, being explicit about the command list and the before and after epoch behaviour, and naming the one addition (`lotus-shed verifreg`, because it hits the same actor) as an addition.

Lesson: when the draft proposes something beyond what the thread agreed, either drop it or mark it explicitly as the user's addition with the reason. Never let it ride as if it were already settled.
