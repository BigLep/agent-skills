#!/usr/bin/env python3
"""Render a deck in headless Chrome: one PNG per slide plus a layout report.

Usage:
  python3 check.py DECK.html                 # PNGs at full size next to the deck, in shots/
  python3 check.py DECK.html --scale 0.5     # half-size PNGs, cheaper to look at for a whole deck
  python3 check.py DECK.html --no-shots      # layout report only
  python3 check.py DECK.html --motion        # also capture two mid-motion frames of every animated slide

Every animation in the template ends on the element's own attributes, so the PNGs show the
finished picture: the same frame the room sees when the motion settles, and the same as print.
--motion adds early frames (shots/<deck>/motion/) so you can see where things start from.

Look at the PNGs. The report catches what measuring can catch (labels crossing shapes,
content running into the footer, clipped prompts, uneven cell rows). Your eyes catch the rest.

Needs Chrome, Edge, Brave, or Chromium installed. If none is found the script says so and exits 2;
fall back to a browser tool or to opening the file by hand.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
ON_PATH = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser", "chrome"]

PROBE = r"""
<script>
(async () => {
  const kill = document.createElement('style');
  kill.textContent = '*{transition:none!important;animation:none!important}';
  document.head.appendChild(kill);
  try { await document.fonts.ready; } catch (e) {}
  const stage = document.getElementById('stage');
  const slides = [...stage.querySelectorAll('.slide')];
  const out = [];
  const short = el => (el.tagName.toLowerCase() + (el.className && el.className.baseVal === undefined && el.className ? '.' + String(el.className).trim().split(/\s+/).join('.') : '')
      + ' "' + (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 48) + '"');
  slides.forEach((s, k) => {
    slides.forEach((o, j) => o.classList.toggle('on', j === k));
    s.querySelectorAll('[data-b]').forEach(e => e.classList.add('in'));
    const issues = [];
    const sr = stage.getBoundingClientRect(), sc = sr.width / 1600;
    const box = { l: 96, r: 1504, t: 56, b: 796 };

    // 1. nothing leaves the content area or reaches the footer
    const seen = new Set();
    s.querySelectorAll('*').forEach(el => {
      if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
      const r = el.getBoundingClientRect();
      if (!r.width && !r.height) return;
      const x0 = (r.left - sr.left) / sc, x1 = (r.right - sr.left) / sc, y0 = (r.top - sr.top) / sc, y1 = (r.bottom - sr.top) / sc;
      const over = Math.max(box.l - x0, x1 - box.r, box.t - y0, y1 - box.b);
      if (over > 2) {
        if ([...seen].some(p => p.contains(el))) return;
        seen.add(el);
        issues.push('OVERFLOW ' + Math.round(over) + 'px past the content area: ' + short(el));
      }
    });

    // 2. clipped boxes
    s.querySelectorAll('pre, .ask, .pane, .board, .prompt, .need, .strip, .cell, .side, .stat, .pick, .fact').forEach(el => {
      if (el.scrollHeight > el.clientHeight + 2) issues.push('CLIPPED ' + (el.scrollHeight - el.clientHeight) + 'px of content is cut off inside ' + short(el));
      if (el.scrollWidth > el.clientWidth + 2) issues.push('CLIPPED sideways inside ' + short(el));
    });

    // 3. pictures that got squeezed
    s.querySelectorAll('svg').forEach(v => {
      const r = v.getBoundingClientRect();
      if (r.height / sc < 140) issues.push('SQUEEZED picture is only ' + Math.round(r.height / sc) + 'px tall. Cut words on this slide so the picture gets room');
    });

    // 4. SVG labels must sit inside a shape or clear of it, and on the canvas
    s.querySelectorAll('svg text').forEach(t => {
      const g = t.closest('g') || t.closest('svg');
      const shapes = [...g.querySelectorAll('rect,circle')].map(r => r.getBBox());
      const b = t.getBBox(), pad = 6, vb = t.ownerSVGElement.viewBox.baseVal;
      if (!b.width) return;
      const inside = shapes.some(r => b.x >= r.x + pad && b.x + b.width <= r.x + r.width - pad && b.y >= r.y && b.y + b.height <= r.y + r.height + pad);
      const clear = shapes.every(r => b.x + b.width <= r.x || b.x >= r.x + r.width || b.y + b.height <= r.y || b.y >= r.y + r.height);
      const onCanvas = b.x >= vb.x && b.x + b.width <= vb.x + vb.width && b.y >= vb.y && b.y + b.height <= vb.y + vb.height;
      if (!onCanvas) issues.push('LABEL off the canvas: "' + t.textContent.trim() + '". Widen the viewBox or shorten the label');
      else if (!(inside || clear)) issues.push('LABEL crosses a shape edge: "' + t.textContent.trim() + '". Widen the shape or shorten the label');
    });

    // 5. rows line up across cells
    ['h3', 'p'].forEach(sel => {
      const lines = [...s.querySelectorAll('.cell ' + sel)].map(h => Math.round(h.getBoundingClientRect().height / parseFloat(getComputedStyle(h).lineHeight)));
      if (new Set(lines).size > 1) issues.push('UNEVEN cell ' + sel + ' line counts ' + JSON.stringify(lines) + '. Make every ' + (sel === 'h3' ? 'claim' : 'sentence') + ' take the same number of lines');
    });

    // 6. reading text size
    s.querySelectorAll('h1,h2,h3,p,li b,pre').forEach(el => {
      if (el.closest('svg')) return;
      const px = parseFloat(getComputedStyle(el).fontSize);
      if (px < 26 && !el.classList.contains('cap')) issues.push('SMALL text at ' + px + 'px: ' + short(el));
    });

    const motion = s.querySelectorAll('.a-fade,.a-rise,.a-pop,.a-grow,.a-grow-y,.a-dim,.a-draw,.a-flow,.a-travel,.a-pulse,.a-count').length;
    out.push({ slide: k + 1, frag: s.dataset.frag || '', motion, issues: [...new Set(issues)] });
  });
  const pre = document.createElement('pre');
  pre.id = 'wdtm-report';
  pre.textContent = 'WDTM_' + 'BEGIN' + JSON.stringify(out) + 'WDTM_' + 'END';
  document.body.appendChild(pre);
})();
</script>
"""


def find_browser():
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    for c in CANDIDATES:
        if Path(c).exists():
            return c
    for n in ON_PATH:
        p = shutil.which(n)
        if p:
            return p
    return None


def run(browser, args, done, timeout=60):
    """Start headless Chrome, wait until done() says the work is finished, then stop it.

    Chrome often keeps running after a headless screenshot or DOM dump, so waiting for it
    to exit on its own can hang. We poll for the result instead.
    """
    profile = tempfile.mkdtemp(prefix="wdtm-chrome-")
    out_path = Path(profile) / "stdout.txt"
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           "--hide-scrollbars", "--user-data-dir=" + profile] + args
    try:
        with open(out_path, "w") as out, open(os.devnull, "w") as err:
            proc = subprocess.Popen(cmd, stdout=out, stderr=err)
            start = time.time()
            while time.time() - start < timeout:
                if proc.poll() is not None:
                    break
                try:
                    text = out_path.read_text(errors="replace")
                except OSError:
                    text = ""
                if done(text):
                    break
                time.sleep(0.25)
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        return out_path.read_text(errors="replace")
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def file_settled(path):
    """True once a screenshot exists and has stopped growing."""
    state = {"size": -1, "same": 0}

    def check(_text):
        try:
            size = Path(path).stat().st_size
        except OSError:
            return False
        if size > 0 and size == state["size"]:
            state["same"] += 1
        else:
            state["same"] = 0
        state["size"] = size
        return state["same"] >= 2
    return check


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--shots", help="folder for PNGs. Default: shots/<deck name>/ next to the deck")
    ap.add_argument("--scale", type=float, default=1.0, help="PNG scale, 0.5 gives 800 by 450")
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--motion", action="store_true", help="also capture early frames of animated slides, to check where motion starts")
    args = ap.parse_args()

    deck = Path(args.deck).resolve()
    if not deck.exists():
        sys.exit(f"No deck at {deck}")
    browser = find_browser()
    if not browser:
        print("No Chrome, Edge, Brave, or Chromium found. Set CHROME_PATH, or check the deck with a browser tool or by opening it.")
        sys.exit(2)

    src = deck.read_text(encoding="utf-8")
    n = len(re.findall(r'<section\b[^>]*class="[^"]*\bslide\b', src))

    # layout report
    probe = deck.with_name("." + deck.stem + ".probe.html")
    probe.write_text(src.replace("</body>", PROBE + "</body>"), encoding="utf-8")
    try:
        dom = run(browser, ["--window-size=1600,900", "--virtual-time-budget=6000", "--dump-dom", probe.as_uri()],
                  done=lambda text: "WDTM_END" in text)
    finally:
        try:
            probe.unlink()
        except OSError:
            pass
    m = re.search(r"WDTM_BEGIN(.*?)WDTM_END", dom, re.S)
    problems = 0
    if not m:
        print("Could not read the layout report from the browser. Check the PNGs by eye.")
    else:
        import html as _html
        report = json.loads(_html.unescape(m.group(1)))
        for s in report:
            for i in s["issues"]:
                problems += 1
                print(f"slide {s['slide']:>2}  {i}")
        if not problems:
            print(f"Layout report clean across {n} slides.")
        animated = [s["slide"] for s in report if s.get("motion")]
        by_frag = {}
        for s in report:
            by_frag.setdefault(s.get("frag") or "?", []).append(s.get("motion", 0))
        print("Motion: " + ("slides " + ", ".join(map(str, animated)) if animated else "none")
              + "   (" + ", ".join(f"{f} {sum(1 for m in ms if m)}/{len(ms)}" for f, ms in by_frag.items()) + " slides animated)")

    # screenshots
    if not args.no_shots:
        shots = Path(args.shots) if args.shots else deck.parent / "shots" / deck.stem
        shots.mkdir(parents=True, exist_ok=True)
        for old in shots.glob("slide-*.png"):
            old.unlink()

        # a still copy of the deck: fades switched off, so no slide is caught half visible
        still = deck.with_name("." + deck.stem + ".still.html")
        still.write_text(src.replace("</head>", "<style>*{transition:none!important;animation:none!important}</style>"
                                     "<script>window.WDTM_STILL=true</script></head>", 1), encoding="utf-8")

        def shoot(k):
            out = shots / f"slide-{k:02d}.png"
            run(browser, ["--window-size=1600,900", f"--force-device-scale-factor={args.scale}",
                          "--virtual-time-budget=4000", f"--screenshot={out}", still.as_uri() + f"#{k}"],
                done=file_settled(out))
            return out

        try:
            with ThreadPoolExecutor(max_workers=4) as ex:
                outs = list(ex.map(shoot, range(1, n + 1)))
        finally:
            try:
                still.unlink()
            except OSError:
                pass
        made = [o for o in outs if o.exists()]
        print(f"Wrote {len(made)} of {n} PNGs to {shots}")
        for o in made:
            print(f"  {o}")

        if args.motion and m:
            # early frames: builds all in, slide transitions off, motion left running
            moving = deck.with_name("." + deck.stem + ".moving.html")
            moving.write_text(src.replace("</head>", "<style>*{transition:none!important}.slide.on{animation:none!important}</style></head>", 1),
                              encoding="utf-8")
            mdir = shots / "motion"
            mdir.mkdir(exist_ok=True)
            for old in mdir.glob("*.png"):
                old.unlink()
            jobs = [(s["slide"], ms) for s in report if s.get("motion") for ms in (250, 700)]

            def shoot_early(job):
                k, ms = job
                out = mdir / f"slide-{k:02d}-{ms}ms.png"
                run(browser, ["--window-size=1600,900", f"--force-device-scale-factor={args.scale}",
                              f"--virtual-time-budget={ms}", f"--screenshot={out}", moving.as_uri() + f"#{k}"],
                    done=file_settled(out))
                return out
            try:
                with ThreadPoolExecutor(max_workers=4) as ex:
                    early = [o for o in ex.map(shoot_early, jobs) if o.exists()]
            finally:
                try:
                    moving.unlink()
                except OSError:
                    pass
            print(f"Wrote {len(early)} mid-motion frames to {mdir}. They should show things arriving, never a broken layout.")

    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
