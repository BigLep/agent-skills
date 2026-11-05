#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run every saved case through the hook's decide() and report mismatches.

Cases come from two files in ../evals/:
    examples.jsonl  Made-up cases, committed, so the suite works on a fresh clone.
    cases.jsonl     Real turns from my sessions, gitignored (they contain private text).
                    Grown with `replay.py add` whenever the hook does the wrong thing.

Each line: {"id", "expected", "note", "inbox_used", "unattended"?, "message", "source"?}
"expected" is "open" or "skip:<reason>"; any skip counts as a match only if the reason matches too.

Exit status is 1 if any case fails, so this is safe to run before and after a rule change.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plannotator_if_questions import decide  # noqa: E402

EVALS_DIR = Path(__file__).resolve().parent.parent / "evals"
EXAMPLES_FILE = EVALS_DIR / "examples.jsonl"
CASES_FILE = EVALS_DIR / "cases.jsonl"


def load_cases(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_cases(path: Path, cases: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases))


def all_cases() -> list[tuple[str, dict]]:
    return [(f.name, c) for f in (EXAMPLES_FILE, CASES_FILE) for c in load_cases(f)]


def run(case: dict) -> str:
    return decide(
        case["message"], inbox_used=case.get("inbox_used", False), unattended=case.get("unattended", False)
    ).decision


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true", help="list passing cases too")
    args = parser.parse_args()

    cases = all_cases()
    failures = 0
    for source, case in cases:
        actual = run(case)
        ok = actual == case["expected"]
        failures += not ok
        if args.verbose or not ok:
            mark = "ok  " if ok else "FAIL"
            print(f"{mark} {source}:{case['id']}  expected {case['expected']}, got {actual}  ({case.get('note', '')})")
    print(f"{len(cases) - failures}/{len(cases)} cases pass")
    if not CASES_FILE.is_file():
        print(f"(no private corpus at {CASES_FILE}; only examples were run)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
