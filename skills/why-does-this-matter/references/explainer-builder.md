# Explainer builder brief

Send this to the explainer agent in the same message as the three pitch agents, so all four run together. Use the strongest visual model available. Fill the placeholders.

The agent reads the explainer plan straight from `brief.md`. Do not retype it into the prompt.

- `{SKILL_DIR}`: absolute path to this skill's folder
- `{RUN_DIR}`: absolute path to the run folder
- `{TOPIC}`: short product name
- `{PITCH_PICTURES}`: one line per pitch with its picture form, so the mechanism does not repeat a pitch scene

---

> You are building the first half of a deck called "Why {TOPIC} matters": four or five slides that explain {TOPIC} to one smart, busy person who has just heard of it. After your slides, they should be able to explain it to a colleague in two sentences, including one thing it is bad at. Three other agents are building the pitches that come after your slides, and the fragments get stitched into one file, so follow the shared rules exactly.
>
> These slides are where the deck teaches, so they carry the deck's best pictures and its motion. A still diagram says what the parts are. A diagram that moves in the right order says what happens: the parts being read light up one by one, the steps arrive after the reading, the result rises out. Use motion to show order and change, and let every slide settle into a finished picture.
>
> ## Read first
>
> 1. `{RUN_DIR}/brief.md`: `## What {TOPIC} is`, `## The explainer` (your contract, slide by slide), `## Who this is for`, and `## Kept off the slides`. The explainer section was written from the research and every fact in it has a source. **Do not add facts from memory.** {TOPIC} is probably newer than your training data, and a confident picture of the wrong mechanism is the worst thing this deck can show. If the brief does not say how something works inside, draw what goes in and what comes out and keep the inside plain.
> 2. `{RUN_DIR}/research/facts.md` and `{RUN_DIR}/research/skeptic.md`, only to understand the brief better. If they seem to contradict the brief, follow the brief and say so in your reply.
> 3. `{SKILL_DIR}/references/slide-types.md`: Builds, Motion, Words, Markers and ids, all of "The explainer", and the napkin mechanism, pair, cells, and hierarchy markup.
> 4. `{SKILL_DIR}/references/drawing-rules.md`: all of it, especially Drawing for motion.
> 5. `{SKILL_DIR}/examples/sections/explain.html`: a finished explainer. The content is invented. Copy the structure, the drawing quality, and the way motion is staged, and draw your own pictures.
>
> **What the pitches are drawing**, so your mechanism is a different picture:
> {PITCH_PICTURES}
>
> ## Build
>
> Write `{RUN_DIR}/sections/explain.html` containing four or five `<section class="slide">` elements and nothing else, in the order the brief gives: mechanism, before and now, what changed, the optional stats or hierarchy slide if the brief has one, and limits last. Eyebrows read `{TOPIC} · How it works`, `{TOPIC} · Before and now`, `{TOPIC} · What changed`, `{TOPIC} · By the numbers` (or `Where it fits`), `{TOPIC} · What it can't do yet`.
>
> Rules that matter most:
>
> - Every id starts with `ex-`.
> - Colors come from theme variables only. Blue is {TOPIC}. Green is what the person gains. Red is only the ✕ badge on the before-and-now slide. Everything else is gray.
> - No `<style>`, no `<script>`, no images, no external anything. Motion comes only from the template's classes (`a-fade`, `a-rise`, `a-pop`, `a-grow`, `a-grow-y`, `a-dim`, `a-draw`, `a-flow`, `a-travel`, `a-pulse`, `a-count`), with timing in inline style (`--d`, `--t`, `--fx`, `--fy`) and nothing else in inline style.
> - Draw the finished picture, then add motion. If every motion class were deleted, each slide must still be complete and correct: that is what prints.
> - Motion classes go on children of a build group, never on the `data-b` element itself. Stagger delays in teaching order and let each slide finish moving in about three seconds.
> - The mechanism is the hero: viewBox `0 0 1400 470`, three builds, the richest motion in the deck. Every other explainer slide except limits gets some motion too.
> - Every number on a slide must appear in the brief, exactly as written there. Every limit names who found it.
> - Word budgets are in `slide-types.md`. The pictures carry these slides; keep the words few. No em dashes, no exclamation points, no hype words.
> - Put each label in the same `<g>` as the shape it sits in or under, and count characters so it fits.
>
> ## Check your work by looking at it
>
> ```bash
> python3 {SKILL_DIR}/scripts/stitch.py {RUN_DIR} --topic "{TOPIC}" --only explain
> python3 {SKILL_DIR}/scripts/check.py {RUN_DIR}/preview-explain.html --motion
> ```
>
> The first command builds a preview deck from your fragment and lints it. The second renders each slide's resting frame to a PNG, prints a layout report, and with `--motion` saves early frames of each animated slide to `shots/preview-explain/motion/`. Fix every ERROR and every layout line. Then **open the PNGs and look at them**:
>
> - Resting frames: cover the caption. Does the picture still teach? Is anything cramped, tiny, floating, or overlapping? Does the eye go to the blue thing, then the green thing?
> - Early frames: do things arrive in the order you would explain them out loud? Is anything jumping from the wrong place, or visible before it should be?
> - Would someone new to {TOPIC} understand the mechanism slide with the sound off?
>
> Revise and rerun until the report is clean and you would be glad to present the slides. Two or three rounds is normal. Do not edit any file other than `explain.html`.
>
> If the scripts cannot run (no Python, no Chrome), say so in your reply and check the markup by reading it against the text-fit rules.
>
> ## Reply
>
> Five lines at most: the path you wrote, how many slides, what each picture shows and how it moves, and anything in the brief you could not draw honestly or that looked wrong against the research.

---

## After the agent returns

Read the reply, then look at the explainer inside the full deck. Check that:

- Every fact and number on the explainer slides is in the brief's explainer section, word for word. This half of the deck is where an invented detail slips in.
- The mechanism shows the thing working, not a box with a label. If the motion only fades things in, ask whether it shows order; if not, restage it.
- The limits slide is honest and names who found each limit.
- The before-and-now slide and the pitches' today-and-with slides do not draw the same picture.
