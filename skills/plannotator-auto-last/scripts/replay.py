#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Replay real Claude Code turns through the hook's decide() and grow the test corpus.

Subcommands
    turns   List the turn ends in one session with the hook's decision for each.
            Answers "why didn't plannotator-last open (or why did it)?" for a given turn.
    show    Print one turn's full reply text, its question lines and the decision with evidence.
    add     Save one turn to evals/cases.jsonl with the decision I expected, so future rule changes
            are tested against it.
    sample  Replay many sessions and summarize decisions (sanity check after a rule change).
            With --seed N, also save N turns per decision as baseline cases.

Sessions are Claude Code transcripts (~/.claude/projects/<project>/<session-id>.jsonl).
--session takes a path or a session id; the default is the most recently modified transcript for
the current directory's project (normally the session you are in).

A "turn end" is the last assistant text before the next user prompt (or the end of the file).
Its decision is computed exactly as the Stop hook would have seen it: last_assistant_message is that
text, and the Inbox check looks at tool calls since the preceding user prompt.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plannotator_if_questions import (  # noqa: E402
    Decision,
    assistant_texts,
    decide,
    is_inbox_tool_use,
    is_user_prompt,
    load_transcript,
    question_lines,
)
from run_cases import CASES_FILE, load_cases, write_cases  # noqa: E402

PROJECTS_DIR = Path.home() / ".claude" / "projects"


@dataclass
class Turn:
    index: int
    uuid: str
    timestamp: str
    message: str
    inbox_used: bool

    @property
    def decision(self) -> Decision:
        return decide(self.message, inbox_used=self.inbox_used)


def turns_in(entries: list[dict]) -> list[Turn]:
    turns: list[Turn] = []
    last_text: dict | None = None
    inbox = False

    def close() -> None:
        nonlocal last_text
        if last_text is not None:
            text = [t for t in assistant_texts(last_text) if t.strip()][-1]
            turns.append(Turn(len(turns), last_text.get("uuid", ""), last_text.get("timestamp", ""), text, inbox))
        last_text = None

    for entry in entries:
        if is_user_prompt(entry):
            close()
            inbox = False
        elif entry.get("type") == "assistant":
            content = (entry.get("message") or {}).get("content")
            if isinstance(content, list) and any(isinstance(b, dict) and is_inbox_tool_use(b) for b in content):
                inbox = True
            if any(t.strip() for t in assistant_texts(entry)):
                last_text = entry
    close()
    return turns


def resolve_session(arg: str | None) -> Path:
    if arg:
        path = Path(arg).expanduser()
        if path.is_file():
            return path
        matches = list(PROJECTS_DIR.glob(f"*/{arg}*.jsonl"))
        if len(matches) == 1:
            return matches[0]
        sys.exit(f"session not found or ambiguous: {arg} ({len(matches)} matches)")
    project = PROJECTS_DIR / re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
    candidates = list(project.glob("*.jsonl")) or list(PROJECTS_DIR.glob("*/*.jsonl"))
    if not candidates:
        sys.exit(f"no transcripts under {PROJECTS_DIR}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def pick_turn(turns: list[Turn], index: int) -> Turn:
    try:
        return turns[index]
    except IndexError:
        sys.exit(f"turn {index} out of range (session has {len(turns)} turns)")


def snippet(text: str, width: int = 90) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def cmd_turns(args: argparse.Namespace) -> None:
    path = resolve_session(args.session)
    turns = turns_in(load_transcript(path))
    print(f"session: {path}")
    for turn in turns[-args.limit :]:
        d = turn.decision
        print(f"[{turn.index:>3}] {d.decision:<22} {len(turn.message):>5}ch  {snippet(turn.message)}")
    print("\nUse `show --turn N` for detail, `add --turn N --expected ...` to save a case.")


def cmd_show(args: argparse.Namespace) -> None:
    turn = pick_turn(turns_in(load_transcript(resolve_session(args.session))), args.turn)
    d = turn.decision
    print(f"turn {turn.index}  uuid {turn.uuid}  {turn.timestamp}")
    print(f"decision: {d.decision}\nevidence: {d.detail}\nchars: {len(turn.message)}  inbox_used: {turn.inbox_used}")
    print("question lines:")
    for q in question_lines(turn.message) or ["(none)"]:
        print(f"  - {q}")
    print("\n--- reply ---\n" + turn.message)


def case_from(path: Path, turn: Turn, expected: str, note: str) -> dict:
    return {
        "id": f"{path.stem[:8]}-{turn.uuid[:8]}",
        "expected": expected,
        "note": note,
        "inbox_used": turn.inbox_used,
        "message": turn.message,
        "source": {"session": str(path), "turn_uuid": turn.uuid, "timestamp": turn.timestamp},
    }


def upsert(cases: list[dict], case: dict) -> str:
    for i, existing in enumerate(cases):
        if existing["id"] == case["id"]:
            cases[i] = case
            return "updated"
    cases.append(case)
    return "added"


def cmd_add(args: argparse.Namespace) -> None:
    path = resolve_session(args.session)
    turn = pick_turn(turns_in(load_transcript(path)), args.turn)
    cases = load_cases(CASES_FILE)
    case = case_from(path, turn, args.expected, args.note)
    action = upsert(cases, case)
    write_cases(CASES_FILE, cases)
    actual = turn.decision.decision
    status = "passes" if actual == args.expected else f"FAILS today (hook says {actual})"
    print(f"{action} case {case['id']} expecting {args.expected}: {status}")


def cmd_sample(args: argparse.Namespace) -> None:
    rng = random.Random(args.random_seed)
    sessions = sorted(PROJECTS_DIR.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    sessions = [p for p in sessions if p.stat().st_size > 20_000][: args.sessions]
    counts: collections.Counter[str] = collections.Counter()
    by_decision: dict[str, list[tuple[Path, Turn]]] = collections.defaultdict(list)
    for path in sessions:
        for turn in turns_in(load_transcript(path)):
            counts[turn.decision.decision] += 1
            by_decision[turn.decision.decision].append((path, turn))
    print(f"sessions: {len(sessions)}  turns: {sum(counts.values())}")
    for decision, n in counts.most_common():
        print(f"  {decision:<22} {n}")
        for path, turn in rng.sample(by_decision[decision], min(args.examples, n)):
            print(f"      {path.stem[:8]} [{turn.index}] {snippet(turn.message, 80)}")
    if args.seed:
        cases = load_cases(CASES_FILE)
        added = 0
        for decision, items in by_decision.items():
            for path, turn in rng.sample(items, min(args.seed, len(items))):
                added += upsert(cases, case_from(path, turn, decision, "baseline: decision at seeding time")) == "added"
        write_cases(CASES_FILE, cases)
        print(f"\nseeded {added} baseline cases into {CASES_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("turns", help="list turns in a session with decisions")
    p.add_argument("--session")
    p.add_argument("--limit", type=int, default=15)
    p.set_defaults(func=cmd_turns)

    p = sub.add_parser("show", help="show one turn in full with evidence")
    p.add_argument("--session")
    p.add_argument("--turn", type=int, default=-1, help="turn index; negative counts from the end")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("add", help="save a turn to evals/cases.jsonl")
    p.add_argument("--session")
    p.add_argument("--turn", type=int, required=True)
    p.add_argument("--expected", required=True, help="open, or skip:<reason>")
    p.add_argument("--note", required=True, help="why this is the right decision")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("sample", help="replay many sessions and summarize")
    p.add_argument("--sessions", type=int, default=40)
    p.add_argument("--examples", type=int, default=3)
    p.add_argument("--seed", type=int, default=0, help="save N turns per decision as baseline cases")
    p.add_argument("--random-seed", type=int, default=1)
    p.set_defaults(func=cmd_sample)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
