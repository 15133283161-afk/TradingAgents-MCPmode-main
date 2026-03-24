#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果查看器
用于展示各智能体的分析结果
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
try:
    import markdown2
    # markdown2 使用 markdown() 函数而不是 markdown.markdown()
    class MarkdownWrapper:
        @staticmethod
        def markdown(text, extensions=None):
            return markdown2.markdown(text, extras=['tables', 'fenced-code-blocks'])
    markdown = MarkdownWrapper()
except ImportError:
    try:
        import markdown
    except ImportError:
        # Fallback: 创建一个简单的 markdown 转换函数
        class MarkdownWrapper:
            @staticmethod
            def markdown(text, extensions=None):
                return text.replace('\n', '<br>')
        markdown = MarkdownWrapper()
import re


class ResultsViewer:
    """结果查看器"""
    
    def __init__(self):
        self.dump_dir = Path("src/dump")
        self.markdown_dir = Path("src/dumptools/markdown_reports")
        
        # 智能体映射
        self.agent_mapping = {
            # 分析师团队
            'company_overview_analyst': {'name': '🏢 公司概述分析师', 'emoji': '🏢'},
            'market_analyst': {'name': '📈 市场分析师', 'emoji': '📈'}, 
            'sentiment_analyst': {'name': '😊 情绪分析师', 'emoji': '😊'},
            'news_analyst': {'name': '📰 新闻分析师', 'emoji': '📰'},
            'fundamentals_analyst': {'name': '📋 基本面分析师', 'emoji': '📋'},
            'shareholder_analyst': {'name': '👥 股东分析师', 'emoji': '👥'},
            'product_analyst': {'name': '🏭 产品分析师', 'emoji': '🏭'},
            
            # 研究员团队
            'bull_researcher': {'name': '📈 看涨研究员', 'emoji': '📈'},
            'bear_researcher': {'name': '📉 看跌研究员', 'emoji': '📉'},
            
            # 管理层
            'research_manager': {'name': '🎯 研究经理', 'emoji': '🎯'},
            'trader': {'name': '💰 交易员', 'emoji': '💰'},
            
            # 风险管理团队
            'aggressive_risk_analyst': {'name': '⚡ 激进风险分析师', 'emoji': '⚡'},
            'safe_risk_analyst': {'name': '🛡️ 保守风险分析师', 'emoji': '🛡️'},
            'neutral_risk_analyst': {'name': '⚖️ 中性风险分析师', 'emoji': '⚖️'},
            'risk_manager': {'name': '🎯 风险经理', 'emoji': '🎯'}
        }
    
    def show_analysts_results(self):
        """显示分析师团队结果"""
        st.title(" 分析师团队报告")
        
        # 获取最新会话数据
        latest_session = self._get_latest_session_data()
        if not latest_session:
            st.warning(" 暂无分析数据")
            return
        
        # 显示会话信息
        self._show_session_info(latest_session)
        
        # 分析师列表
        analyst_agents = ['company_overview_analyst', 'market_analyst', 'sentiment_analyst', 
                         'news_analyst', 'fundamentals_analyst', 'shareholder_analyst', 'product_analyst']
        
        # 创建标签页
        tabs = st.tabs([self.agent_mapping[agent]['emoji'] + " " + 
                       self.agent_mapping[agent]['name'].split(' ', 1)[1] for agent in analyst_agents])
        
        for i, agent_name in enumerate(analyst_agents):
            with tabs[i]:
                self._show_agent_result(latest_session, agent_name)
    
    def show_investment_debate(self):
        """显示投资辩论结果"""
        st.title("💭 看涨看跌辩论")
        
        latest_session = self._get_latest_session_data()
        if not latest_session:
            st.warning("📝 暂无辩论数据")
            return
        
        # 显示会话信息
        self._show_session_info(latest_session)
        
        # 辩论标签页
        tab1, tab2, tab3 = st.tabs(["📈 看涨观点", "📉 看跌观点", "🔄 辩论历史"])
        
        with tab1:
            self._show_agent_result(latest_session, 'bull_researcher')
        
        with tab2:
            self._show_agent_result(latest_session, 'bear_researcher')
        
        with tab3:
            self._show_debate_history(latest_session, 'investment')
    
    def show_research_manager(self):
        """显示研究经理结果"""
        st.title("🎯 研究经理报告")
        
        latest_session = self._get_latest_session_data()
        if not latest_session:
            st.warning("📝 暂无数据")
            return
        
        self._show_session_info(latest_session)
        self._show_agent_result(latest_session, 'research_manager')
    
    def show_trader(self):
        """显示交易员结果"""
        st.title("💰 交易员报告")
        
        latest_session = self._get_latest_session_data()
        if not latest_session:
            st.warning("📝 暂无数据")
            return
        
        self._show_session_info(latest_session)
        self._show_agent_result(latest_session, 'trader')
    
    def show_risk_debate(self):
        """显示风险辩论结果"""
        st.title("⚠️ 风险评估辩论")
        
        latest_session = self._get_latest_session_data()
        if not latest_session:
            st.warning("📝 暂无数据")
            return
        
        self._show_session_info(latest_session)
        
        # 风险辩论标签页
        tab1, tab2, tab3, tab4 = st.tabs(["⚡ 激进观点", "🛡️ 保守观点", "⚖️ 中性观点", "🔄 辩论历史"])
        
        with tab1:
            self._show_agent_result(latest_session, 'aggressive_risk_analyst')
        
        with tab2:
            self._show_agent_result(latest_session, 'safe_risk_analyst')
        
        with tab3:
            self._show_agent_result(latest_session, 'neutral_risk_analyst')
        
        with tab4:
            self._show_debate_history(latest_session, 'risk')
    
    def show_risk_manager(self):
        """显示风险经理结果"""
        st.title("🎯 风险经理 - 最终决策")
        
        latest_session = self._get_latest_session_data()
        if not latest_session:
            st.warning("📝 暂无数据")
            return
        
        self._show_session_info(latest_session)
        self._show_agent_result(latest_session, 'risk_manager')
        
        # 显示最终交易决策
        if 'final_trade_decision' in latest_session:
            st.markdown("---")
            st.markdown("## 🎯 最终交易决策")
            st.success(latest_session['final_trade_decision'])
    
    def show_history(self):
        """显示历史报告"""
        st.title("📋 历史分析报告")
        
        # 获取所有会话文件
        sessions = self._get_all_sessions()
        
        if not sessions:
            st.warning("📝 暂无历史数据")
            return
        
        # 会话选择
        session_options = []
        for session_file, session_data in sessions.items():
            session_id = session_data.get('session_id', session_file.stem)
            user_query = session_data.get('user_query', '无查询')
            created_at = session_data.get('created_at', '')
            
            if created_at:
                try:
                    # 解析时间戳
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = created_at[:16]
            else:
                time_str = "未知时间"
            
            session_options.append({
                'label': f"📝 {time_str} - {user_query[:30]}{'...' if len(user_query) > 30 else ''}",
                'value': session_file,
                'data': session_data
            })
        
        # 按时间排序（最新在前）
        session_options.sort(key=lambda x: x['value'].stat().st_mtime, reverse=True)
        
        selected_option = st.selectbox(
            "选择历史会话",
            options=session_options,
            format_func=lambda x: x['label']
        )
        
        if selected_option:
            selected_data = selected_option['data']
            
            # 显示选中会话的详细信息
            self._show_session_info(selected_data)
            
            # 创建概览标签页
            tab1, tab2, tab3 = st.tabs(["📊 执行概览", "📈 智能体结果", "📄 导出报告"])
            
            with tab1:
                self._show_session_overview(selected_data)
            
            with tab2:
                self._show_all_agents_summary(selected_data)
            
            with tab3:
                self._show_export_options(selected_option['value'])
    
    def _get_latest_session_data(self) -> Optional[Dict[str, Any]]:
        """获取最新会话数据"""
        try:
            session_files = list(self.dump_dir.glob("session_*.json"))
            if not session_files:
                return None
            
            latest_file = max(session_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"加载会话数据失败: {e}")
            return None
    
    def _get_all_sessions(self) -> Dict[Path, Dict[str, Any]]:
        """获取所有会话数据"""
        sessions = {}
        try:
            session_files = list(self.dump_dir.glob("session_*.json"))
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions[session_file] = data
                except Exception as e:
                    st.warning(f"无法加载 {session_file.name}: {e}")
                    continue
            
            return sessions
        except Exception as e:
            st.error(f"获取历史会话失败: {e}")
            return {}
    
    def _show_session_info(self, session_data: Dict[str, Any]):
        """显示会话基本信息"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 会话ID", session_data.get('session_id', 'N/A'))
        
        with col2:
            status = session_data.get('status', 'unknown')
            status_emoji = "✅" if status == 'completed' else "🔄" if status == 'running' else "❓"
            st.metric("状态", f"{status_emoji} {status}")
        
        with col3:
            created_at = session_data.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d %H:%M')
                except:
                    time_str = created_at[:16]
            else:
                time_str = "未知"
            st.metric("⏰ 创建时间", time_str)
        
        with col4:
            agents = session_data.get('agents', [])
            completed_count = len([a for a in agents if a.get('status') == 'completed'])
            st.metric(" 已完成智能体", f"{completed_count}/{len(agents)}")
        
        # 用户查询
        user_query = session_data.get('user_query', '')
        if user_query:
            st.info(f"🔍 分析问题: {user_query}")
        
        st.markdown("---")
    
    def _show_agent_result(self, session_data: Dict[str, Any], agent_name: str):
        """显示单个智能体结果"""
        agents = session_data.get('agents', [])
        agent_data = next((a for a in agents if a.get('agent_name') == agent_name), None)
        
        if not agent_data:
            st.warning(f"暂无 {self.agent_mapping.get(agent_name, {}).get('name', agent_name)} 的数据")
            return
        
        # 智能体状态
        status = agent_data.get('status', 'unknown')
        status_emoji = "✅" if status == 'completed' else "🔄" if status == 'running' else "❓"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("执行状态", f"{status_emoji} {status}")
        
        with col2:
            start_time = agent_data.get('start_time', '')
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M:%S')
                except:
                    time_str = start_time[:8]
            else:
                time_str = "未知"
            st.metric(" 开始时间", time_str)
        
        with col3:
            end_time = agent_data.get('end_time', '')
            if end_time:
                try:
                    dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M:%S')
                except:
                    time_str = end_time[:8]
            else:
                time_str = "运行中..."
            st.metric(" 完成时间", time_str)
        
        # 显示结果
        result = agent_data.get('result', '')
        if result:
            st.markdown("### 📄 分析结果")
            
            # 转换Markdown为HTML显示
            try:
                html_result = markdown.markdown(result, extensions=['tables', 'fenced_code'])
                st.markdown(html_result, unsafe_allow_html=True)
            except Exception as e:
                # 如果Markdown转换失败，直接显示原文
                st.markdown(result)
        else:
            st.info(" 该智能体暂未生成结果")
        
        # 显示MCP工具调用
        mcp_calls = session_data.get('mcp_calls', [])
        agent_mcp_calls = [call for call in mcp_calls if call.get('agent_name') == agent_name]
        
        if agent_mcp_calls:
            with st.expander(f" MCP工具调用记录 ({len(agent_mcp_calls)}次)"):
                for i, call in enumerate(agent_mcp_calls, 1):
                    st.markdown(f"**调用 {i}**:")
                    st.text(f"工具: {call.get('tool_name', 'N/A')}")
                    st.text(f"时间: {call.get('timestamp', 'N/A')}")
                    
                    result = call.get('tool_result', '')
                    if result:
                        if len(result) > 200:
                            st.text_area(f"结果 {i}", result[:200] + "...", height=100, disabled=True)
                        else:
                            st.text_area(f"结果 {i}", result, height=60, disabled=True)
                    st.markdown("---")
    
    def _show_debate_history(self, session_data: Dict[str, Any], debate_type: str):
        """显示辩论历史"""
        if debate_type == 'investment':
            debate_data = session_data.get('investment_debate_history', [])
            title = "💭 投资观点辩论历史"
        else:
            debate_data = session_data.get('risk_debate_history', [])
            title = "⚠️ 风险评估辩论历史"
        
        if not debate_data:
            st.info(f"暂无{debate_type}辩论记录")
            return
        
        st.markdown(f"### {title}")
        
        for i, round_data in enumerate(debate_data, 1):
            st.markdown(f"#### 第 {i} 轮辩论")
            
            # 显示每轮辩论的参与者和观点
            for agent_name, content in round_data.items():
                if agent_name in self.agent_mapping:
                    agent_info = self.agent_mapping[agent_name]
                    st.markdown(f"**{agent_info['name']}:**")
                    st.markdown(content[:300] + "..." if len(content) > 300 else content)
                    st.markdown("---")
    
    def _show_session_overview(self, session_data: Dict[str, Any]):
        """显示会话概览"""
        # 执行统计
        agents = session_data.get('agents', [])
        mcp_calls = session_data.get('mcp_calls', [])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("智能体执行数", len(agents))
            completed_count = len([a for a in agents if a.get('status') == 'completed'])
            st.metric(" 已完成", completed_count)
        
        with col2:
            st.metric("MCP工具调用", len(mcp_calls))
            unique_tools = len(set(call.get('tool_name', '') for call in mcp_calls))
            st.metric("使用工具种类", unique_tools)
        
        with col3:
            # 计算总执行时间
            start_times = [a.get('start_time') for a in agents if a.get('start_time')]
            end_times = [a.get('end_time') for a in agents if a.get('end_time')]
            
            if start_times and end_times:
                try:
                    start_dt = min(datetime.fromisoformat(t.replace('Z', '+00:00')) for t in start_times)
                    end_dt = max(datetime.fromisoformat(t.replace('Z', '+00:00')) for t in end_times)
                    duration = (end_dt - start_dt).total_seconds()
                    st.metric("总执行时间", f"{duration:.1f}秒")
                except:
                    st.metric("总执行时间", "计算中...")
            else:
                st.metric("总执行时间", "未知")
        
        # 错误和警告
        errors = session_data.get('errors', [])
        warnings = session_data.get('warnings', [])
        
        if errors:
            st.error(f" 发现 {len(errors)} 个错误:")
            for error in errors:
                st.text(f"• {error}")
        
        if warnings:
            st.warning(f"发现 {len(warnings)} 个警告:")
            for warning in warnings:
                st.text(f"• {warning}")
    
    def _show_all_agents_summary(self, session_data: Dict[str, Any]):
        """显示所有智能体结果摘要"""
        agents = session_data.get('agents', [])
        
        if not agents:
            st.info(" 暂无智能体执行记录")
            return
        
        # 按阶段分组显示
        stage_groups = {
            "🏢 公司概述阶段": ['company_overview_analyst'],
            "📊 分析师团队": ['market_analyst', 'sentiment_analyst', 'news_analyst', 
                          'fundamentals_analyst', 'shareholder_analyst', 'product_analyst'],
            "💭 研究员辩论": ['bull_researcher', 'bear_researcher'],
            "👔 管理层决策": ['research_manager', 'trader'],
            "⚠️ 风险管理": ['aggressive_risk_analyst', 'safe_risk_analyst', 
                         'neutral_risk_analyst', 'risk_manager']
        }
        
        for stage_name, agent_names in stage_groups.items():
            st.markdown(f"### {stage_name}")
            
            stage_agents = [a for a in agents if a.get('agent_name') in agent_names]
            
            if not stage_agents:
                st.info(f"该阶段暂无执行记录")
                continue
            
            for agent_data in stage_agents:
                agent_name = agent_data.get('agent_name', '')
                agent_info = self.agent_mapping.get(agent_name, {'name': agent_name, 'emoji': '🤖'})
                
                status = agent_data.get('status', 'unknown')
                status_emoji = "✅" if status == 'completed' else "🔄" if status == 'running' else "❓"
                
                with st.expander(f"{status_emoji} {agent_info['name']}", expanded=False):
                    result = agent_data.get('result', '')
                    if result:
                        # 显示结果的前200字符
                        preview = result[:200] + "..." if len(result) > 200 else result
                        st.markdown(preview)
                        
                        if len(result) > 200:
                            if st.button(f"查看完整结果", key=f"view_{agent_name}"):
                                st.markdown("---")
                                st.markdown(result)
                    else:
                        st.info(" 暂未生成结果")
    
    def _show_export_options(self, session_file: Path):
        """显示导出选项"""
        st.markdown("### 📄 导出报告")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(" 导出Markdown", use_container_width=True):
                self._export_to_markdown(session_file)
        
        with col2:
            if st.button(" 导出PDF", use_container_width=True):
                self._export_to_pdf(session_file)
        
        with col3:
            if st.button(" 导出DOCX", use_container_width=True):
                self._export_to_docx(session_file)
    
    def _export_to_markdown(self, session_file: Path):
        """导出为Markdown"""
        try:
            from src.dumptools.json_to_markdown import JSONToMarkdownConverter
            
            converter = JSONToMarkdownConverter("src/dump")
            result = converter.convert_json_to_markdown(str(session_file))
            
            if result:
                st.success(f" Markdown报告已生成: {result}")
                
                # 提供下载链接
                if Path(result).exists():
                    with open(result, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    st.download_button(
                        label=" 下载Markdown文件",
                        data=content,
                        file_name=Path(result).name,
                        mime="text/markdown"
                    )
            else:
                st.error(" Markdown导出失败")
        except Exception as e:
            st.error(f" 导出失败: {e}")
    
    def _export_to_pdf(self, session_file: Path):
        """导出为PDF"""
        try:
            from src.dumptools.md2pdf import MarkdownToPDFConverter
            
            # 先转换为Markdown
            from src.dumptools.json_to_markdown import JSONToMarkdownConverter
            converter = JSONToMarkdownConverter("src/dump")
            md_file = converter.convert_json_to_markdown(str(session_file))
            
            if md_file:
                # 转换为PDF
                pdf_converter = MarkdownToPDFConverter()
                pdf_file = pdf_converter.convert_to_pdf(md_file)
                
                if pdf_file:
                    st.success(f" PDF报告已生成: {pdf_file}")
                else:
                    st.error(" PDF转换失败")
            else:
                st.error(" 无法生成Markdown文件，PDF转换失败")
        except Exception as e:
            st.error(f" PDF导出失败: {e}")
    
    def _export_to_docx(self, session_file: Path):
        """导出为DOCX"""
        try:
            from src.dumptools.md2docx import MarkdownToDocxConverter
            
            # 先转换为Markdown
            from src.dumptools.json_to_markdown import JSONToMarkdownConverter
            converter = JSONToMarkdownConverter("src/dump")
            md_file = converter.convert_json_to_markdown(str(session_file))
            
            if md_file:
                # 转换为DOCX
                docx_converter = MarkdownToDocxConverter()
                docx_file = docx_converter.convert_to_docx(md_file)
                
                if docx_file:
                    st.success(f" DOCX报告已生成: {docx_file}")
                else:
                    st.error(" DOCX转换失败")
            else:
                st.error(" 无法生成Markdown文件，DOCX转换失败")
        except Exception as e:
            st.error(f"DOCX导出失败: {e}")
