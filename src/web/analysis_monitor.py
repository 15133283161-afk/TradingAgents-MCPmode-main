#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析监控器
实时监控智能体分析过程
"""

import streamlit as st
import asyncio
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.workflow_orchestrator import WorkflowOrchestrator


class AnalysisMonitor:
    """分析监控器"""
    
    def __init__(self):
        self.dump_dir = Path("src/dump")
        self.dump_dir.mkdir(exist_ok=True)
    
    def show_analysis_interface(self):
        """显示分析界面"""
        st.title("📊 实时分析监控")
        
        # 连接状态检查
        if not self._check_connection():
            st.error("❌ 系统未连接，请先在侧边栏点击连接按钮")
            return
        
        # 分析输入区
        with st.container():
            st.markdown("### 📝 开始新的分析")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                user_query = st.text_input(
                    "请输入您要分析的股票或问题",
                    placeholder="例如: 分析苹果公司(AAPL)股票，腾讯控股怎么样？，给我分析平安银行",
                    help="支持自然语言查询，系统会自动识别股票代码和市场"
                )
            
            with col2:
                start_analysis = st.button(
                    "🚀 开始分析",
                    use_container_width=True,
                    disabled=st.session_state.analysis_running
                )
        
        # 开始分析
        if start_analysis and user_query:
            if not st.session_state.analysis_running:
                st.session_state.analysis_running = True
                st.session_state.user_query = user_query
                st.rerun()
        
        # 分析进行中
        if st.session_state.analysis_running:
            self._show_analysis_progress()
        
        # 显示当前会话结果
        if hasattr(st.session_state, 'current_session') and st.session_state.current_session:
            self._show_current_session_results()
    
    def _check_connection(self) -> bool:
        """检查系统连接状态"""
        if 'orchestrator' not in st.session_state or st.session_state.orchestrator is None:
            with st.sidebar:
                if st.button("🔗 连接系统", use_container_width=True):
                    with st.spinner("正在连接系统..."):
                        try:
                            orchestrator = WorkflowOrchestrator("mcp_config.json")
                            # 使用异步运行初始化
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(orchestrator.initialize())
                            
                            st.session_state.orchestrator = orchestrator
                            st.success("✅ 系统连接成功！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 连接失败: {e}")
                            return False
        
        return st.session_state.orchestrator is not None
    
    def _show_analysis_progress(self):
        """显示分析进度"""
        st.markdown("---")
        st.markdown("### 🔄 分析进行中...")
        
        # 创建进度显示容器
        progress_container = st.container()
        status_container = st.container()
        
        with progress_container:
            st.info(f"📝 分析问题: {st.session_state.user_query}")
            
            # 总体进度条
            overall_progress = st.progress(0)
            overall_status = st.empty()
            
            # 阶段进度显示
            stage_container = st.container()
        
        # 启动分析（在后台线程中）
        if not hasattr(st.session_state, 'analysis_thread') or not st.session_state.analysis_thread.is_alive():
            st.session_state.analysis_thread = threading.Thread(
                target=self._run_analysis_async,
                args=(st.session_state.user_query,)
            )
            st.session_state.analysis_thread.start()
        
        # 监控分析进度
        self._monitor_progress(overall_progress, overall_status, stage_container)
        
        # 停止分析按钮
        if st.button("⏹️ 停止分析", type="secondary"):
            st.session_state.analysis_running = False
            st.rerun()
    
    def _run_analysis_async(self, user_query: str):
        """在后台异步运行分析"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行分析
            result = loop.run_until_complete(
                st.session_state.orchestrator.run_analysis(user_query)
            )
            
            # 保存结果
            st.session_state.analysis_result = result
            st.session_state.analysis_running = False
            
            loop.close()
            
        except Exception as e:
            st.session_state.analysis_error = str(e)
            st.session_state.analysis_running = False
    
    def _monitor_progress(self, progress_bar, status_text, stage_container):
        """监控分析进度"""
        start_time = time.time()
        
        # 定义阶段映射
        stage_mapping = {
            0: "🏢 公司概述分析",
            1: "📊 分析师团队分析",
            2: "💭 投资观点辩论",
            3: "👔 投资决策制定",
            4: "⚠️ 风险评估分析"
        }
        
        while st.session_state.analysis_running:
            elapsed_time = int(time.time() - start_time)
            
            # 查找最新的会话文件
            latest_session = self._find_latest_session()
            if latest_session:
                progress_data = self._parse_session_progress(latest_session)
                
                # 更新进度条
                progress_value = min(progress_data['progress'] / 100.0, 1.0)
                progress_bar.progress(progress_value)
                
                # 更新状态文本
                current_stage = progress_data['current_stage']
                stage_name = stage_mapping.get(current_stage, f"阶段 {current_stage}")
                status_text.text(f"⏱️ 已运行 {elapsed_time}s | 当前: {stage_name}")
                
                # 显示阶段详情
                with stage_container:
                    self._display_stage_progress(progress_data)
            
            time.sleep(2)  # 2秒更新一次
            
            # 检查是否完成
            if hasattr(st.session_state, 'analysis_result'):
                progress_bar.progress(1.0)
                status_text.text("✅ 分析完成！")
                break
            
            if hasattr(st.session_state, 'analysis_error'):
                status_text.text(f"❌ 分析失败: {st.session_state.analysis_error}")
                break
    
    def _find_latest_session(self) -> Optional[Path]:
        """查找最新的会话文件"""
        try:
            session_files = list(self.dump_dir.glob("session_*.json"))
            if session_files:
                return max(session_files, key=lambda f: f.stat().st_mtime)
            return None
        except Exception:
            return None
    
    def _parse_session_progress(self, session_file: Path) -> Dict[str, Any]:
        """解析会话进度"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 分析进度
            agents = data.get('agents', [])
            total_agents = 15  # 总共15个智能体
            completed_agents = len([a for a in agents if a.get('status') == 'completed'])
            
            progress = (completed_agents / total_agents) * 100 if total_agents > 0 else 0
            
            # 确定当前阶段
            current_stage = self._determine_current_stage(agents)
            
            return {
                'session_id': data.get('session_id', ''),
                'progress': progress,
                'current_stage': current_stage,
                'completed_agents': completed_agents,
                'total_agents': total_agents,
                'agents': agents,
                'status': data.get('status', 'running')
            }
            
        except Exception:
            return {'progress': 0, 'current_stage': 0, 'agents': []}
    
    def _determine_current_stage(self, agents: List[Dict]) -> int:
        """确定当前执行阶段"""
        # 阶段0: 公司概述
        company_overview_done = any(a.get('agent_name') == 'company_overview_analyst' 
                                  and a.get('status') == 'completed' for a in agents)
        if not company_overview_done:
            return 0
        
        # 阶段1: 分析师团队 (7个分析师)
        analyst_names = ['market_analyst', 'sentiment_analyst', 'news_analyst', 
                        'fundamentals_analyst', 'shareholder_analyst', 'product_analyst']
        analysts_done = sum(1 for name in analyst_names 
                           if any(a.get('agent_name') == name and a.get('status') == 'completed' 
                                 for a in agents))
        if analysts_done < 6:
            return 1
        
        # 阶段2: 研究员辩论
        bull_done = any(a.get('agent_name') == 'bull_researcher' 
                       and a.get('status') == 'completed' for a in agents)
        bear_done = any(a.get('agent_name') == 'bear_researcher' 
                       and a.get('status') == 'completed' for a in agents)
        if not (bull_done and bear_done):
            return 2
        
        # 阶段3: 管理层
        manager_done = any(a.get('agent_name') == 'research_manager' 
                          and a.get('status') == 'completed' for a in agents)
        trader_done = any(a.get('agent_name') == 'trader' 
                         and a.get('status') == 'completed' for a in agents)
        if not (manager_done and trader_done):
            return 3
        
        # 阶段4: 风险管理
        return 4
    
    def _display_stage_progress(self, progress_data: Dict[str, Any]):
        """显示阶段进度详情"""
        agents = progress_data.get('agents', [])
        
        # 按阶段分组显示
        st.markdown("#### 各阶段执行状态")
        
        # 阶段0: 公司概述
        company_agent = next((a for a in agents if a.get('agent_name') == 'company_overview_analyst'), None)
        if company_agent:
            status_emoji = "✅" if company_agent.get('status') == 'completed' else "🔄" if company_agent.get('status') == 'running' else "⏳"
            st.text(f"{status_emoji} 🏢 公司概述分析师")
        
        # 阶段1: 分析师团队
        analyst_mapping = {
            'market_analyst': '📈 市场分析师',
            'sentiment_analyst': '😊 情绪分析师', 
            'news_analyst': '📰 新闻分析师',
            'fundamentals_analyst': '📋 基本面分析师',
            'shareholder_analyst': '👥 股东分析师',
            'product_analyst': '🏭 产品分析师'
        }
        
        st.text("📊 分析师团队:")
        for agent_name, display_name in analyst_mapping.items():
            agent = next((a for a in agents if a.get('agent_name') == agent_name), None)
            if agent:
                status_emoji = "✅" if agent.get('status') == 'completed' else "🔄" if agent.get('status') == 'running' else "⏳"
                st.text(f"  {status_emoji} {display_name}")
        
        # 继续显示其他阶段...
    
    def _show_current_session_results(self):
        """显示当前会话结果"""
        st.markdown("---")
        st.markdown("### 📈 分析结果")
        
        if hasattr(st.session_state, 'analysis_result'):
            result = st.session_state.analysis_result
            
            # 显示基本信息
            st.success("🎉 分析完成！")
            
            # 提供查看详细结果的按钮
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 查看分析师报告", use_container_width=True):
                    st.switch_page("pages/analysts.py")
            
            with col2:
                if st.button("💭 查看投资辩论", use_container_width=True):
                    st.switch_page("pages/debate.py")
            
            with col3:
                if st.button("⚠️ 查看风险评估", use_container_width=True):
                    st.switch_page("pages/risk.py")
