"""BWOC -> Hermes plugin.

Registers BWOC fleet coordination as Hermes tools, a `hermes bwoc <sub>` CLI
command, and a `/bwoc` slash command — every surface a thin wrapper over the
`bwoc` CLI (see `cli.py`). A `BwocMemoryProvider` (see `memory.py`) bridges
`bwoc memory`; Hermes discovers memory providers separately, so it is exported
here rather than registered through `ctx`.
"""

from __future__ import annotations

import json

from . import schemas, tools
from .memory import BwocMemoryProvider

__all__ = ["register", "BwocMemoryProvider"]

TOOLSET = "bwoc"

# Subcommands surfaced through `hermes bwoc <sub>` and `/bwoc <sub>`.
_CLI_SUBCOMMANDS = ["list", "status", "send", "run", "chat", "task", "team", "memory"]


def register(ctx) -> None:
    """Hermes plugin entrypoint."""
    # 1) Tools — one per schema, all in the "bwoc" toolset.
    for schema in schemas.ALL_SCHEMAS:
        name = schema["name"]
        ctx.register_tool(
            name=name,
            toolset=TOOLSET,
            schema=schema,
            handler=tools.HANDLERS[name],
            description=schema["description"],
        )

    # 2) CLI command — `hermes bwoc <list|status|send|run|chat|task|team|memory>`.
    ctx.register_cli_command(
        name="bwoc",
        help="Coordinate the BWOC agent fleet (wraps the `bwoc` CLI).",
        setup_fn=_cli_setup,
        handler_fn=_cli_handler,
    )

    # 3) Slash command — `/bwoc <sub> [args...]`.
    ctx.register_command(
        name="bwoc",
        handler=_slash_handler,
        description="Run a bwoc fleet command, e.g. `/bwoc list` or `/bwoc status <agent>`.",
    )

    # 4) Memory provider.
    # TODO: Hermes discovers MemoryProvider subclasses separately from `ctx`.
    # If a registration hook exists, wire it here; otherwise the host picks up
    # `BwocMemoryProvider` via provider discovery. See:
    # https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
    _register_memory(ctx)


def _register_memory(ctx) -> None:
    """Best-effort memory-provider registration across possible Hermes APIs."""
    for attr in ("register_memory_provider", "register_memory"):
        hook = getattr(ctx, attr, None)
        if callable(hook):
            hook(BwocMemoryProvider())
            return
    # No hook on ctx — provider is exported for separate discovery. (See TODO.)


# --- CLI command plumbing --------------------------------------------------


def _cli_setup(parser) -> None:
    """argparse setup for `hermes bwoc <sub> ...`.

    TODO: confirm Hermes passes a stdlib argparse subparser here. See plugin
    docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
    """
    parser.add_argument(
        "subcommand",
        choices=_CLI_SUBCOMMANDS,
        help="bwoc verb to run",
    )
    parser.add_argument(
        "rest",
        nargs="*",
        help="positional args/flags forwarded to `bwoc <subcommand>`",
    )


def _cli_handler(args, **kwargs) -> str:
    """Forward `hermes bwoc <sub> <rest...>` straight to the `bwoc` CLI."""
    from . import cli

    sub = getattr(args, "subcommand", None)
    rest = list(getattr(args, "rest", []) or [])
    if sub:
        result = cli.run_bwoc(sub, *rest)
    else:
        result = {"ok": False, "stdout": "", "stderr": "no subcommand given", "code": 2}
    print(result["stdout"], end="")
    if result["stderr"]:
        print(result["stderr"], end="")
    return json.dumps(result, ensure_ascii=False)


# --- slash command plumbing ------------------------------------------------


def _slash_handler(args, **kwargs) -> str:
    """`/bwoc <sub> [args...]` -> `bwoc <sub> [args...]`.

    `args` may arrive as a raw string or a pre-split list depending on the
    Hermes host; handle both. TODO: confirm slash-arg shape against:
    https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
    """
    from . import cli

    if isinstance(args, str):
        parts = args.split()
    elif isinstance(args, (list, tuple)):
        parts = list(args)
    else:
        parts = []

    if not parts:
        return json.dumps(
            {"ok": False, "stdout": "", "stderr": "usage: /bwoc <sub> [args...]", "code": 2},
            ensure_ascii=False,
        )

    result = cli.run_bwoc(*parts)
    return json.dumps(result, ensure_ascii=False)
