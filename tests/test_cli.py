"""Smoke test exercising the real `bwoc list` (read-only)."""

from __future__ import annotations

import json

import pytest

from bwoc_plugin_hermes import cli, tools


def test_run_bwoc_list_ok():
    result = cli.run_bwoc("list")
    assert result["ok"] is True, result
    assert result["stdout"].strip(), "expected non-empty stdout from `bwoc list`"
    assert result["code"] == 0


def test_bwoc_list_wrapper_json():
    result = cli.bwoc_list()  # adds --json
    assert result["ok"] is True, result
    assert result["stdout"].strip()


def test_handle_list_returns_json_string():
    out = tools.handle_list({})
    assert isinstance(out, str)
    parsed = json.loads(out)
    assert parsed["ok"] is True
    assert set(parsed) >= {"ok", "stdout", "stderr", "code"}


def test_run_bwoc_missing_binary(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda _name: None)
    result = cli.run_bwoc("list")
    assert result["ok"] is False
    assert result["code"] == 127


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
