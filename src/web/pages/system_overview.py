#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统概览页面
参考 mcp_tools_showcase.py：从 mcp_config.json 读取配置，在未连接时也显示「已配置」状态。
"""

import json
from pathlib import Path

import streamlit as st
from src.web.sidebar import get_agent_display_name, get_agent_type



def _load_mcp_config():
    """从 mcp_config.json 加载 MCP 配置（兼容 mcpServers / servers）"""
    config_file = Path("mcp_config.json")
    if not config_file.exists():
        return None
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None
    servers = data.get("mcpServers") or data.get("servers") or {}
    if not servers:
        return None
    return {"servers": servers, "server_count": len(servers)}

@st.cache_data(ttl=30)
def get_system_capabilities():
    """获取系统能力统计信息"""
    try:
        if st.session_state.get('orchestrator') and hasattr(st.session_state.orchestrator, 'agents'):
            agents_count = len(st.session_state.orchestrator.agents)
            enabled_count = sum(1 for v in st.session_state.active_agents.values() if v)
            # 从 orchestrator 的 mcp_manager 获取真实 MCP 工具信息（不再硬编码为 0）
            orch = st.session_state.orchestrator
            if hasattr(orch, 'mcp_manager') and orch.mcp_manager:
                mcp_tools_info = orch.mcp_manager.get_tools_info()
                # 权限展示仍使用 session 的 active_agents，与侧边栏一致
                mcp_tools_info['agent_permissions'] = st.session_state.active_agents
            else:
                mcp_tools_info = {
                    'total_tools': 0,
                    'server_count': 0,
                    'servers': {},
                    'agent_permissions': st.session_state.active_agents
                }
            # 未连接时：用 mcp_config.json 判断是否已配置（参考 mcp_tools_showcase.py）
            if mcp_tools_info.get('total_tools', 0) == 0:
                file_config = _load_mcp_config()
                if file_config:
                    mcp_tools_info['config_available'] = True
                    mcp_tools_info['config_server_count'] = file_config['server_count']
                    if mcp_tools_info.get('server_count', 0) == 0:
                        mcp_tools_info['server_count'] = file_config['server_count']
            return {
                'agents_count': agents_count,
                'mcp_tools_info': mcp_tools_info
            }
        # 无 orchestrator：仅根据 mcp_config.json 显示是否已配置
        file_config = _load_mcp_config()
        mcp_fallback = {
            'total_tools': 0,
            'server_count': file_config['server_count'] if file_config else 0,
            'servers': {},
            'agent_permissions': st.session_state.get('active_agents', {})
        }
        if file_config:
            mcp_fallback['config_available'] = True
            mcp_fallback['config_server_count'] = file_config['server_count']
        return {'agents_count': 15, 'mcp_tools_info': mcp_fallback}
    except Exception:
        file_config = _load_mcp_config()
        mcp_fallback = {
            'total_tools': 0,
            'server_count': file_config['server_count'] if file_config else 0,
            'servers': {},
            'agent_permissions': {}
        }
        if file_config:
            mcp_fallback['config_available'] = True
            mcp_fallback['config_server_count'] = file_config['server_count']
        return {'agents_count': 15, 'mcp_tools_info': mcp_fallback}

def show_system_overview(MCP_KNOWN_TOOL_COUNT=None):
    """显示系统概览"""
    st.markdown('<h2 class="main-title">🏛️ 系统概览</h2>', unsafe_allow_html=True)
    capabilities = get_system_capabilities()
    if capabilities:
        mcp_info = capabilities.get('mcp_tools_info', {})
        total_tools = mcp_info.get('total_tools', 0)
        server_count = mcp_info.get('server_count', 0)
        agents_count = capabilities.get('agents_count', 0)
        permissions = mcp_info.get('agent_permissions', {})
        enabled_agents = len([agent for agent, enabled in permissions.items() if enabled])
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # 已连接显示数量；有配置未连接显示「已配置」；否则「未连接」（逻辑参考 mcp_tools_showcase）
            configured_tool_count = MCP_KNOWN_TOOL_COUNT
            if not isinstance(configured_tool_count, int) or configured_tool_count <= 0:
                configured_tool_count = sum(
                    server_data.get('tool_count', 0)
                    for server_data in mcp_info.get('servers', {}).values()
                )

            if total_tools > 0:
                mcp_tools_label = f"{total_tools} 个"
            elif mcp_info.get("config_available"):
                mcp_tools_label = f"已配置{configured_tool_count}个" if configured_tool_count > 0 else "已配置"
            else:
                mcp_tools_label = "未连接"
            st.metric("MCP工具", mcp_tools_label)
        with col2:
            # 服务器数：来自实际连接或 mcp_config.json 的 config_server_count
            if server_count > 0:
                mcp_server_label = f"{server_count} 个"
            elif mcp_info.get("config_available"):
                mcp_server_label = f"{mcp_info.get('config_server_count', 0)} 个(已配置)"
            else:
                mcp_server_label = "未检测"
            st.metric(" MCP服务器", mcp_server_label)
        with col3:
            st.metric(" 智能体总数", f"{agents_count} 个")
        with col4:
            st.metric(" 已启用", f"{enabled_agents}/{agents_count}")
        st.markdown("---")
        st.markdown("###  智能体状态")
        agent_groups = {
            ' 分析师团队': ['company_overview_analyst', 'market_analyst', 'sentiment_analyst',
                           'news_analyst', 'fundamentals_analyst', 'shareholder_analyst', 'product_analyst'],
            ' 研究员团队': ['bull_researcher', 'bear_researcher'],
            ' 管理层': ['research_manager', 'trader'],
            ' 风险管理': ['aggressive_risk_analyst', 'safe_risk_analyst', 'neutral_risk_analyst', 'risk_manager'],
        }
        for group_name, agent_names in agent_groups.items():
            with st.expander(group_name, expanded=True):
                cols = st.columns(4)
                for i, agent in enumerate(agent_names):
                    with cols[i % 4]:
                        enabled = st.session_state.active_agents.get(agent, False)
                        agent_display = get_agent_display_name(agent)
                        agent_type = get_agent_type(agent)
                        status_icon = "✅" if enabled else "⭕"
                        status_text = "已启用" if enabled else "已禁用"
                        status_color = "#10b981" if enabled else "#64748b"
                        st.markdown(f"""
                        <div class="report-card" style="margin:0.5rem 0;padding:1rem;text-align:center;">
                            <div style="font-size:1.5rem;margin-bottom:0.5rem;">{status_icon}</div>
                            <div style="font-weight:600;color:#ccd6f6;font-size:0.85rem;margin-bottom:0.25rem;">
                                {agent_display}
                            </div>
                            <span class="agent-tag {agent_type}">{agent_type.upper()}</span>
                            <div style="font-size:0.75rem;color:{status_color};margin-top:0.5rem;">{status_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
        if total_tools > 0:
            st.markdown("---")
            st.markdown("###  MCP 工具详情")
            servers_info = mcp_info.get('servers', {})
            for server_name, server_data in servers_info.items():
                with st.expander(f"**{server_name}** ({server_data.get('tool_count', 0)} 个工具)", expanded=False):
                    tools = server_data.get('tools', [])
                    if tools:
                        for tool in tools[:10]:
                            tool_desc = tool.get('description', '无描述')[:80] + ('...' if len(tool.get('description', '')) > 80 else '')
                            st.markdown(f"  - `{tool.get('name', '未知')}`: {tool_desc}")
                        if len(tools) > 10:
                            st.info(f"  ... 还有 {len(tools) - 10} 个工具")
                    else:
                        st.info("  暂无工具信息")
    else:
        st.warning("⚠️ 无法获取系统信息，请先连接系统")
