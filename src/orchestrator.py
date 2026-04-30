"""Multi-agent orchestration for CodePhronesis wisdom mining pipeline.

Pipeline Architecture (demonstrating multi-agent collaboration):

  Phase 1: GIT MINING   — extract git history, churn, contributors, blame
  Phase 2: PARALLEL     — PatternMiner (source code) || DecisionTracer (git history)
  Phase 3: QUANTIFY     — DebtQuantifier receives pattern findings for context
  Phase 4: SYNTHESIZE   — WisdomSynthesizer (LONG-CHAIN REASONING) aggregates
                           all findings into the final Wisdom Report

This demonstrates:
  - 4 specialized agents with distinct expertise domains
  - Parallel agent execution (Phase 2)
  - Sequential context handoff (2 → 3 → 4)
  - Long-chain reasoning in the final synthesis stage
  - Full token usage tracking across all agents
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime

import anthropic

from .agents import (
    PatternMiner,
    DecisionTracer,
    DebtQuantifier,
    WisdomSynthesizer,
)
from .utils.token_tracker import TokenTracker
from .utils.git_ops import get_log, get_blame, get_churn, get_contributors


class Orchestrator:
    """Orchestrates the 4-agent CodePhronesis wisdom mining pipeline."""

    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.tracker = TokenTracker()
        self._init_agents()

    def _init_agents(self):
        self.pattern_miner = PatternMiner(self.client, self.tracker)
        self.decision_tracer = DecisionTracer(self.client, self.tracker)
        self.debt_quantifier = DebtQuantifier(self.client, self.tracker)
        self.wisdom_synthesizer = WisdomSynthesizer(self.client, self.tracker)

    # ── Public API ────────────────────────────────────────────

    def run(self, repo_path: str) -> str:
        """Execute the full 4-phase wisdom mining pipeline and return the report."""
        self.tracker.start()
        repo_path = os.path.abspath(repo_path)

        # Phase 1: Git Mining
        git_context = self._phase1_git_mining(repo_path)

        # Phase 2: Parallel Analysis
        findings = self._phase2_parallel_analysis(repo_path, git_context)

        # Phase 3: Quantification
        debt_findings = self._phase3_quantify(repo_path, findings, git_context)

        # Phase 4: Wisdom Synthesis (long-chain reasoning)
        report = self._phase4_synthesize(findings, debt_findings, git_context, repo_path)

        return report

    # ── Phase 1: Git Mining ───────────────────────────────────

    def _phase1_git_mining(self, repo_path: str) -> dict:
        """Extract git history, churn, contributors, and blame data."""
        commits = get_log(repo_path, max_commits=100)
        churn = get_churn(repo_path, max_files=30)
        contributors = get_contributors(repo_path)

        # Collect source files
        sources = self._ingest_sources(repo_path)

        # Blame for top-churn files
        blame_data: dict[str, list[dict]] = {}
        for fname, _ in churn[:10]:
            blame_data[fname] = get_blame(repo_path, fname)

        return {
            "commits": commits,
            "churn": churn,
            "contributors": contributors,
            "sources": sources,
            "blame_data": blame_data,
        }

    # ── Phase 2: Parallel Analysis ────────────────────────────

    def _phase2_parallel_analysis(self, repo_path: str, git: dict) -> dict[str, str]:
        """Run PatternMiner and DecisionTracer concurrently."""
        sources = git["sources"]
        source_block = self._format_sources(sources)

        # Build git history narrative
        git_narrative = self._build_git_narrative(git)

        tasks = {
            "patterns": (
                self.pattern_miner,
                f"Analyze this codebase for recurring patterns, idioms, and tribal knowledge conventions.\n\n{source_block}"
            ),
            "decisions": (
                self.decision_tracer,
                f"Mine this git history for engineering decisions and recovered rationale.\n\n{git_narrative}\n\n## Source Files for Reference\n{source_block[:8000]}"
            ),
        }

        results: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {
                pool.submit(agent.run, prompt): key
                for key, (agent, prompt) in tasks.items()
            }
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as exc:
                    results[key] = f"**ERROR**: {exc}"

        return results

    # ── Phase 3: Quantification ───────────────────────────────

    def _phase3_quantify(self, repo_path: str, findings: dict[str, str],
                         git: dict) -> str:
        """DebtQuantifier analyzes code with context from PatternMiner."""
        sources = git["sources"]
        source_block = self._format_sources(sources)

        pattern_context = findings.get("patterns", "No pattern analysis available.")
        churn_context = self._format_churn(git["churn"])

        prompt = (
            "Quantify the technical debt in this codebase. Use the pattern analysis "
            "below as context for what conventions exist, and the churn data to "
            "identify high-risk hotspots.\n\n"
            f"## Pattern Analysis Context\n{pattern_context[:4000]}\n\n"
            f"## File Churn Data\n{churn_context}\n\n"
            f"## Source Code\n{source_block}"
        )
        return self.debt_quantifier.run(prompt)

    # ── Phase 4: Wisdom Synthesis ─────────────────────────────

    def _phase4_synthesize(self, findings: dict[str, str], debt_findings: str,
                           git: dict, repo_path: str) -> str:
        """Long-chain reasoning: synthesize ALL findings into the Wisdom Report."""
        prompt_parts = [
            "# Multi-Agent Findings for Synthesis\n",
            f"## Repository: {repo_path}",
            f"## Contributors: {', '.join(f'{name}({count})' for name, count in git['contributors'][:10])}",
            "",
            "## PatternMiner Findings (code conventions, idioms, tribal knowledge)",
            findings.get("patterns", "N/A"),
            "",
            "## DecisionTracer Findings (git archaeology, recovered rationale)",
            findings.get("decisions", "N/A"),
            "",
            "## DebtQuantifier Findings (numeric scores, risk metrics)",
            debt_findings,
            "",
            "## File Churn Top-10",
            self._format_churn(git["churn"]),
            "",
            "---",
            "Synthesize ALL findings above into a comprehensive Wisdom Report.",
            "Cross-reference pattern findings with git decisions to validate conclusions.",
            "Layer debt metrics on top to prioritize recommendations.",
            "Identify at least 5 non-obvious 'wisdom nuggets'.",
            "Generate the complete Wisdom Report as defined in your system instructions.",
        ]
        return self.wisdom_synthesizer.run("\n".join(prompt_parts))

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _ingest_sources(repo_path: str,
                        file_patterns: tuple[str, ...] | None = None) -> dict[str, str]:
        root = Path(repo_path)
        patterns = file_patterns or (".py", ".js", ".ts", ".go", ".java", ".rs", ".rb")
        sources: dict[str, str] = {}
        for pat in patterns:
            for fpath in root.rglob(f"*{pat}"):
                if any(skip in fpath.parts for skip in (
                    "node_modules", ".git", "__pycache__", "venv", ".venv",
                    "dist", "build", ".mypy_cache", ".pytest_cache", ".tox",
                )):
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8")
                    if len(content) > 24000:
                        content = content[:24000] + "\n// ... (truncated)"
                    sources[str(fpath.relative_to(root))] = content
                except Exception:
                    pass
        return sources

    @staticmethod
    def _format_sources(sources: dict[str, str]) -> str:
        if not sources:
            return "(no source files found)"
        blocks = []
        for fname, content in list(sources.items())[:20]:
            ext = fname.rsplit(".", 1)[-1] if "." in fname else ""
            blocks.append(f"### {fname}\n```{ext}\n{content}\n```")
        return "\n\n".join(blocks)

    @staticmethod
    def _build_git_narrative(git: dict) -> str:
        parts = ["# Git History Analysis Data\n"]
        parts.append(f"## Contributors ({len(git['contributors'])} total)")
        for name, count in git["contributors"][:15]:
            parts.append(f"- {name}: {count} commits")

        parts.append(f"\n## Recent Commits ({len(git['commits'])} analyzed)")
        for c in git["commits"][:60]:
            parts.append(f"- `{c.hash[:8]}` {c.author} ({c.date}): {c.subject}")
            if c.body and c.body != c.subject:
                parts.append(f"  > {c.body[:200]}")

        parts.append(f"\n## Top Churn Files")
        for fname, count in git["churn"][:15]:
            parts.append(f"- {fname} ({count} changes)")

        return "\n".join(parts)

    @staticmethod
    def _format_churn(churn: list[tuple[str, int]]) -> str:
        return "\n".join(f"- {fname}: {count} changes" for fname, count in churn[:15])
