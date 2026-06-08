"""Skill re-export: BWOC framework skills -> Hermes skill directories.

A thin, generic generator. It reads the BWOC framework skills from a workspace
(via the read-only `bwoc skill list/show --json` CLI) and writes one Hermes
skill stub per BWOC skill into `<out_dir>/fw-<name>/SKILL.md`. The generated
files are intentionally lean re-export pointers — the real skill spec stays in
the framework at `modules/skills/<name>/SPEC.md`.

Output is host/agent-neutral and gitignored (see `bwoc_plugin_hermes/_skills/`).
`register(ctx)` in `__init__.py` registers each generated dir with Hermes via
`ctx.register_skill(name, path)`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from . import cli


def _skill_list(workspace: str) -> list[dict[str, Any]]:
    """`bwoc skill list --workspace <ws> --json` -> list of skill dicts."""
    result = cli.run_bwoc("skill", "list", "--workspace", workspace, "--json")
    if not result["ok"]:
        raise RuntimeError(
            f"`bwoc skill list` failed (code {result['code']}): {result['stderr'].strip()}"
        )
    data = json.loads(result["stdout"] or "{}")
    return list(data.get("skills", []))


def _skill_show(workspace: str, name: str) -> dict[str, Any]:
    """`bwoc skill show <name> --workspace <ws> --json` -> skill dict."""
    result = cli.run_bwoc(
        "skill", "show", name, "--workspace", workspace, "--json"
    )
    if not result["ok"]:
        raise RuntimeError(
            f"`bwoc skill show {name}` failed (code {result['code']}): "
            f"{result['stderr'].strip()}"
        )
    data = json.loads(result["stdout"] or "{}")
    return dict(data.get("skill", {}))


def _render(skill: dict[str, Any]) -> str:
    """Render a lean re-export SKILL.md for one BWOC framework skill."""
    name = skill["name"]
    desc = (skill.get("description") or "").strip()
    exposes = skill.get("exposes") or []

    # YAML frontmatter is host-neutral; the namespaced Hermes name is fw-<name>.
    lines = [
        "---",
        f"name: bwoc-fw-{name}",
        f"description: {desc}",
        "---",
        "",
        f"# bwoc-fw-{name}",
        "",
        f"Re-exports BWOC framework skill `{name}`.",
        "",
        "## Purpose",
        "",
        desc or f"Bridges the BWOC framework skill `{name}` into the host.",
        "",
        "## Spec",
        "",
        f"Canonical spec: `modules/skills/{name}/SPEC.md` in the BWOC framework "
        "workspace. This file is a generated pointer — do not edit by hand "
        "(regenerate with `python -m bwoc_plugin_hermes.skills`).",
    ]

    if exposes:
        lines += [
            "",
            "## Exposes",
            "",
            *(f"- `{item}`" for item in exposes),
        ]

    return "\n".join(lines) + "\n"


def sync_skills(workspace: str, out_dir: str) -> list[str]:
    """Generate Hermes skill stubs for every BWOC framework skill.

    For each skill returned by `bwoc skill list`, runs `bwoc skill show` and
    writes `<out_dir>/fw-<name>/SKILL.md`. Returns the list of skill names
    generated (empty list is valid — nothing to re-export).
    """
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    for entry in _skill_list(workspace):
        name = entry.get("name")
        if not name:
            continue
        # Re-fetch the full record (list and show share a shape, but show is
        # the documented per-skill detail source).
        skill = _skill_show(workspace, name) or entry
        skill_dir = out_root / f"fw-{name}"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(_render(skill), encoding="utf-8")
        generated.append(name)

    return generated


def _default_out_dir() -> Path:
    """`bwoc_plugin_hermes/_skills/` next to this module."""
    return Path(__file__).resolve().parent / "_skills"


def main() -> int:
    """CLI entrypoint: requires `BWOC_WORKSPACE`; writes into `_skills/`."""
    workspace = os.environ.get("BWOC_WORKSPACE")
    if not workspace:
        raise SystemExit("BWOC_WORKSPACE env is required (path to a BWOC workspace)")

    out_dir = _default_out_dir()
    names = sync_skills(workspace, str(out_dir))
    print(
        f"generated {len(names)} skill(s) into {out_dir}: "
        + (", ".join(names) if names else "(none)")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
