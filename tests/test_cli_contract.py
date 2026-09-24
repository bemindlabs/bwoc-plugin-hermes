"""Contract test: every argv the adapter builds is one a real `bwoc` accepts.

Each wrapper in `cli` is called with every option set, against a stub that
forwards the argv to the real CLI with `--help` appended. The CLI's parser
still rejects an unknown subcommand or flag (non-zero exit), but nothing
executes — so mutating verbs are checked safely, with no workspace.

Runs only when BWOC_CONTRACT_BIN names the `bwoc` to check (CI installs the
latest release); skipped otherwise.
"""

from __future__ import annotations

import os
import stat

import pytest

from bwoc_plugin_hermes import cli

REAL = os.environ.get("BWOC_CONTRACT_BIN")
pytestmark = pytest.mark.skipif(not REAL, reason="set BWOC_CONTRACT_BIN to run")

CALLS = {
    "list": lambda: cli.bwoc_list(status="active", backend="claude"),
    "status": lambda: cli.bwoc_status("agent-x"),
    "status (fleet)": lambda: cli.bwoc_status(),
    "send": lambda: cli.bwoc_send("agent-x", "hi", sender="agent-y", reply_to="m1"),
    "run": lambda: cli.bwoc_run("agent-x", "do", timeout_s=60),
    "task add": lambda: cli.bwoc_task("add", team="t", title="T", deps="a,b", task_id="t1"),
    "task list": lambda: cli.bwoc_task("list", team="t"),
    "task claim": lambda: cli.bwoc_task("claim", team="t", task_id="t1", as_agent="agent-x"),
    "task complete": lambda: cli.bwoc_task("complete", team="t", task_id="t1", as_agent="agent-x"),
    "team create": lambda: cli.bwoc_team("create", team_id="t", members="a,b"),
    "team list": lambda: cli.bwoc_team("list"),
    "team retire": lambda: cli.bwoc_team("retire", team_id="t", yes=True),
    "memory list": lambda: cli.bwoc_memory("list"),
    "memory show --all": lambda: cli.bwoc_memory("show", all_entries=True),
    "memory show": lambda: cli.bwoc_memory("show", name="n"),
    "memory search": lambda: cli.bwoc_memory("search", query="q"),
    "memory put --force": lambda: cli.bwoc_memory("put", name="n", content="c", force=True),
    "memory put --append": lambda: cli.bwoc_memory("put", name="n", content="c", append=True),
    "memory rm": lambda: cli.bwoc_memory("rm", name="n", yes=True),
    "skill list": lambda: cli.run_bwoc("skill", "list", "--workspace", "w", "--json"),
    "skill show": lambda: cli.run_bwoc("skill", "show", "s", "--workspace", "w", "--json"),
}


@pytest.fixture
def forwarding_bwoc(tmp_path, monkeypatch):
    stub = tmp_path / "bwoc"
    err = tmp_path / "stderr"
    stub.write_text(
        f'#!/bin/sh\n"{REAL}" "$@" --help >/dev/null 2>"{err}" || {{ cat "{err}" >&2; exit 2; }}\n'
    )
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setattr(cli, "BWOC_BIN", str(stub))


@pytest.mark.parametrize("name", list(CALLS))
def test_argv_is_accepted_by_the_cli(forwarding_bwoc, name):
    result = CALLS[name]()
    assert result["ok"], f"`{name}` built an argv bwoc rejects: {result['stderr'].strip()}"


def test_a_rejected_argv_fails(forwarding_bwoc):
    # Negative control: the stub really forwards, so a bad argv must fail.
    assert not cli.run_bwoc("fleet", "--json")["ok"]
