#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时分析页面
"""

import streamlit as st
from src.web.sidebar import get_agent_display_name, get_agent_type
from src.web.analysis_engine import AnalysisEngine, start_analysis, stop_analysis
from src.workflow_orchestrator import WorkflowOrchestrator


def show_real_time_analysis():
    """实时分析页面"""
    st.markdown('<h2 class="main-title">🔍 智能实时分析</h2>', unsafe_allow_html=True)

    # 检查后台分析状态（在主线程中执行）
    AnalysisEngine.check_and_update_analysis_state()

    if not st.session_state.orchestrator:
        AnalysisEngine.auto_connect_system(WorkflowOrchestrator)

    if not st.session_state.orchestrator:
        st.info("👆 请先在侧边栏连接系统")
        return

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    user_query = st.text_area(
        "💬 请输入要分析的股票或公司",
        placeholder="例如：分析苹果公司股票的投资价值...",
        height=120,
        key="analysis_query",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        if st.button("🚀 开始分析", type="primary", use_container_width=True, disabled=st.session_state.analysis_running):
            if not user_query.strip():
                st.warning("⚠️ 请输入要分析的内容")
            else:
                enabled_agents = [agent for agent in st.session_state.active_agents.keys()
                                if st.session_state.active_agents[agent]]

                start_analysis(
                    query=user_query.strip(),
                    orchestrator=st.session_state.orchestrator,
                    active_agents=enabled_agents
                )
                st.rerun()

    with col2:
        if st.button("⏹️ 停止", use_container_width=True, disabled=not st.session_state.analysis_running):
            stop_analysis()
            st.rerun()

    with col3:
        if st.button("🔄 清空", use_container_width=True):
            st.session_state.current_query = ""
            st.rerun()

    with col4:
        if st.button("🔃 刷新状态", use_container_width=True):
            st.rerun()

    if 'analysis_error' in st.session_state:
        st.error(f"❌ 分析失败: {st.session_state.analysis_error}")
        if st.button("清除错误", key="clear_error"):
            del st.session_state['analysis_error']
            st.rerun()

    if st.session_state.analysis_running:
        st.markdown("---")
        st.markdown("### 📊 分析进度")

        enabled_agents = [agent for agent in st.session_state.active_agents.keys()
                         if st.session_state.active_agents[agent]]

        cols = st.columns(4)
        for i, agent in enumerate(enabled_agents[:16]):
            with cols[i % 4]:
                agent_display = get_agent_display_name(agent)
                agent_type = get_agent_type(agent)
                st.markdown(f"""
                <div class="report-card" style="margin:0.5rem 0;padding:1rem;text-align:center;">
                    <div style="font-size:2rem;margin-bottom:0.5rem;">🔄</div>
                    <div style="font-weight:600;color:#ccd6f6;font-size:0.9rem;margin-bottom:0.25rem;">
                        {agent_display}
                    </div>
                    <span class="agent-tag {agent_type}">{agent_type.upper()}</span>
                    <div style="font-size:0.75rem;color:#8892b0;margin-top:0.5rem;">运行中...</div>
                </div>
                """, unsafe_allow_html=True)

        st.info("💡 智能体正在分析中，请点击「🔃 刷新状态」按钮查看最新进度（分析可能需要几分钟）")

    # 检查是否需要自动刷新（分析完成后）
    if st.session_state.get('pending_rerun', False):
        st.session_state.pending_rerun = False
        st.rerun()

    if st.session_state.analysis_completed and st.session_state.current_session_data:
        # 设置当前页面标识，用于区分不同页面的导出按钮
        st.session_state.active_page = 'real_time_analysis'
        from src.web.pages.analysis_results import show_analysis_results
        show_analysis_results()
