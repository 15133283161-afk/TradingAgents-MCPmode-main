#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主应用
Streamlit应用的主入口
"""

import streamlit as st
import sys
import os
import warnings
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.session_manager import SessionManager
from src.web.sidebar import show_sidebar
from src.web.pages import (
    show_real_time_analysis,
    show_history_sessions,
    show_debate_timeline,
    show_system_overview
)


def configure_page():
    """配置页面"""
    st.set_page_config(
        page_title="AI实验室 - 智能交易分析系统",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    warnings.filterwarnings("ignore")
    logging.getLogger().setLevel(logging.ERROR)


def load_custom_css():
    """加载自定义CSS样式"""
    css_dir = os.path.join(os.path.dirname(__file__), "css")
    css_files = ["styles.css", "financial_styles.css"]

    for name in css_files:
        css_file = os.path.join(css_dir, name)
        if not os.path.exists(css_file):
            continue

        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            # 记录日志但不在前端打断用户体验
            logging.warning(f"加载CSS文件失败: {css_file}, 错误: {e}")


def main():
    """主界面"""
    configure_page()
    load_custom_css()
    SessionManager.init_session_state()

    show_sidebar()

    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem 2rem 1rem;">
        <h1 class="main-title">🔬 AI智能交易分析系统</h1>
        <p style="color:#8892b0;font-size:1.25rem;">基于多智能体协同的智能投资决策平台</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 实时分析",
        "📚 历史会话",
        "🗣️ 辩论展示",
        "🏛️ 系统概览"
    ])

    with tab1:
        show_real_time_analysis()
    with tab2:
        show_history_sessions()
    with tab3:
        show_debate_timeline()
    with tab4:
        show_system_overview()


if __name__ == "__main__":
    main()
