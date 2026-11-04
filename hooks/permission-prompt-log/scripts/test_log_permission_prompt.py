#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8"]
# ///
"""Tests for the permission-prompt-log hook. Run: ./test_log_permission_prompt.py (extra args go to pytest)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from log_permission_prompt import explain, split_command  # noqa: E402

RULES = {
    "allow": ["Bash(git fetch:*)", "Bash(kubectl get:*)", "Bash(ls *)", "Read"],
    "ask": ["Bash(rm *)", "Bash(git push --force*)"],
    "deny": [],
}


def why(command: str, **kw) -> dict:
    return explain("Bash", {"command": command}, kw.get("cwd", "/work/proj"), kw.get("mode", "default"), RULES)


@pytest.mark.parametrize(
    "command, parts",
    [
        ("ls", ["ls"]),
        ("git fetch && git status", ["git fetch", "git status"]),
        ("a | b; c || d", ["a", "b", "c", "d"]),
        ("echo 'a && b'", ["echo 'a && b'"]),
        ('echo "a; b" | wc', ['echo "a; b"', "wc"]),
        ("cmd 2>&1 | tail", ["cmd 2>&1", "tail"]),
        ("cmd &> out.txt", ["cmd &> out.txt"]),
    ],
)
def test_split_command(command, parts):
    assert split_command(command) == parts


def test_ask_rule_wins():
    r = why("rm -rf build")
    assert r["why"] == "ask_rule"
    assert r["matched_ask_rules"] == ["Bash(rm *)"]


def test_no_allow_rule():
    assert why("make build")["why"] == "no_allow_rule"


def test_unmatched_subcommand_names_the_part():
    r = why("git fetch && make build")
    assert r["why"] == "unmatched_subcommand"
    assert r["unmatched_subcommands"] == ["make build"]
    assert "compound" in r["signals"]


def test_fully_unmatched_compound_is_no_allow_rule():
    assert why("make a && make b")["why"] == "no_allow_rule"


def test_unknown_when_allow_matches():
    assert why("git fetch origin")["why"] == "unknown"


def test_signals():
    s = why("ls $(pwd) > /etc/out", cwd="/work/proj")["signals"]
    assert {"command_substitution", "redirect", "outside_cwd_path", "mode:default"} <= set(s)
    assert "outside_cwd_path" not in why("ls /work/proj/src")["signals"]
    assert "redirect" not in why("cmd 2>&1")["signals"]


def test_non_bash_tool():
    assert explain("Read", {"file_path": "/x"}, "/w", "", RULES)["why"] == "unknown"
    assert explain("Edit", {"file_path": "/x"}, "/w", "", RULES)["why"] == "no_allow_rule"


def test_hook_contract(tmp_path):
    """Reads stdin, prints nothing, exits 0, appends one JSON line."""
    log = tmp_path / "log.jsonl"
    event = {
        "session_id": "s1",
        "cwd": str(tmp_path),
        "permission_mode": "default",
        "hook_event_name": "PermissionRequest",
        "tool_name": "Bash",
        "tool_input": {"command": "make build"},
    }
    env = {**os.environ, "PERMISSION_PROMPT_LOG": str(log), "HOME": str(tmp_path)}
    for _ in range(2):
        p = subprocess.run(
            [sys.executable, str(HERE / "log_permission_prompt.py")],
            input=json.dumps(event), capture_output=True, text=True, env=env,
        )
        assert (p.returncode, p.stdout) == (0, "")
    lines = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(lines) == 2
    assert lines[0]["command"] == "make build" and lines[0]["why"] == "no_allow_rule"


def test_bad_input_never_fails(tmp_path):
    env = {**os.environ, "PERMISSION_PROMPT_LOG": str(tmp_path / "l.jsonl")}
    p = subprocess.run(
        [sys.executable, str(HERE / "log_permission_prompt.py")],
        input="not json", capture_output=True, text=True, env=env,
    )
    assert (p.returncode, p.stdout) == (0, "")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, *sys.argv[1:]]))
