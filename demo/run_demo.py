"""End-to-end demo for CodePhronesis — works with or without an API key.

Usage:
  python demo/run_demo.py              # simulated (no API key needed)
  python demo/run_demo.py --live       # real API calls (needs ANTHROPIC_API_KEY)
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box

# Force plain terminal to avoid Windows gbk Unicode errors
console = Console(force_terminal=False)


def banner():
    console.print()
    console.print(Panel(
        "[bold bright_cyan]CodePhronesis[/]  [dim]phronesis -- practical wisdom mining[/]\n"
        "[italic]Multi-Agent Practical Wisdom Mining from Codebases[/]",
        subtitle="[dim]4 agents / 2-phase parallel / long-chain synthesis[/]",
        box=box.DOUBLE,
        border_style="bright_cyan",
    ))


def phase_header(num: int, name: str, desc: str, style: str = "yellow"):
    console.print(f"\n  [bold {style}]>> Phase {num}: {name}[/]")
    console.print(f"    [dim]{desc}[/]")


def token_table(records: list[dict]) -> Table:
    tbl = Table(title="Token Consumption Across Agents", box=box.ROUNDED, border_style="bright_black")
    tbl.add_column("Agent", style="cyan", no_wrap=True)
    tbl.add_column("Input", justify="right", style="green")
    tbl.add_column("Output", justify="right", style="bright_green")
    tbl.add_column("Cache Hit", justify="right", style="bright_blue")
    tbl.add_column("Duration", justify="right", style="magenta")

    for r in records:
        tbl.add_row(r["name"], f"{r['in']:,}", f"{r['out']:,}",
                     f"{r['cache']:,}", f"{r['ms']:.0f}ms")

    ti = sum(r["in"] for r in records)
    to = sum(r["out"] for r in records)
    tc = sum(r["cache"] for r in records)
    tbl.add_section()
    tbl.add_row("[bold]TOTAL[/]", f"[bold]{ti:,}[/]", f"[bold]{to:,}[/]",
                 f"[bold]{tc:,}[/]", f"[bold]{sum(r['ms'] for r in records)/1000:.1f}s[/]")
    return tbl


def run_simulated():
    """Simulate the full pipeline without API calls -- perfect for demos and screenshots."""
    banner()

    # Phase 1
    phase_header(1, "Git Archaeology",
                 "Extracting commit history, churn, contributors, and file blame...")
    time.sleep(0.3)

    # Execute actual Phase 1 to show real data
    from src.orchestrator import Orchestrator
    orch = Orchestrator(api_key="demo-no-api")
    git = orch._phase1_git_mining(str(Path(__file__).parent.parent))

    console.print(f"    [green][OK][/] {len(git['commits'])} commits, {len(git['contributors'])} contributors, {len(git['sources'])} source files")
    for c in git["commits"][:3]:
        console.print(f"      {c.hash[:8]} | {c.author} | {c.subject[:60]}")

    # Phase 2
    phase_header(2, "Parallel Deep Analysis",
                 "PatternMiner (code conventions) || DecisionTracer (git archaeology)",
                 style="bright_yellow")
    with console.status("[bold bright_yellow]2 agents running in parallel...[/]", spinner="dots"):
        time.sleep(1.0)
    console.print("    [green][OK][/] PatternMiner: 5,241 chars -- 12 conventions, 8 anti-patterns, 5 tribal knowledge patterns")
    console.print("    [green][OK][/] DecisionTracer: 4,893 chars -- 15 engineering decisions recovered, 3 knowledge hotspots")

    # Phase 3
    phase_header(3, "Technical Debt Quantification",
                 "DebtQuantifier -- complexity / coupling / duplication / churn risk",
                 style="bright_magenta")
    with console.status("[bold bright_magenta]DebtQuantifier analyzing...[/]", spinner="dots"):
        time.sleep(0.8)
    console.print("    [green][OK][/] Debt Health Score: [bold]72/100[/] -- WARNING zone")
    console.print("       Complexity: 18/25 | Coupling: 12/25 | Duplication: 8/20 | Churn: 9/15 | Coverage: 15/15")

    # Phase 4
    phase_header(4, "Wisdom Synthesis",
                 "WisdomSynthesizer -- LONG-CHAIN REASONING across all findings (3200 tokens extended thinking)",
                 style="bright_cyan")
    with console.status("[bold bright_cyan]Synthesizing wisdom...[/]", spinner="dots"):
        time.sleep(1.5)
    console.print("    [green][OK][/] Wisdom Report generated: 8,742 chars")

    # Token table
    console.print()
    console.print(token_table([
        {"name": "PatternMiner", "in": 14872, "out": 2341, "cache": 11920, "ms": 3200},
        {"name": "DecisionTracer", "in": 17543, "out": 2897, "cache": 13800, "ms": 4100},
        {"name": "DebtQuantifier", "in": 11280, "out": 1932, "cache": 8450, "ms": 2100},
        {"name": "WisdomSynth.", "in": 24610, "out": 3878, "cache": 7200, "ms": 6800},
    ]))

    # Wisdom Report preview
    console.print()
    console.print(Panel("[bold]Wisdom Report -- Preview[/]", border_style="bright_cyan", box=box.DOUBLE))
    console.print(Markdown("""\
### Executive Summary
The codebase shows strong architectural consistency with a clear 4-agent pipeline pattern.
Three key engineering decisions were recovered from git history: the choice of ephemeral
caching for system prompts, the parallel-then-sequential pipeline design, and the
token-tracking-as-first-class-citizen architecture. Debt is moderate (72/100), concentrated
in the orchestrator module which has grown organically.

### Wisdom Nuggets (Top 3)
1. **The orchestrator's parallel phase was not the first design choice** -- git history shows a
   sequential-only pipeline was committed first, then replaced after the author realized
   PatternMiner and DecisionTracer have no data dependencies.
2. **TokenTracker is a standalone utility despite being tightly coupled to agents** -- this
   was an intentional architectural choice to keep the tracking concern separate, as confirmed
   by the module's zero internal dependencies.
3. **The `thinking_budget` varies by agent role** -- analysis agents get 2000-2400 tokens,
   the synthesizer gets 3200. This tiering reflects practical experimentation visible in
   the commit history where budgets were tuned across 3 separate commits.

### Prioritized Action Plan
| Priority | Action | Impact | Effort | Risk |
|----------|--------|--------|--------|------|
| P0 | Add error recovery to parallel agent phase | High | Med | Low |
| P1 | Extract git operations to async interface | Med | High | Med |
| P2 | Add Wisdom Report versioning/diff | Med | Low | Low |
| P3 | Implement agent result caching layer | Low | High | High |
"""))


def run_live():
    """Run with real Anthropic API calls."""
    repo = str(Path(__file__).parent.parent)
    from src.orchestrator import Orchestrator

    banner()
    orch = Orchestrator()

    with console.status("[bold green]Running full pipeline...[/]", spinner="dots"):
        report = orch.run(repo)

    console.print()
    console.print(token_table([
        {"name": r.agent_name, "in": r.input_tokens, "out": r.output_tokens,
         "cache": r.cache_hit_tokens, "ms": r.duration_ms}
        for r in orch.tracker.records
    ]))
    console.print()
    console.print(Markdown(report[:3000]))
    if len(report) > 3000:
        console.print(f"\n[dim]({len(report):,} total chars -- truncated for display)[/]")


if __name__ == "__main__":
    if "--live" in sys.argv:
        run_live()
    else:
        run_simulated()
