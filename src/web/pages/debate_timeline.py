#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辩论时间轴页面
"""

import streamlit as st
from src.web.sidebar import get_agent_display_name, get_agent_type


def show_debate_timeline(show_header: bool = True):
    """专业辩论时间轴展示"""
    if show_header:
        st.markdown('<h2 class="main-title">🗣️ 专业辩论展示</h2>', unsafe_allow_html=True)

    if not st.session_state.current_session_data:
        st.info("请先在「历史会话」标签页选择一个会话来查看辩论过程")
        return

    data = st.session_state.current_session_data
    agents = data.get('agents', [])
    completed_agents = [agent for agent in agents if agent.get('status') == 'completed' and agent.get('result')]

    if not completed_agents:
        st.info("该会话中暂无完成的智能体分析结果")
        return

    def calculate_votes(agents):
        """计算投票数，确保每个智能体只投一票"""
        bull_count = 0
        bear_count = 0
        neutral_count = 0

        for agent in agents:
            agent_name = agent.get('agent_name', '').lower()
            result = agent.get('result', '').lower()

            # 优先根据智能体名称判断（明确的角色立场）
            if 'bull' in agent_name:
                bull_count += 1
            elif 'bear' in agent_name:
                bear_count += 1
            else:
                # 对于其他智能体，根据结果内容判断倾向
                bull_keywords = ['看涨', '买入', '上涨', 'bullish', '积极', '利好', '推荐买入']
                bear_keywords = ['看跌', '卖出', '下跌', 'bearish', '消极', '利空', '推荐卖出']

                bull_score = sum(1 for kw in bull_keywords if kw in result)
                bear_score = sum(1 for kw in bear_keywords if kw in result)

                if bull_score > bear_score:
                    bull_count += 1
                elif bear_score > bull_score:
                    bear_count += 1
                else:
                    neutral_count += 1

        return bull_count, bear_count, neutral_count

    bull_count, bear_count, neutral_count = calculate_votes(completed_agents)
    total = bull_count + bear_count + neutral_count

    if total > 0:
        bull_pct = (bull_count / total) * 100 if total > 0 else 0
        bear_pct = (bear_count / total) * 100 if total > 0 else 0

        st.markdown(f"""
        <div class="info-card">
            <h3 style="text-align:center;color:#ccd6f6;margin-bottom:1rem;">投票统计（共{total}票）</h3>
            <div style="display:flex;align-items:center;gap:2rem;justify-content:center;">
                <div style="text-align:center;">
                    <div style="font-size:2rem;font-weight:700;color:#10b981;">{bull_count}</div>
                    <div style="font-size:0.85rem;color:#8892b0;">看涨 ({bull_pct:.1f}%)</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:2rem;font-weight:700;color:#f59e0b;">{neutral_count}</div>
                    <div style="font-size:0.85rem;color:#8892b0;">中立 ({100-bull_pct-bear_pct:.1f}%)</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:2rem;font-weight:700;color:#ef4444;">{bear_count}</div>
                    <div style="font-size:0.85rem;color:#8892b0;">看跌 ({bear_pct:.1f}%)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📜 辩论时间轴")

    st.markdown('<div class="timeline">', unsafe_allow_html=True)

    for i, agent in enumerate(completed_agents):
        position = 'right' if i % 2 == 0 else 'left'
        agent_name = agent.get('agent_name', '')
        display_name = get_agent_display_name(agent_name)
        agent_type = get_agent_type(agent_name)
        result = agent.get('result', '')
        # 固定展示完整内容
        display_result = result

        st.markdown(f"""
        <div class="timeline-item {position}">
            <div class="timeline-content">
                <span class="agent-tag {agent_type}">{agent_type.upper()}</span>
                <h4 style="color:#000000;margin:0.5rem 0;">{display_name}</h4>
                <div class="timeline-text-content">
                    {display_result}
                </div>
                <div style="color:#64ffda;font-size:0.75rem;margin-top:0.5rem;">
                    内容长度: {len(result)} 字符
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 添加统计信息
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center;color:#8892b0;font-size:0.9rem;">
         共展示 <strong style="color:#64ffda;">{len(completed_agents)}</strong> 个智能体的辩论结果
    </div>
    """, unsafe_allow_html=True)
