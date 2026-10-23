#!/usr/bin/env python3
"""Stitch slide fragments into one self-contained deck, and lint them on the way.

Usage:
  python3 stitch.py RUN_DIR --topic "Opus 5.5"
  python3 stitch.py RUN_DIR --topic "Opus 5.5" --only pitch-2
  python3 stitch.py RUN_DIR --topic "Opus 5.5" --only explain

RUN_DIR/sections/ holds the fragments, stitched in this order:
  open.html                       title
  explain.html                    the new thing, explained: 4 or 5 animated slides
  context.html                    what I'm working from
  pitch-1.html .. pitch-3.html    one pitch each: divider, pitch, today and with, handoff
  close.html                      pick one, remember

Each fragment is a run of <section class="slide"> elements and nothing else.
The deck is written to RUN_DIR/<topic-slug>.html (or RUN_DIR/preview-<name>.html with --only).
Exit code is 1 when there are errors. The deck is still written so you can look at it.
"""
import argparse
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
MARKER = "<!-- SLIDES -->"

# Text in these does not count against the word budget: labels, not reading text.
SKIP_CLASSES = {"eyebrow", "num", "lbl", "t", "n", "mark", "k", "copy", "top", "src", "srcs", "big", "by", "ask", "go"}
SKIP_TAGS = {"svg", "pre", "script", "style"}
VOID = {"br", "hr", "img", "input", "meta", "link", "rect", "circle", "path", "line", "ellipse", "polygon", "polyline", "use", "stop"}

WORDS_PER_SLIDE_WARN = 105
FRAGMENTS = ["open", "explain", "context", "pitch-1", "pitch-2", "pitch-3", "close"]
PREFIX = {"open": "open-", "explain": "ex-", "context": "ctx-", "close": "close-",
          "pitch-1": "p1-", "pitch-2": "p2-", "pitch-3": "p3-"}
MOTION = {"a-fade", "a-rise", "a-pop", "a-grow", "a-grow-y", "a-dim", "a-draw", "a-flow", "a-travel", "a-pulse", "a-count"}
LOOPS = {"a-flow", "a-travel"}
STYLE_VARS = {"--d", "--t", "--fx", "--fy", "--n"}
HANDOFF_WORDS = 95

BANNED = ["delve", "leverage", "landscape", "tapestry", "robust", "seamless", "crucial", "pivotal",
          "transformative", "journey", "harness", "foster", "elevate", "unlock", "game-changer", "game changer"]


class Prose(HTMLParser):
    """Collects the reading text of each slide, skipping labels and pictures."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.stack = []  # (tag, skipping?)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        if tag == "section" and "slide" in classes:
            self.slides.append([])
        parent_skip = self.stack[-1][1] if self.stack else False
        skip = parent_skip or tag in SKIP_TAGS or bool(classes & SKIP_CLASSES)
        if tag not in VOID:
            self.stack.append((tag, skip))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not self.slides:
            return
        if self.stack and self.stack[-1][1]:
            return
        self.slides[-1].append(data)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "deck"


def slides_of(frag):
    """Split a fragment into its <section class="slide"> blocks."""
    return re.findall(r'<section\b[^>]*class="[^"]*\bslide\b.*?</section>', frag, re.S)


def motion_classes(frag):
    out = []
    for m in re.finditer(r'<([a-zA-Z]+)\b([^>]*)>', frag):
        attrs = m.group(2)
        c = re.search(r'\bclass="([^"]*)"', attrs)
        classes = set(c.group(1).split()) if c else set()
        out.append((m.group(1), attrs, classes))
    return out


def lint(name, frag, errors, warns):
    slides = slides_of(frag)
    n_slides = len(slides)
    if n_slides == 0:
        errors.append(f"{name}: no <section class=\"slide\"> found")
    if name == "open" and n_slides != 1:
        warns.append(f"{name}: has {n_slides} slides. The opening is the title slide only; the explainer follows it")
    if name == "explain":
        if not 4 <= n_slides <= 5:
            (errors if n_slides < 3 or n_slides > 6 else warns).append(
                f"explain: has {n_slides} slides. The explainer is 4 or 5: mechanism, before and now, what changed, what it can't do yet, and one optional")
        if re.search(r'class="slide divider"', frag):
            errors.append("explain: contains a divider. Dividers open pitches only")
        if not re.search(r'class="cells[^"]*\blimits\b', frag):
            errors.append("explain: no limits slide (class=\"cells limits\"). The explainer shows what it can't do yet, from the skeptic research")
        animated = sum(1 for sl in slides if re.search(r'class="[^"]*\ba-[a-z-]+', sl))
        if animated == 0:
            errors.append("explain: no motion at all. The mechanism slide and at least two others animate (see Motion in slide-types.md)")
        elif animated < 3:
            warns.append(f"explain: only {animated} animated slide(s). The explainer is where motion earns its place; aim for at least 3")
    if name.startswith("pitch-"):
        if n_slides not in (3, 4):
            errors.append(f"{name}: has {n_slides} slides, a pitch is 4 (divider, pitch, today and with, handoff) or 3 without today and with")
        if not re.search(r'class="slide divider"', frag):
            errors.append(f"{name}: no divider slide. Every pitch opens on <section class=\"slide divider\">")
        elif not re.search(r'class="because"', frag) or not re.search(r'class="src"', frag):
            errors.append(f"{name}: the divider is missing its reason or its source. The reason and where it came from are the point of the slide")
        if re.search(r'class="tags?"', frag):
            errors.append(f"{name}: impact and effort tags are not shown in the deck. Ranking stays in the brief")
        ask = re.search(r'<div class="ask">(.*?)</div>', frag, re.S)
        if not re.search(r'class="handoff"', frag) or not ask:
            errors.append(f"{name}: no handoff slide with a <div class=\"ask\"> prompt. Every pitch ends with the prompt that carries it to the person's own agent")
        else:
            text = re.sub(r"<[^>]+>", " ", ask.group(1))
            words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’./%$:-]*", text))
            if words > HANDOFF_WORDS:
                warns.append(f"{name}: the handoff prompt is {words} words. Keep it to {HANDOFF_WORDS} so it fits without shrinking type")
            if "http" not in text:
                warns.append(f"{name}: the handoff prompt has no link. The receiving agent has probably never heard of the topic; give it the primary source to read first")
    if name == "context":
        if not re.search(r'class="facts"', frag):
            errors.append("context: no facts grid. The deck shows what it knows about the person and where each fact came from")
        if len(re.findall(r'class="fact[ "]', frag)) and len(re.findall(r'class="src"', frag)) < len(re.findall(r'class="fact[ "]', frag)):
            errors.append("context: a fact has no source chip")
    if name == "close":
        if not re.search(r'class="picks"', frag):
            errors.append("close: no pick slide (class=\"picks\"). The deck ends by asking the person to pick one pitch")
        else:
            n_picks = len(re.findall(r'class="pick"', frag))
            if n_picks != 3:
                errors.append(f"close: the pick slide has {n_picks} cards. It has one per pitch, three")

    # ids carry the fragment's prefix
    pre = PREFIX.get(name)
    if pre:
        for i in re.findall(r'\bid="([^"]+)"', frag):
            if not i.startswith(pre):
                warns.append(f"{name}: id=\"{i}\" should start with {pre}")
                break

    # motion
    for tag, attrs, classes in motion_classes(frag):
        bad = {c for c in classes if c.startswith("a-")} - MOTION
        if bad:
            errors.append(f"{name}: unknown motion class {sorted(bad)}. The classes are {', '.join(sorted(MOTION))}")
        if "data-b=" in attrs and classes & MOTION:
            warns.append(f"{name}: a motion class sits on a [data-b] element. Put it on a child of the build group so the build and the motion don't fight over transform")
        if "a-draw" in classes and 'pathLength="1"' not in attrs:
            errors.append(f"{name}: a-draw on a <{tag}> without pathLength=\"1\". Without it the line draws as dots")
        st = re.search(r'\bstyle="([^"]*)"', attrs)
        if st:
            props = {d.split(":")[0].strip() for d in st.group(1).split(";") if d.strip()}
            if props - STYLE_VARS:
                warns.append(f"{name}: style=\"{st.group(1)[:60]}\". Inline style is for motion timing ({', '.join(sorted(STYLE_VARS))}) only")
    for k, sl in enumerate(slides, 1):
        loops = len(re.findall(r'class="[^"]*\b(a-flow|a-travel)\b', sl))
        if loops > 10:
            warns.append(f"{name} slide {k}: {loops} looping elements. More than about ten reads as noise; let most things settle")
    return n_slides


    if re.search(r"<(script|link|iframe)\b", frag, re.I) or re.search(r"@import", frag, re.I):
        errors.append(f"{name}: contains <script>, <link>, <iframe> or @import. The deck must stay self-contained")
    if re.search(r'\b(src|href)\s*=\s*"(https?:)?//', frag, re.I):
        errors.append(f"{name}: loads an external resource. Draw it as inline SVG instead")
    if re.search(r"<style\b", frag, re.I):
        errors.append(f"{name}: contains a <style> block. Use the classes in the template; the theme is fixed")
    if re.search(r"<(img|image)\b", frag, re.I):
        warns.append(f"{name}: contains an image tag. Pictures are inline SVG so the deck works offline")

    for m in re.finditer(r'(fill|stroke|stop-color|color|background)\s*(=\s*"|:)\s*(#[0-9a-fA-F]{3,8}|rgb)', frag):
        errors.append(f"{name}: hardcoded color near '{frag[m.start():m.end() + 8]}'. Use var(--blue), var(--green), var(--line-2) and friends")
        break
    for bad in re.findall(r'var\(--([a-z0-9-]+)\)', frag):
        if bad not in {"bg", "panel", "panel-2", "line", "line-2", "text", "text-soft", "muted", "blue", "blue-soft",
                       "green", "green-soft", "red", "red-soft", "display", "mono", "n", "s"}:
            errors.append(f"{name}: var(--{bad}) is not a theme token")
            break

    for b in set(re.findall(r'data-b="(\d+)"', frag)):
        if int(b) > 4:
            warns.append(f"{name}: data-b=\"{b}\". Four builds per slide is the ceiling")
    for size in re.findall(r'<text\b[^>]*font-size="([\d.]+)"', frag):
        if float(size) < 13:
            warns.append(f"{name}: SVG text at size {size}. Labels are 15 in a cell, 17 on a board")
            break
    if re.search(r'<text\b(?![^>]*JetBrains Mono)[^>]*>', frag) and not re.search(r'<g\b[^>]*JetBrains Mono', frag):
        warns.append(f"{name}: an SVG <text> without font-family=\"JetBrains Mono\". Sentences belong in HTML captions")
    for m in re.finditer(r'<path\b[^>]*\bd="([^"]*)"[^>]*marker-end', frag):
        if len(re.findall(r"[Mm]", m.group(1))) > 1:
            warns.append(f"{name}: one <path> with marker-end draws several lines ({m.group(1)[:40]}...). Only the last gets an arrowhead; use one path per arrow")
            break
    return n_slides


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--topic", required=True, help="the thing being explained, as the product names it. Keep it under 24 characters for the footer")
    ap.add_argument("--title", help="browser tab title. Default: Why <topic> matters")
    ap.add_argument("--only", help="build a preview from one fragment, for example pitch-2 or explain")
    ap.add_argument("--out", help="output path")
    args = ap.parse_args()

    run = Path(args.run_dir)
    sections = run / "sections"
    if not sections.is_dir():
        sys.exit(f"No sections folder at {sections}")

    if args.only:
        names = [args.only.replace(".html", "")]
    else:
        names = FRAGMENTS

    errors, warns, parts, ids_seen, handoff_at = [], [], [], {}, {}
    total_slides = 0
    for name in names:
        f = sections / f"{name}.html"
        if not f.exists():
            errors.append(f"{name}: missing file {f}")
            continue
        frag = f.read_text(encoding="utf-8")
        # a fragment is slides only; drop anything an agent wrapped around them
        frag = re.sub(r"(?is)^.*?(?=<!--\s*SLIDE|<section\b)", "", frag, count=1)
        frag = re.sub(r"(?is)</section>(?!.*</section>).*$", "</section>", frag, count=1)
        frag = re.sub(r'class="slide on"', 'class="slide"', frag)
        frag = re.sub(r'<section\b(?![^>]*data-frag)', f'<section data-frag="{name}"', frag)
        for k, sl in enumerate(slides_of(frag)):
            if 'class="handoff"' in sl:
                handoff_at[name] = total_slides + k + 1
        total_slides += lint(name, frag, errors, warns)

        for i in re.findall(r'\bid="([^"]+)"', frag):
            if i in ids_seen:
                errors.append(f"{name}: id=\"{i}\" is already used in {ids_seen[i]}. Prefix ids with the fragment's prefix (p2-arw, ex-arw)")
            ids_seen[i] = name
        for ref in set(re.findall(r'url\(#([^)]+)\)', frag)):
            if not re.search(r'\bid="' + re.escape(ref) + '"', frag):
                errors.append(f"{name}: url(#{ref}) points at an id that is not in this fragment")

        parts.append(f"  <!-- ===== {name} ===== -->\n" + frag.strip() + "\n")

    body = "\n".join(parts)
    body = body.replace('class="slide"', 'class="slide on"', 1)

    # pick cards point at "#pitch-N" and "{{pitch-N}}": resolve them to the handoff slide's number
    for ref in set(re.findall(r'(?:href="#|\{\{)(pitch-\d)', body)):
        if ref in handoff_at:
            body = body.replace(f'href="#{ref}"', f'href="#{handoff_at[ref]}"').replace("{{" + ref + "}}", str(handoff_at[ref]))
        elif not args.only:
            errors.append(f"close: a pick card points at {ref}, which has no handoff slide")

    # words
    p = Prose()
    p.feed(body)
    counts = []
    for i, chunks in enumerate(p.slides, 1):
        text = " ".join(" ".join(chunks).split())
        n = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’./%$-]*", text))
        counts.append(n)
        if n > WORDS_PER_SLIDE_WARN:
            warns.append(f"slide {i}: {n} prose words. Explainer and pair slides carry 20 to 45, a pitch slide about 75, the context slide about 90. Cut words, do not shrink type")
        if "—" in text or "–" in text:
            warns.append(f"slide {i}: contains a dash (— or –). Use a comma, a period, or a colon")
        if "!" in text:
            warns.append(f"slide {i}: contains an exclamation point")
        low = text.lower()
        for w in BANNED:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                warns.append(f"slide {i}: uses \"{w}\". Say it with a plain verb")
    if counts and not args.only and sum(counts) > 50 * len(counts):
        warns.append(f"deck: {sum(counts)} prose words over {len(counts)} slides. The deck averages about 40 per slide; pictures carry the rest")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in tpl:
        sys.exit("Template is missing the SLIDES marker")
    topic = html.escape(args.topic)
    if len(args.topic) > 24:
        warns.append(f"topic \"{args.topic}\" is {len(args.topic)} characters. Over 24 crowds the footer; use the short product name")
    title = html.escape(args.title or f"Why {args.topic} matters")
    out = tpl.replace(MARKER, body, 1)
    out = out.replace("<title>Why TOPIC matters</title>", f"<title>{title}</title>")
    out = out.replace("<b>TOPIC</b>", f"<b>{topic}</b>")

    if args.out:
        dest = Path(args.out)
    elif args.only:
        dest = run / f"preview-{names[0]}.html"
    else:
        dest = run / f"{slug(args.topic)}.html"
    dest.write_text(out, encoding="utf-8")

    if not args.only:
        # the full deck replaces the section previews the slide agents made
        import shutil
        for f in run.glob("preview-*.html"):
            f.unlink()
        for d in (run / "shots").glob("preview-*"):
            if d.is_dir():
                shutil.rmtree(d, ignore_errors=True)

    print(f"Wrote {dest.resolve()}")
    print(f"Slides: {total_slides}   Prose words per slide: {counts}")
    for w in warns:
        print(f"WARN   {w}")
    for e in errors:
        print(f"ERROR  {e}")
    if not warns and not errors:
        print("Lint clean.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
