# Drawing rules

Every picture is inline SVG using the theme's CSS variables for color. Nothing is a cartoon. Think line diagram drawn by a sharp colleague, not a children's book.

## Canvas sizes

| Slot | viewBox | Notes |
|---|---|---|
| Board (mechanism, hierarchy) | `0 0 1400 520` | Fills the white board. Crop the viewBox tighter if the drawing doesn't need the height. |
| Explainer mechanism | `0 0 1400 470` | The hero picture. Leaves room for a one-line caption under it. |
| Cell (three cells) | `0 0 400 230` | Top half of the card. Draw large: elements should touch the edges. |
| Pair side | `0 0 400 180` | Centered pictogram, about 160 wide, or a full-width bar. |
| Pitch board | `0 0 1400 330` | Shorter than a mechanism board because three columns of copy sit under it. Keep the bottom 40 units for the mono labels under each object. |

Always set `preserveAspectRatio="xMidYMid meet"`.

## Strokes, fills, corners

- Strokes 2 to 3px at these viewBox sizes. Never thicker than 3, never thinner than 1.5.
- Boxes: `rx` 10 to 20. Pills: `rx` half the height.
- Fills: `var(--panel)` for the main object, `var(--panel-2)` for a secondary or inset object, `var(--line-2)` for outlines and for "text bar" placeholders.
- Highlighted object: `stroke="var(--blue)"` with `fill="var(--blue-soft)"` or `var(--panel)`.
- Result object: `stroke="var(--green)"` plus a check badge (circle r 26, green stroke, green tick path).
- Never hardcode a hex color inside an SVG.

## Vocabulary

Use these before inventing new shapes. Most of them appear in `examples/sections/` or in the markup in `slide-types.md`.

- **Request pill or box**: rounded rect, panel-2 fill, mono text in quotes. Label under it in mono caps: YOU ASK.
- **Document**: tall rect with a dark title bar (`var(--text)`) and gray text bars (`var(--line-2)`). Green bars mark the parts the mechanism improved.
- **Folder card**: rect with a header line, mono path label, rows of bars for contents.
- **Card being read** (SKILL.md, config, prompt): inset rect with blue stroke, mono filename, first bar blue.
- **Match spark**: circle in blue-soft with a blue bolt path, mono label MATCH under it.
- **Connector**: `stroke="var(--muted)" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"` with an arrowhead marker for direction. Connectors go left to right on a board. Inside a cell they may run top to bottom when the width won't hold three objects in a row. Each SVG defines its own marker with a unique id (`arw-mech`, `arw-hier`, `arw-c2`); never share an id across slides.
- **Menu or list card**: the card-being-read variant for a set of named things (tools, commands, files). Rows are mono text instead of gray bars. The row in play gets a blue-soft fill and blue stroke. The spark next to it can read CALL, RUN, or MATCH, whichever verb is true.
- **Toggle**: pill 44 by 24 with a circle knob. On is blue with the knob right, off is line-2 with the knob left. Use for permissions and settings.
- **Grid or sheet**: rect with 2 to 3 vertical and horizontal lines in line-2. Use for spreadsheets and tables.
- **Sibling cards**: two or three folder cards side by side, one highlighted, for "one per app" or "one of many" ideas.
- **Nested boxes** (hierarchy): concentric rounded rects, each 100px inset from the last, alternating panel and panel-2 fills, mono caps label top-left of each. The innermost, the topic, gets the blue stroke and blue-soft fill.
- **Runs or repetitions**: equal green bars with mono labels RUN 1, RUN 2, RUN 3.
- **Contrast badges**: ✕ in red-soft circle, ✓ in green-soft circle. These live in HTML, not SVG.

## Labels inside SVG

- `font-family="JetBrains Mono"`, uppercase, `letter-spacing="2.5"`, size 17 on a board, 15 in a cell, `fill="var(--muted)"`.
- Quoted user text stays in sentence case, size 22 on a board, 19 in a cell, `fill="var(--text-soft)"`.
- No sans-serif text inside SVG. Sentences belong in HTML captions.

## Text must fit its shape

Every label sits inside or under a shape, never across its edge. Size the shape from the text, not the other way round.

- JetBrains Mono is 0.6em wide per character, plus any `letter-spacing`. A quote of 18 characters at size 22 is 18 × 13.2 = 238 units wide. Give the pill 24 units of padding each side, so the pill is at least 286 wide.
- Uppercase labels with `letter-spacing="2.5"` are 0.6em + 2.5 per character.
- Text baseline `y` sits about 0.35em below the shape's vertical center.
- If a label won't fit, shorten the label or widen the shape. Never shrink text below the sizes above.
- After the fragment is built, run `scripts/check.py`. It flags any SVG text whose box crosses the edge of a shape in its own `<g>`. Put each label in the same `<g>` as the shape it belongs to, and give separate objects separate groups.

## What not to draw

- No faces, people, hands, or characters.
- No yellow, orange, purple, or gradients.
- No drop shadows, no 3D, no clip art metaphors (lightbulbs, rockets, trophies).
- No more than four builds in one picture.
- No motion that loops forever except `a-flow` connectors and `a-travel` tokens.


## Additions for this skill

### Draw this person's world

A pitch scene works when the person recognizes their own desk in it. Use the nouns from the profile and the brief.

- Label their tools and files in mono caps as they would say them: `NOTION CALL BOARD`, `QUICKBOOKS EXPORT`, `TUESDAY STANDUP`. A generic label (`DATA`, `INPUT`, `TOOL`) means the scene could belong to anyone, so replace it.
- Draw a tool as a labeled window or card. Do not draw logos or brand marks, and do not imitate a product's interface closely. A rounded rect with the name is enough.
- Quantities from the brief can appear as labels (`12 CLIENTS`, `90 MIN EACH`). Every number in a picture must be in the brief.
- Leave out anything the brief lists under "Kept off the slides".
- Dividers and the context slide have no pictures. Their job is the reason and its source, in words.

### More vocabulary

- **App window**: rect with a 40-unit header strip in panel-2, the tool's name in mono caps in the strip, content rows below as gray bars.
- **Time bar**: a full-width pill track in panel-2 with a filled portion. Gray fill for today, green fill for the payoff. Label above with the time, label below with the monthly total. Same track width on both sides of a pair.
- **Calendar week**: five columns with mono day labels, blocks as rounded rects. Blocks the new thing removes are gray on the left side and absent or green-outlined on the right.
- **Inbox or queue**: a stack of equal rows with a short bar each. The rows handled are green, the rows left for the person are panel.
- **Chat turn**: a request pill on the left, a reply card on the right with a blue stroke. Use it when the recommendation is a conversation.
- **Stack of documents**: three offset rects, front one with a title bar and text bars. Means "many of these".
- **Counter chip**: a small pill with a number and a unit in mono (`12 ×`). Use it to show repetition without drawing twelve things.
- **Steps inside the new thing**: two or three white pills inside the blue box, each with a short lowercase mono phrase saying what it does (`reads all three`, `ties out the totals`). This is how a scene shows the mechanism without a second slide.

### Four builders, four different pictures

The explainer and each of the three pitches are built by different agents, and the natural result is four copies of "three boxes, an arrow, a blue box, an arrow, a green document". The explainer's mechanism owns the left-to-right flow. The pitches vary the form to fit the idea: a calendar for time won back, a sheet for analysis, lanes for sorting, a chat turn for a conversation, a queue for triage. The brief's "Picture ideas" line is the starting point, and each builder is told what the others are drawing.

### One path per arrow

An arrowhead lands only on the last point of a `<path>`. Three arrows drawn as one path with three `M ... L ...` segments show one arrowhead. Give each arrow its own `<path>`.

### Text fit, again

Most layout failures are a label wider than its box. Count characters before choosing a width: at size 17 with `letter-spacing="2.5"` each character is 12.7 units, so `LAST MONTH'S MEMO` (17 characters) is 216 units and needs a box at least 264 wide. At size 15 with the same spacing each character is 11.5 units.


## Drawing for motion

Motion classes are listed in `slide-types.md` under Motion. How to draw so they work:

- **Draw the finished picture first.** Motion classes only say where an element comes from. If you delete every class, the slide must still be complete and correct, because that is what prints and what `check.py` photographs.
- **Layer a highlight over a gray base to show something being processed.** Draw the gray shape, then the same shape in blue-soft with a blue stroke and `a-fade`, then the label on top. Stagger the delays (`--d:.3s`, `.45s`, `.6s` ...) and the room watches the new thing work through the items. The months in `examples/sections/explain.html` do this.
- **Group what moves together.** A pill and its label go in one `<g class="a-pop">` so they arrive as one object. The `<g>` sits inside the build group, never on it.
- **Tokens that travel** (`a-travel`) are small: a 30 by 40 page, a 24-unit circle, a short pill. Draw each where it lands and give it `--fx`/`--fy` for where it starts. Give three to five tokens the same `--t` and staggered `--d` so they read as a stream, not a pile. At rest they sit at their destination, so place them where a still picture would show sorted items.
- **Bars grow from where they are anchored.** `a-grow` grows from the left edge, `a-grow-y` from the bottom. Draw the bar at its final length.
- **`a-draw` is for solid strokes only.** Add `pathLength="1"` to the path. A dotted connector uses `a-flow` instead.
- **Order the delays the way you would explain it out loud.** Input, the new thing working, the result, the check. About three seconds from first to last. A slide where everything moves at once teaches nothing.
- **One `a-pulse` per slide at most**, on the single thing the eye should land on.
