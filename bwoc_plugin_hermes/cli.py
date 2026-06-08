"""Safe runner + typed wrappers over the `bwoc` CLI.

Every call shells out to `bwoc` via an argument LIST (never `shell=True`),
so user-supplied strings cannot be interpreted by a shell. This module holds
zero business logic — it only maps verbs to the exact discovered CLI flags.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Optional

BWOC_BIN = "bwoc"


def run_bwoc(*args: str, timeout: Optional[float] = None) -> dict:
    """Run `bwoc <args...>` and return a structured result.

    Returns: {"ok": bool, "stdout": str, "stderr": str, "code": int}.
    Never raises on a non-zero exit; transport/binary errors are surfaced
    as ok=False with a descriptive stderr.
    """
    cmd = [BWOC_BIN, *[str(a) for a in args]]

    if shutil.which(BWOC_BIN) is None:
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"`{BWOC_BIN}` not found on PATH",
            "code": 127,
        }

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "stdout": exc.stdout or "",
            "stderr": f"timed out after {timeout}s",
            "code": 124,
        }
    except OSError as exc:  # binary vanished, permission, etc.
        return {"ok": False, "stdout": "", "stderr": str(exc), "code": 1}

    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "code": proc.returncode,
    }


# --- typed wrappers (exact flags discovered via `bwoc <verb> --help`) -------


def bwoc_list(
    status: Optional[str] = None,
    backend: Optional[str] = None,
    json_out: bool = True,
) -> dict:
    """`bwoc list [--status S] [--backend B] [--json]`."""
    args = ["list"]
    if status:
        args += ["--status", status]
    if backend:
        args += ["--backend", backend]
    if json_out:
        args.append("--json")
    return run_bwoc(*args)


def bwoc_status(agent: Optional[str] = None, json_out: bool = True) -> dict:
    """`bwoc status [NAME] [--json]`. Omit agent for the summary table."""
    args = ["status"]
    if agent:
        args.append(agent)
    if json_out:
        args.append("--json")
    return run_bwoc(*args)


def bwoc_send(
    to: str,
    message: str,
    sender: Optional[str] = None,
    reply_to: Optional[str] = None,
    no_wakeup: bool = True,
) -> dict:
    """`bwoc send <TO> <MESSAGE> [--from F] [--reply-to ID] [--no-wakeup]`.

    `no_wakeup` defaults to True: a programmatic host should not side-effect
    into an interactive tmux session.
    """
    args = ["send", to, message]
    if sender:
        args += ["--from", sender]
    if reply_to:
        args += ["--reply-to", reply_to]
    if no_wakeup:
        args.append("--no-wakeup")
    return run_bwoc(*args)


def bwoc_run(
    agent: str,
    task: str,
    timeout_s: Optional[int] = None,
    json_out: bool = True,
) -> dict:
    """`bwoc run <AGENT> --task <TASK> [--timeout N] [--json]`."""
    args = ["run", agent, "--task", task]
    if timeout_s is not None:
        args += ["--timeout", str(timeout_s)]
    if json_out:
        args.append("--json")
    # Give subprocess a margin over the CLI's own timeout so we capture output.
    sp_timeout = (timeout_s + 30) if timeout_s is not None else None
    return run_bwoc(*args, timeout=sp_timeout)


def bwoc_task(
    action: str,
    team: Optional[str] = None,
    title: Optional[str] = None,
    task_id: Optional[str] = None,
    as_agent: Optional[str] = None,
    deps: Optional[str] = None,
    json_out: bool = True,
) -> dict:
    """`bwoc task <add|list|claim|complete> ...` (shared task list).

    - add:      <TEAM> <TITLE> [--deps a,b] [--id ID]
    - list:     <TEAM>
    - claim:    <TEAM> <TASK> --as <AGENT>
    - complete: <TEAM> <TASK> --as <AGENT>
    """
    args = ["task", action]
    if action == "add":
        if team:
            args.append(team)
        if title:
            args.append(title)
        if deps:
            args += ["--deps", deps]
        if task_id:
            args += ["--id", task_id]
    elif action == "list":
        if team:
            args.append(team)
    elif action in ("claim", "complete"):
        if team:
            args.append(team)
        if task_id:
            args.append(task_id)
        if as_agent:
            args += ["--as", as_agent]
    if json_out:
        args.append("--json")
    return run_bwoc(*args)


def bwoc_team(
    action: str,
    team_id: Optional[str] = None,
    members: Optional[str] = None,
    yes: bool = False,
    json_out: bool = True,
) -> dict:
    """`bwoc team <create|list|retire> ...`.

    - create: <ID> [--members a,b,c]
    - list:   (no args)
    - retire: <ID> [--yes]
    """
    args = ["team", action]
    if action == "create":
        if team_id:
            args.append(team_id)
        if members:
            args += ["--members", members]
    elif action == "retire":
        if team_id:
            args.append(team_id)
        if yes:
            args.append("--yes")
    if json_out:
        args.append("--json")
    return run_bwoc(*args)


def bwoc_memory(
    action: str,
    name: Optional[str] = None,
    query: Optional[str] = None,
    content: Optional[str] = None,
    all_entries: bool = False,
    force: bool = False,
    append: bool = False,
    yes: bool = False,
    json_out: bool = True,
) -> dict:
    """`bwoc memory <list|show|search|put|rm> ...` (workspace memory).

    - list:   [--json]
    - show:   [NAME | --all] [--json]
    - search: <QUERY> [--json]
    - put:    <NAME> [CONTENT] [--force | --append]
    - rm:     <NAME> [--yes]

    Note: `--json` is honoured by list/show(--all)/search; put/rm ignore it.
    """
    args = ["memory", action]
    if action == "list":
        if json_out:
            args.append("--json")
    elif action == "show":
        if all_entries:
            args.append("--all")
            if json_out:
                args.append("--json")
        elif name:
            args.append(name)
    elif action == "search":
        if query:
            args.append(query)
        if json_out:
            args.append("--json")
    elif action == "put":
        if name:
            args.append(name)
        if content is not None:
            args.append(content)
        if force:
            args.append("--force")
        if append:
            args.append("--append")
    elif action == "rm":
        if name:
            args.append(name)
        if yes:
            args.append("--yes")
    return run_bwoc(*args)
