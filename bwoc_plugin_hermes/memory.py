"""A Hermes MemoryProvider bridging workspace memory via `bwoc memory`.

The bwoc-backed logic is complete: list/show/search/put map onto the exact
`bwoc memory` subcommands. The base-class import path is the only uncertain
piece — Hermes discovers memory providers separately from tools/commands.

TODO: confirm the real import path + abstract method names for the memory
provider base class. See:
https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
The defensive import below falls back to a local stub so this module always
imports cleanly (and unit tests run) regardless of host availability.
"""

from __future__ import annotations

import json

from . import cli

try:  # pragma: no cover - depends on host runtime
    # TODO: verify this is the correct provider base + module path in Hermes.
    from hermes.memory import MemoryProvider  # type: ignore
except Exception:  # noqa: BLE001 - host not present (e.g. local dev / CI)

    class MemoryProvider:  # type: ignore
        """Local stub so the module imports without the Hermes runtime.

        TODO: replace with the real base class once the import path is
        confirmed; method names below mirror the expected provider contract.
        """

        pass


class BwocMemoryProvider(MemoryProvider):
    """Bridge Hermes' memory interface onto `bwoc memory`.

    Every method is a thin shell-out; no caching or business logic here.
    """

    name = "bwoc"

    # --- read paths --------------------------------------------------------

    def list(self) -> dict:
        """Return all workspace memory entries as parsed JSON (or raw stdout)."""
        result = cli.bwoc_memory("list", json_out=True)
        return self._parse(result)

    def get(self, name: str) -> dict:
        """Return a single memory entry's content."""
        result = cli.bwoc_memory("show", name=name, json_out=False)
        return self._parse(result)

    def search(self, query: str) -> dict:
        """Case-insensitive substring search across memory entries."""
        result = cli.bwoc_memory("search", query=query, json_out=True)
        return self._parse(result)

    # --- write path --------------------------------------------------------

    def put(
        self,
        name: str,
        content: str,
        *,
        force: bool = False,
        append: bool = False,
    ) -> dict:
        """Write (or append/overwrite) a memory entry."""
        result = cli.bwoc_memory(
            "put",
            name=name,
            content=content,
            force=force,
            append=append,
        )
        return self._parse(result)

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def _parse(result: dict) -> dict:
        """Attach a best-effort parsed `data` field when stdout is JSON."""
        out = dict(result)
        stdout = result.get("stdout", "") or ""
        try:
            out["data"] = json.loads(stdout)
        except (ValueError, TypeError):
            out["data"] = None
        return out
