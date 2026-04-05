# TradingAgents-MCPmode 项目说明

## 项目概述

**TradingAgents-MCPmode** 是一个基于 AI 多智能体协作的股票投资分析系统。系统通过 15+ 个专业 AI 智能体协同工作，从多个维度对股票/公司进行全面的投资分析，并通过辩论机制驱动最终决策，输出专业的投资建议报告。

---

## 技术栈

| 类别 | 技术/库 |
|------|---------|
| 语言 | Python 3.10+ |
| Web 框架 | Streamlit |
| 工作流编排 | LangGraph |
| LLM 集成 | LangChain + LangChain-OpenAI |
| MCP 协议 | langchain-mcp-adapters |
| 异步 HTTP | aiohttp |
| 数据验证 | Pydantic |
| PDF 生成 | reportlab |
| Word 生成 | python-docx |
| 环境变量 | python-dotenv |
| LLM 服务商 | DeepSeek API（兼容 OpenAI 接口） |
| 股市数据 | Tushare（A 股）、Investoday（MCP 接入） |

---

## 项目结构

```
TradingAgents-MCPmode-main/
├── main.py                          # 应用入口，启动 Streamlit
├── .env                             # 环境变量配置（API Key、模型参数等）
├── mcp_config.json                  # MCP 服务器配置
├── README.md                        # 项目说明（中文）
├── SRC_介绍.md                      # 源码详细说明
│
├── src/                             # 主源码目录
│   ├── __init__.py
│   ├── base_agent.py                # 所有智能体的抽象基类
│   ├── agent_states.py              # 状态类定义（AgentState、DebateState）
│   ├── workflow_orchestrator.py     # 核心工作流编排器
│   ├── mcp_manager.py               # MCP 工具管理 & LLM 初始化
│   ├── progress_tracker.py          # 会话追踪 & JSON 持久化
│   │
│   ├── agents/                      # 15 个专业 AI 智能体
│   │   ├── analysts.py              # 7 个分析师智能体
│   │   ├── researchers.py           # 2 个辩论研究员（多头/空头）
│   │   ├── managers.py              # 2 个决策管理者
│   │   └── risk_management.py       # 4 个风险分析师
│   │
│   ├── core/                        # 核心工具
│   │   ├── state_manager.py         # 状态管理工具
│   │   └── data_persistence.py      # 数据持久化层
│   │
│   ├── web/                         # Streamlit Web 界面
│   │   ├── app.py                   # 主应用（4 个 Tab 页）
│   │   ├── session_manager.py       # 会话状态管理
│   │   ├── sidebar.py               # 侧边栏 UI
│   │   ├── analysis_engine.py       # 分析执行引擎（异步）
│   │   ├── analysis_monitor.py      # 实时监控
│   │   ├── export_manager.py        # 报告导出
│   │   ├── config_manager.py        # 配置管理
│   │   ├── results_viewer.py        # 结果展示
│   │   ├── css_loader.py            # CSS 加载工具
│   │   ├── css/                     # 样式文件
│   │   │   ├── styles.css
│   │   │   └── financial_styles.css
│   │   └── pages/                   # Streamlit 页面组件
│   │       ├── real_time_analysis.py    # 实时分析页
│   │       ├── history_sessions.py      # 历史会话页
│   │       ├── debate_timeline.py       # 辩论时间线可视化
│   │       ├── analysis_results.py      # 结果展示页
│   │       └── system_overview.py       # 系统配置页
│   │
│   ├── dumptools/                   # 导出工具
│   │   ├── json_to_markdown.py      # JSON → Markdown
│   │   ├── md2pdf.py                # Markdown → PDF
│   │   └── md2docx.py               # Markdown → Word
│   │
│   └── dump/                        # 会话 JSON 数据存储
│       └── session_*.json
│
├── exports/                         # 导出报告目录
└── markdown_reports/                # Markdown 报告输出目录
```

---

## 智能体架构

系统共 **15 个专业 AI 智能体**，分为 4 个团队协同工作：

### 1. 分析师团队（7 个，并行执行）
| 智能体 | 职责 |
|--------|------|
| 公司概况分析师 | 公司基本信息、主营业务 |
| 市场分析师 | 技术分析、价格趋势 |
| 情绪分析师 | 市场情绪、投资者心理 |
| 新闻分析师 | 新闻事件、政策变化 |
| 基本面分析师 | 财务报表、估值分析 |
| 股东分析师 | 股权结构、重大交易 |
| 产品分析师 | 商业模式、产品线 |

### 2. 研究团队（2 个，辩论机制）
| 智能体 | 职责 |
|--------|------|
| 多头研究员 | 构建看多投资逻辑 |
| 空头研究员 | 构建看空投资逻辑 |

> 支持 0~5 轮可配置辩论，辩论轮次越多分析越深入。

### 3. 管理层团队（2 个）
| 智能体 | 职责 |
|--------|------|
| 研究主管 | 评估辩论结果，形成投资决策 |
| 交易员 | 制定具体执行方案（仓位、时机） |

### 4. 风险管理团队（4 个，辩论机制）
| 智能体 | 职责 |
|--------|------|
| 激进风险分析师 | 高风险高收益视角 |
| 保守风险分析师 | 资本保护视角 |
| 中性风险分析师 | 平衡风险收益视角 |
| 风险主管 | 最终风险评估与控制 |

---

## 工作流程

```
用户输入分析请求
        ↓
公司概况分析师（单独执行）
        ↓
[并行] 市场/情绪/新闻/基本面/股东/产品 分析师
        ↓
[循环辩论] 多头研究员 ↔ 空头研究员（N 轮）
        ↓
研究主管（整合辩论，形成投资决策）
        ↓
交易员（制定执行计划）
        ↓
[循环辩论] 激进/保守/中性 风险分析师（N 轮）
        ↓
风险主管（最终风险评估）
        ↓
输出完整投资分析报告
```

---

## 核心数据结构

### AgentState（智能体共享状态）

```python
class AgentState(MessagesState):
    user_query: str                    # 用户查询
    company_details: str               # 公司详情

    # 分析师报告
    company_overview_report: str
    market_report: str
    sentiment_report: str
    news_report: str
    fundamentals_report: str
    shareholder_report: str
    product_report: str

    # 辩论状态
    investment_debate_state: Dict[str, Any]
    investment_plan: str

    # 交易决策
    trader_investment_plan: str
    risk_debate_state: Dict[str, Any]
    final_trade_decision: str

    # 执行追踪
    mcp_tool_calls: List[Dict[str, Any]]
    agent_execution_history: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
```

### 会话 JSON 结构（src/dump/session_*.json）

```json
{
  "session_id": "20260209_170336_378572_d043c6fe",
  "created_at": "2026-02-09T17:03:36",
  "status": "active",
  "user_query": "分析贵州茅台的投资价值",
  "active_agents": ["company_overview_analyst", "..."],
  "agents": [
    { "name": "company_overview_analyst", "result": "...", "timestamp": "..." }
  ],
  "mcp_calls": [],
  "final_results": {}
}
```

---

## 环境配置（.env）

```env
# LLM 配置
OPENAI_API_KEY=<DeepSeek API Key>
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
LLM_TEMPERATURE=0.1

# 工作流配置
MAX_DEBATE_ROUNDS=1          # 投资辩论轮次（0~5）
MAX_RISK_DEBATE_ROUNDS=1     # 风险辩论轮次（0~5）
DEBUG_MODE=true
VERBOSE_LOGGING=true

# 各智能体 MCP 工具权限（每个智能体可独立开关）
COMPANY_OVERVIEW_ANALYST_MCP_ENABLED=true
MARKET_ANALYST_MCP_ENABLED=true
# ... 共 15 个智能体

# 数据 API Key
TUSHARE_TOKEN=<Tushare Token>
INVESTODAY_API_KEY=<Investoday API Key>
```

---

## MCP 配置（mcp_config.json）

```json
{
  "mcpServers": {
    "investoday": {
      "url": "https://data-api.investoday.net/data/mcp/preset?apiKey=${INVESTODAY_API_KEY}"
    }
  }
}
```

---

## 关键设计模式

| 模式 | 应用场景 |
|------|----------|
| **状态机模式** | LangGraph 管理智能体执行流（条件边、并行节点） |
| **策略模式** | BaseAgent 抽象基类 + 各智能体实现自定义 system prompt |
| **观察者模式** | ProgressTracker 监控执行，实时写入 JSON 会话文件 |
| **工厂模式** | MCPManager 动态创建带工具权限的智能体 |
| **辩论驱动决策** | 多头/空头对立视角 + 多轮辩论提升分析质量 |

---

## 报告导出格式

| 格式 | 工具 | 输出目录 |
|------|------|---------|
| Markdown | 内置转换 | `markdown_reports/` |
| PDF | reportlab | `exports/` |
| Word (.docx) | python-docx | `exports/` |
| JSON 会话 | 自动保存 | `src/dump/` |

---

## 启动方式

```bash
# 安装依赖
pip install streamlit langchain-openai langchain-mcp-adapters langgraph \
            aiohttp python-dotenv pydantic reportlab python-docx

# 配置 .env 文件（填写 API Key）

# 启动应用
streamlit run main.py
```

访问地址：`http://localhost:8501`

---

## Web 界面说明

应用分为 4 个 Tab 页：

| Tab | 功能 |
|-----|------|
| 🔍 实时分析 | 输入分析请求，启动/停止/刷新分析，实时进度监控 |
| 📚 历史会话 | 浏览已保存的分析会话，加载历史结果 |
| 🗣️ 辩论时间线 | 可视化智能体辩论过程，展示论点演化 |
| 🏛️ 系统概览 | 智能体状态、MCP 工具可用性、系统配置 |

---

## 注意事项

1. **API Key 安全**：`.env` 文件包含真实 API Key，请勿提交到公开代码仓库。
2. **并发执行**：分析运行在后台线程，支持取消操作，不阻塞 UI。
3. **辩论轮次**：`MAX_DEBATE_ROUNDS` 越大分析越深入，但耗时和 Token 消耗也越多。
4. **MCP 权限**：每个智能体可通过 `.env` 独立控制是否启用外部数据工具。
5. **数据持久化**：所有分析结果自动保存为 JSON，支持历史回溯，无需数据库。
6. **中文优化**：系统所有 Prompt 和 UI 均为中文，专为 A 股市场分析设计。
7. **无测试覆盖**：当前项目无正式单元测试，依赖手动测试和 `DEBUG_MODE=true` 日志排查。
