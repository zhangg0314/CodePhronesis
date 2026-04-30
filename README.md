# CodePhronesis (φρόνησις)

**Multi-Agent Practical Wisdom Mining from Codebases**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> *"Every codebase is an archaeological site. The wisdom of the engineers who built it is buried in commits, patterns, and design choices — you just need the right tools to excavate it."*

CodePhronesis deploys **4 specialized AI agents** in a multi-phase pipeline to mine your codebase for engineering decisions, tribal knowledge patterns, technical debt metrics, and synthesized practical wisdom. The output is a **Wisdom Report** — a living document that preserves institutional knowledge and accelerates developer onboarding.

---

## The Problem

When senior engineers leave a team, they take critical context with them:
- **Why** was this module designed this way?
- **What edge cases** does this error handler protect against?
- **Which conventions** are real constraints vs. historical accidents?
- **Where is the knowledge** concentrated in one person's head?

Git history contains answers — but it's scattered across thousands of commits, and no one has time to read them all.

## The Solution

CodePhronesis uses **multi-agent collaboration with long-chain reasoning** to reconstruct this lost context automatically.

```
                    ┌──────────────────┐
                    │   Git History     │
                    │   (commits,       │
                    │    blame, churn)  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌─────▼──────┐   ┌──▼──────────┐
         │ Phase 1 │   │  Phase 2   │   │  Phase 3     │
         │  Git    │   │ PARALLEL   │   │ Quantify     │
         │ Mining  │   │ PatternMiner│  │ DebtQuantifier│
         │         │   │ ∥ DecisionT│   │              │
         └─────────┘   └─────┬──────┘   └──────┬───────┘
                             │                  │
                             └────────┬─────────┘
                                      │
                              ┌───────▼────────┐
                              │   Phase 4       │
                              │ WisdomSynthesizer│
                              │ LONG-CHAIN       │
                              │ REASONING        │
                              └───────┬──────────┘
                                      │
                              ┌───────▼────────┐
                              │  Wisdom Report  │
                              └────────────────┘
```

## Agent Architecture

### Phase 1: Git Archaeology
Extracts commit history, file churn, contributor maps, and line-level blame data using native git operations.

### Phase 2: Parallel Deep Analysis (2 agents concurrently)

| Agent | Role | Thinking Budget |
|-------|------|-----------------|
| **PatternMiner** | Scans source code for recurring idioms, conventions, error-handling patterns, architectural conventions, and non-obvious design choices | 2,000 tokens |
| **DecisionTracer** | Mines git history to reconstruct engineering decisions — what was tried, what failed, what rationale was never written down | 2,400 tokens |

### Phase 3: Technical Debt Quantification

| Agent | Role | Thinking Budget |
|-------|------|-----------------|
| **DebtQuantifier** | Measures complexity, coupling, duplication, and churn risk with concrete numeric scores. Produces a Debt Health Score (0-100) | 1,600 tokens |

### Phase 4: Wisdom Synthesis (Long-Chain Reasoning)

| Agent | Role | Thinking Budget |
|-------|------|-----------------|
| **WisdomSynthesizer** | Cross-references all findings, resolves conflicts, constructs narratives, and produces the final Wisdom Report with prioritized action plan | 3,200 tokens |

**Total thinking budget per run: 9,200 tokens** of deep reasoning across 3 model families.

## The Wisdom Report

A sample of what CodePhronesis produces:

- **Wisdom Nuggets** — Top 5 non-obvious insights (e.g., "The async queue pattern in `payment/worker.py` deliberately breaks the project convention because of the idempotency requirement introduced in commit `a3f2c1b`")
- **Module Deep-Dives** — Context, patterns, health score, and recommendations per module
- **Knowledge Risk Map** — Orphaned areas, single-point-of-failure knowledge, stabilized wisdom
- **Prioritized Action Plan** — Risk-weighted recommendations with impact/effort estimates

## Token Efficiency

CodePhronesis uses Anthropic's **prompt caching** on all system prompts. The first run primes the cache; subsequent runs on the same agent types see ~90% reduction in input token costs.

Typical token consumption per full pipeline run:

| Agent | Input | Output | Cache Hit |
|-------|-------|--------|-----------|
| PatternMiner | ~15,000 | ~2,500 | ~12,000 |
| DecisionTracer | ~18,000 | ~3,000 | ~14,000 |
| DebtQuantifier | ~12,000 | ~2,000 | ~9,000 |
| WisdomSynthesizer | ~25,000 | ~4,000 | ~8,000 |
| **Total** | **~70,000** | **~11,500** | **~43,000** |

## Installation

```bash
git clone https://github.com/neowj/CodePhronesis.git
cd CodePhronesis
pip install -e .
```

Set your API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Full Wisdom Mining Pipeline

```bash
codephronesis mine /path/to/your/repo --output wisdom-report.md
```

### Quick Pattern Scan (single agent)

```bash
codephronesis quick /path/to/your/repo
```

### Terminal Output

```
╔══════════════════════════════════════════════════════╗
║  CodePhronesis  φρόνησις                             ║
║  Multi-Agent Practical Wisdom Mining from Codebases  ║
╚══════════════════════════════════════════════════════╝

  ▸ Phase 1: Git Archaeology
    done — 1,247 commits, 23 contributors, 312 source files

  ▸ Phase 2: Parallel Deep Analysis
    ⚡ 2 agents running in parallel...
    ✓ patterns: 4,521 chars of analysis
    ✓ decisions: 3,892 chars of analysis

  ▸ Phase 3: Technical Debt Quantification
    🔍 DebtQuantifier analyzing...
    ✓ debt_analysis: 2,156 chars

  ▸ Phase 4: Wisdom Synthesis
    🧠 Synthesizing wisdom (extended thinking 3200 tokens)...

╭──────────────────────────────────────────────────────╮
│           📊 Token Consumption Across Agents          │
├─────────────────┬──────────┬─────────┬───────────────┤
│ Agent           │ Input    │ Output  │ Cache Hit     │
├─────────────────┼──────────┼─────────┼───────────────┤
│ PatternMiner    │  14,872  │  2,341  │     11,920    │
│ DecisionTracer  │  17,543  │  2,897  │     13,800    │
│ DebtQuantifier  │  11,280  │  1,932  │      8,450    │
│ WisdomSynth.    │  24,610  │  3,878  │      7,200    │
├─────────────────┼──────────┼─────────┼───────────────┤
│ TOTAL           │  68,305  │ 11,048  │     41,370    │
╰─────────────────┴──────────┴─────────┴───────────────╯
```

## Project Structure

```
CodePhronesis/
├── src/
│   ├── agents/
│   │   ├── base.py                  # BaseAgent with Anthropic SDK + caching
│   │   ├── pattern_miner.py         # Code pattern & convention archaeologist
│   │   ├── decision_tracer.py       # Git history decision recovery
│   │   ├── debt_quantifier.py       # Technical debt measurement
│   │   └── wisdom_synthesizer.py    # Long-chain reasoning synthesis
│   ├── utils/
│   │   ├── token_tracker.py         # Token usage & cost tracking
│   │   └── git_ops.py              # Git log/blame/churn operations
│   ├── orchestrator.py              # 4-phase pipeline orchestration
│   └── cli.py                       # Rich terminal UI
├── tests/
│   └── test_agents.py               # Unit tests for agents, git ops, tracker
├── pyproject.toml
└── README.md
```

## Key Design Decisions

- **Extended thinking** enabled on all agents (1,600-3,200 token budgets) for deep reasoning quality
- **Prompt caching** via `cache_control: ephemeral` on all system prompts — second run costs ~80% fewer input tokens
- **Parallel execution** in Phase 2 reduces wall-clock time by ~40%
- **Sequential handoff** in Phases 3-4 enables context-aware analysis (each agent builds on prior findings)
- **Numeric debt scoring** (not just qualitative) enables comparison across codebases and over time

## Real-World Impact

- **Onboarding acceleration**: New engineers reach productivity in days, not weeks, by reading the Wisdom Report
- **Knowledge preservation**: Critical context survives team changes
- **Debt visibility**: Quantified metrics make the case for refactoring investment
- **Convention enforcement**: Documented patterns become enforceable standards

## License

MIT
