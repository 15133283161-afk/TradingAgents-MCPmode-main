# TradingAgents-MCPmode - src 目录介绍文档

## 项目概述

**TradingAgents-MCPmode** 是一个基于 MCP (Model Context Protocol) 工具的多智能体交易决策系统。该项目通过多个专业化智能体协作，对股票进行全面分析，从多个维度评估投资机会和风险，最终生成交易决策建议。

### 核心特性

- **多智能体协作架构**：15+ 个专业化智能体分工协作
- **MCP 工具集成**：通过 MCP 协议集成外部数据工具，获取实时市场数据
- **辩论式决策**：研究员和风险分析师进行多轮辩论，确保决策的全面性
- **状态管理**：基于 LangGraph 的工作流编排，智能体间状态传递
- **实时进度跟踪**：完整的会话记录和进度监控系统
- **Web 界面**：基于 Streamlit 的可视化监控界面

---

## 目录结构

```
src/
├── __init__.py                 # 包初始化文件
├── base_agent.py               # 智能体基类
├── agent_states.py             # 状态管理类
├── workflow_orchestrator.py    # 工作流编排器
├── mcp_manager.py              # MCP 工具管理器
├── progress_tracker.py         # 进度跟踪器
│
├── agents/                     # 智能体团队
│   ├── __init__.py
│   ├── analysts.py             # 分析师团队 (7个)
│   ├── researchers.py          # 研究员团队 (2个)
│   ├── managers.py             # 管理层 (2个)
│   └── risk_management.py      # 风险管理团队 (4个)
│
├── core/                       # 核心功能模块
│   ├── __init__.py
│   ├── state_manager.py        # 状态管理器
│   └── data_persistence.py     # 数据持久化管理器
│
├── web/                        # Web 界面
│   ├── __init__.py
│   ├── analysis_monitor.py     # 分析监控器
│   ├── config_manager.py       # 配置管理
│   ├── results_viewer.py       # 结果查看器
│   ├── css_loader.py           # CSS 加载器
│   ├── financial_styles.css    # 金融样式
│   └── function/               # 功能模块
│       ├── agent_results.py
│       ├── analysis_engine.py
│       ├── dashboard.py
│       ├── history_management.py
│       ├── history_page.py
│       ├── progress_display.py
│       └── system_status.py
│
├── dumptools/                  # 导出工具
│   ├── __init__.py
│   ├── json_to_markdown.py     # JSON 转 Markdown
│   ├── md2docx.py              # Markdown 转 Word
│   └── md2pdf.py               # Markdown 转 PDF
│
└── dump/                       # 会话数据存储
    └── session_*.json          # 会话记录文件
```

---

## 核心模块详解

### 1. 基础架构

#### `base_agent.py` - 智能体基类
所有智能体的抽象基类，提供：
- LLM 调用封装 (`call_llm_with_context`)
- MCP 工具调用 (`call_mcp_tool`)
- 上下文构建 (`build_context_prompt`)
- 状态验证 (`validate_state`)
- 输出格式化 (`format_output`)

#### `agent_states.py` - 状态管理
定义智能体间的数据传递状态：
- `AgentState`: 主状态类，包含所有分析报告
- `InvestDebateState`: 投资辩论状态
- `RiskDebateState`: 风险辩论状态

#### `workflow_orchestrator.py` - 工作流编排器
负责整个分析流程的编排：
- 创建 LangGraph 状态图
- 定义智能体执行顺序和条件边
- 支持并行执行（分析师团队）
- 实现辩论轮次控制

#### `mcp_manager.py` - MCP 工具管理器
管理 MCP 协议集成：
- MCP 服务器连接管理
- 工具发现和注册
- 智能体权限控制
- React 智能体创建

---

### 2. 智能体团队

#### 分析师团队 (`analysts.py`) - 7 个专业分析师

| 智能体 | 职责 | 分析重点 |
|--------|------|----------|
| **公司概述分析师** | 公司基础信息收集 | 成立背景、业务范围、行业分类 |
| **市场分析师** | 技术分析 | 价格趋势、技术指标、交易量 |
| **情绪分析师** | 市场情绪分析 | 社交媒体情绪、投资者心理 |
| **新闻分析师** | 信息面分析 | 新闻事件、政策变化 |
| **基本面分析师** | 财务分析 | 财务报表、估值指标 |
| **股东分析师** | 股权结构分析 | 股东变化、大宗交易 |
| **产品分析师** | 业务分析 | 主营业务、产品线、商业模式 |

**执行方式**：公司概述分析师首先执行，其余 6 个分析师并行执行

#### 研究员团队 (`researchers.py`) - 2 个对立观点研究员

| 智能体 | 观点 | 辩论策略 |
|--------|------|----------|
| **看涨研究员** | 构建看涨论证 | 强调增长潜力、识别价值低估点 |
| **看跌研究员** | 构建看跌论证 | 识别投资风险、质疑过度乐观 |

**辩论机制**：多轮辩论（默认 3 轮），互相反驳对方观点

#### 管理层 (`managers.py`) - 2 个决策管理者

| 智能体 | 职责 | 输出 |
|--------|------|------|
| **研究经理** | 评估辩论结果 | 投资决策（买入/卖出/持有） |
| **交易员** | 制定执行计划 | 具体交易策略、仓位管理 |

#### 风险管理团队 (`risk_management.py`) - 4 个风险视角

| 智能体 | 风险偏好 | 观点特征 |
|--------|----------|----------|
| **激进风险分析师** | 高风险高回报 | 强调机会成本、风险可控性 |
| **保守风险分析师** | 资本保护优先 | 强调下行风险、不确定性 |
| **中立风险分析师** | 平衡风险收益 | 量化风险收益比、概率分析 |
| **风险经理** | 最终决策 | 综合三方观点、风险控制措施 |

**辩论机制**：三方循环辩论（默认 2 轮），激进 → 保守 → 中性 → 激进...

---

### 3. 核心功能模块

#### `state_manager.py` - 状态管理器
跟踪工作流执行状态：
- 智能体执行状态（pending/running/completed/failed）
- 工作流整体进度
- 辩论轮次控制
- 预估剩余时间

#### `data_persistence.py` - 数据持久化管理器
确保 AI 生成内容完整保存：
- 会话数据保存到 JSON
- 智能体结果完整记录（不截断）
- MCP 工具调用记录
- LLM 交互完整记录
- 时间线事件追踪

#### `progress_tracker.py` - 进度跟踪器
简化的进度跟踪实现：
- 会话 ID 生成
- JSON 会话文件管理
- 智能体执行跟踪
- MCP 工具调用记录

---

### 4. Web 界面模块

#### `analysis_monitor.py` - 分析监控器
实时监控分析过程：
- 系统连接状态检查
- 分析输入界面
- 实时进度显示
- 阶段进度详情
- 分析结果展示

#### 功能模块 (`web/function/`)
- `dashboard.py`: 仪表板
- `agent_results.py`: 智能体结果展示
- `analysis_engine.py`: 分析引擎
- `history_management.py`: 历史记录管理
- `progress_display.py`: 进度显示
- `system_status.py`: 系统状态

---

### 5. 导出工具模块

#### `json_to_markdown.py` - JSON 转 Markdown
将会话 JSON 导出为 Markdown 报告：
- 支持单个文件转换
- 支持批量转换
- 可选只导出关键智能体（研究经理、交易员、风险经理）
- 可选包含 MCP 工具调用信息
- 自动标题规范化和编号
- Emoji 清理

#### `md2docx.py` - Markdown 转 Word
将 Markdown 报告转换为 Word 文档

#### `md2pdf.py` - Markdown 转 PDF
将 Markdown 报告转换为 PDF 文档

---

## 工作流程

### 分析流程（5 个阶段）

```
┌─────────────────────────────────────────────────────────────┐
│  阶段 0: 公司概述分析                                        │
│  └─ 公司概述分析师                                           │
│     └─ 获取公司基础信息、业务范围、行业分类                  │
├─────────────────────────────────────────────────────────────┤
│  阶段 1: 分析师团队并行分析 (6个分析师并发)                  │
│  ├─ 市场分析师 ──┐                                          │
│  ├─ 情绪分析师 ──┤                                          │
│  ├─ 新闻分析师 ──┼─> 并行执行 ─> 汇总报告                   │
│  ├─ 基本面分析师 ┤                                          │
│  ├─ 股东分析师 ──┤                                          │
│  └─ 产品分析师 ──┘                                          │
├─────────────────────────────────────────────────────────────┤
│  阶段 2: 研究员辩论 (多轮)                                   │
│  ┌──────────┐         ┌──────────┐                         │
│  │ 看涨研究员 │ <───> │ 看跌研究员 │                         │
│  └──────────┘         └──────────┘                         │
│       ↓                                                   │
│  研究经理 -> 投资决策                                        │
├─────────────────────────────────────────────────────────────┤
│  阶段 3: 交易员决策                                          │
│  └─ 交易员                                                  │
│     └─ 制定具体交易计划、仓位管理、止损止盈                 │
├─────────────────────────────────────────────────────────────┤
│  阶段 4: 风险管理辩论 (多轮三方循环)                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│  │ 激进风险 │ -> │ 保守风险 │ -> │ 中性风险 │ --┐           │
│  └─────────┘    └─────────┘    └─────────┘   │           │
│       ↑                                    │           │
│       └────────────────────────────────────┘           │
│       ↓                                                   │
│  风险经理 -> 最终交易决策                                   │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户查询
    ↓
AgentState 初始化
    ↓
分析师报告 (7 个)
    ↓
投资辩论历史
    ↓
投资决策
    ↓
交易计划
    ↓
风险辩论历史
    ↓
最终交易决策
```

---

## 环境变量配置

### LLM 配置
```bash
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
```

### MCP 工具权限控制
```bash
# 分析师团队
COMPANY_OVERVIEW_ANALYST_MCP_ENABLED=true
MARKET_ANALYST_MCP_ENABLED=true
SENTIMENT_ANALYST_MCP_ENABLED=true
NEWS_ANALYST_MCP_ENABLED=true
FUNDAMENTALS_ANALYST_MCP_ENABLED=true
SHAREHOLDER_ANALYST_MCP_ENABLED=true
PRODUCT_ANALYST_MCP_ENABLED=true

# 研究员团队
BULL_RESEARCHER_MCP_ENABLED=true
BEAR_RESEARCHER_MCP_ENABLED=true

# 管理层
RESEARCH_MANAGER_MCP_ENABLED=false
TRADER_MCP_ENABLED=false

# 风险管理团队
AGGRESSIVE_RISK_ANALYST_MCP_ENABLED=false
SAFE_RISK_ANALYST_MCP_ENABLED=false
NEUTRAL_RISK_ANALYST_MCP_ENABLED=false
RISK_MANAGER_MCP_ENABLED=false
```

### 辩论轮次配置
```bash
MAX_DEBATE_ROUNDS=3          # 投资辩论最大轮数
MAX_RISK_DEBATE_ROUNDS=2     # 风险辩论最大轮数
```

### 调试配置
```bash
DEBUG_MODE=true              # 调试模式
VERBOSE_LOGGING=true         # 详细日志
```

---

## MCP 配置文件

项目使用 `mcp_config.json` 配置 MCP 服务器连接：

```json
{
  "mcpServers": {
    "server-name": {
      "command": "server-command",
      "args": [],
      "env": {}
    }
  },
  "agent_permissions": {}
}
```

---

## 会话数据存储

所有会话数据保存在 `src/dump/` 目录下，文件名格式：

```
session_YYYYMMDD_HHMMSS_microseconds_randomhash.json
```

会话数据结构：
```json
{
  "session_id": "唯一会话ID",
  "created_at": "创建时间",
  "updated_at": "更新时间",
  "status": "会话状态",
  "user_query": "用户查询",
  "active_agents": ["启用的智能体列表"],
  "stages": ["阶段信息"],
  "agents": [
    {
      "agent_name": "智能体名称",
      "action": "执行动作",
      "start_time": "开始时间",
      "status": "状态",
      "result": "完整结果",
      "system_prompt": "系统提示",
      "user_prompt": "用户提示",
      "context": "上下文",
      "end_time": "结束时间"
    }
  ],
  "actions": ["行动记录"],
  "mcp_calls": ["MCP工具调用记录"],
  "errors": ["错误信息"],
  "warnings": ["警告信息"],
  "final_results": {}
}
```

---

## 使用示例

### 基本使用

```python
import asyncio
from src.workflow_orchestrator import WorkflowOrchestrator

async def main():
    # 初始化工作流编排器
    orchestrator = WorkflowOrchestrator("mcp_config.json")

    # 初始化 MCP 连接
    await orchestrator.initialize()

    # 运行分析
    result = await orchestrator.run_analysis("分析苹果公司(AAPL)股票")

    # 查看结果
    print(result.final_trade_decision)

    # 关闭连接
    await orchestrator.close()

asyncio.run(main())
```

### 导出报告

```python
from src.dumptools.json_to_markdown import JSONToMarkdownConverter

# 转换最新的会话记录
converter = JSONToMarkdownConverter()
markdown_file = converter.convert_latest_json()

# 或转换指定文件
markdown_file = converter.convert_json_to_markdown("src/dump/session_xxx.json")

# 或批量转换所有文件
markdown_files = converter.convert_all_json()

# 或只导出关键智能体（研究经理、交易员、风险经理）
converter_key = JSONToMarkdownConverter(key_agents_only=True)
markdown_file = converter_key.convert_latest_json()
```

---

## 技术栈

- **LLM 框架**: LangChain, LangGraph
- **MCP 协议**: langchain-mcp-adapters
- **Web 界面**: Streamlit
- **数据处理**: Pydantic
- **异步处理**: asyncio
- **文档导出**: Markdown, python-docx, reportlab

---

## 设计特点

### 1. 模块化设计
- 清晰的职责分离
- 智能体独立可测试
- 易于扩展新的智能体

### 2. 状态管理
- 基于 LangGraph 的状态图
- 智能体间状态自动传递
- 支持字典和对象两种状态格式

### 3. 并行执行
- 分析师团队并行处理
- 提高整体执行效率
- 状态自动合并

### 4. 权限控制
- 环境变量控制每个智能体的 MCP 工具访问权限
- 灵活的启用/禁用机制
- 支持部分智能体启用

### 5. 完整的追踪
- 所有 AI 生成内容完整保存
- MCP 工具调用详细记录
- 时间线事件追踪
- 支持会话回溯和分析

---

## 扩展开发

### 添加新的智能体

1. 在 `src/agents/` 对应文件中创建智能体类
2. 继承 `BaseAgent`
3. 实现 `get_system_prompt()` 和 `process()` 方法
4. 在 `workflow_orchestrator.py` 中注册智能体
5. 添加工作流节点和边

### 添加新的 MCP 工具

1. 在 `mcp_config.json` 中配置 MCP 服务器
2. 设置环境变量启用智能体权限
3. 智能体会自动发现可用工具

### 自定义工作流

修改 `workflow_orchestrator.py` 中的 `_create_workflow()` 方法：
- 添加/删除节点
- 修改执行顺序
- 调整条件边逻辑

---

## 注意事项

1. **MCP 连接**：确保 MCP 服务器正常运行，网络连接稳定
2. **LLM 配置**：配置正确的 API Key 和 Base URL
3. **并发控制**：并行执行时注意状态竞态问题（已通过深拷贝解决）
4. **数据持久化**：会话文件较大，定期清理旧文件
5. **权限管理**：合理配置 MCP 工具权限，避免不必要的 API 调用

---

## 文件说明

### 核心文件

| 文件 | 行数 | 说明 |
|------|------|------|
| [base_agent.py](src/base_agent.py) | ~526 | 智能体基类，提供核心功能 |
| [workflow_orchestrator.py](src/workflow_orchestrator.py) | ~820 | 工作流编排器，定义执行流程 |
| [mcp_manager.py](src/mcp_manager.py) | ~354 | MCP 工具管理器 |
| [agent_states.py](src/agent_states.py) | ~117 | 状态管理类 |
| [progress_tracker.py](src/progress_tracker.py) | ~270 | 进度跟踪器 |

### 智能体文件

| 文件 | 行数 | 智能体数量 |
|------|------|-----------|
| [analysts.py](src/agents/analysts.py) | ~610 | 7 个分析师 |
| [researchers.py](src/agents/researchers.py) | ~240 | 2 个研究员 |
| [managers.py](src/agents/managers.py) | ~209 | 2 个管理者 |
| [risk_management.py](src/agents/risk_management.py) | ~476 | 4 个风险分析师 |

### 工具文件

| 文件 | 行数 | 说明 |
|------|------|------|
| [json_to_markdown.py](src/dumptools/json_to_markdown.py) | ~512 | JSON 转 Markdown 工具 |
| [state_manager.py](src/core/state_manager.py) | ~270 | 状态管理器 |
| [data_persistence.py](src/core/data_persistence.py) | ~416 | 数据持久化管理器 |

---

## 总结

TradingAgents-MCPmode 是一个设计精良的多智能体交易分析系统，具有以下优势：

- **全面性**：覆盖市场技术、基本面、情绪、新闻等多个维度
- **专业性**：每个智能体专注于特定领域，提供深度分析
- **客观性**：通过对立辩论机制，避免单一偏见
- **可控性**：风险管理团队从多个角度评估风险
- **透明性**：完整的会话记录，可追溯每一步决策
- **灵活性**：支持模块化扩展，易于定制

该系统适用于专业投资机构、量化交易团队、个人投资者等场景，能够提供全面、客观、专业的投资分析和交易决策支持。

---

**文档生成时间**: 2026-01-27
**项目版本**: 1.0.0
**作者**: TradingAgents Team
