# Pitch builder brief

Send one of these to each of the three pitch agents, in the same message as the explainer agent, so all four run together. Fill the placeholders.

The agent reads its pitch straight from `brief.md`. Do not retype or summarize the pitch into the prompt: a retyped prompt is where wording drifts, and the brief is the contract.

- `{N}`: 1 to 3
- `{NAME}`: the pitch's name, as in its `## N. <Name>` heading
- `{SKILL_DIR}`: absolute path to this skill's folder
- `{RUN_DIR}`: absolute path to the run folder
- `{TOPIC}`: short product name
- `{OTHER_PICTURES}`: one line for the explainer's mechanism and one per other pitch, with its picture form (flow, sheet, queue, lanes, calendar, chat turn), so the four builders do not draw the same thing

---

> You are building four slides that pitch one idea to one specific person. The slides are part of a deck called "Why {TOPIC} matters". Another agent is building the explainer that comes before the pitches, and two more are building the other pitches, and the fragments get stitched into one file, so follow the shared rules exactly.
>
> **Your pitch is number {N} of 3: "{NAME}".** A pitch makes the case for one idea and then hands it off: the person may pick it and paste its prompt into whatever agent they use to dig deeper. By the time your slides appear, the explainer has already taught how {TOPIC} works, so your job is this person's job, not the mechanism again.
>
> Read `{RUN_DIR}/brief.md` first. You need four parts of it:
>
> - `## What {TOPIC} is`: the facts. Do not add to them from memory; this product may be newer than your training data.
> - `## Who this is for`: the person you are pitching to.
> - `## {N}. {NAME}`: your pitch. Every field is yours to use. The claim, the reason, the sources, the three copy columns, and the handoff prompt are used word for word. They were checked against what is known about the person, so rewording them can make them untrue.
> - `## Kept off the slides`: what must not appear.
>
> **What the other builders are drawing**, so you can pick a different form:
> {OTHER_PICTURES}
>
> ## Then read
>
> 1. `{SKILL_DIR}/references/slide-types.md`: read Builds, Motion, Words, Markers and ids, Source chips, and all of "A pitch", plus the napkin pair markup.
> 2. `{SKILL_DIR}/references/drawing-rules.md`: all of it.
> 3. `{SKILL_DIR}/examples/sections/pitch-1.html`: a finished pitch. The content is invented. Copy the structure and the drawing quality, and draw your own pictures.
>
> ## Build
>
> Write `{RUN_DIR}/sections/pitch-{N}.html` containing four `<section class="slide">` elements and nothing else:
>
> 1. **divider**: the pitch's number, the claim as the headline, the reason in the Because card, and its source chips. Eyebrow `Pitch 0{N} of 03`. No picture. This slide tells the person why the pitch is theirs and where that knowledge came from, so copy it exactly.
> 2. **pitch**: eyebrow `Pitch 0{N} · How it works`, the pitch headline, a scene on the board, and the three copy columns (How it works, What changes for you, Proof).
> 3. **today and with**: eyebrow `Pitch 0{N} · Today and with {TOPIC}`, the brief's "Job in quotes" as the headline, `Today` on the left, `With {TOPIC}` on the right. Draw the same object on both sides so the difference stands out. If the brief has no honest "today" for this pitch, leave this slide out and deliver three.
> 4. **handoff**: eyebrow `Pitch 0{N} · Take it further`, the handoff prompt from the brief word for word in `<div class="ask">`, one `<p>` per paragraph, the URL in `<b>`, fill-in parts in `<i>[brackets]</i>`. Then the strip: Bring, You'll leave with, Watch out (the short one).
>
> Rules that matter most:
>
> - Every id starts with `p{N}-`.
> - Colors come from theme variables only. Blue is {TOPIC}. Green is what the person gains. Red is only the ✕ badge. Everything else is gray.
> - No `<style>`, no `<script>`, no images, no external anything. Inline `style` only for motion timing (`--d`, `--t`, `--fx`, `--fy`).
> - Motion is light on pitch slides: `a-flow` on connectors, `a-grow` on the green parts and the time bars, `a-pop` on the check. Motion classes go on children of a build group, never on the `data-b` element.
> - Label the person's tools and files with their real names. Every number on a slide must appear in the brief. Do not invent statistics.
> - Word budgets are in `slide-types.md`. No em dashes, no exclamation points, no hype words.
> - No scores, no impact or effort labels, no tags under the headline. The ranking is not part of the deck.
> - Put each label in the same `<g>` as the shape it sits in or under, and count characters so it fits.
>
> ## Check your work by looking at it
>
> ```bash
> python3 {SKILL_DIR}/scripts/stitch.py {RUN_DIR} --topic "{TOPIC}" --only pitch-{N}
> python3 {SKILL_DIR}/scripts/check.py {RUN_DIR}/preview-pitch-{N}.html
> ```
>
> The first command builds a preview deck from your fragment and lints it. The second renders each slide to a PNG (the resting frame, after motion settles) and prints a layout report. Fix every ERROR and every layout line. Then **open each PNG and look at it** as the person would:
>
> - Cover the caption in your mind. Does the picture still say something?
> - Is the scene recognizably this person's work, or could it be anyone's?
> - Is anything cramped, tiny, floating in empty space, or overlapping?
> - Does the eye go to the blue thing, then the green thing?
> - Is the whole handoff prompt visible, with nothing clipped?
>
> Revise and rerun until the report is clean and you would be glad to present the slides. Two or three rounds is normal. Do not edit any file other than `pitch-{N}.html`.
>
> If the scripts cannot run (no Python, no Chrome), say so in your reply and check the markup by reading it against the text-fit rules.
>
> ## Reply
>
> Four lines at most: the path you wrote, how many slides, what each picture shows, and anything in the brief you could not draw honestly or that looked untrue about the person.

---

## After the agents return

Read each reply, then run the full stitch and check yourself. Agents checked their sections alone; only the full deck shows whether the explainer and three pitches read as one piece. Look for:

- A pitch scene that repeats the explainer's mechanism instead of showing this person's job. Redraw it around their nouns.
- Two pitches with nearly the same picture. Redraw the weaker one in a different form.
- A divider whose claim, reason, or source differs from the brief.
- A handoff prompt that was shortened, reworded, or lost its link. The brief's wording wins.

Small fixes are faster to make yourself than to send back.
