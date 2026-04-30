"""Tests for CodePhronesis agents and orchestration."""

from __future__ import annotations

import os
import tempfile
import subprocess
from pathlib import Path

import pytest


# ── Git operations tests (no API key needed) ──────────────

def test_git_log_on_agentflow_repo():
    """Verify git log extraction works on our own repo."""
    from src.utils.git_ops import get_log, get_churn, get_contributors

    repo = Path(__file__).parent.parent
    commits = get_log(str(repo), max_commits=10)
    churn = get_churn(str(repo))
    contribs = get_contributors(str(repo))

    assert isinstance(commits, list)
    assert isinstance(churn, list)
    assert isinstance(contribs, list)


def test_git_ops_on_temp_repo():
    """Verify git operations on a fresh repo."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "init"], cwd=tmp, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp, check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp, check=True, capture_output=True,
        )
        (Path(tmp) / "test.py").write_text("print('hello')\n")
        subprocess.run(["git", "add", "."], cwd=tmp, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "initial commit"],
            cwd=tmp, check=True, capture_output=True,
        )

        from src.utils.git_ops import get_log, get_churn

        commits = get_log(tmp)
        assert len(commits) == 1
        assert commits[0].subject == "initial commit"
        assert commits[0].author == "Test"

        churn = get_churn(tmp)
        assert any("test.py" in f for f, _ in churn)


# ── Token tracker tests ──────────────────────────────────

def test_token_tracker_basic():
    from src.utils.token_tracker import TokenTracker

    t = TokenTracker()
    t.start()
    t.record("TestAgent", 100, 50, cache_hit_tokens=80, duration_ms=1200.0)
    t.record("TestAgent", 200, 100, duration_ms=800.0)

    assert t.total_input == 300
    assert t.total_output == 150
    assert t.total_tokens == 450
    assert t.total_cache_hit == 80
    assert len(t.records) == 2


def test_token_tracker_summary():
    from src.utils.token_tracker import TokenTracker

    t = TokenTracker()
    t.start()
    t.record("AgentA", 1000, 500, cache_hit_tokens=200, duration_ms=3000.0)

    summary = t.summary()
    assert "1,500" in summary  # total tokens formatted
    assert "AgentA" in summary


# ── Agent instantiation tests ────────────────────────────

def test_agents_import():
    from src.agents import (
        BaseAgent,
        PatternMiner,
        DecisionTracer,
        DebtQuantifier,
        WisdomSynthesizer,
    )
    assert BaseAgent is not None
    assert PatternMiner is not None
    assert DecisionTracer is not None
    assert DebtQuantifier is not None
    assert WisdomSynthesizer is not None


def test_agent_properties():
    from src.agents import PatternMiner, DecisionTracer, WisdomSynthesizer

    pm = PatternMiner(None)  # type: ignore — no client needed for property test
    assert pm.agent_name == "PatternMiner"
    assert pm.thinking_budget == 2000
    assert len(pm.system_prompt) > 100

    dt = DecisionTracer(None)  # type: ignore
    assert dt.agent_name == "DecisionTracer"
    assert dt.thinking_budget == 2400

    ws = WisdomSynthesizer(None)  # type: ignore
    assert ws.agent_name == "WisdomSynthesizer"
    assert ws.thinking_budget == 3200
    assert ws.max_tokens == 8192


# ── Orchestrator tests ───────────────────────────────────

def test_orchestrator_init():
    from src.orchestrator import Orchestrator

    orch = Orchestrator(api_key="sk-fake-test-key")
    assert orch.pattern_miner is not None
    assert orch.decision_tracer is not None
    assert orch.debt_quantifier is not None
    assert orch.wisdom_synthesizer is not None
    assert orch.tracker is not None


def test_orchestrator_ingest():
    """Verify source file ingestion."""
    from src.orchestrator import Orchestrator

    orch = Orchestrator(api_key="sk-fake")
    repo = Path(__file__).parent.parent
    sources = orch._ingest_sources(str(repo))

    assert len(sources) > 0
    # Should contain our own source files
    py_files = [f for f in sources if f.endswith(".py")]
    assert len(py_files) > 0


def test_format_sources():
    from src.orchestrator import Orchestrator

    orch = Orchestrator(api_key="sk-fake")
    sources = {"a.py": "print(1)", "b.py": "print(2)"}
    out = orch._format_sources(sources)
    assert "### a.py" in out
    assert "### b.py" in out
    assert "```" in out


def test_format_churn():
    from src.orchestrator import Orchestrator

    orch = Orchestrator(api_key="sk-fake")
    churn = [("a.py", 10), ("b.py", 5)]
    out = orch._format_churn(churn)
    assert "a.py: 10 changes" in out
    assert "b.py: 5 changes" in out
