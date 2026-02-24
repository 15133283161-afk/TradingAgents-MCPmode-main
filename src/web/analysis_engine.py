#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析引擎
处理智能体分析的核心逻辑
"""

import streamlit as st
import asyncio
import threading
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv


class AnalysisState:
    """分析状态管理"""
    def __init__(self):
        self.cancelled = False
        self.running = False
        self.result = None
        self.error = None
        self.result_dict = None  # 存储分析结果字典


class AnalysisEngine:
    """分析引擎"""

    @staticmethod
    def auto_connect_system(WorkflowOrchestrator):
        """自动连接MCP系统（含 MCP 客户端初始化，系统概览可显示工具数）"""
        if not st.session_state.orchestrator and WorkflowOrchestrator:
            with st.spinner("🔄 正在连接AI系统..."):
                try:
                    load_dotenv()
                    orchestrator = WorkflowOrchestrator()
                    # 初始化 MCP 连接与工具发现，使系统概览能显示真实工具数
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(orchestrator.initialize())
                    except Exception as mcp_e:
                        # MCP 初始化失败不影响 orchestrator 使用，仅工具数为 0
                        pass
                    st.session_state.orchestrator = orchestrator
                    st.session_state.auto_connected = True
                    st.success("✅ 系统连接成功！AI智能体团队已准备就绪")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 系统连接失败: {e}")

    @staticmethod
    async def run_analysis_async(user_query: str, orchestrator, analysis_state: AnalysisState, enabled_agents: List[str]):
        """异步执行分析"""
        try:
            if analysis_state.cancelled:
                return None

            load_dotenv()

            if not enabled_agents:
                raise ValueError("没有启用的智能体，请在侧边栏选择要启用的智能体")

            def cancel_checker():
                return analysis_state.cancelled

            result = await orchestrator.run_analysis(
                user_query=user_query,
                cancel_checker=cancel_checker,
                active_agents=enabled_agents
            )

            if analysis_state.cancelled:
                return None

            analysis_state.result = result
            analysis_state.running = False
            return result

        except Exception as e:
            if analysis_state.cancelled:
                return None
            analysis_state.error = str(e)
            analysis_state.running = False
            raise

    @staticmethod
    def start_analysis_thread(query: str, orchestrator, enabled_agents: List[str], analysis_state: AnalysisState):
        """在后台线程中运行分析"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                AnalysisEngine.run_analysis_async(query, orchestrator, analysis_state, enabled_agents)
            )

            loop.close()

            if result and not analysis_state.cancelled:
                try:
                    dump_dir = Path("src/dump")
                    dump_dir.mkdir(parents=True, exist_ok=True)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    session_file = dump_dir / f"session_{timestamp}_{abs(hash(query)) % 1000000:06d}.json"

                    # 获取 agent_execution_history（列表格式）
                    agent_history = getattr(result, 'agent_execution_history', [])

                    # 构建结果字典
                    result_dict = {
                        'session_id': timestamp,
                        'user_query': query,
                        'status': 'completed',
                        'timestamp': datetime.now().isoformat(),
                        'agents': [],
                        'agent_execution_history': agent_history
                    }

                    # 将 agent_execution_history 列表转换为 agents 列表
                    if agent_history:
                        for agent_data in agent_history:
                            agent_name = agent_data.get('agent_name', 'unknown')
                            result_content = agent_data.get('result', '')

                            result_dict['agents'].append({
                                'agent_name': agent_name,
                                'status': agent_data.get('status', 'completed'),
                                'result': result_content,  # 使用 'result' 字段而不是 'response'
                                'end_time': agent_data.get('timestamp', datetime.now().isoformat())  # 使用 'timestamp' 字段
                            })

                    # 只有当有有效数据时才保存文件
                    if result_dict['agents']:
                        with open(session_file, 'w', encoding='utf-8') as f:
                            json.dump(result_dict, f, ensure_ascii=False, indent=2)

                        # 将结果存储在 analysis_state 中
                        analysis_state.result_dict = result_dict
                    else:
                        # 即使没有保存文件，仍然将结果存储以便显示
                        analysis_state.result_dict = result_dict
                except Exception as e:
                    analysis_state.error = str(e)

            analysis_state.running = False

        except Exception as e:
            analysis_state.error = str(e)
            analysis_state.running = False

    @staticmethod
    def start_analysis(query: str, orchestrator, active_agents: List[str]) -> AnalysisState:
        """开始分析"""
        # 在主线程中筛选启用的智能体
        enabled_agents = [agent for agent in active_agents if st.session_state.active_agents.get(agent, False)]

        if not enabled_agents:
            raise ValueError("没有启用的智能体，请在侧边栏选择要启用的智能体")

        analysis_state = AnalysisState()
        analysis_state.running = True

        thread = threading.Thread(
            target=AnalysisEngine.start_analysis_thread,
            args=(query, orchestrator, enabled_agents, analysis_state),
            daemon=True
        )
        thread.start()

        st.session_state.analysis_state_obj = analysis_state
        st.session_state.analysis_running = True
        st.session_state.current_query = query

        return analysis_state

    @staticmethod
    def stop_analysis():
        """停止分析"""
        st.session_state.analysis_cancelled = True
        st.session_state.analysis_running = False

        analysis_state = st.session_state.get('analysis_state_obj')
        if analysis_state:
            analysis_state.cancelled = True

        st.warning("⏸️ 分析已停止")

    @staticmethod
    def check_and_update_analysis_state():
        """检查分析状态并更新session_state（在主线程中调用）"""
        analysis_state = st.session_state.get('analysis_state_obj')

        if not analysis_state or analysis_state.running:
            return

        # 分析已完成或出错
        st.session_state.analysis_running = False

        if analysis_state.error:
            st.session_state.analysis_error = analysis_state.error
        elif analysis_state.result_dict and not analysis_state.cancelled:
            result_dict = analysis_state.result_dict

            # 只在首次完成时设置刷新标记（避免无限循环）
            was_already_completed = st.session_state.get('analysis_completed', False)

            # 更新 session_state
            st.session_state.current_session_data = result_dict
            st.session_state.analysis_completed = True

            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            st.session_state.chat_history.append({
                'query': result_dict.get('user_query', ''),
                'timestamp': datetime.now().isoformat(),
                'result': result_dict
            })

            # 只在首次完成时触发自动刷新
            if not was_already_completed:
                st.session_state.pending_rerun = True


# Module-level wrapper functions for convenient importing
def start_analysis(query: str, orchestrator, active_agents: List[str]) -> AnalysisState:
    """开始分析 - 模块级包装函数"""
    return AnalysisEngine.start_analysis(query, orchestrator, active_agents)


def stop_analysis():
    """停止分析 - 模块级包装函数"""
    return AnalysisEngine.stop_analysis()
