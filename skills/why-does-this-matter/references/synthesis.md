# Synthesis

Turn four research files into an explainer plan and three pitches, and write them to `brief.md`.

## Contents

1. Gate checks
2. Intake questions, when the profile is thin
3. Planning the explainer
4. Generating candidates
5. Scoring and choosing three
6. The reason behind each pitch
7. The handoff prompt
8. The `brief.md` template
9. Self-check before slides

## 1. Gate checks

Two things must be true before you plan anything.

**The topic is real and identified.** `facts.md` names one product and cites a primary source. If it lists several candidates or found nothing, ask the person which one they mean or for a link.

**You know who this is for.** You need role, industry, and tools at medium confidence or better. Recurring jobs are the most useful field; if they are missing, you can usually infer a first list from the role and confirm it with the person in one question.

## 2. Intake questions, when the profile is thin

Ask only for the fields that are missing. Use a multiple choice tool if you have one, and ask in chat if you do not. Offer four options each and always let them type their own. Build the options from whatever the profile did find, so the questions feel informed.

1. **Role.** "Which is closest to what you do day to day?" Options drawn from context, for example: run my own business, lead a team, individual specialist, consultant or advisor to clients.
2. **Industry and who you serve.** "Who is your work for?" Options drawn from context.
3. **Tools.** "Which of these do you already use most days?" Multi-select. Offer the common stacks for their role.
4. **Goal (optional, ask if three questions did not cover it).** "What would make this worth your time?" Save hours on routine work, improve the quality of what I ship, offer something new to clients, understand it well enough to advise others.

Write the answers into `profile.md` under a heading `## From the person`, so the run folder stays a complete record.

## 3. Planning the explainer

The first half of the deck teaches the new thing. The explainer agent draws it, but you decide what it says, because this is where a wrong fact does the most damage: the topic is newer than any model's training, and a confident animation of the wrong mechanism is worse than a wrong bullet.

Write the explainer section of the brief from `facts.md` and `skeptic.md` only. Every fact on an explainer slide carries its source in the brief. If `facts.md` does not say how something works inside, draw what goes in and what comes out and leave the inside plain; do not invent internals.

Plan these slides (the slide types are in `slide-types.md`, under The explainer):

- **E1 mechanism.** The one sentence the person should be able to repeat, as the headline. What goes in, what the thing does in two or three steps, what comes out. Say what should move and in what order: this is the brief for the richest motion in the deck. Anchor the input and output in the person's world when that helps ("YOUR TALLY FORM"), and keep the inside in the thing's own terms.
- **E2 before and now.** One request, as the person would phrase it. What they had does it this way; the new thing does it that way. Draw the same object on both sides.
- **E3 what changed.** The three capabilities the three pitches rest on, each as a short claim and one sentence.
- **E4, optional: stats or hierarchy.** Stats when there are two or three numbers people will repeat and the research says who measured them. If the maker's number and an independent number disagree, this slide shows both, labeled. Hierarchy when where the thing lives is confusing.
- **E5 limits.** The three limits most likely to cost this person an afternoon, from `skeptic.md`. Each one says what to do about it and who found it.

## 4. Generating candidates

Write eight to twelve. A candidate has three parts:

- **The job:** something from the person's recurring jobs or current projects.
- **The capability:** something from "What is new" in `facts.md`.
- **The change:** what is different about the job afterward (faster, better, newly possible, or no longer theirs to do).

Work the grid both ways. Go down the capabilities and ask which of this person's jobs each one touches. Then go down the jobs and ask whether anything new helps. The second pass finds the candidates the launch post never mentioned, and those are usually the best ones.

Use `in-the-wild.md` for proof that a use works and for ideas you would not have had. Use `skeptic.md` to remove candidates that depend on something that fails today.

Include at least one candidate that is an **implication** and not a task: something the person should decide, stop doing, or tell their clients because this exists. For a consultant, "your clients will ask you about this within a month" can outrank any workflow.

## 5. Scoring and choosing three

This is background work. It decides which three become pitches and in what order, and the scores go in the brief for anyone who wants them. The deck never shows a score, a quadrant, or an impact label.

Score every candidate for this person, not for people in general.

**Impact, 1 to 5**

| Score | Meaning |
|---|---|
| 5 | Changes a job they do weekly, or opens revenue or an offer they could not make before |
| 4 | Saves hours every month on a job that matters to their stated goals |
| 3 | Clear improvement on a job they do monthly |
| 2 | Nice to have, or a job they rarely do |
| 1 | Interesting, with no clear place in their work |

**Effort, 1 to 5**

| Score | Meaning |
|---|---|
| 1 | Works today with tools and files they already have. Under 30 minutes to a first result |
| 2 | Needs a plan upgrade, a connection, or an hour of setup |
| 3 | Needs a new tool or an afternoon |
| 4 | Needs other people, data cleanup, or several days |
| 5 | Needs a project, a budget, or approval |

**Confidence: high, medium, low.** High means someone showed it working and nothing in the Skeptic file contradicts it. Low means it is plausible and unproven. Never pitch a low-confidence candidate first.

**Rank** by impact divided by effort. Break ties with time to first result, then confidence. Then choose three by hand:

- **Three is a choice, not a list.** The person will pick one and take it to their agent, so the three should be clearly different options. No two share a job, and no two rest on the same fact about the person.
- **Spread them.** A good three is one they could start today (effort 1 or 2, first), one for this week, and one bigger bet with the highest impact. This spread stays in the background; the deck shows only the order.
- **At most one implication.** Its handoff asks the agent to help think through the decision or the conversation.
- **Keep the runners-up.** The next three to five go in the brief under "Also worth a look", one line each. They are not in the deck, but the person or their agent can use them.

Numbers on slides (minutes saved, hours per month) are estimates unless a source measured them. Build each estimate from something the profile supports ("twelve clients, about ninety minutes each") and write "about". If you cannot ground a number, show the change without one.

## 6. The reason behind each pitch

Every pitch gets one reason. The reason is what the person sees first, on a dark slide, in large type, so it has to hold up.

A good reason:

- **Is about the person.** It starts with "You" and states something they do, have, or are working on. "You write a close memo for every client, every month."
- **Is specific enough to be wrong.** If it could be said to anyone in their industry, it is not a reason, it is a demographic. A reason the person could correct ("not anymore, I handed that off in June") is doing its job.
- **Names its source.** One or two, from `profile.md`: the kind and the name. `Memory · Month-end routine`. `File · AI Writing Style Guide.md`. `You told me · In this chat`.
- **Is not sensitive.** If the true reason rests on a sensitive detail, state the reason at the level the person would say out loud, and list the detail's kind under "Also used".
- **Is not inferred, if you can help it.** A reason built on an inference says so: "It looks like you..." and the source reads `Inferred · from your Workshops folder`.

## 7. The handoff prompt

Each pitch ends with a prompt the person pastes into whatever agent they use (Claude, ChatGPT, Cursor, something else) to dig deeper. That agent has none of their memories, none of this research, and has probably never heard of the topic. Write it to stand alone. 95 words or fewer, four or five short paragraphs:

1. **The idea.** "I want to dig into one idea with you: <the pitch in one line>."
2. **About me.** One or two facts from the context table that this pitch rests on, as the person would say them. Only facts from the shown rows; nothing from "Used, not shown" or "Kept off the slides".
3. **The new thing.** What it is in one sentence, who made it, when it launched, "probably after your training data", and "Read <primary URL> before you answer." Use the maker's own page or the best independent source from `facts.md`.
4. **The ask.** Questions first ("Ask me three questions about ..."), then one concrete first deliverable (a test design, a first version, a plan for one client), then "tell me what would make it fail."

It names no product-specific feature of the receiving agent (no "use my memory", no "search my Drive"). Fill-in parts go in [brackets]. If a pitch's first step is a conversation or a decision rather than a build, the ask is to help prepare that conversation.

## 8. The `brief.md` template

Write the file exactly in this shape. The slide agents read their section verbatim, so an empty field becomes an invented slide.

```markdown
# Why <Topic> matters for <role, in a few words>

<date> · Prepared for <name or role>

## The short version

<Three sentences. What the topic is. What it changes for this person. Which pitch to try first.>

## What <Topic> is

- **In one sentence:** <plain words>
- **Made by:** <maker>, launched <date>
- **Lives inside:** <container>
- **Primary source for handoffs:** <URL the handoff prompts send agents to>
- **What changed:**
  1. <capability, six words or fewer> · <one sentence> · <source>
  2. ...
  3. ...
- **Get it:** <plan, price, how to start>

## The explainer

<The explainer agent reads this section. Every fact carries its source. Nothing here comes from memory.>

### E1. Mechanism
- **Headline:** <10 words or fewer, one phrase in *asterisks*>
- **Goes in:** <what, named in the person's world if that helps>
- **Inside:** <two or three steps, in the thing's own terms, each 5 words or fewer> · <source>
- **Comes out:** <what>
- **Motion:** <what moves, in what order: "the twelve months light up one by one, then the two steps pop in, then the memo rises out">
- **Caption:** <one sentence, what it actually holds or does>

### E2. Before and now
- **Request:** "<one request in quotes>"
- **Before (<what they had>):** <bold line> / <soft line>
- **Now (<Topic>):** <bold line> / <soft line>
- **Picture:** <the same object on both sides, and what differs>

### E3. What changed
- **Headline:** <one sentence>
- 1. <claim, 20 characters or so> · <sentence> · <picture idea> · <source>
- 2. ...
- 3. ...

### E4. Stats (or Hierarchy, or "none")
- **Headline:** <one sentence>
- 1. <label> · <number exactly as written> · <sentence> · <who measured it, date>
- ...

### E5. Limits
- **Headline:** <one sentence>
- 1. <claim> · <what to do about it> · <who found it, date> · <how to draw the failure>
- 2. ...
- 3. ...

## Who this is for

<Five or six bullets from profile.md: role, who they serve, tools, what they already use AI for, how they like things.>

## What I'm working from

<The context slide, as a table. Five facts that shaped the pitches, in the person's own terms, each 14 words or fewer. Use these labels in this order. Skip a row only if nothing is known.>

| Label | Fact | Source |
|---|---|---|
| Your role | <fact> | <Kind · Name> |
| Who you serve | <fact> | <Kind · Name> |
| Your tools | <fact> | <Kind · Name> |
| Work that repeats | <fact> | <Kind · Name> |
| On your plate now | <fact> | <Kind · Name> |
| Used, not shown | <the kinds of sensitive detail that shaped the ranking, 18 words or fewer> | <Kind · Name> |

**Sources read:** <every memory, file, and tool that was opened, by name>

**Already doing with AI, so not suggested:** <list>

## Three pitches, three reasons

| # | Pitch | Because you | You'll leave with | Source |
|---|---|---|---|---|
| 1 | <name, 28 characters or fewer> | <the reason, 9 words or fewer, lowercase, continuing "Because you"> | <the first thing the agent session produces, 24 characters or fewer> | <Kind · Name> |
| 2 | ... | | | |
| 3 | ... | | | |

## Ranking, for the record

<Not shown in the deck.>

| # | Pitch | Impact | Effort | Confidence | First result |
|---|---|---|---|---|---|
| 1 | <name> | 5 | 1 | high | 20 min |

## 1. <Name, 28 characters or fewer>

- **Claim:** <one sentence, written as the divider headline, 14 words or fewer. Mark the phrase to highlight with *asterisks*.>
- **Because:** <the reason. One sentence starting with "You", 24 words or fewer.>
- **Source:** <one or two, each as Kind · Name>
- **Also used:** <kinds of sensitive detail behind this pitch, or "nothing">
- **Pitch headline:** <7 words or fewer, says what the picture shows: "Three exports in, one memo out.">
- **How it works:** <22 words or fewer. What goes in, what the new thing does, what comes out.>
- **What changes for you:** <22 words or fewer. The difference in their week.>
- **Proof:** <18 words or fewer. Who showed this working and what happened. If it is only claimed, say "claimed".>
- **Proof by:** <name, publication, date>
- **What changed:** <the capability that makes it possible> · <source>
- **Job in quotes:** "<the job as the person would say it, 6 words or fewer. The today-and-with headline.>"
- **Today:** <bold line, 6 words or fewer> / <soft line: how they do this job now, with a time or cost if you can ground one>
- **With <Topic>:** <bold line, 6 words or fewer> / <soft line: how it goes instead>
- **Handoff prompt:**
  > <paragraph 1: the idea>
  >
  > <paragraph 2: about me>
  >
  > <paragraph 3: the new thing, with the primary URL>
  >
  > <paragraph 4: the ask>
- **Bring:** <24 characters or fewer, so it stays on one line>
- **You'll leave with:** <24 characters or fewer>
- **Watch out:** <one caveat, from the Skeptic file if there is one. Full sentence here.>
- **Watch out, short:** <the same caveat in 24 characters or fewer, for the handoff strip>
- **Scores:** impact <n>, effort <n>, confidence <high/medium/low>
- **Picture ideas:** <pitch scene: what goes in, what acts, what comes out, named with their tools, and a form that differs from the other pitches. today and with: what to contrast.>
- **Sources:** <links>

## 2. ...

## 3. ...

## Also worth a look

<The next three to five candidates, one line each: the idea, the reason, and why it is not in the top three. Not in the deck.>

## Considered and cut

<Candidates that did not survive, one line each with the reason. This is how the person sees the ranking was a choice.>

## What we could not verify

<Claims with thin sourcing, profile fields that were guessed, numbers that are estimates.>

## Kept off the slides

<Kinds of private detail that informed the ranking and must not appear on a slide or in a handoff prompt. Name the kinds, not the details themselves. The slide agents read this section.>

## The line to remember

<One sentence, 12 words or fewer.>

## Sources

<Every link, with dates.>
```

## 9. Self-check before slides

Read the brief as the person would and answer honestly:

- After the explainer, could they explain the new thing to a colleague in two sentences, including one thing it is bad at?
- Does every fact in the explainer section trace to `facts.md` or `skeptic.md`, with its source written next to it?
- Are the three pitches three different choices? Could pitch one be started in the next hour with what they have?
- Does every "Because" state something true about this person, with a source they would recognize? Or could it be said to anyone in their industry?
- Would each handoff prompt work pasted cold into an agent that knows nothing about the person or the topic? Does it link the primary source? Does it contain anything from "Kept off the slides"? It must not.
- Does any pitch rely on a claim that appears only in the maker's own launch post? Mark its confidence accordingly.
- Does each Proof line prove this pitch's claim (an accuracy pitch needs accuracy proof, not speed), and does it avoid repeating a number the explainer already shows?
- If you hid the topic's name, would the three still read as pitches for this specific thing, or as general AI advice? If general, go back to "What changed" and tie each one to a capability.
