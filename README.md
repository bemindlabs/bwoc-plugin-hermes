<h1 align="center">bwoc-plugin-hermes</h1>

<p align="center">
  <strong>BWOC → Hermes</strong> plugin adapter — bring the BWOC agent fleet into <a href="https://hermes-agent.nousresearch.com">Hermes</a> (Nous Research).
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <a href="https://bemindlabs.github.io/bwoc-handbook/"><img alt="Handbook" src="https://img.shields.io/badge/docs-BWOC%20Handbook-1f6feb"></a>
  <img alt="Status" src="https://img.shields.io/badge/status-WIP-orange">
  <img alt="Host" src="https://img.shields.io/badge/host-Hermes-8b5cf6">
  <img alt="Part of BWOC" src="https://img.shields.io/badge/part%20of-BWOC-6f42c1">
  <img alt="Runtime" src="https://img.shields.io/badge/runtime-Python-3776ab">
</p>

---

## ✨ Overview

`bwoc-plugin-hermes` is a **Hermes plugin** that registers the [**BWOC**](https://github.com/bemindlabs/BWOC-Framework) agent fleet into a Hermes agent: coordination **tools**, slash/CLI **commands**, **skills**, and a **memory provider** — all wrapping the `bwoc` CLI.

Hermes plugins are Python: a `plugin.yaml` manifest plus a `register(ctx)` entrypoint that calls `ctx.register_tool(...)`, `ctx.register_command(...)`, and friends. Each tool handler shells out to `bwoc` and returns a JSON string.

> [!NOTE]
> **Status: WIP.** Coordination tools, the `hermes bwoc` CLI command, and a memory provider are implemented and unit-tested (`pytest`). Some Hermes host bindings are TODO-guarded pending confirmation — see the [roadmap](#️-roadmap).

## 🧩 What it exposes

| Surface | BWOC capability | Hermes API |
|---|---|---|
| **Tools** | Coordinate the fleet | `ctx.register_tool` → `bwoc list/status/send/run/chat/task/team` |
| **Slash + CLI commands** | Quick fleet ops | `ctx.register_command` · `ctx.register_cli_command` (`hermes bwoc <sub>`) |
| **Skills** | Reuse BWOC skills | `ctx.register_skill` |
| **Memory provider** | Shared deep-memory | `MemoryProvider` subclass → `bwoc memory` |

## 🏗️ How it works

```
Hermes agent  ──tool call──▶  tools.py handler  ──subprocess──▶  bwoc CLI  ──▶  BWOC workspace
                              (register_tool)                               (agents, teams,
                                                                             tasks, memory)
```

Tool schemas live in `schemas.py` (LLM-facing JSON Schema); handlers in `tools.py` return `json.dumps({...})`. The host must have `bwoc` on `PATH`.

## 📋 Prerequisites

- [Hermes](https://hermes-agent.nousresearch.com) (Nous Research)
- Python ≥ 3.10
- The [`bwoc` CLI](https://github.com/bemindlabs/BWOC-Framework) installed and on `PATH`
- 📚 Reference: the [BWOC Handbook](https://bemindlabs.github.io/bwoc-handbook/)
- A BWOC workspace (`bwoc init`) reachable from where Hermes runs

## 📦 Installation

```bash
hermes plugins install bemindlabs/bwoc-plugin-hermes
hermes plugins enable bwoc
```

Or clone into your Hermes plugins directory and enable:

```bash
git clone https://github.com/bemindlabs/bwoc-plugin-hermes ~/.hermes/plugins/bwoc
hermes plugins enable bwoc
```

Then add to `~/.hermes/config.yaml`:

```yaml
plugins:
  enabled:
    - bwoc
```

## 🚀 Usage

```text
# as tools (the agent calls these during a turn)
bwoc_list                  # list registered agents
bwoc_send <agent> ...  # append a message to an agent's inbox
bwoc_run  <agent> ...  # run a single task headless

# as a CLI subcommand
hermes bwoc list
hermes bwoc status <agent>
```

## 🗂️ Repository layout

```
bwoc-plugin-hermes/
├── plugin.yaml                  # manifest (name/version/description/requires_env)
├── pyproject.toml               # packaging
└── bwoc_plugin_hermes/
    ├── __init__.py              # register(ctx) entrypoint
    ├── schemas.py               # tool JSON schemas (LLM-facing)
    ├── tools.py                 # tool handlers (subprocess bwoc)
    └── memory.py                # MemoryProvider bridging `bwoc memory`
```

## 🛠️ Development

```bash
ruff check .                 # lint
ruff format .                # format
pytest -q                    # test
python -m build              # build
```

## 🗺️ Roadmap

- [x] Scaffold: `plugin.yaml`, `register()` entrypoint, packaging
- [x] Coordination tools + schemas (`list/status/send/run/chat/task/team`)
- [x] `hermes bwoc <sub>` CLI command
- [x] `MemoryProvider` bridging `bwoc memory`
- [x] `pytest` coverage
- [ ] Skill re-export (`register_skill`)
- [ ] Confirm Hermes host bindings + smoke test

## 🔗 BWOC host-adapter set

One of five BWOC → host adapters, one per agent host:

| Host | Repo |
|---|---|
| Claude Code | [bwoc-plugin-claude](https://github.com/bemindlabs/bwoc-plugin-claude) |
| OpenAI Codex | [bwoc-plugin-codex](https://github.com/bemindlabs/bwoc-plugin-codex) |
| Antigravity | [bwoc-plugin-agy](https://github.com/bemindlabs/bwoc-plugin-agy) |
| OpenClaw | [bwoc-plugin-openclaw](https://github.com/bemindlabs/bwoc-plugin-openclaw) |
| **Hermes** | [bwoc-plugin-hermes](https://github.com/bemindlabs/bwoc-plugin-hermes) |

## 🙏 Maintainer

Maintained by **Bemind Technology**, part of the BWOC host-adapter set. This connector is **generic**: it ships no agents, teams, or workspace identities of its own — it discovers your fleet from the local `bwoc` workspace at runtime.

## 🤝 Contributing

Issues and PRs welcome. Keep handlers a **thin wrapper over the `bwoc` CLI** — logic belongs in the framework, not here.

## 📄 License

[MIT](LICENSE) © Bemind Technology
