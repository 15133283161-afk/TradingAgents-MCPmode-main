#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析结果页面
"""

import streamlit as st
from src.web.sidebar import get_agent_display_name, get_agent_type
from src.web.export_manager import ExportManager


def show_analysis_results():
    """分析结果展示"""
    st.markdown('<h2 class="main-title">📊 分析结果详情</h2>', unsafe_allow_html=True)

    if not st.session_state.current_session_data:
        st.info("请先运行分析或加载历史会话查看结果")
        return

    data = st.session_state.current_session_data

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("会话ID", data.get('session_id', 'N/A')[:8] + "...")
    with col2:
        st.metric("状态", data.get('status', 'N/A'))
    with col3:
        completed_agents = len([agent for agent in data.get('agents', []) if agent.get('status') == 'completed'])
        st.metric("完成智能体", f"{completed_agents}/{len(data.get('agents', []))}")

    if data.get('user_query'):
        st.markdown("**🔍 分析查询:**")
        st.info(data['user_query'])

    # 如果没有设置 active_page，设置默认值
    if 'active_page' not in st.session_state:
        st.session_state.active_page = 'analysis_results'

    ExportManager.show_export_buttons(data)

    if data.get('agents'):
        completed_agents = [agent for agent in data['agents'] if agent.get('status') == 'completed']

        if completed_agents:
            st.markdown("---")
            st.markdown("### 🤖 智能体分析详情")

            agent_groups = {
                "📊 分析师团队": ['company_overview_analyst', 'market_analyst', 'sentiment_analyst',
                                'news_analyst', 'fundamentals_analyst', 'shareholder_analyst', 'product_analyst'],
                "🔄 看涨看跌辩论": ['bull_researcher', 'bear_researcher'],
                "👔 研究与交易": ['research_manager', 'trader'],
                "⚖️ 风险管理": ['aggressive_risk_analyst', 'safe_risk_analyst', 'neutral_risk_analyst', 'risk_manager']
            }

            for group_name, agent_names in agent_groups.items():
                group_agents = [agent for agent in completed_agents if agent.get('agent_name') in agent_names]

                if group_agents:
                    st.markdown(f"#### {group_name}")
                    for agent in group_agents:
                        agent_name = agent.get('agent_name', '')
                        display_name = get_agent_display_name(agent_name)
                        agent_type = get_agent_type(agent_name)
                        result = agent.get('result', '')

                        with st.expander(f"**{display_name}**", expanded=False):
                            st.markdown(f"""
                            <span class="agent-tag {agent_type}">{agent_type.upper()}</span>
                            """, unsafe_allow_html=True)
                            st.markdown(result)
                else:
                    st.info(f"{group_name.split(' ', 1)[1]}暂无完成的分析结果")
        else:
            st.info("该会话中暂无完成的智能体分析结果")
