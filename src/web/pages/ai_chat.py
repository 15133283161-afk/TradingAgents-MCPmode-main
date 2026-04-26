#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 对话页面
"""

import asyncio

import streamlit as st
from dotenv import load_dotenv

from src.workflow_orchestrator import WorkflowOrchestrator

try:
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError:
    try:
        from langchain.schema import HumanMessage, AIMessage
    except ImportError:
        from langchain_core.messages import HumanMessage, AIMessage


def _build_chat_messages(history):
    messages = []
    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        if not content:
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def _generate_ai_reply(user_input: str, orchestrator) -> str:
    load_dotenv()
    history = st.session_state.get("ai_chat_messages", [])
    system_prompt = """你是 AI 智能交易分析系统中的对话助手。

你的职责：
1. 使用中文与用户直接对话。
2. 结合本系统的股票投资分析场景，为用户提供清晰、专业、简洁的回答。
3. 如果用户的问题与投资分析、系统功能、智能体分工、分析结果理解有关，优先结合本项目场景回答。
4. 不要假装已经执行了不存在的分析；如果需要正式分析，提醒用户去“实时分析”页发起。
5. 回答保持简洁，结构清楚，避免冗长。
"""
    messages = [HumanMessage(content=system_prompt)]
    messages.extend(_build_chat_messages(history))
    messages.append(HumanMessage(content=user_input))

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(orchestrator.mcp_manager.llm.ainvoke(messages))
        content = getattr(response, "content", "")
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        parts.append(text)
                elif isinstance(item, str):
                    parts.append(item)
            return "\n".join(parts).strip() or "抱歉，我暂时无法生成回复。"
        return str(content).strip() or "抱歉，我暂时无法生成回复。"
    finally:
        loop.close()



def show_ai_chat():
    """AI 对话页面"""
    st.markdown('<h2 class="main-title">🤖 AI 对话助手</h2>', unsafe_allow_html=True)
    st.caption("可用于咨询系统功能、分析思路、结果解读；正式股票分析请前往“实时分析”页。")

    if "ai_chat_messages" not in st.session_state:
        st.session_state.ai_chat_messages = []
    if "ai_chat_busy" not in st.session_state:
        st.session_state.ai_chat_busy = False

    if not st.session_state.orchestrator:
        with st.spinner("正在连接 AI 系统..."):
            try:
                orchestrator = WorkflowOrchestrator()
                st.session_state.orchestrator = orchestrator
                st.success("系统已连接，现在可以开始对话")
            except Exception as e:
                st.error(f"系统连接失败: {e}")
                return

    toolbar_col1, toolbar_col2 = st.columns([1, 1])
    with toolbar_col1:
        if st.button("清空对话", use_container_width=True):
            st.session_state.ai_chat_messages = []
            st.rerun()
    with toolbar_col2:
        if st.button("载入分析结果上下文", use_container_width=True):
            session_data = st.session_state.get("current_session_data")
            if not session_data:
                st.warning("当前没有可用的分析结果")
            else:
                user_query = session_data.get("user_query", "")
                final_results = session_data.get("final_results", {})
                summary = final_results if isinstance(final_results, str) else str(final_results)
                content = f"当前已加载分析结果。\n用户问题：{user_query}\n分析摘要：{summary[:2000]}"
                st.session_state.ai_chat_messages.append({"role": "assistant", "content": content})
                st.rerun()

    st.markdown("---")

    if not st.session_state.ai_chat_messages:
        st.markdown("""
        <div class="info-card" style="padding:1.2rem 1rem;">
            <div style="color:#ccd6f6;font-weight:600;margin-bottom:0.5rem;">可以这样开始：</div>
            <div style="color:#8892b0;line-height:1.8;">
                1. 这个系统里各个智能体分别做什么？<br>
                2. 帮我解释一下为什么要做多空辩论？<br>
                3. 我刚跑完分析，帮我解读结果重点。<br>
                4. 现在适合分析哪些股票维度？
            </div>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.ai_chat_messages:
        with st.chat_message("user" if message.get("role") == "user" else "assistant"):
            st.markdown(message.get("content", ""))

    user_input = st.chat_input("请输入你想咨询的问题")

    if user_input and not st.session_state.ai_chat_busy:
        st.session_state.ai_chat_messages.append({"role": "user", "content": user_input})
        st.session_state.ai_chat_busy = True
        try:
            with st.chat_message("assistant"):
                with st.spinner("AI 正在思考..."):
                    reply = _generate_ai_reply(user_input, st.session_state.orchestrator)
                    st.markdown(reply)
            st.session_state.ai_chat_messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            error_message = f"对话失败：{e}"
            st.error(error_message)
            st.session_state.ai_chat_messages.append({"role": "assistant", "content": error_message})
        finally:
            st.session_state.ai_chat_busy = False
            st.rerun()
