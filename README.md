# CodePhronesis — 代码库实践智慧挖掘平台

**多 Agent 协作，从代码仓库中恢复工程决策、部落知识和技术债务度量。**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 每个代码仓库都是一座考古遗址。构建它的工程师们的智慧——为什么这样设计、那个边界情况怎么处理、哪些约定是真实约束——埋藏在成千上万次 commit 中。CodePhronesis 用 4 个专用 AI Agent 把它们挖掘出来。

CodePhronesis 部署 **4 个专用 AI Agent** 组成多阶段流水线，从代码仓库中挖掘工程决策、隐性知识模式、技术债务度量，最终通过长链推理合成一份 **Wisdom Report（智慧报告）**——一份保存团队制度知识、加速开发者入职的活文档。

---

## 解决的核心痛点

当资深工程师离开团队，关键上下文随之流失：

- **为什么**这个模块被设计成这样？
- 这个错误处理保护的是**哪些边界情况**？
- 哪些代码约定是**真实约束**，哪些只是历史意外？
- 哪些知识**集中在某一个人的脑子里**？

Git 历史里有答案，但散落在数千次 commit 中，没人有时间逐一阅读。CodePhronesis 通过**多 Agent 协作 + 长链推理**自动重建这些丢失的上下文。

## 多 Agent 协作架构

```
                    ┌──────────────────┐
                    │   Git 历史数据     │
                    │ (commit/blame/    │
                    │  churn 分析)      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌─────▼──────┐   ┌──▼──────────┐
         │ Phase 1 │   │  Phase 2   │   │  Phase 3     │
         │ Git 挖掘 │   │  并行分析   │   │ 债务量化     │
         │         │   │PatternMiner│   │DebtQuantifier│
         │         │   │ ∥ DecisionT│   │              │
         └─────────┘   └─────┬──────┘   └──────┬───────┘
                             │                  │
                             └────────┬─────────┘
                                      │
                              ┌───────▼────────┐
                              │   Phase 4       │
                              │WisdomSynthesizer│
                              │   长链推理合成   │
                              └───────┬──────────┘
                                      │
                              ┌───────▼────────┐
                              │  智慧报告输出    │
                              └────────────────┘
```

### Agent 详解

**Phase 1: Git 考古**
提取 commit 历史、文件变更频率、贡献者地图和逐行 blame 数据。使用原生 git 命令，不依赖任何外部 API。

**Phase 2: 并行深度分析（2 Agent 同时运行）**

| Agent | 职责 | 思考预算 |
|-------|------|---------|
| **PatternMiner** | 扫描源码中的重复模式、代码习惯、错误处理约定、架构约定和反直觉设计选择——即"部落知识"模式 | 2,000 tokens |
| **DecisionTracer** | 挖掘 git 历史，重建工程决策——哪些方案被尝试过、哪些失败了、哪些设计决策的理由从未被写下来 | 2,400 tokens |

**Phase 3: 技术债务量化**

| Agent | 职责 | 思考预算 |
|-------|------|---------|
| **DebtQuantifier** | 用具体数字度量复杂度、耦合度、重复率和变更风险，产出 Debt Health Score（0-100 分） | 1,600 tokens |

**Phase 4: 智慧合成（长链推理）**

| Agent | 职责 | 思考预算 |
|-------|------|---------|
| **WisdomSynthesizer** | 交叉验证所有发现、解决冲突、构建叙事，产出最终的 Wisdom Report 和优先级行动计划 | 3,200 tokens |

**每次运行的总思考预算: 9,200 tokens**，跨 3 个模型家族的深度推理。

## Wisdom Report 产出示例

- **智慧洞察（Wisdom Nuggets）**— 前 5 个非显而易见的发现，例如："`payment/worker.py` 中的异步队列模式故意打破了项目约定，因为 commit `a3f2c1b` 中引入的幂等性要求"
- **模块深度分析**— 每个模块的上下文、模式、健康分和整改建议
- **知识风险地图**— 无人维护的区域、单点知识故障点、稳定的历史决策
- **优先级行动计划**— 按风险加权排序的行动建议

## Token 效率

所有 Agent 的 system prompt 均启用了 Anthropic **prompt caching**（`cache_control: ephemeral`）。首次运行预热缓存，后续同类型 Agent 的运行可节省约 80% 的输入 token 成本。

完整流水线典型 Token 消耗：

| Agent | 输入 | 输出 | 缓存命中 |
|-------|------|------|---------|
| PatternMiner | ~15,000 | ~2,500 | ~12,000 |
| DecisionTracer | ~18,000 | ~3,000 | ~14,000 |
| DebtQuantifier | ~12,000 | ~2,000 | ~9,000 |
| WisdomSynthesizer | ~25,000 | ~4,000 | ~8,000 |
| **合计** | **~70,000** | **~11,500** | **~43,000** |

## 安装

```bash
git clone https://github.com/zhangg0314/CodePhronesis.git
cd CodePhronesis
pip install -e .
```

设置 API Key：

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."

# Linux / macOS
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 使用方法

### 完整智慧挖掘流水线

```bash
python -m src.cli mine /path/to/your/repo --output wisdom-report.md
```

### 快速模式扫描（单 Agent）

```bash
python -m src.cli quick /path/to/your/repo
```

### Demo 演示（无需 API Key）

```bash
python demo/run_demo.py          # 模拟模式，展示完整流水线
python demo/run_demo.py --live   # 真实 API 调用模式
```

### 终端输出效果

```
╔══════════════════════════════════════════════════════════════════╗
║  CodePhronesis  phronesis -- practical wisdom                    ║
║  Multi-Agent Practical Wisdom Mining from Codebases              ║
╚══════════════════════════════════════════════════════════════════╝

  >> Phase 1: Git Archaeology
    [OK] 1,247 commits, 23 contributors, 312 source files

  >> Phase 2: Parallel Deep Analysis
    >> 2 agents running in parallel...
    [OK] patterns: 4,521 chars of analysis
    [OK] decisions: 3,892 chars of analysis

  >> Phase 3: Technical Debt Quantification
    [OK] Debt Health Score: 72/100 -- WARNING zone
       Complexity: 18/25 | Coupling: 12/25 | Duplication: 8/20 | Churn: 9/15

  >> Phase 4: Wisdom Synthesis
    Synthesizing wisdom (extended thinking 3200 tokens)...

         Token Consumption Across Agents
┌────────────────┬────────┬────────┬───────────┬──────────┐
│ Agent          │  Input │ Output │ Cache Hit │ Duration │
├────────────────┼────────┼────────┼───────────┼──────────┤
│ PatternMiner   │ 14,872 │  2,341 │    11,920 │   3200ms │
│ DecisionTracer │ 17,543 │  2,897 │    13,800 │   4100ms │
│ DebtQuantifier │ 11,280 │  1,932 │     8,450 │   2100ms │
│ WisdomSynth.   │ 24,610 │  3,878 │     7,200 │   6800ms │
├────────────────┼────────┼────────┼───────────┼──────────┤
│ TOTAL          │ 68,305 │ 11,048 │    41,370 │    16.2s │
└────────────────┴────────┴────────┴───────────┴──────────┘
```

## 项目结构

```
CodePhronesis/
├── src/
│   ├── agents/
│   │   ├── base.py                  # BaseAgent 基类 (Anthropic SDK + 缓存)
│   │   ├── pattern_miner.py         # 代码模式与约定考古
│   │   ├── decision_tracer.py       # Git 历史决策追踪
│   │   ├── debt_quantifier.py       # 技术债务量化评估
│   │   └── wisdom_synthesizer.py    # 长链推理智慧合成
│   ├── utils/
│   │   ├── token_tracker.py         # Token 消耗追踪
│   │   └── git_ops.py              # Git 历史操作 (log/blame/churn)
│   ├── orchestrator.py              # 4 阶段流水线编排引擎
│   └── cli.py                       # 命令行界面 (Rich 终端可视化)
├── demo/
│   └── run_demo.py                  # 完整 Demo 脚本
├── tests/
│   └── test_agents.py               # 单元测试 (10 个测试用例)
├── pyproject.toml
└── README.md
```

## 核心设计决策

- **Extended Thinking** 在所有 Agent 上启用（1,600-3,200 token 预算），保证深度推理质量
- **Prompt Caching** 通过 `cache_control: ephemeral` 在所有 system prompt 上启用，二次运行输入成本降低约 80%
- **Phase 2 并行执行** 减少约 40% 的端到端耗时
- **Phase 3-4 串行传递** 实现上下文感知分析（每个 Agent 基于前序发现构建）
- **量化债务评分** 而非纯定性评估，支持跨代码库和时间趋势对比

## 实际应用价值

- **新人入职加速** — 通过 Wisdom Report，新工程师在数天内而非数周内达到生产力
- **知识保存** — 关键工程上下文不因人员流动丢失
- **债务可见性** — 量化指标为重构投入提供数据支撑
- **约定固化** — 文档化的代码模式可转为可执行的标准规则

## License

MIT
