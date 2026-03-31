# AGENTS.md

## 项目定位
TradingAgents-MCPmode 是一个基于 LangGraph 的多智能体投资分析系统。
核心目标是：围绕用户输入的股票/公司问题，组织 15 个角色化智能体，完成分析、辩论、决策和风控，并输出可追踪报告。

## 关键入口
- 应用入口：`main.py`（启动 Streamlit）
- 工作流编排：`src/workflow_orchestrator.py`
- 状态定义：`src/agent_states.py`
- MCP 与模型管理：`src/mcp_manager.py`
- 进度追踪与会话落盘：`src/progress_tracker.py`
- Web 层：`src/web/`（页面、会话管理、分析引擎、导出等）

## 智能体清单（15）
### 分析师团队（7）
1. company_overview_analyst
2. market_analyst
3. sentiment_analyst
4. news_analyst
5. fundamentals_analyst
6. shareholder_analyst
7. product_analyst

### 研究辩论团队（2）
1. bull_researcher
2. bear_researcher

### 管理层（2）
1. research_manager
2. trader

### 风险团队（4）
1. aggressive_risk_analyst
2. safe_risk_analyst
3. neutral_risk_analyst
4. risk_manager

## 实际执行流程（与代码一致）
1. company_overview_analyst 单独执行。
2. analysts_parallel 并行执行 6 个分析师：market/sentiment/news/fundamentals/shareholder/product。
3. 投资辩论阶段：bull_researcher 与 bear_researcher 交替发言。
4. 研究结论阶段：research_manager 汇总辩论并形成投资方案。
5. 交易计划阶段：trader 产出交易执行计划。
6. 风险辩论阶段：aggressive -> safe -> neutral 循环。
7. 风险收敛阶段：risk_manager 给出最终风控与交易决策。

## 轮次控制规则
- 投资辩论轮次：`MAX_DEBATE_ROUNDS`（默认读取 `.env`）。
- 风险辩论轮次：`MAX_RISK_DEBATE_ROUNDS`（默认读取 `.env`）。
- 计数逻辑：
  - 投资辩论每 2 次发言视为 1 轮。
  - 风险辩论每 3 次发言视为 1 轮。

## 并行与状态合并
- 并行分析通过 `analysts_parallel` 节点完成。
- 每个并发任务使用 state 深拷贝，完成后合并关键报告字段与历史字段：
  - 报告：market/sentiment/news/fundamentals/shareholder/product
  - 历史：agent_execution_history, mcp_tool_calls, warnings, errors

## 可启用/禁用机制
- `run_analysis(..., active_agents=[])` 可指定本轮启用智能体。
- 被禁用智能体会被跳过并记录 warning。
- 对辩论智能体，跳过时仍会推进计数，避免条件分支中断。

## 会话与输出
- 会话 JSON：`src/dump/session_*.json`
- 报告导出：
  - Markdown：`markdown_reports/`
  - PDF/Word：`exports/`

## 运行方式
```bash
pip install -r requirements.txt
streamlit run main.py
```

## 开发注意事项
1. 保持 `AgentState` 字段兼容，避免新增字段后未在状态转换中复制。
2. 修改节点顺序时，同步检查条件边和轮次计数逻辑。
3. 并行节点改动后，务必检查合并字段是否完整。
4. `progress_tracker` 负责可观测性，新增关键动作应写入追踪日志。
5. `.env` 中包含密钥，严禁提交到公开仓库。
