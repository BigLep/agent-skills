---
name: humble-relay
description: |
  Rewrite an agent-produced draft (GitHub issue or PR comment, Slack message, email, doc) so it reads as the user relaying agent work they have partly verified, not as an author who checked everything. Adds a provenance note ("with agent help"), hedges only the claims the user did not verify themselves, cites sources inline (comment links, code links, docs) so readers can audit, and turns the agent's recommendations into questions for the people who own the decision. Use this whenever the user is about to post or send text that an agent drafted or researched, especially when they say "put this in my voice", "I'll post this", "draft a comment for me", "tone this down", "I don't want to sound that confident", "make it clear an agent helped", "hedge this", or asks for a comment to review before posting. Also use on the user's own text when they ask to soften confidence.
---

# Humble relay

An agent writes like an author who verified every claim. The user posts as a reviewer who verified some claims, is relaying the rest, and wants the reader to know which is which. This skill produces the second voice from the start so the user does not have to hand-edit every draft.

## Why this matters

When the user posts agent text verbatim, three things go wrong. Readers assume the user personally checked everything, so a wrong detail damages the user's credibility rather than the agent's. Recommendations read as decisions, which steps on the people who own the code. And nothing tells readers how to verify the claims for themselves. The user's own edits (see `references/worked-example.md`) fix all three, and they do it selectively: plain facts stay plain, only relayed judgments get hedged.

## The four moves

### 1. Provenance note

Add a short note that an agent did the work when the agent did substantive analysis: read code, compared a PR against an issue, traced a review thread, researched history. If the user was asking the agent questions to understand the topic, that counts as reliance, so add the note. Skip it when the agent only formatted, added links, or fixed typos.

Place it where the analysis begins, not as a disclaimer at the top. "With agent help, I compared the issue, the review thread, and the merged code" is the house phrasing. Vary it when it reads awkwardly ("an agent traced this for me", "I had an agent compare X against Y"), but keep it to one clause. One note per document is enough.

### 2. Hedge only what the user did not verify

Infer from the conversation which claims the user could check themselves versus which they are relaying. Default split:

Leave plain:
- Anything visible in a diff, a linked comment, a quoted line, or a command the user ran
- Links, quotes, file paths, names, dates
- Statements about what the user themselves did, decided, or wants

Hedge with "I believe", "I think", "it looks like", "my understanding is":
- The agent's interpretation of why code behaves a certain way
- Claims about actor or library behaviour the agent read but the user did not
- Summaries of what a review thread meant, as opposed to what it literally says
- Anything that was the agent's inference rather than something it quoted

Do not hedge every sentence. Uniform "I believe" reads as insecure rather than honest and buries the claims that actually deserve caution. In the worked example roughly one clause in four gets a hedge. If the conversation does not tell you whether the user verified something, hedge it; the user can remove a hedge more easily than a reader can detect a missing one.

### 3. Cite sources so readers can audit

Every non-obvious claim should point at something a reader can open: the specific review comment, the line in the merged file, the issue comment, the plan document, the actor source. Prefer inline links on the phrase that makes the claim ("@LexLuthr's [final review points](url) asked to switch..."). Fall back to a short source list at the end only when inline links would clutter a sentence past readability.

Name people with @mentions instead of roles ("the reviewer", "the author"). Roles hide who said what and make the thread harder to follow.

If you do not have the URL, fetch it (`gh api`, `gh pr view --comments`, permalink to the file at the merged commit) rather than leaving a role reference. An unlinked "the review asked for X" is exactly the kind of claim a reader cannot check.

### 4. Turn recommendations into questions

The agent tends to prescribe: "Worth a short follow-up PR", "A CLI-level itest would close this". The user is usually not the owner of that decision. Rewrite these as questions addressed to the people who are: "Is this worth a short follow-up PR?", "Is a CLI-level itest required?"

Keep the agent's reasoning next to the question so it is a well-informed question, not a vague one. Statements of fact that the user did verify stay as statements; only the judgment call becomes a question.

## Things not to change

- Do not add scope the conversation did not agree to. If the agent's draft contains a proposal that goes beyond what was already decided in the thread (a new gating rule, a stricter behaviour), either drop it or flag it as the user's addition ("the one thing I am adding beyond what was discussed is X, because Y"). The user has been burned by drafts that quietly extended agreed scope.
- Do not restate the purpose vaguely. If the comment exists to make something explicit (the command list, the before and after epoch behaviour), say that in the first line.
- Keep the user's structure, headings, and any numbering they gave you. Touch wording, not organisation.
- Keep the user's spelling conventions from the draft they gave you.
- No em dashes.

## Workflow

1. Read the draft and the conversation. Note which claims came from the agent's own digging and which the user asked about or could see directly.
2. Decide whether provenance applies (substantive analysis, or the user relied on the agent to understand). Usually yes.
3. Rewrite, applying the four moves. Fetch any missing comment or code URLs before finishing.
4. Present the result as a fenced markdown block ready to paste. Below it, list in one or two lines what you hedged and why, and any place where you were unsure whether the user had verified a claim, so they can flip it.
5. If the user asked for the text on the clipboard, use the copy-to-clipboard skill after presenting it.

For the full before and after pair that this skill is modelled on, read `references/worked-example.md`. Read it the first time you use this skill and whenever you are unsure how much to hedge.
