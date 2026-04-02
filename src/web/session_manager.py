#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话状态管理器
管理Streamlit应用的会话状态
"""

import streamlit as st
from typing import Dict, Any, List


class SessionManager:
    """会话状态管理器"""
    @staticmethod
    def init_session_state():
        """初始化会话状态"""
        defaults = {
            'orchestrator': None,
            'analysis_running': False,
            'selected_session_file': None,
            'current_session_data': None,
            'analysis_completed': False,
            'auto_connected': False,
            'analysis_cancelled': False,
            'active_agents': {
                # 所有智能体默认启用
                'company_overview_analyst': True,   # 公司概述
                'market_analyst': True,             # 市场分析
                'fundamentals_analyst': True,       # 基本面分析
                'sentiment_analyst': True,          # 情绪分析
                'news_analyst': True,               # 新闻分析
                'shareholder_analyst': True,        # 股东分析
                'product_analyst': True,            # 产品分析
                'bull_researcher': True,            # 看涨研究
                'bear_researcher': True,            # 看跌研究
                'research_manager': True,           # 研究经理
                'trader': True,                     # 交易员
                'aggressive_risk_analyst': True,    # 激进风险分析
                'safe_risk_analyst': True,          # 保守风险分析
                'neutral_risk_analyst': True,       # 中性风险分析
                'risk_manager': True,               # 风险经理
            },
            'debate_rounds': 0,
            'risk_debate_rounds': 0,
            'chat_history': [],
            'current_query': '',
            'pending_rerun': False,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get_active_agents() -> List[str]:
        """获取启用的智能体列表"""
        return [agent for agent, enabled in st.session_state.active_agents.items() if enabled]

    @staticmethod
    def set_active_agent(agent_name: str, enabled: bool):
        """设置智能体启用状态"""
        if agent_name in st.session_state.active_agents:
            st.session_state.active_agents[agent_name] = enabled

    @staticmethod
    def add_chat_history(query: str, result: Dict[str, Any]):
        """添加对话历史"""
        from datetime import datetime
        st.session_state.chat_history.append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'result': result
        })

    @staticmethod
    def clear_chat_history():
        """清空对话历史"""
        st.session_state.chat_history = []

    @staticmethod
    def reset_analysis_state():
        """重置分析状态"""
        st.session_state.analysis_running = False
        st.session_state.analysis_completed = False
        st.session_state.analysis_cancelled = False
        st.session_state.current_query = ''
