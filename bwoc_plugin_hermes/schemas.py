"""LLM-facing JSON Schemas for the BWOC coordination tools.

Shape per Hermes plugin docs:
  {"name","description","parameters":{"type":"object","properties":{...},"required":[...]}}
"""

from __future__ import annotations

LIST_SCHEMA = {
    "name": "bwoc_list",
    "description": "List BWOC agents registered in the workspace. Optionally filter by status or backend.",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by status (exact match), e.g. active, stopped, retired.",
            },
            "backend": {
                "type": "string",
                "description": "Filter by backend (exact match), e.g. claude, codex, ollama.",
            },
        },
        "required": [],
    },
}

STATUS_SCHEMA = {
    "name": "bwoc_status",
    "description": "Show a per-agent health and identity snapshot (read-only). Omit `agent` for the summary table.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "description": "Agent id ('agent-foo') or bare name ('foo'). Omit for the full summary table.",
            }
        },
        "required": [],
    },
}

SEND_SCHEMA = {
    "name": "bwoc_send",
    "description": "Append a message to an agent's inbox. Non-blocking; the agent processes it on its own loop.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Recipient agent id ('agent-foo') or bare name ('foo').",
            },
            "message": {
                "type": "string",
                "description": "Message body to deliver.",
            },
            "sender": {
                "type": "string",
                "description": "Optional sender identity. Default 'user'. Pass an agent name for agent->agent messaging.",
            },
            "reply_to": {
                "type": "string",
                "description": "Optional prior envelope messageId ('msg-<slug>-<hex>') to thread this as a reply.",
            },
        },
        "required": ["to", "message"],
    },
}

RUN_SCHEMA = {
    "name": "bwoc_run",
    "description": "Run a single task on an agent non-interactively (headless) and capture the result.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "description": "Agent id ('agent-foo') or bare name ('foo').",
            },
            "task": {
                "type": "string",
                "description": "Task prompt to deliver to the agent.",
            },
            "timeout_s": {
                "type": "integer",
                "description": "Optional: kill the agent and report timeout after this many seconds.",
            },
        },
        "required": ["agent", "task"],
    },
}

TASK_SCHEMA = {
    "name": "bwoc_task",
    "description": "Manage a team's shared task list: add, list, claim, or complete tasks.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "list", "claim", "complete"],
                "description": "Operation to perform.",
            },
            "team": {
                "type": "string",
                "description": "Team id the task belongs to (required for all actions).",
            },
            "title": {
                "type": "string",
                "description": "Task title (used by 'add').",
            },
            "task_id": {
                "type": "string",
                "description": "Task id (used by 'claim'/'complete'; optional explicit id for 'add').",
            },
            "as_agent": {
                "type": "string",
                "description": "Claiming/completing agent id (required for 'claim'/'complete'; must be a team member).",
            },
            "deps": {
                "type": "string",
                "description": "Optional comma-separated task ids that gate this task ('add' only).",
            },
        },
        "required": ["action"],
    },
}

TEAM_SCHEMA = {
    "name": "bwoc_team",
    "description": "Manage Saṅgha teams: create a team, list teams, or retire a team.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "list", "retire"],
                "description": "Operation to perform.",
            },
            "team_id": {
                "type": "string",
                "description": "Team id (required for 'create'/'retire').",
            },
            "members": {
                "type": "string",
                "description": "Comma-separated agent ids that belong to the team ('create' only).",
            },
        },
        "required": ["action"],
    },
}

MEMORY_SCHEMA = {
    "name": "bwoc_memory",
    "description": "Read or write workspace-level memory (.bwoc/memory/): list, show, search, put, rm.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "show", "search", "put", "rm"],
                "description": "Operation to perform.",
            },
            "name": {
                "type": "string",
                "description": "Entry name (with or without .md). Used by show/put/rm.",
            },
            "query": {
                "type": "string",
                "description": "Substring to search for (used by 'search').",
            },
            "content": {
                "type": "string",
                "description": "Inline entry body (used by 'put').",
            },
            "all_entries": {
                "type": "boolean",
                "description": "For 'show': print every entry concatenated instead of one named entry.",
            },
            "force": {
                "type": "boolean",
                "description": "For 'put': overwrite an existing entry.",
            },
            "append": {
                "type": "boolean",
                "description": "For 'put': append to an existing entry.",
            },
        },
        "required": ["action"],
    },
}

ALL_SCHEMAS = [
    LIST_SCHEMA,
    STATUS_SCHEMA,
    SEND_SCHEMA,
    RUN_SCHEMA,
    TASK_SCHEMA,
    TEAM_SCHEMA,
    MEMORY_SCHEMA,
]
