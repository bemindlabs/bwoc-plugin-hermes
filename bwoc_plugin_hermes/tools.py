"""Hermes tool handlers — thin bridges from a tool call to a `bwoc` CLI run.

Each handler has the Hermes signature `handler(params: dict, **kwargs) -> str`
and returns a JSON string. All business logic lives in the `bwoc` CLI; these
handlers only marshal params -> flags and serialize the result.
"""

from __future__ import annotations

import json

from . import cli


def _dumps(result: dict) -> str:
    """Serialize a `run_bwoc` result dict to a compact JSON string."""
    return json.dumps(result, ensure_ascii=False)


def handle_list(params: dict, **kwargs) -> str:
    return _dumps(
        cli.bwoc_list(
            status=params.get("status"),
            backend=params.get("backend"),
        )
    )


def handle_status(params: dict, **kwargs) -> str:
    return _dumps(cli.bwoc_status(agent=params.get("agent")))


def handle_send(params: dict, **kwargs) -> str:
    return _dumps(
        cli.bwoc_send(
            to=params["to"],
            message=params["message"],
            sender=params.get("sender"),
            reply_to=params.get("reply_to"),
        )
    )


def handle_run(params: dict, **kwargs) -> str:
    return _dumps(
        cli.bwoc_run(
            agent=params["agent"],
            task=params["task"],
            timeout_s=params.get("timeout_s"),
        )
    )


def handle_task(params: dict, **kwargs) -> str:
    return _dumps(
        cli.bwoc_task(
            action=params["action"],
            team=params.get("team"),
            title=params.get("title"),
            task_id=params.get("task_id"),
            as_agent=params.get("as_agent"),
            deps=params.get("deps"),
        )
    )


def handle_team(params: dict, **kwargs) -> str:
    return _dumps(
        cli.bwoc_team(
            action=params["action"],
            team_id=params.get("team_id"),
            members=params.get("members"),
        )
    )


def handle_memory(params: dict, **kwargs) -> str:
    return _dumps(
        cli.bwoc_memory(
            action=params["action"],
            name=params.get("name"),
            query=params.get("query"),
            content=params.get("content"),
            all_entries=bool(params.get("all_entries", False)),
            force=bool(params.get("force", False)),
            append=bool(params.get("append", False)),
        )
    )


# Maps schema tool name -> handler, for register() wiring.
HANDLERS = {
    "bwoc_list": handle_list,
    "bwoc_status": handle_status,
    "bwoc_send": handle_send,
    "bwoc_run": handle_run,
    "bwoc_task": handle_task,
    "bwoc_team": handle_team,
    "bwoc_memory": handle_memory,
}
