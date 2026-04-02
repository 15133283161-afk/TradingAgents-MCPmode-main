#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS样式加载器
用于在Streamlit应用中加载自定义CSS样式
"""

import streamlit as st
from pathlib import Path


def load_financial_css():
    """加载CSS样式"""
    css_file = Path(__file__).parent / "financial_styles.css"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        return True
    else:
        st.warning(f"⚠️ CSS文件未找到: {css_file}")
        return False


def inject_custom_html():
    """注入自定义HTML元素 - 移除不稳定的动态类选择器"""
    # 只保留必要的全局隐藏，移除动态类名选择器
    # 注意：不能隐藏 header，否则侧边栏展开按钮会消失
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    /* header {visibility: hidden;} */  /* 注释掉，保留侧边栏按钮 */
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def create_header_html():
    """创建专业的顶部抬头HTML"""
    header_html = """
    <div class="header-container animate-fade-in">
        <div class="header-lab">🏛️ 人工智能实验室</div>
        <h1 class="header-title">TradingAgents-MCPmode</h1>
        <p class="header-subtitle">基于MCP工具的多智能体交易分析系统</p>
    </div>
    """
    return header_html


def create_metric_card_html(title, value, subtitle=""):
    """创建指标卡片HTML"""
    card_html = f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {f'<div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 4px;">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    return card_html


def create_status_indicator_html(status, text):
    """创建状态指示器HTML"""
    status_class = f"status-indicator status-{status}"
    
    icons = {
        'running': '🔄',
        'completed': '✅', 
        'idle': '💤',
        'error': '❌'
    }
    icon = icons.get(status, '📊')
    status_html = f"""
    <div class="{status_class}">
        <span>{icon}</span>
        <span>{text}</span>
    </div>
    """
    return status_html


def create_section_card_html(title, content, icon="📊"):
    """创建区域卡片HTML"""
    card_html = f"""
    <div class="financial-card animate-fade-in">
        <h3 class="card-title">
            <span>{icon}</span>
            <span>{title}</span>
        </h3>
        {content}
    </div>
    """
    return card_html


def create_workflow_stage_html(stage_title, agents):
    """创建工作流程阶段HTML"""
    agent_badges = ""
    for agent in agents:
        agent_badges += f'<span class="agent-badge">{agent}</span>'
    stage_html = f"""
    <div class="workflow-stage animate-fade-in">
        <div class="stage-title">{stage_title}</div>
        <div class="agent-list">{agent_badges}</div>
    </div>
    """
    return stage_html


def apply_button_style():
    """应用按钮样式"""
    button_css = """
    <style>
    .stButton > button {
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #d69e2e 0%, #b7791f 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(214, 158, 46, 0.3);
    }
    </style>
    """
    st.markdown(button_css, unsafe_allow_html=True)


def create_export_buttons_html():
    """创建导出按钮组HTML"""
    buttons_html = """
    <div style="display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0;">
        <button class="btn-export" onclick="window.export_markdown()"> 导出Markdown</button>
        <button class="btn-export" onclick="window.export_pdf()"> 导出PDF</button>
        <button class="btn-export" onclick="window.export_docx()"> 导出Word</button>
    </div>
    """
    return buttons_html
