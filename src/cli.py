"""Command-line interface with rich terminal visualization.

Designed for visual impact — terminal screenshots from this CLI serve as
'proof of usage' for AI developer program applications."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box

from .orchestrator import Orchestrator

console = Console()


def _banner():
    console.print()
    console.print(Panel(
        "[bold bright_cyan]CodePhronesis[/]  [dim]φρόνησις[/]\n"
        "[italic]Multi-Agent Practical Wisdom Mining from Codebases[/]",
        subtitle="[dim]4 agents · 2-phase parallel · long-chain synthesis[/]",
        box=box.DOUBLE,
        border_style="bright_cyan",
    ))


def _phase_header(num: int, name: str, description: str, style: str = "yellow"):
    console.print(f"\n  [bold {style}]▸ Phase {num}: {name}[/]")
    console.print(f"    [dim]{description}[/]")


def _token_table(tracker) -> Table:
    table = Table(
        title="📊 Token Consumption Across Agents",
        box=box.ROUNDED,
        border_style="bright_black",
    )
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Input", justify="right", style="green")
    table.add_column("Output", justify="right", style="bright_green")
    table.add_column("Cache Hit", justify="right", style="bright_blue")
    table.add_column("Duration", justify="right", style="magenta")

    for r in tracker.records:
        table.add_row(
            r.agent_name,
            f"{r.input_tokens:,}",
            f"{r.output_tokens:,}",
            f"{r.cache_hit_tokens:,}",
            f"{r.duration_ms:.0f}ms",
        )

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/]",
        f"[bold]{tracker.total_input:,}[/]",
        f"[bold]{tracker.total_output:,}[/]",
        f"[bold]{tracker.total_cache_hit:,}[/]",
        f"[bold]{tracker.elapsed_seconds:.1f}s[/]",
    )
    return table


@click.group()
def cli():
    """CodePhronesis — Multi-Agent Practical Wisdom Mining.

    Deploy a team of 4 specialized AI agents to mine your codebase
    for engineering decisions, tribal knowledge patterns, technical debt
    metrics, and synthesized wisdom. The output is a Wisdom Report that
    preserves institutional knowledge for current and future developers.

    Pipeline:
      Phase 1 — Git history mining
      Phase 2 — PatternMiner || DecisionTracer (parallel)
      Phase 3 — DebtQuantifier (context-aware analysis)
      Phase 4 — WisdomSynthesizer (long-chain reasoning → Wisdom Report)
    """


@cli.command()
@click.argument("repo", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Save Wisdom Report to file")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output (just the report)")
def mine(repo: str, output: str | None, quiet: bool):
    """Run the full 4-agent wisdom mining pipeline on REPO.

    REPO must be a git repository. The pipeline extracts git history,
    runs parallel pattern/debt analysis, and synthesizes findings into
    a comprehensive Wisdom Report through long-chain reasoning.
    """
    _banner()

    orch = Orchestrator()

    # ── Phase 1: Git Mining ──────────────────────
    _phase_header(1, "Git Archaeology",
                  "Extracting commit history, churn, contributors, and file blame...")
    if not quiet:
        console.print("    [dim]⏳ Reading git history...[/]", end="")

    git_context = orch._phase1_git_mining(repo)

    if not quiet:
        commits_n = len(git_context["commits"])
        contrib_n = len(git_context["contributors"])
        files_n = len(git_context["sources"])
        console.print(f" [green]done[/] — {commits_n} commits, {contrib_n} contributors, {files_n} source files")

    # ── Phase 2: Parallel Analysis ────────────────
    _phase_header(2, "Parallel Deep Analysis",
                  "PatternMiner (code conventions) ∥ DecisionTracer (git archaeology)",
                  style="bright_yellow")

    with console.status(
        "[bold bright_yellow]⚡ 2 agents running in parallel...[/]",
        spinner="dots",
    ):
        findings = orch._phase2_parallel_analysis(repo, git_context)

    if not quiet:
        for key in ("patterns", "decisions"):
            if key in findings and not findings[key].startswith("**ERROR"):
                chars = len(findings[key])
                console.print(f"    [green]✓[/] {key}: {chars:,} chars of analysis")

    # ── Phase 3: Quantification ───────────────────
    _phase_header(3, "Technical Debt Quantification",
                  "DebtQuantifier — complexity · coupling · duplication · churn risk",
                  style="bright_magenta")

    with console.status(
        "[bold bright_magenta]🔍 DebtQuantifier analyzing...[/]",
        spinner="dots",
    ):
        debt_findings = orch._phase3_quantify(repo, findings, git_context)

    if not quiet:
        chars = len(debt_findings)
        console.print(f"    [green]✓[/] debt_analysis: {chars:,} chars")

    # ── Phase 4: Wisdom Synthesis ─────────────────
    _phase_header(4, "Wisdom Synthesis",
                  "WisdomSynthesizer — LONG-CHAIN REASONING across all findings",
                  style="bright_cyan")

    with console.status(
        "[bold bright_cyan]🧠 Synthesizing wisdom (extended thinking 3200 tokens)...[/]",
        spinner="dots",
    ):
        report = orch._phase4_synthesize(findings, debt_findings, git_context, repo)

    # ── Token Summary ─────────────────────────────
    console.print()
    console.print(_token_table(orch.tracker))

    # ── Report Output ─────────────────────────────
    console.print()
    if output:
        Path(output).write_text(report, encoding="utf-8")
        console.print(Panel(
            f"[green]✓ Wisdom Report saved to:[/] [bold]{output}[/]\n"
            f"[dim]Size: {len(report):,} chars | Agents: 4 | "
            f"Tokens: {orch.tracker.total_tokens:,}[/]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            "[bold]🧠 Wisdom Report[/]",
            border_style="bright_cyan",
            box=box.DOUBLE,
        ))
        # Show first portion; full content saved via --output
        preview = report[:5000]
        console.print(Markdown(preview))
        if len(report) > 5000:
            console.print(
                f"\n[dim]... ({len(report):,} total chars — use --output to save full report)[/]"
            )


@cli.command()
@click.argument("repo", type=click.Path(exists=True))
def quick(repo: str):
    """Quick scan — PatternMiner only (single agent, fast mode)."""
    _banner()
    orch = Orchestrator()
    sources = orch._ingest_sources(repo)
    source_block = orch._format_sources(sources)

    console.print("  [bold yellow]▸ Quick Pattern Scan[/]")
    with console.status("[bold yellow]PatternMiner analyzing...[/]", spinner="dots"):
        result = orch.pattern_miner.run(
            f"Give a quick pattern/convention analysis. Top 5 patterns found.\n\n{source_block}"
        )
    console.print(Markdown(result[:3000]))
    console.print(_token_table(orch.tracker))


@cli.command()
def version():
    """Show version info."""
    from . import __version__
    console.print(f"[bold cyan]CodePhronesis[/] v{__version__}")
    console.print("[dim]4-agent pipeline: PatternMiner · DecisionTracer · DebtQuantifier · WisdomSynthesizer[/]")


if __name__ == "__main__":
    cli()
