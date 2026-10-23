# Slide types

The deck uses napkin's slide types plus the ones built for this skill: **context**, **stats**, **limits**, **divider**, **pitch**, **handoff**, and **pick**. All of them live in `assets/template.html`. Finished examples are in `examples/sections/`.

## Contents

1. Deck structure
2. Builds, motion, words, chrome, ids
3. The opening: title, context
4. The explainer: mechanism, before and now, what changed, stats, limits
5. A pitch: divider, pitch, today and with, handoff
6. The close: pick, remember
7. Napkin base types: hierarchy, mechanism, cells, pair, remember, steps
8. Checking by hand

## Deck structure

| Fragment | Slides | Written by |
|---|---|---|
| `open.html` | title | you |
| `explain.html` | mechanism, before and now, what changed, (stats or hierarchy), limits | the explainer agent |
| `context.html` | what I'm working from | you |
| `pitch-1.html` to `pitch-3.html` | divider, pitch, today and with, handoff | one pitch agent each |
| `close.html` | pick, remember | you |

That is about 21 slides, in two halves. The first half teaches the new thing until the person could explain it to a colleague. The second half pitches three ideas and hands each one off. A pitch is a pitch, not a plan: it makes the case, and the handoff prompt carries it into whichever agent the person uses to dig deeper.

The context slide sits between the halves on purpose. By then the room knows what the thing does, and the next question is "so what about me". The context slide answers where the deck's knowledge of the person came from, and the pitches follow.

The deck does not show scores, a quadrant, or impact and effort labels. Ranking decides the order and lives in the brief. A pitch may drop its today-and-with slide when there is no honest before and after.

## Builds

- Put `data-b="n"` on the element that should appear on click n. Slides open with build 1 already visible, so the first build is the resting state.
- Inside SVG, put `data-b` on a `<g>`. In HTML, put it on a wrapper inside the card, never on the card frame.
- Maximum four builds per slide. Use builds where order teaches: a flow, a before and after. A title and a divider never build.

## Motion

The explainer is where the deck teaches, and motion teaches order and change better than a still picture: months lighting up one by one says "it reads all of it", a bar growing says "this takes longer", dots flowing along a connector say "this goes in". The template has a fixed set of motion classes. Fragments never add `<style>` or `<script>`, so these classes are the whole vocabulary.

| Class | Does | Use it for |
|---|---|---|
| `a-fade` | fades in | a highlight layer over a gray shape, a label arriving |
| `a-rise` | fades in while rising 24 units | a result document, a card arriving |
| `a-pop` | scales up from 60% with a small overshoot | badges, checkmarks, step pills, chips |
| `a-grow` | grows from its left edge | time bars, progress, a filled portion of a track |
| `a-grow-y` | grows up from its bottom edge | vertical bars, a stack getting taller |
| `a-dim` | starts at full opacity, settles to the element's own `opacity` | the part the new thing makes unnecessary |
| `a-draw` | draws a solid stroke from start to end. Needs `pathLength="1"` on the element | a line chart, a route, a tick |
| `a-flow` | marches the dots of a dotted connector forward, looping | connectors that carry something into the new thing |
| `a-travel` | moves from an offset to where it is drawn, looping | tokens moving through a pipeline, items being sorted into lanes |
| `a-pulse` | swells gently three times, then rests | the one thing the eye should land on |
| `a-count` | the number in the text runs up from zero (HTML or SVG text) | stats; a cost or a count that should feel big or small |

Timing goes in inline style, and inline style is for timing only: `style="--d:.4s"` delays the start, `style="--t:3s"` sets an `a-travel` loop length, `style="--fx:-300;--fy:0"` says where an `a-travel` element starts, in SVG units relative to where it is drawn.

Rules:

- **Every animation ends on the element's own attributes.** Draw the finished picture; the class only says where it comes from. The resting frame, the printed PDF, and `check.py`'s PNG are the same picture, so a slide never depends on motion to make sense.
- **Motion waits for its build.** Anything inside a `data-b` group starts when that build appears. Put motion classes on children of the build group, never on the group itself, or the build and the motion fight over `transform`.
- **Motion says one thing per slide.** Stagger it so the eye follows the order that teaches (input, then the new thing working, then the payoff), and let a slide's motion finish in about three seconds. Loops (`a-flow`, `a-travel`) are for connectors and moving tokens only; ten or more looping elements on one slide read as noise.
- **The explainer animates; the pitches move lightly.** Every explainer slide except limits should move, and the mechanism slide should be the richest motion in the deck. On pitch slides, flowing connectors, a growing bar, and a check popping in are enough.
- **Motion never carries a fact.** A number that only appears mid-animation, or a state shown only during a loop, is invisible in print and to anyone who looks away. Facts sit in the resting frame.
- The template turns motion off for people who ask their system for reduced motion, and for print.

## Words

Pictures do the first half of the explaining, and the copy finishes the thought. Budgets, in prose words:

| Slide | Budget |
|---|---|
| title | 30 |
| mechanism (explainer) | 25 (headline plus caption) |
| before and now | 35 |
| what changed | 50 |
| stats | 45 |
| limits | 45 |
| context | 90 (six facts of about 14 words) |
| divider | 40 (claim plus reason) |
| pitch | 75 (headline plus three columns of about 22) |
| today and with | 35 |
| handoff | 30, not counting the prompt. The prompt is 95 words or fewer |
| pick | 65 |
| remember | 12 |

Eyebrows, labels, numbers, source chips, the handoff prompt, and text inside SVG do not count. If it will not fit, cut words. Never shrink type: reading text is 26px or larger everywhere.

## Chrome

The footer is fixed: breadcrumb left, dots center, count right. `stitch.py` sets the breadcrumb to `Rundown University › Why it matters › <Topic>` and the `<title>` to `Why <Topic> matters`. Use the short product name for the topic, 24 characters or fewer. The template draws a wide dot where the explainer starts and where each pitch starts, and turns the footer light on dark slides.

## Markers and ids

Every SVG that uses an arrowhead defines its own `<marker>`. Every id in a fragment starts with the fragment's prefix: `open-`, `ex-`, `ctx-`, `p1-`, `p2-`, `p3-`, `close-`. Two SVGs sharing one id means the arrows on the later slide can disappear, because the browser resolves the id to the first copy, which sits in a hidden slide.

## Source chips

A source chip says where a fact about the person came from. It appears on the context slide and on every divider.

```html
<span class="src"><i>Memory</i>Month-end routine</span>
```

The `<i>` is the kind: `Memory`, `File`, `Folder`, `Wiki`, `Notion` (or another connected tool by name), `This chat`, `You told me`, `Inferred`. After it comes the name the person would recognize. Use the file's name, not its path. Keep a chip under 44 characters so it fits on one line.

---

# The opening

## title

Always first, and the only slide in `open.html`. Eyebrow is `Why it matters · <what the topic lives inside>`. The h1 says what the thing newly does, in one sentence of 12 words or fewer, with one phrase in `<em>`. The subline promises both halves: "How it works, then three pitches for a fractional CFO with twelve clients." No builds.

```html
  <!-- SLIDE: title -->
  <section class="slide on">
    <div class="head">
      <span class="eyebrow">Why it matters · AI models</span>
      <h1>Orion 2 holds a <em>whole client file</em> in its head at once.</h1>
      <p class="sub">How it works, then three pitches for a fractional CFO with twelve clients.</p>
    </div>
    <div></div>
  </section>
```

## context · what I'm working from

The only slide in `context.html`. It comes after the explainer and before the first pitch. Six cells from the brief's "What I'm working from" table, in this order: Your role, Who you serve, Your tools, Work that repeats, On your plate now, and Used, not shown. Each cell has a label, one fact of about 14 words, and a source chip.

This slide exists because people often do not know what an AI has remembered about them. Seeing it lets them trust the pitches that follow, and lets them catch a fact that has gone stale. The headline invites the correction.

The last cell gets `class="fact skip"`. It names the kinds of sensitive detail that shaped the ranking without printing them.

Two builds, one per row. Markup: `examples/sections/context.html`.

---

# The explainer

`explain.html`, four or five slides, built by one agent on the strongest visual model. Its job: after these slides, the person could explain the new thing to a colleague, including what it is bad at. Every slide's eyebrow is `<Topic> · <what this slide covers>`. The content of every slide comes from the brief's "The explainer" section, which the synthesis step writes from the research files; the agent draws it and does not add facts.

| # | Slide | Required | Says |
|---|---|---|---|
| E1 | mechanism | yes | what goes in, what the new thing does, what comes out |
| E2 | before and now | yes | the same request, handled by what they had and by the new thing |
| E3 | what changed | yes | the three capabilities the pitches rest on |
| E4 | stats or hierarchy | optional | numbers worth remembering with who measured them, or where the thing lives |
| E5 | limits | yes | what it can't do yet, from the skeptic research |

The finished example of all five is `examples/sections/explain.html`.

## mechanism · the hero picture, animated

The napkin **mechanism** slide (markup below under Napkin base types), drawn on a board with viewBox `0 0 1400 470` and animated. It is the slide the person remembers, so it gets the most care in the deck.

- Three builds: what goes in, the new thing working, what comes out. Motion inside each build plays when that build appears.
- **Show the new thing working, not just sitting there.** Draw its steps inside the blue box, and animate them in the order they happen: the parts it reads light up one after another, the steps pop in after the reading, the result rises out. If the thing sorts, draw items traveling into lanes. If it checks, draw the check landing. The motion should say what a caption would otherwise have to.
- Use the person's world for the input and output when the brief gives one ("A YEAR OF STATEMENTS", "YOUR TALLY FORM"), and the thing's own vocabulary for the inside ("CHOICE", "SCORE"). This is where the deck earns the right to pitch.
- The h2 is the mechanism as one sentence the person could repeat, 10 words or fewer. The caption says what the thing actually holds or does, in one sentence.

## before and now · same request, twice

The napkin **pair** slide. The h2 is one request in quotes. Left is what they had (`✕`, header names it: "Last year's model", "A chat model", "By hand"). Right is the new thing (`✓`, header is the topic name). Draw the same object on both sides so the difference is what the eye lands on, and animate the right side's difference arriving (`a-pop` on each item in turn, `a-grow` on a bar). Eyebrow `<Topic> · Before and now`.

## what changed · three cells

The napkin **cells** slide. Eyebrow `<Topic> · What changed`. Pick the three capabilities the three pitches rest on, so this slide sets up everything after it. Every claim takes the same number of lines, and so does every sentence. Each cell picture gets one small motion: the thing arriving, the check popping, the bar growing.

## stats · optional, numbers worth remembering

Use it when the topic has two or three numbers people will repeat (a price, a speed, a size), and when the research says who measured them. Each stat has a label, the number in `<b class="a-count">`, one sentence, and who measured it in `<span class="by">`. Give the stat about the new thing `class="stat new"` (blue number) and the payoff for the person `class="stat pay"` (green number). If the maker's number and an independent number disagree, show both and label them; that is often the most useful slide in the deck.

One build per stat. Eyebrow `<Topic> · By the numbers`.

```html
  <!-- SLIDE: stats · numbers worth remembering, each with who measured it -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">Orion 2 · By the numbers</span>
      <h2>Three numbers, and <em>who measured them</em>.</h2>
    </div>
    <div class="stats">
      <div class="stat new" data-b="1">
        <span class="lbl">Fits in one request</span>
        <b class="a-count">12</b>
        <p>months of statements for one client.</p>
        <span class="by">Northwind docs, March</span>
      </div>
      <!-- two more; style="--n:2" on .stats for two -->
    </div>
  </section>
```

## hierarchy · optional, where it fits

The napkin **hierarchy** slide. Use it in place of stats when the topic sits inside named containers the person needs to know (a model inside a platform, reachable through three gateways). Animate each level with `a-rise` inside its build.

## limits · what it can't do yet

The napkin **cells** slide with `class="cells limits"`: gray numbers reading LIMIT 01, 02, 03. Always in the explainer, always last. It comes from the skeptic research and the brief, never from the maker's own limitations page alone. The headline is honest and short: "Three places it still needs you." Each cell's sentence says what to do about the limit, and ends with `<span class="by">` naming who found it.

Draw each limit as the failure, in gray: the wrong date in a dashed pill, the long bar, the confident answer with a question mark. Motion is optional here; at most one `a-pulse` on the failure itself.

```html
      <div class="cell" data-b="1">
        <svg viewBox="0 0 400 230" aria-hidden="true" preserveAspectRatio="xMidYMid meet"><!-- the failure, drawn --></svg>
        <span class="num">01</span>
        <h3>Weak at date math.</h3>
        <p>Check every period-end date.<span class="by">Northwind known issues, March</span></p>
      </div>
```

---

# A pitch

Each `pitch-N.html` is four slides built by one agent. The eyebrow of every slide carries the pitch number: `Pitch 0N of 03` on the divider, `Pitch 0N · <what this slide covers>` on the rest. The finished example is `examples/sections/pitch-1.html`.

## divider · the pitch, the reason, and where the reason came from

First slide of every pitch, and the one that makes the deck change gear: dark, with the pitch's number at 300px. It carries three things from the brief, word for word:

- the **claim** as the h2, 14 words or fewer, one phrase in `<em>`
- the **reason** in the Because card, one sentence starting with "You"
- one or two **source chips**

No builds and no picture. `stitch.py` refuses a pitch whose divider has no reason or no source.

```html
  <!-- SLIDE: divider · the pitch, the reason, and where the reason came from -->
  <section class="slide divider">
    <div class="big">01</div>
    <div class="why">
      <span class="eyebrow">Pitch 01 of 03</span>
      <h2>Let it write the <em>month-end close memo</em> for all twelve clients.</h2>
      <div class="because">
        <span class="lbl">Because</span>
        <p>You write a close memo for every client, every month, and each one follows last month's format.</p>
        <div class="srcs">
          <span class="src"><i>Memory</i>Month-end routine</span>
          <span class="src"><i>File</i>Close memo template.docx</span>
        </div>
      </div>
    </div>
  </section>
```

## pitch · picture on top, three columns of copy under it

Second slide. Eyebrow `Pitch 0N · How it works`. The h2 is the brief's pitch headline, seven words or fewer, so it stays on one line and leaves the height to the picture.

The board holds a **scene**, viewBox `0 0 1400 330`: the person's own files and tools on the left in gray, the new thing in the middle in blue, and what they get on the right in green. Name their things as they name them (QUICKBOOKS EXPORT, not DATA SOURCE). The explainer already taught the mechanism, so the scene shows it applied to this person's job, not the mechanism again.

Under the scene, three columns from the brief, each about 22 words:

| Column | Says | Notes |
|---|---|---|
| How it works | what goes in, what the new thing does, what comes out | |
| What changes for you | the difference in their week | gets `class="pay"`, label shows green |
| Proof | who showed it working, and what happened | ends with `<span class="by">` naming the source and date. If it is only claimed, say so |

Three builds for the scene (what they have, the new thing, the payoff). The columns arrive with the last build. Light motion: `a-flow` on connectors, `a-grow` on the green parts, `a-pop` on the check.

The scene does not have to be a left-to-right flow. If the idea is better shown as a calendar week, a sheet with highlighted cells, or lanes, draw that. What stays fixed is the color meaning and that the picture uses this person's nouns.

```html
  <!-- SLIDE: pitch · picture on top, three columns of copy under it -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">Pitch 01 · How it works</span>
      <h2>Three exports in, one memo out.</h2>
    </div>
    <div class="board explain">
      <svg viewBox="0 0 1400 330" role="img" aria-label="..." preserveAspectRatio="xMidYMid meet">
        <!-- scene: see examples/sections/pitch-1.html -->
      </svg>
      <div class="cols" data-b="3">
        <div><span class="lbl">How it works</span><p>...</p></div>
        <div class="pay"><span class="lbl">What changes for you</span><p>...</p></div>
        <div><span class="lbl">Proof</span><p>...<span class="by">Dana Ruiz, Ledger Weekly, 12 Mar</span></p></div>
      </div>
    </div>
  </section>
```

## today and with

Third slide. The napkin **pair** slide with three changes: the eyebrow reads `Pitch 0N · Today and with <Topic>`, the left header reads `Today`, and the right reads `With <Topic>`. The h2 is the brief's "Job in quotes", as the person would say it.

Draw the same object on both sides so the difference is what the eye lands on: the same time bar at two lengths, the same document with and without the green parts. Two unrelated pictures make the reader compare drawing styles. `a-grow` on both bars makes the difference in length land.

## handoff · the prompt that carries the pitch to the person's own agent

Last slide of a pitch. A pitch is meant to be picked up and explored somewhere else, in Claude, ChatGPT, Cursor, or whatever the person uses. The handoff prompt is how it travels, so it has to stand on its own: the other agent has none of the person's memories and has probably never heard of the topic.

Eyebrow `Pitch 0N · Take it further`. The h2 is short and names no product: "Paste this into the agent you use most."

The top panel holds the prompt from the brief, word for word, in `<div class="ask">` with one `<p>` per paragraph. 95 words or fewer, four or five short paragraphs:

1. The idea in one sentence: "I want to dig into one idea with you: ..."
2. About me: one or two facts the person would say out loud, the ones this pitch rests on.
3. The new thing: what it is in one sentence, when it launched, "probably after your training data", and "Read `<b>`URL`</b>` before you answer." The URL is the primary source from the brief.
4. The ask: questions first, then one concrete first deliverable (a test design, a first version, a plan), and "tell me what would make it fail."

Fill-in parts go in `<i>[brackets]</i>` so they show blue. The Copy button is wired up by the template and copies the paragraphs with blank lines between them. Never put a sensitive detail in the prompt: it is written to be pasted into a tool the deck knows nothing about.

The strip under it holds three facts, each 24 characters or fewer so each stays on one line: `Bring` (what to have open or attach), `You'll leave with` (`class="pay"`, the first thing the agent session should produce), and `Watch out` (the one caveat from the brief, plain text, not red).

Two builds: the prompt, then the strip.

```html
  <!-- SLIDE: handoff · the prompt that carries this pitch to the person's own agent -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">Pitch 01 · Take it further</span>
      <h2>Paste this into the agent you use most.</h2>
    </div>
    <div class="handoff">
      <div class="prompt" data-b="1">
        <span class="lbl">Paste this</span>
        <button class="copy" type="button">Copy</button>
        <div class="ask">
          <p>I want to dig into one idea with you: letting Orion 2 draft my month-end close memos.</p>
          <p>About me: I'm a fractional CFO for twelve small companies. Every month I write a close memo per client from a QuickBooks export, bank statements, and last month's memo.</p>
          <p>Orion 2 is a model from Northwind Labs, released in March, probably after your training data. Read <b>https://northwind.example/orion-2</b> before you answer.</p>
          <p>Ask me three questions about how I close a month. Then design a test on <i>[one client]</i> and tell me what would make it fail.</p>
        </div>
      </div>
      <div class="strip" data-b="2">
        <div><span class="lbl">Bring</span><p>One client's exports and memo.</p></div>
        <div class="pay"><span class="lbl">You'll leave with</span><p>A tested plan for one memo.</p></div>
        <div><span class="lbl">Watch out</span><p>It fumbles period-end dates.</p></div>
      </div>
    </div>
  </section>
```

---

# The close

## pick · three pitches, one choice

First slide of the close. Three cards side by side, one per pitch: the number, the pitch name (28 characters or fewer), the reason shortened to about nine words reading on from the label "Because you", and "You'll leave with" from the handoff. Each card is a link to its pitch's handoff slide: write `href="#pitch-N"` and `{{pitch-N}}`, and `stitch.py` fills in the slide number. No times, no scores, no ranking words: the order already says which is easiest to start.

One build per card. Markup: `examples/sections/close.html`.

```html
      <a class="pick" href="#pitch-1" data-b="1">
        <span class="n">01</span>
        <b>Month-end close memo</b>
        <p><span class="lbl">Because you</span>write one for every client, every month.</p>
        <div class="get"><span class="lbl">You'll leave with</span><p>A tested plan for one client's memo.</p></div>
        <span class="go">Handoff · slide {{pitch-1}}</span>
      </a>
```

## remember

Always last. One sentence, 12 words or fewer, in the biggest type on the deck. No picture. Markup under Napkin base types.

---

# Napkin base types

These are unchanged from the napkin skill. In this deck, **mechanism** is the explainer's hero slide (on a taller viewBox, with motion), **pair** is both before-and-now and today-and-with, **cells** is what-changed and limits, **hierarchy** is the explainer's optional where-it-fits slide, and **remember** closes the deck. The word budgets in these napkin sections are napkin's; this deck's budgets are in the table above. The markup here is still; add motion classes as described under Motion.

## hierarchy (where it fits) · nested boxes, one level per build

Optional. Use it when the topic sits inside two or more named containers, or when the topic itself contains parts worth naming (a plugin holds skills, a server holds tools). Draw every level as a nested box, outermost first, one build per level. The topic's box gets the blue stroke wherever it sits; levels inside the topic are drawn in gray as its contents. Caption names the levels in one sentence.

```html
  <!-- SLIDE: hierarchy (where it fits) · nested boxes, one level per build -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">Where it fits</span>
      <h2>A skill lives three levels down.</h2>
    </div>
    <div class="board">
      <svg viewBox="0 0 1400 520" role="img" aria-label="Nested boxes: Claude Code contains a plugin, the plugin contains skills, one skill folder contains SKILL.md" preserveAspectRatio="xMidYMid meet">
        <!-- level 1 -->
        <g data-b="1">
          <rect x="10" y="10" width="1380" height="500" rx="20" fill="var(--panel)" stroke="var(--line-2)" stroke-width="2"/>
          <text x="40" y="50" font-family="JetBrains Mono" font-size="18" letter-spacing="2.5" fill="var(--muted)">CLAUDE CODE</text>
        </g>
        <!-- level 2 -->
        <g data-b="2">
          <rect x="110" y="80" width="1180" height="400" rx="18" fill="var(--panel-2)" stroke="var(--line-2)" stroke-width="2"/>
          <text x="140" y="118" font-family="JetBrains Mono" font-size="18" letter-spacing="2.5" fill="var(--muted)">PLUGIN · product-management</text>
        </g>
        <!-- level 3 -->
        <g data-b="3">
          <rect x="210" y="150" width="980" height="300" rx="16" fill="var(--panel)" stroke="var(--line-2)" stroke-width="2"/>
          <text x="240" y="186" font-family="JetBrains Mono" font-size="18" letter-spacing="2.5" fill="var(--muted)">SKILLS</text>
          <g font-family="JetBrains Mono" font-size="20" fill="var(--text-soft)">
            <rect x="250" y="215" width="280" height="200" rx="12" fill="var(--panel-2)" stroke="var(--line-2)" stroke-width="2"/>
            <text x="275" y="255">write-spec/</text>
            <rect x="275" y="278" width="150" height="8" rx="4" fill="var(--line-2)"/><rect x="275" y="302" width="200" height="8" rx="4" fill="var(--line-2)"/>
            <rect x="560" y="215" width="280" height="200" rx="12" fill="var(--panel-2)" stroke="var(--line-2)" stroke-width="2"/>
            <text x="585" y="255">roadmap-update/</text>
            <rect x="585" y="278" width="150" height="8" rx="4" fill="var(--line-2)"/><rect x="585" y="302" width="200" height="8" rx="4" fill="var(--line-2)"/>
          </g>
        </g>
        <!-- level 4: the one we mean -->
        <g data-b="4">
          <rect x="870" y="215" width="280" height="200" rx="12" fill="var(--blue-soft)" stroke="var(--blue)" stroke-width="3"/>
          <text x="895" y="255" font-family="JetBrains Mono" font-size="20" fill="var(--blue)">proposal/</text>
          <rect x="895" y="280" width="230" height="110" rx="8" fill="var(--panel)" stroke="var(--blue)" stroke-width="2"/>
          <text x="912" y="312" font-family="JetBrains Mono" font-size="18" fill="var(--blue)">SKILL.md</text>
          <rect x="912" y="330" width="120" height="8" rx="4" fill="var(--blue)"/>
          <rect x="912" y="350" width="180" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="912" y="368" width="150" height="7" rx="3.5" fill="var(--line-2)"/>
        </g>
      </svg>
      <p class="cap">Claude Code holds plugins, plugins hold skills, and a skill is one folder.</p>
    </div>
  </section>
```

## mechanism · four builds

The core slide. What goes in, what happens, what comes out, left to right. Builds follow the flow: input, the thing that acts, the key moment, the result. Caption says what the acting thing actually holds or does. If two things act (Claude and a server, a person and a tool), give each its own box in the middle with an 80-unit gap between them, and put the spark and its label in that gap in their own `<g>`, clear of both boxes. Blue goes on the box that is the topic; the other actor is drawn in gray. If the result lands somewhere else (inside an app, in a file), draw that place as the green-stroked box and put the result inside it.

```html
  <!-- SLIDE: mechanism · four builds -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">How it fires</span>
      <h2>Your request goes in. The card shapes what comes out.</h2>
    </div>
    <div class="board">
      <svg viewBox="0 30 1400 360" role="img" aria-label="Your request goes to Claude, Claude matches and reads the skill card, and the result comes out shaped by the card" preserveAspectRatio="xMidYMid meet">
        <defs>
          <marker id="arw-mech" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0 0 L10 5 L0 10 z" fill="var(--muted)"/>
          </marker>
        </defs>
        <g data-b="1">
          <rect x="40" y="130" width="300" height="130" rx="16" fill="var(--panel-2)" stroke="var(--line-2)" stroke-width="2"/>
          <text x="190" y="185" text-anchor="middle" font-family="JetBrains Mono" font-size="22" fill="var(--text-soft)">"write the proposal</text>
          <text x="190" y="217" text-anchor="middle" font-family="JetBrains Mono" font-size="22" fill="var(--text-soft)">for Acme"</text>
          <text x="190" y="315" text-anchor="middle" font-family="JetBrains Mono" font-size="17" letter-spacing="2.5" fill="var(--muted)">YOU ASK</text>
        </g>
        <g data-b="2">
          <path d="M355 195 L455 195" stroke="var(--muted)" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round" marker-end="url(#arw-mech)"/>
          <rect x="475" y="40" width="470" height="310" rx="20" fill="var(--panel)" stroke="var(--blue)" stroke-width="2.5"/>
          <text x="710" y="82" text-anchor="middle" font-family="JetBrains Mono" font-size="17" letter-spacing="2.5" fill="var(--blue)">CLAUDE</text>
          <rect x="580" y="112" width="300" height="200" rx="12" fill="var(--panel-2)" stroke="var(--blue)" stroke-width="3"/>
          <text x="600" y="148" font-family="JetBrains Mono" font-size="18" fill="var(--blue)">SKILL.md</text>
          <rect x="600" y="168" width="190" height="10" rx="5" fill="var(--blue)"/>
          <rect x="600" y="196" width="240" height="8" rx="4" fill="var(--line-2)"/>
          <rect x="600" y="220" width="215" height="8" rx="4" fill="var(--line-2)"/>
          <rect x="600" y="244" width="250" height="8" rx="4" fill="var(--line-2)"/>
          <rect x="600" y="268" width="150" height="8" rx="4" fill="var(--line-2)"/>
        </g>
        <g data-b="3">
          <circle cx="530" cy="150" r="30" fill="var(--blue-soft)"/>
          <path d="M535 128 L521 154 L532 154 L527 174 L543 145 L532 145 Z" fill="var(--blue)"/>
          <text x="530" y="215" text-anchor="middle" font-family="JetBrains Mono" font-size="15" letter-spacing="2" fill="var(--muted)">MATCH</text>
        </g>
        <g data-b="4">
          <path d="M960 195 L1060 195" stroke="var(--muted)" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round" marker-end="url(#arw-mech)"/>
          <rect x="1085" y="60" width="240" height="270" rx="12" fill="var(--panel)" stroke="var(--green)" stroke-width="2.5"/>
          <rect x="1110" y="98" width="130" height="12" rx="6" fill="var(--text)"/>
          <rect x="1110" y="132" width="190" height="8" rx="4" fill="var(--line-2)"/>
          <rect x="1110" y="156" width="170" height="8" rx="4" fill="var(--line-2)"/>
          <rect x="1110" y="180" width="190" height="8" rx="4" fill="var(--line-2)"/>
          <rect x="1110" y="216" width="100" height="10" rx="5" fill="var(--green)"/>
          <rect x="1110" y="244" width="180" height="8" rx="4" fill="var(--line-2)"/>
          <rect x="1110" y="268" width="160" height="8" rx="4" fill="var(--line-2)"/>
          <circle cx="1320" cy="68" r="26" fill="var(--panel)" stroke="var(--green)" stroke-width="3"/>
          <path d="M1308 68 L1316 76 L1332 59" fill="none" stroke="var(--green)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
          <text x="1205" y="375" text-anchor="middle" font-family="JetBrains Mono" font-size="17" letter-spacing="2.5" fill="var(--muted)">YOUR STRUCTURE, YOUR VOICE</text>
        </g>
      </svg>
      <p class="cap">The card holds the steps, the questions to ask first, and what "done" looks like.</p>
    </div>
  </section>
```

## cells · one build per cell

Optional. Three facts worth knowing, or three to five steps of a process. Each cell has a picture that fills the top half, a two-digit number, a bold claim, one sentence. One build per cell, in order. Rows are a shared grid, so numbers, claims and sentences line up across columns even if one claim wraps. Still, write claims of similar length: all one line (about 20 characters at three columns) or all two lines, never mixed. The same goes for the sentences under them: every sentence in a row takes the same number of lines, so if one needs two, cut or pad the others to match. For steps add `class="cells steps"` (numbers read STEP 01) and for four or five columns add `compact` and `style="--n:4"` or `--n:5`; compact claims are 30px so they hold about 16 characters per line. Cell pictures at four or five columns use viewBox `0 0 300 220`.

```html
  <!-- SLIDE: cells · one build per cell -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">Three things to know</span>
      <h2>It's small, it fires on its own, and it holds.</h2>
    </div>
    <div class="cells">
      <div class="cell" data-b="1">
        <svg viewBox="0 0 400 230" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
          <rect x="10" y="20" width="220" height="190" rx="12" fill="var(--panel-2)" stroke="var(--line-2)" stroke-width="2"/>
          <path d="M10 62 L230 62" stroke="var(--line-2)" stroke-width="2"/>
          <text x="30" y="48" font-family="JetBrains Mono" font-size="15" fill="var(--muted)">.claude/skills/</text>
          <rect x="30" y="82" width="150" height="26" rx="6" fill="var(--blue-soft)"/>
          <text x="42" y="100" font-family="JetBrains Mono" font-size="15" fill="var(--blue)">proposal/</text>
          <rect x="30" y="122" width="120" height="24" rx="6" fill="var(--line)"/>
          <rect x="30" y="160" width="140" height="24" rx="6" fill="var(--line)"/>
          <path d="M250 115 L300 115" stroke="var(--muted)" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>
          <rect x="312" y="70" width="78" height="90" rx="10" fill="var(--panel)" stroke="var(--blue)" stroke-width="3"/>
          <text x="351" y="105" text-anchor="middle" font-family="JetBrains Mono" font-size="13" fill="var(--blue)">SKILL.md</text>
          <rect x="326" y="120" width="50" height="6" rx="3" fill="var(--blue)"/>
          <rect x="326" y="134" width="40" height="5" rx="2.5" fill="var(--line-2)"/>
        </svg>
        <span class="num">01</span>
        <h3>A folder with one text file.</h3>
        <p>No code. Plain instructions, the kind you'd hand a new hire.</p>
      </div>
      <div class="cell" data-b="2">
        <svg viewBox="0 0 400 230" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
          <rect x="10" y="85" width="230" height="60" rx="30" fill="var(--panel-2)" stroke="var(--line-2)" stroke-width="2"/>
          <text x="125" y="122" text-anchor="middle" font-family="JetBrains Mono" font-size="19" fill="var(--text-soft)">/proposal Acme</text>
          <path d="M255 115 L300 115" stroke="var(--muted)" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>
          <circle cx="350" cy="115" r="42" fill="var(--blue-soft)"/>
          <path d="M357 85 L337 121 L352 121 L345 147 L367 108 L352 108 Z" fill="var(--blue)"/>
        </svg>
        <span class="num">02</span>
        <h3>Fires on a command, or on its own.</h3>
        <p>Type the name, or just describe the job.</p>
      </div>
      <div class="cell" data-b="3">
        <svg viewBox="0 0 400 230" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
          <g font-family="JetBrains Mono" font-size="15" fill="var(--muted)">
            <text x="10" y="60">RUN 1</text><text x="10" y="123">RUN 2</text><text x="10" y="186">RUN 3</text>
          </g>
          <rect x="90" y="42" width="300" height="26" rx="13" fill="var(--green)"/>
          <rect x="90" y="105" width="300" height="26" rx="13" fill="var(--green)"/>
          <rect x="90" y="168" width="300" height="26" rx="13" fill="var(--green)"/>
        </svg>
        <span class="num">03</span>
        <h3>Same quality every time.</h3>
        <p>Your best prompt, saved once, run by anyone on the team.</p>
      </div>
    </div>
  </section>
```

## pair · without first, with second

Optional, and the strongest slide when you have a real comparison. h2 is the same request in quotes. Left is without (✕, red badge), right is with (✓, green badge). Two builds, without first. Picture per side; text is one bold line plus one soft line.

```html
  <!-- SLIDE: pair · without first, with second -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">Same request, twice</span>
      <h2>"Write the proposal for Acme."</h2>
    </div>
    <div class="pair">
      <div class="side" data-b="1">
        <div class="top"><span class="mark x">✕</span><b>Without the skill</b></div>
        <svg viewBox="0 0 400 180" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
          <rect x="120" y="8" width="160" height="164" rx="10" fill="var(--panel-2)" stroke="var(--line-2)" stroke-width="2"/>
          <rect x="142" y="34" width="80" height="10" rx="5" fill="var(--line-2)"/>
          <rect x="142" y="60" width="116" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="142" y="78" width="104" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="142" y="96" width="116" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="142" y="114" width="90" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="142" y="132" width="110" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="230" y="14" width="66" height="26" rx="13" fill="var(--red-soft)"/>
          <text x="263" y="32" text-anchor="middle" font-family="JetBrains Mono" font-size="13" fill="var(--red)">ACME?</text>
        </svg>
        <p>A tidy, generic proposal.<span>Right format. Wrong company. No pricing logic.</span></p>
      </div>
      <div class="side" data-b="2">
        <div class="top"><span class="mark ok">✓</span><b>With the skill</b></div>
        <svg viewBox="0 0 400 180" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
          <rect x="120" y="8" width="160" height="164" rx="10" fill="var(--panel)" stroke="var(--green)" stroke-width="2.5"/>
          <rect x="142" y="34" width="80" height="10" rx="5" fill="var(--text)"/>
          <rect x="142" y="60" width="52" height="9" rx="4.5" fill="var(--green)"/>
          <rect x="142" y="78" width="116" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="142" y="102" width="62" height="9" rx="4.5" fill="var(--green)"/>
          <rect x="142" y="120" width="104" height="7" rx="3.5" fill="var(--line-2)"/>
          <rect x="142" y="138" width="116" height="7" rx="3.5" fill="var(--line-2)"/>
          <g font-family="JetBrains Mono" font-size="12" fill="var(--muted)">
            <text x="20" y="70">SCOPE</text><text x="20" y="112">BUDGET</text>
          </g>
          <path d="M70 66 L118 66 M70 108 L118 108" stroke="var(--muted)" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round"/>
        </svg>
        <p>It asks for scope and budget first.<span>Then writes in your sections, with your terms.</span></p>
      </div>
    </div>
  </section>
```

## remember

Always last. One sentence, 12 words or fewer, in the biggest type on the deck. No picture.

```html
  <!-- SLIDE: remember -->
  <section class="slide">
    <div></div>
    <div class="remember">
      <span class="k">Remember this</span>
      <p>A skill is how you stop re-explaining yourself to the AI.</p>
    </div>
  </section>
```

## steps skeleton (four columns)

Same markup as cells with the classes and column count changed. Pictures omitted here; draw one per step from the vocabulary.

```html
  <!-- SLIDE: cells (steps) · one build per step -->
  <section class="slide">
    <div class="head">
      <span class="eyebrow">How it runs</span>
      <h2>Four moves, in order.</h2>
    </div>
    <div class="cells steps compact" style="--n:4">
      <div class="cell" data-b="1"><svg viewBox="0 0 300 220" aria-hidden="true" preserveAspectRatio="xMidYMid meet"><!-- picture --></svg><span class="num">01</span><h3>Connect it</h3><p>Sign in once.</p></div>
      <div class="cell" data-b="2"><svg viewBox="0 0 300 220" aria-hidden="true" preserveAspectRatio="xMidYMid meet"><!-- picture --></svg><span class="num">02</span><h3>Ask plainly</h3><p>No command needed.</p></div>
      <div class="cell" data-b="3"><svg viewBox="0 0 300 220" aria-hidden="true" preserveAspectRatio="xMidYMid meet"><!-- picture --></svg><span class="num">03</span><h3>It picks a tool</h3><p>From the menu.</p></div>
      <div class="cell" data-b="4"><svg viewBox="0 0 300 220" aria-hidden="true" preserveAspectRatio="xMidYMid meet"><!-- picture --></svg><span class="num">04</span><h3>You get it back</h3><p>In the chat.</p></div>
    </div>
  </section>
```


---

# Checking by hand

`scripts/check.py` runs these for you. If you have a browser tool and no Chrome for the script, navigate to each slide (the deck sets the URL hash to the slide number, and opening `deck.html#7` shows slide 7 with every build in) and run them in the page. Wait half a second after a key press before measuring so the fade has finished.

Labels inside pictures. Every string returned is a label crossing the edge of a shape or running off the canvas:

```js
[...document.querySelectorAll('.slide.on svg text')].flatMap(t => {
  const g = t.closest('g') || t.closest('svg');
  const shapes = [...g.querySelectorAll('rect,circle')].map(r => r.getBBox());
  const b = t.getBBox(), pad = 6, vb = t.ownerSVGElement.viewBox.baseVal;
  const inside = shapes.some(r => b.x >= r.x + pad && b.x + b.width <= r.x + r.width - pad && b.y >= r.y && b.y + b.height <= r.y + r.height + pad);
  const clear = shapes.every(r => b.x + b.width <= r.x || b.x >= r.x + r.width || b.y + b.height <= r.y || b.y >= r.y + r.height);
  const onCanvas = b.x >= vb.x && b.x + b.width <= vb.x + vb.width && b.y >= vb.y && b.y + b.height <= vb.y + vb.height;
  return (inside || clear) && onCanvas ? [] : [t.textContent.trim()];
})
```

Rows on a cells slide. Both arrays must hold one repeated number:

```js
['h3','p'].map(sel => [...document.querySelectorAll('.slide.on .cell ' + sel)].map(h => Math.round(h.getBoundingClientRect().height / parseFloat(getComputedStyle(h).lineHeight))))
```

Clipped prompt on a handoff slide. Must return false:

```js
(p => p.scrollHeight > p.clientHeight + 2)(document.querySelector('.slide.on .ask'))
```

Motion. To see a slide's resting frame, the one print shows, add `<style>*{animation:none!important}</style>` in the console or look at `check.py`'s PNG. To see where motion starts, run `check.py --motion`, which saves frames at 250 and 700 ms.
