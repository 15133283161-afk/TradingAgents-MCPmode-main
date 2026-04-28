# 智能交易分析系统

基于多智能体协同的智能投资决策平台，利用 MCP (Model Context Protocol) 模式集成多个 AI 智能体，为投资决策提供全方位分析。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 核心功能

- **🤖 多智能体协同**：15 个专业 AI 智能体分工协作
- **📊 全方位分析**：涵盖公司基本面、市场技术、情绪分析等多个维度
- **🗣️ 智能辩论**：看涨/看跌研究员进行投资观点辩论
- **⚖️ 风险管理**：多层次风险评估体系
- **📥 报告导出**：支持 Markdown、PDF、Word 多种格式
- **💾 历史记录**：保存和查看历史分析会话

## 🏗️ 系统架构

```
TradingAgents-MCPmode/
├── src/
│   ├── agents/              # AI 智能体定义
│   │   ├── analysts/        # 分析师团队
│   │   ├── researchers/     # 研究员团队
│   │   ├── risk/           # 风险管理团队
│   │   └── management/     # 管理层
│   ├── web/                # Web 界面
│   │   ├── pages/          # Streamlit 页面
│   │   ├── analysis_engine.py
│   │   └── export_manager.py
│   ├── workflow_orchestrator.py  # 工作流编排器
│   └── dumptools/          # 数据导出工具
├── main.py                 # 应用入口
└── requirements.txt        # 依赖清单
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip 包管理器
- Anthropic API Key (或其他兼容 LLM API)

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/TradingAgents-MCPmode.git
cd TradingAgents-MCPmode
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API Keys：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Anthropic API 配置
ANTHROPIC_API_KEY=your_api_key_here

# 可选：使用其他兼容 API
OPENAI_API_BASE=your_api_base
OPENAI_API_KEY=your_api_key
```

### 4. 启动应用

```bash
streamlit run main.py
```

应用将在浏览器中自动打开：http://localhost:8501

## 🤖 智能体说明

### 📊 分析师团队（7 个）

| 智能体 | 职责 |
|--------|------|
| 公司概述分析师 | 提供公司基本信息、业务模式分析 |
| 市场分析师 | 技术分析、价格趋势判断 |
| 情绪分析师 | 市场情绪、投资者心理分析 |
| 新闻分析师 | 最新新闻、公告信息解读 |
| 基本面分析师 | 财务指标、估值分析 |
| 股东分析师 | 股东结构、持股变化分析 |
| 产品分析师 | 产品竞争力、市场地位分析 |

### 🔬 研究员团队（2 个）

| 智能体 | 职责 |
|--------|------|
| 看涨研究员 | 基于多方因素阐述看涨理由 |
| 看跌研究员 | 基于多方因素阐述看跌理由 |

### 👔 管理层（2 个）

| 智能体 | 职责 |
|--------|------|
| 研究经理 | 综合各方意见，形成投资建议 |
| 交易员 | 制定具体的交易执行计划 |

### ⚖️ 风险管理团队（4 个）

| 智能体 | 职责 |
|--------|------|
| 激进风险分析师 | 高风险高收益策略评估 |
| 稳健风险分析师 | 低风险稳健策略评估 |
| 中性风险分析师 | 中等风险平衡策略评估 |
| 风险经理 | 综合风险评估，风控建议 |

## 📖 使用指南

### 基础使用流程

1. **连接系统**
   - 点击侧边栏"🔗 连接系统"按钮
   - 等待 AI 智能体团队初始化完成

2. **配置智能体**
   - 在侧边栏选择要启用的智能体
   - 设置投资辩论轮次（0-5 轮）
   - 设置风险辩论轮次（0-5 轮）

3. **开始分析**
   - 在"🔍 实时分析"页面输入分析目标
   - 例如："分析贵州茅台的投资价值"
   - 点击"🚀 开始分析"按钮

4. **查看进度**
   - 点击"🔃 刷新状态"查看分析进度
   - 分析完成后自动显示结果

5. **导出报告**
   - 在"📊 分析结果"页面查看完整报告
   - 选择导出格式：Markdown / PDF / Word

### 高级功能

#### 历史会话管理

- 切换到"📚 历史会话"标签页
- 查看所有历史分析记录
- 点击历史记录可重新加载查看

#### 辩论时间线

- 切换到"🗣️ 辩论展示"标签页
- 查看智能体之间的辩论过程
- 了解不同观点的碰撞和融合

#### 系统配置

- 切换到"🏛️ 系统配置"标签页
- 查看所有智能体的配置和状态
- 了解系统运行情况

## ⚙️ 配置说明

### 最简配置（推荐新手）

默认已启用 3 个核心智能体，提供快速基础分析：

- ✅ 公司概述分析师
- ✅ 市场分析师
- ✅ 基本面分析师

### 完整配置（专业分析）

启用全部 15 个智能体，获得全面深入的投资分析：

1. 在侧边栏展开各个智能体组
2. 勾选需要的智能体
3. 设置辩论轮次（建议 1-2 轮）

### 性能优化建议

| 配置 | 智能体数量 | 分析时间 | 适用场景 |
|------|-----------|---------|---------|
| 最简模式 | 3 个 | 1-2 分钟 | 快速决策 |
| 标准模式 | 7 个 | 3-5 分钟 | 日常分析 |
| 完整模式 | 15 个 | 5-10 分钟 | 深度研究 |

### 配置域名和 HTTPS（可选）

#### 1. 配置域名解析

在阿里云域名管理中添加 A 记录指向服务器 IP

#### 2. 安装 Nginx 和 SSL 证书

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

#### 3. 配置 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 常用运维命令

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 更新代码后重新部署
git pull
docker-compose up -d --build

# 清理未使用的镜像
docker system prune -a
```

## 📦 依赖清单

主要依赖：

```
streamlit>=1.28.0
anthropic>=0.18.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
reportlab>=4.0.0
python-docx>=1.0.0
```

完整依赖列表见 [requirements.txt](requirements.txt)

## 🔧 故障排除

### 常见问题

**Q1: ImportError: cannot import name 'start_analysis'**

A: 确保使用最新版本代码，运行 `git pull` 更新项目。

**Q2: st.session_state has no attribute "active_agents"**

A: 重启 Streamlit 应用，清除浏览器缓存。

**Q3: 导出报告时出现 key 冲突错误**

A: 已在新版本修复，更新到最新代码即可。

**Q4: 分析过程卡住不动**

A: 点击"🔃 刷新状态"按钮，或检查 API Key 是否正确配置。

### 调试模式

启用详细日志：

```bash
streamlit run main.py --logger.level=debug
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-repo/TradingAgents-MCPmode.git
cd TradingAgents-MCPmode

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行测试
pytest
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - Web 应用框架
- [MCP](https://modelcontextprotocol.io/) - 模型上下文协议

## 📮 联系方式

- 问题反馈：
- 邮箱：15133283161@163.com
- QQ:1978546298

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
