#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
侧边栏
显示侧边栏界面
"""

import streamlit as st


def get_agent_display_name(agent_name: str) -> str:
    """获取智能体显示名称"""
    name_mapping = {
        'company_overview_analyst': '公司概述分析师',
        'market_analyst': '市场分析师',
        'sentiment_analyst': '情绪分析师',
        'news_analyst': '新闻分析师',
        'fundamentals_analyst': '基本面分析师',
        'shareholder_analyst': '股东分析师',
        'product_analyst': '产品分析师',
        'bull_researcher': '看涨研究员',
        'bear_researcher': '看跌研究员',
        'research_manager': '研究经理',
        'trader': '交易员',
        'aggressive_risk_analyst': '激进风险分析师',
        'safe_risk_analyst': '️保守风险分析师',
        'neutral_risk_analyst': '中性风险分析师',
        'risk_manager': '风险经理'
    }
    return name_mapping.get(agent_name, agent_name)


def get_agent_type(agent_name: str) -> str:
    """获取智能体类型"""
    if 'analyst' in agent_name:
        return 'analyst'
    elif 'bull' in agent_name:
        return 'bull'
    elif 'bear' in agent_name:
        return 'bear'
    elif 'manager' in agent_name or 'trader' in agent_name:
        return 'manager'
    elif 'risk' in agent_name:
        return 'risk'
    return 'other'


def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.markdown('<h3 style="text-align:center;color:#000000;">AI实验室</h3>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("系统状态")
        if st.session_state.orchestrator:
            st.success("✅ 系统已连接")
            st.caption("所有智能体已就绪")
        else:
            st.warning("⚠️ 等待连接")
            if st.button("🔗 连接系统", use_container_width=True):
                from src.web.analysis_engine import AnalysisEngine
                from src.workflow_orchestrator import WorkflowOrchestrator
                AnalysisEngine.auto_connect_system(WorkflowOrchestrator)

        st.markdown("---")

        st.markdown("### 智能体控制")

        agent_groups = {
            '分析师团队': ['company_overview_analyst', 'market_analyst', 'sentiment_analyst',
                           'news_analyst', 'fundamentals_analyst', 'shareholder_analyst', 'product_analyst'],
            '研究员团队': ['bull_researcher', 'bear_researcher'],
            '管理层': ['research_manager', 'trader'],
            '风险管理': ['aggressive_risk_analyst', 'safe_risk_analyst', 'neutral_risk_analyst', 'risk_manager'],
        }

        enabled_count = sum(1 for v in st.session_state.active_agents.values() if v)
        st.info(f"已启用 {enabled_count}/15 个智能体")

        for group_name, agents in agent_groups.items():
            with st.expander(group_name, expanded=True):
                for agent in agents:
                    display_name = get_agent_display_name(agent)
                    st.session_state.active_agents[agent] = st.checkbox(
                        display_name,
                        value=st.session_state.active_agents[agent],
                        key=f"agent_{agent}"
                    )
        st.markdown("---")

        st.markdown("### 🌀 辩论配置")

        st.session_state.debate_rounds = st.number_input(
            "投资辩论轮次",
            min_value=0,
            max_value=5,
            value=int(st.session_state.debate_rounds),
            step=1,
            help="设置投资辩论的轮次数（0-5轮）"
        )

        st.session_state.risk_debate_rounds = st.number_input(
            "风险辩论轮次",
            min_value=0,
            max_value=5,
            value=int(st.session_state.risk_debate_rounds),
            step=1,
            help="设置风险辩论的轮次数（0-5轮）"
        )

        st.markdown("---")

        if st.session_state.chat_history:
            st.markdown("### 💬 对话历史")
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
                query_preview = chat['query'][:30] + "..." if len(chat['query']) > 30 else chat['query']
                if st.button(f"💭 {query_preview}", key=f"history_{i}", use_container_width=True):
                    st.session_state.current_session_data = chat['result']
                    st.session_state.analysis_completed = True
                    st.rerun()
