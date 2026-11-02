#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8"]
# ///
"""Tests for the plannotator-auto-last Stop hook. Run: ./test_decide.py (extra args go to pytest).

Covers the rules directly, the hook's stdin/stdout contract in dry-run mode, Inbox detection from a
transcript, and every case in evals/ (examples plus the private corpus when present).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from plannotator_if_questions import decide, inbox_used_in_turn  # noqa: E402
from run_cases import all_cases, run  # noqa: E402

PAD = "x" * 400


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Short? yes.", "skip:short"),
        (PAD + " All done, nothing to ask.", "skip:no_question"),
        (PAD + " See https://example.com/a?b=1 for details.", "skip:no_question"),
        (PAD + "\nWant me to commit this?", "skip:yes_no_offer"),
        (PAD + "\n- **OK to force push #12?**", "skip:yes_no_offer"),
        (PAD + " Nothing is committed yet. Should I push it?", "skip:yes_no_offer"),
        (PAD + "\nA few things:\n- which branch\n- is the deadline Friday?\n- who reviews", "open"),
        (PAD + "\nWhich region do you want?\nWant me to deploy?", "open"),
        (PAD + "\nWhy does this fail on CI?", "open"),
        (PAD + "\n**Which region should we use?** And who reviews it?", "open"),
        (PAD + " (Is the deadline still Friday?)", "open"),
        # "?" inside code is quoted material, not a question.
        (PAD + "\nThe regex `a?b` and `**ok?**` now match.\nWant me to push it?", "skip:yes_no_offer"),
        (PAD + "\n```\nwhy didn't it open? see SKILL.md\n```\nAll done.", "skip:no_question"),
        (PAD + '\nIt failed because the "?" is followed by `**`.', "skip:no_question"),
        (PAD + "\n1. What is the **start date**?\n2. Any open recalls?", "open"),
        (PAD + "\nWhich worktree, the one at `/tmp/wt`? Or the other one?", "open"),
    ],
)
def test_rules(message: str, expected: str) -> None:
    assert decide(message).decision == expected


def test_inbox_and_loop_guard() -> None:
    assert decide(PAD + "\nWhich one?", inbox_used=True).decision == "skip:inbox"
    assert decide(PAD + "\nWhich one?", stop_hook_active=True).decision == "skip:stop_hook_active"


def _assistant(*blocks: dict) -> dict:
    return {"type": "assistant", "message": {"content": list(blocks)}}


def test_inbox_detection_is_scoped_to_current_turn() -> None:
    inbox_call = {"type": "tool_use", "name": "mcp__plannotator__plannotator_inbox", "input": {}}
    bash_inbox = {"type": "tool_use", "name": "Bash", "input": {"command": "plannotator inbox call send_message"}}
    tool_result = {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}}
    prompt = {"type": "user", "message": {"content": "next question"}}

    assert inbox_used_in_turn([prompt, _assistant(inbox_call), tool_result, _assistant({"type": "text", "text": "hi"})])
    assert inbox_used_in_turn([prompt, _assistant(bash_inbox)])
    for cmd in ["cd x && ~/dotfiles/bin/inbox-send 'hi'", "echo hi | plannotator inbox call send_message -"]:
        assert inbox_used_in_turn([prompt, _assistant({"type": "tool_use", "name": "Bash", "input": {"command": cmd}})])
    # Merely mentioning the commands (e.g. in a grep pattern) doesn't count.
    grep = {"type": "tool_use", "name": "Bash",
            "input": {"command": "grep -l 'plannotator_inbox\\|inbox-send\\|plannotator inbox call' ./*.jsonl"}}
    assert not inbox_used_in_turn([prompt, _assistant(grep)])
    # An Inbox call in an earlier turn doesn't count.
    assert not inbox_used_in_turn([_assistant(inbox_call), prompt, _assistant({"type": "text", "text": "hi"})])


def _run_hook(event: dict) -> str:
    env = {**os.environ, "PLANNOTATOR_IF_QUESTIONS_DRY_RUN": "1"}
    out = subprocess.run(
        [sys.executable, str(HERE / "plannotator_if_questions.py")],
        input=json.dumps(event), capture_output=True, text=True, env=env, check=True,
    )
    return out.stdout.strip()


def test_hook_contract(tmp_path: Path) -> None:
    transcript = tmp_path / "t.jsonl"
    transcript.write_text("\n".join(json.dumps(e) for e in [
        {"type": "user", "message": {"content": "hi"}},
        _assistant({"type": "tool_use", "name": "mcp__plannotator__plannotator_inbox", "input": {}}),
    ]))
    msg = PAD + "\nWhich one?"
    assert _run_hook({"last_assistant_message": msg}) == "open"
    assert _run_hook({"last_assistant_message": msg, "stop_hook_active": True}) == "skip:stop_hook_active"
    assert _run_hook({"last_assistant_message": msg, "transcript_path": str(transcript)}) == "skip:inbox"


CASES = all_cases()


@pytest.mark.parametrize(("source", "case"), CASES, ids=[f"{s}:{c['id']}" for s, c in CASES])
def test_corpus(source: str, case: dict) -> None:
    assert run(case) == case["expected"], case.get("note", "")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", *sys.argv[1:]]))
