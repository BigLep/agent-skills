---
name: copy-to-clipboard
description: "Copy text to the macOS clipboard, as plain text (default) or with real formatting. Use when the user says /copy-to-clipboard followed by what to copy (new content to generate, or a reference to something in the conversation). Use slack mode when they mention Slack (\"copy this for Slack\", \"paste into Slack\", \"as a slack message\"), and rich mode when they ask for rich text, formatting, HTML, or pasting into Google Docs, Mail, Notion, or similar without naming Slack."
compatibility: "macOS only (uses pbcopy and osascript)."
---

# Copy to Clipboard

The user wants text on their macOS clipboard. Follow these steps.

## Step 1: Determine the text

Based on what the user asked to copy (new content to generate, or a reference to earlier output such as "that slack message" or "the code block above"), either:
- **Generate new content** if the user is asking for something new (e.g., "a slack message explaining X", "an email to Y about Z")
- **Extract from conversation** if the user is referencing prior output (e.g., "your last message", "that code block", "the slack message you wrote")

## Step 2: Pick the mode

| Mode | When | Clipboard contents |
|---|---|---|
| **plain** (default) | Just `/copy-to-clipboard <thing>`, no mention of Slack or formatting | Plain text, markdown preserved as-is |
| **slack** | The user mentions Slack anywhere in the request | HTML flavor (Slack-safe tags, no tables) plus a Slack-style plain fallback |
| **rich** | The user asks for rich text, formatting, or HTML, or names a rich destination (Google Docs, Mail, Notion, Word) without naming Slack | HTML flavor (tables allowed) plus a plain fallback |

If the request is ambiguous, use plain.

## Step 3a: plain mode

Use `printf` piped to `pbcopy`. Use `%s` to avoid escape interpretation, and a quoted heredoc to avoid quoting problems:

```bash
printf '%s' "$(cat <<'CLIPBOARD'
<the text>
CLIPBOARD
)" | pbcopy
```

## Step 3b: slack and rich modes

Write two versions of the content, both built from the source content:

1. **HTML**, hand-written. Start it with `<meta charset="utf-8">` so non-ASCII characters survive. You may check for `pandoc` (`command -v pandoc`) and use it if present, but it is usually not installed; hand-written HTML is the normal path.
2. **Plain-text fallback**, used by apps that ignore HTML.

Then set both flavors with the helper script that lives next to this file. It uses JXA and `NSPasteboard`, takes the content from environment variables, and needs no temp files, hex encoding, or cleanup. Replace `<skill-dir>` with the absolute path of the directory containing this SKILL.md:

```bash
CLIP_HTML="$(cat <<'HTML'
<meta charset="utf-8">
<the html>
HTML
)" CLIP_TEXT="$(cat <<'TEXT'
<the plain fallback>
TEXT
)" osascript -l JavaScript <skill-dir>/set-clipboard.js
```

It prints `ok: html=N chars, text=N chars` on success and fails loudly if either value is empty. Content goes through the environment, so the combined size is limited to roughly 1 MB, which is far more than any message needs.

### slack mode rules

- **No tables.** Slack cannot render them in any paste flavor. Convert each table row to a `<ul><li>` bullet (e.g. `<li><b>Name</b>: value, value</li>`).
- Use only tags Slack's composer honours: `<b>`, `<i>`, `<a href>`, `<ul>`/`<li>`, `<code>`, `<pre>`, `<blockquote>`, `<br>`. No headings: turn a heading into a `<b>` line.
- Plain fallback: Slack's own `*bold*` (single asterisk), `_italic_`, bare URLs instead of `[text](url)`, and `-` bullets.

### rich mode rules

- Any normal HTML is fine: headings, lists, links, code, and real `<table>` markup for tables.
- Plain fallback: the original markdown, so a destination that only takes text still gets something readable.
- If the user names a destination that cannot render tables (Slack, Teams chat, Discord, a chat app), convert tables to bullets as in slack mode.

## Step 4: Verify (slack and rich modes, always)

Run both checks and show the output to the user:

```bash
osascript -e 'clipboard info'   # expect «class HTML» plus string / Unicode text, all with non-zero sizes
pbpaste | head -3               # confirm the plain fallback is the real content
```

If `«class HTML»` is missing, a size is zero, or `pbpaste` shows anything other than the start of the intended fallback, fix it before confirming.

## Step 5: Confirm

Reply with a short confirmation; do not reprint the full text. Name the mode used and anything that was transformed, e.g. "Copied for Slack (HTML + plain fallback); the table was converted to bullets."

## Failure modes (these all happened)

- **Do not use RTF** (`textutil -convert rtf | pbcopy`). It produces an RTF-only clipboard with no plain-text flavor, and nothing pastes in Slack.
- **Never build the plain fallback from `pbpaste`.** The clipboard may still hold a stale test string, and the fallback silently becomes garbage. Always build it from the source content.
- **Do not skip verification.** Both failures above were invisible without `clipboard info` and `pbpaste`.
- `pbcopy` alone cannot set an HTML flavor; that is why slack and rich modes use the helper script.
