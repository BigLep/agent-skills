---
name: why-does-this-matter
description: Turns a new release, model, app, feature, or technology into a personalized visual deck. The deck first explains the new thing with animated diagrams, including what it can't do yet, then pitches the three ideas this specific person should explore. Each pitch is tied to a stated reason drawn from what is known about them (role, industry, tools, current projects), shows where that knowledge came from, and ends in a handoff prompt they can paste into any agent to dig deeper. Researches the topic live, reads the user's memories and files, then builds a napkin-style HTML slide deck. Use this skill whenever someone asks "why does this matter", "what should I do with X", "what can I use X for", "is X worth my time", "how does X apply to my job / my business / my team", "give me use cases for X", "explain the new X and what it means for me", or names a just-launched model, tool, or feature and wants to know what it is and what to try, even if they never say "deck" or "slides". Also use it when the user types /why-does-this-matter followed by a topic.
---

# Why Does This Matter

Topic: the release, model, app, feature, or technology the user named.

## What you're making

Two files in `why-it-matters/<topic-slug>/` in the working directory:

1. **`brief.md`**: the explainer plan, the three pitches, the reason behind each, the context that was used, and sources.
2. **`<topic-slug>.html`**: one self-contained 16:9 deck, about 21 slides, in the light Rundown napkin theme, with motion in the explainer.

The deck has two halves. **First it teaches the new thing** until the person could explain it to a colleague, including what it is bad at. **Then it pitches three ideas**, each with the reason it is for this person, and hands each one off.

The person running this just heard about something new. They cannot judge a use case for a thing they do not understand yet, so the explainer comes first and gets the deck's best pictures: animated diagrams that show the thing working, in order. A generic list of use cases fails them too, because they could get that from any launch post. The value of the pitches is the match between what the thing can newly do and the work this person already does.

Three pitches, not more, because three is a choice and five is a list. A pitch is a pitch: it makes the case, and its last slide is a prompt the person can paste into whatever agent they use (Claude, ChatGPT, Cursor, anything) to explore that one idea in depth. The deck does not try to be the plan.

The match only lands if the person can see it. People usually do not know which memories, files, or past chats an AI is drawing on, so a pitch that arrives without its reason reads as a guess, and one built on a stale or wrong fact cannot be corrected. So the deck shows its working: what it knows about the person, where each fact came from, and which fact each pitch rests on.

## The shape of a run

| Phase | Who does it | Output |
|---|---|---|
| 1. Research | Four agents in parallel, on a lower-cost model | `research/*.md` |
| 2. Synthesis | You, thinking hard | `brief.md` |
| 3. Slides | Four agents in parallel on the strongest visual model (one explainer, three pitches), while you build the title, context, and close | `sections/*.html` |
| 4. Stitch and check | You | the deck |

Tell the person what is happening at each phase in one short line. A run takes a few minutes and silence feels broken.

## Phase 0: Pin down the topic

If no topic was given, ask for one. If the topic is a link or a file, read it.

The topic is probably newer than your training data. That is the whole reason this skill exists, and it has a consequence: **anything you "remember" about it is suspect.** Treat the research files as the only source of facts about the topic. If the name is ambiguous or you do not recognize it, that is normal; let the research settle it. If research cannot confirm the thing exists, stop and ask the person for a link instead of guessing. A confident deck about the wrong product is the worst outcome this skill can produce, and an animated explainer of the wrong mechanism is the most convincing way to deliver it.

Before launching agents, skim what is already in front of you (the message, memory index, project instructions, attachments) and write one line: who this person seems to be. It aims the use-case research. "Unknown so far" is a fine answer.

Create the run folder: `why-it-matters/<topic-slug>/` with `research/` and `sections/` inside.

## Phase 1: Research, in parallel

Read `references/research-briefs.md`. It holds the four briefs. Launch all four agents in a single message so they run at the same time:

| Agent | Question it answers | Writes |
|---|---|---|
| Facts | What is it, how does it work, what is new, who can get it, what does it cost | `research/facts.md` |
| In the wild | What are real people doing with it this month | `research/in-the-wild.md` |
| Skeptic | Where does it fall short, and what is hype | `research/skeptic.md` |
| Context | Who is this person, and where is each fact about them written down | `research/profile.md` |

Use a lower-cost model for these (in Claude Code, `model: "sonnet"` on the Agent tool). Research is reading and summarizing, and the expensive thinking comes next. The Skeptic exists because launch-week coverage is mostly praise; its findings become the explainer's limits slide and each pitch's watch-out.

The Context agent records the source of every fact (which memory, which file, which message). Those sources go on slides, so a fact without one cannot be used as a reason.

## Phase 2: Synthesis

This is the step that decides whether the deck is worth opening. Do it yourself, carefully. Read `references/synthesis.md` for the explainer plan, the ranking method, the handoff prompt, and the `brief.md` template.

1. **Read all four research files.**
2. **Check the profile.** If role, industry, or tool stack is still unknown, ask the person three quick multiple choice questions (the questions are in `references/synthesis.md`). If the profile is solid, do not ask. People who have given Claude their context should not have to repeat it.
3. **Plan the explainer** from `facts.md` and `skeptic.md` only: the mechanism in one sentence and how it should move, the before and now, the three things that changed, optional numbers with who measured them, and three limits. Every fact carries its source in the brief.
4. **Generate eight to twelve candidates.** Each one pairs a job this person already does with a capability that is new. "Summarize documents" is a capability. "Turn Friday's call-board notes into Monday's follow-up emails" is a candidate.
5. **Rank them** by impact against effort for this person, then **choose three** that are clearly different options: one they could start today, one for this week, one bigger bet. The ranking stays in the brief; the deck never shows scores. Cut anything the Skeptic file says does not work yet. Keep the next few as "Also worth a look".
6. **Give every pitch its reason.** One sentence about the person, starting with "You", that is true, specific, and traceable to a named source. If the honest reason is "people in your industry do this", the pitch is generic; replace it.
7. **Write each handoff prompt** so it works pasted cold into an agent that knows nothing about the person or the topic: the idea, the facts about them it rests on, what the new thing is with a link to read first, and a concrete ask. Nothing sensitive goes in it.
8. **Write `brief.md`.** It is the contract for the slide agents, so every field in the template gets filled.

Give the person the three pitches with their reasons as soon as the brief is written. They should not wait for slides to learn the answer, and this is their first chance to say "that's not true about me anymore."

## Phase 3: Slides, in parallel

Read `references/slide-types.md` and `references/drawing-rules.md`, and look at the files in `examples/sections/`. Then:

1. **Launch four agents in a single message**, all on the strongest visual model available (in Claude Code, `model: "opus"`):
   - **The explainer agent**, with the brief in `references/explainer-builder.md`. It writes `sections/explain.html`: four or five animated slides (mechanism, before and now, what changed, optional stats or hierarchy, limits).
   - **Three pitch agents**, one per pitch, with the brief in `references/pitch-builder.md`. Each writes `sections/pitch-N.html`: four slides (divider, pitch, today and with, handoff).
   Each agent reads its part straight from `brief.md`. Tell each one what the others are drawing so the four pictures take different forms.
2. **While they run, write the frame yourself:**
   - `sections/open.html`: the title slide.
   - `sections/context.html`: what I'm working from.
   - `sections/close.html`: pick one (three cards that link to the handoffs) and the line to remember.

The explainer and the pitches are built separately so each gets a full pass of attention on its pictures. The cost of that is drift, so the template, the types, the motion classes, and the drawing rules are fixed, and the scripts check what they can.

## Phase 4: Stitch and check

```bash
python3 <skill-dir>/scripts/stitch.py why-it-matters/<topic-slug> --topic "<Topic>"
python3 <skill-dir>/scripts/check.py why-it-matters/<topic-slug>/<topic-slug>.html --scale 0.5 --motion
```

`stitch.py` assembles the deck in order (open, explain, context, pitch-1 to pitch-3, close), resolves the pick cards' links to the handoff slides, and lints it (duplicate ids, hardcoded colors, external resources, missing reasons or sources, a missing limits slide or handoff, unknown motion classes, word budgets, banned words). `check.py` renders every slide's resting frame to a PNG in headless Chrome and reports layout problems (labels crossing shapes, content in the footer, clipped text, uneven rows) and which slides move. `--motion` adds early frames of the animated slides.

Then **look at every PNG**, and at the early frames of the mechanism slide. Measuring catches overflow. It cannot tell you that a picture is confusing, that two slides look identical, that motion arrives in the wrong order, or that a diagram says nothing. Fix what you find in the fragment files and run both scripts again. Ask of each picture: would it still teach something with the words covered?

Also check the deck against the brief: every fact and number on the explainer slides is in the brief's explainer section, the three pitches are in order, every reason and source on a divider matches the brief word for word, and every handoff prompt matches the brief and still has its link.

Finally, open the deck: `open "<absolute path>"` (macOS), `xdg-open` (Linux), `start` (Windows).

## Reply

Keep it short:

1. What the topic is, in one sentence, and the one limit that matters most.
2. The three pitches, each with its reason, as a short list.
3. **What I used about you**: the sources read, by name, and an invitation to correct anything stale or wrong. If they correct something, rerank and rebuild the affected pitches.
4. Anything you could not verify.
5. A `Links:` section with the deck and the brief as markdown links with absolute paths. Mention that arrow keys move through the deck, that each pitch ends with a prompt to copy into any agent, and that printing from the browser saves a PDF.

## Voice

The deck talks to a smart, busy adult who is new to the topic.

- **The headline is the conclusion**, as one sentence the person could act on or repeat. "Let it write the month-end close memo for all twelve clients," not "Document automation opportunities." Wrap one phrase in `<em>` for the highlight chip.
- **Concrete before abstract.** Name their tool, their client type, their recurring meeting. Work analogies are fine (new hire, recipe card, contractor). No baby talk.
- **Reasons are about the person, not the product.** "You write a close memo for every client, every month" is a reason. "Orion 2 is great at long documents" is a feature.
- **Handoff prompts are paste-ready.** The exact words, with the link, not a description of what to ask.
- **Name sources, skip the hype.** No "experts say." Every claim about the topic carries its source; every number says who measured it. When the maker's number and an independent one disagree, show both. Estimates say "about."
- **No em dashes, no exclamation points.** Plain verbs: use, build, write, check, send. Skip: leverage, unlock, seamless, robust, transformative, game-changer, journey, landscape.
- **Give the copy room, and keep it tight.** Explainer slides are mostly picture. A pitch slide carries three columns of about 22 words each. Never shrink type to fit more in; cut words.

## Rules that hold the deck together

- Do not change the template's theme tokens, fonts, stage size, or type sizes. Fragments contain slides only: no `<style>`, no `<script>`, no external images or fonts. The deck has to work offline in a workshop room.
- **Motion comes only from the template's classes**, and every animation ends on the finished picture, so the deck prints and reads correctly without it. The explainer moves; the pitches move lightly; nothing depends on motion to carry a fact.
- **Blue** marks the new thing being explained. **Green** marks the payoff for the person. **Red** appears only on the ✕ of a pair slide. Nothing else is colored.
- **Each pitch opens on a dark divider slide** with its number, and carries `Pitch 0N` in the eyebrow of every slide in its section. The room should never wonder which pitch they are in.
- Every id inside a fragment starts with the fragment's prefix (`open-`, `ex-`, `ctx-`, `p1-` to `p3-`, `close-`). Two SVGs sharing an id makes arrows vanish on the later slide.
- At most four builds per slide, and only where order teaches something.

## Showing context without exposing it

The deck tells the person what was used. It may also be shown to a room, and its handoff prompts get pasted into other tools. Hold all three:

- **Show the fact and its source** whenever the person would say the fact out loud in a meeting: their role, their tools, their recurring work, a project they are running.
- **Name the kind and the source, not the detail,** when the fact is sensitive: money figures, names of clients or private individuals, health, legal, or personal matters, anything unannounced. "Your pricing notes shaped this" tells them what was used without printing it. These go in the "Used, not shown" cell of the context slide and in the brief, and never in a handoff prompt.
- **Never put credentials, account numbers, or secrets anywhere**, including the brief.
- A source label is a name the person will recognize: the memory's title, the file's name, "this chat", or the connected tool. Not a full path, and never an internal id.

## When something is missing

The full run assumes parallel agents, web search, Python, and a Chromium browser. Degrade in this order and say which path you took:

- **No sub-agents** (for example Claude.ai chat): do the four research passes yourself in sequence, then the synthesis, then build the explainer and the three pitches one at a time. Same files, same order.
- **No web search:** ask the person to paste the announcement, a link you can fetch, or their notes. Do not write about a new release from memory.
- **No context found:** ask the intake questions. The source on those slides is "You told me" and "In this chat". Do not invent a reason to fill a slide.
- **No Python:** assemble by hand. Copy `assets/template.html`, replace the `<!-- SLIDES -->` marker with the fragments in order (open, explain, context, pitch-1 to pitch-3, close), give only the first slide `class="slide on"`, add `data-frag="<fragment name>"` to each section, replace each `href="#pitch-N"` and `{{pitch-N}}` with the number of that pitch's handoff slide, and set the `<title>` and the last breadcrumb node.
- **No Chrome for `check.py`:** step through the deck with a browser tool if you have one and run the checks in `references/slide-types.md` under "Checking by hand". Otherwise open the file and ask the person to arrow through it.
- **No file system:** deliver the brief in chat and offer the deck as a single HTML artifact.

## Reference files

- `references/research-briefs.md`: the four Phase 1 agent briefs. Read before Phase 1.
- `references/synthesis.md`: intake questions, the explainer plan, ranking, handoff prompts, `brief.md` template. Read before Phase 2.
- `references/slide-types.md`: every slide type with markup, and the motion classes. Read before Phase 3.
- `references/drawing-rules.md`: how pictures are drawn, and drawing for motion. Read before Phase 3.
- `references/explainer-builder.md`: the brief for the explainer agent.
- `references/pitch-builder.md`: the brief for each of the three pitch agents.
- `examples/sections/`: a finished title, explainer, context slide, pitch, and close to copy from. The content is invented; copy the structure, drawing style, and motion staging only.
- `assets/template.html`: the deck shell with both fonts, the motion classes, and the slide scripts. `stitch.py` reads it.
