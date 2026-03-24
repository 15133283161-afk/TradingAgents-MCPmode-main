#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
用于管理.env和mcp_config.json的配置
"""

import streamlit as st
import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv, set_key


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.env_file = Path(".env")
        self.mcp_config_file = Path("mcp_config.json")
        load_dotenv()
    
    def show_config_interface(self):
        """显示配置界面"""
        st.title("⚙️ 系统配置")
        
        # 主要配置标签页
        tab1, tab2, tab3 = st.tabs(["🤖 大模型配置", "🔧 智能体权限", "🌐 MCP服务器"])
        
        with tab1:
            self._show_llm_config()
        
        with tab2:
            self._show_agent_permissions()
        
        with tab3:
            self._show_mcp_config()
    
    def _show_llm_config(self):
        """显示大模型配置"""
        st.markdown("###  大模型API配置")
        
        # 加载当前配置
        current_config = self._load_env_config()
        
        with st.form("llm_config_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                api_key = st.text_input(
                    "API密钥",
                    value=current_config.get("LLM_API_KEY", ""),
                    type="password",
                    help="大模型API密钥"
                )
                
                base_url = st.text_input(
                    "API基础URL",
                    value=current_config.get("LLM_BASE_URL", ""),
                    help="API服务的基础URL"
                )
                
                model = st.text_input(
                    "模型名称",
                    value=current_config.get("LLM_MODEL", ""),
                    help="要使用的模型名称"
                )
            
            with col2:
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=float(current_config.get("LLM_TEMPERATURE", "0.1")),
                    step=0.1,
                    help="控制生成文本的随机性"
                )
                
                max_tokens = st.number_input(
                    "最大Token数",
                    min_value=100,
                    max_value=10000,
                    value=int(current_config.get("LLM_MAX_TOKENS", "3000")),
                    step=100,
                    help="单次请求的最大token数量"
                )
                
                # 工作流配置
                st.markdown("#### 🔄 工作流配置")
                
                max_debate_rounds = st.number_input(
                    "最大投资辩论轮次",
                    min_value=1,
                    max_value=10,
                    value=int(current_config.get("MAX_DEBATE_ROUNDS", "3")),
                    help="看涨看跌研究员的最大辩论轮次"
                )
                
                max_risk_debate_rounds = st.number_input(
                    "最大风险辩论轮次", 
                    min_value=1,
                    max_value=10,
                    value=int(current_config.get("MAX_RISK_DEBATE_ROUNDS", "2")),
                    help="风险分析师的最大辩论轮次"
                )
            
            # 调试配置
            st.markdown("#### 🐛 调试配置")
            col3, col4 = st.columns(2)
            
            with col3:
                debug_mode = st.checkbox(
                    "调试模式",
                    value=current_config.get("DEBUG_MODE", "true").lower() == "true",
                    help="启用详细的调试日志"
                )
            
            with col4:
                verbose_logging = st.checkbox(
                    "详细日志",
                    value=current_config.get("VERBOSE_LOGGING", "true").lower() == "true",
                    help="启用详细的执行日志"
                )
            
            # 提交按钮
            submitted = st.form_submit_button("💾 保存大模型配置", use_container_width=True)
            
            if submitted:
                # 保存配置
                config_updates = {
                    "LLM_API_KEY": api_key,
                    "LLM_BASE_URL": base_url,
                    "LLM_MODEL": model,
                    "LLM_TEMPERATURE": str(temperature),
                    "LLM_MAX_TOKENS": str(max_tokens),
                    "MAX_DEBATE_ROUNDS": str(max_debate_rounds),
                    "MAX_RISK_DEBATE_ROUNDS": str(max_risk_debate_rounds),
                    "DEBUG_MODE": "true" if debug_mode else "false",
                    "VERBOSE_LOGGING": "true" if verbose_logging else "false"
                }
                
                if self._save_env_config(config_updates):
                    st.success("✅ 大模型配置已保存！需要重启系统生效。")
                    st.rerun()
                else:
                    st.error("❌ 配置保存失败！")
    
    def _show_agent_permissions(self):
        """显示智能体权限配置"""
        st.markdown("### 🔧 智能体MCP权限配置")
        
        # 加载当前配置
        current_config = self._load_env_config()
        
        # 智能体分组
        agent_groups = {
            "📊 分析师团队": [
                ("COMPANY_OVERVIEW_ANALYST_MCP_ENABLED", "🏢 公司概述分析师"),
                ("MARKET_ANALYST_MCP_ENABLED", "📈 市场分析师"),
                ("SENTIMENT_ANALYST_MCP_ENABLED", "😊 情绪分析师"),
                ("NEWS_ANALYST_MCP_ENABLED", "📰 新闻分析师"),
                ("FUNDAMENTALS_ANALYST_MCP_ENABLED", "📋 基本面分析师"),
                ("SHAREHOLDER_ANALYST_MCP_ENABLED", "👥 股东分析师"),
                ("PRODUCT_ANALYST_MCP_ENABLED", "🏭 产品分析师")
            ],
            "🔬 研究员团队": [
                ("BULL_RESEARCHER_MCP_ENABLED", "📈 看涨研究员"),
                ("BEAR_RESEARCHER_MCP_ENABLED", "📉 看跌研究员")
            ],
            "👔 管理层": [
                ("RESEARCH_MANAGER_MCP_ENABLED", "🎯 研究经理"),
                ("TRADER_MCP_ENABLED", "💰 交易员")
            ],
            "⚠️ 风险管理团队": [
                ("AGGRESSIVE_RISK_ANALYST_MCP_ENABLED", "⚡ 激进风险分析师"),
                ("SAFE_RISK_ANALYST_MCP_ENABLED", "🛡️ 保守风险分析师"),
                ("NEUTRAL_RISK_ANALYST_MCP_ENABLED", "⚖️ 中性风险分析师"),
                ("RISK_MANAGER_MCP_ENABLED", "🎯 风险经理")
            ]
        }
        
        with st.form("agent_permissions_form"):
            permission_updates = {}
            
            # 全局控制
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔓 全部启用", use_container_width=True):
                    for group_agents in agent_groups.values():
                        for agent_key, _ in group_agents:
                            permission_updates[agent_key] = "true"
            
            with col2:
                if st.button("🔒 全部禁用", use_container_width=True):
                    for group_agents in agent_groups.values():
                        for agent_key, _ in group_agents:
                            permission_updates[agent_key] = "false"
            
            st.markdown("---")
            
            # 分组显示权限配置
            for group_name, group_agents in agent_groups.items():
                st.markdown(f"#### {group_name}")
                
                # 计算该组启用的智能体数量
                enabled_count = sum(1 for agent_key, _ in group_agents 
                                  if current_config.get(agent_key, "false").lower() == "true")
                
                st.caption(f"已启用: {enabled_count}/{len(group_agents)}")
                
                cols = st.columns(2)
                for i, (agent_key, agent_name) in enumerate(group_agents):
                    with cols[i % 2]:
                        current_value = current_config.get(agent_key, "false").lower() == "true"
                        new_value = st.checkbox(
                            agent_name,
                            value=current_value,
                            key=agent_key
                        )
                        permission_updates[agent_key] = "true" if new_value else "false"
                
                st.markdown("")
            
            # 提交按钮
            submitted = st.form_submit_button("💾 保存权限配置", use_container_width=True)
            
            if submitted:
                if self._save_env_config(permission_updates):
                    st.success("✅ 智能体权限配置已保存！")
                    st.rerun()
                else:
                    st.error("❌ 配置保存失败！")
    
    def _show_mcp_config(self):
        """显示MCP服务器配置"""
        st.markdown("### 🌐 MCP服务器配置")
        
        # 加载当前MCP配置
        mcp_config = self._load_mcp_config()
        
        if not mcp_config:
            st.warning("⚠️ 未找到MCP配置文件，将创建默认配置")
            mcp_config = {"servers": {}}
        
        with st.form("mcp_config_form"):
            st.markdown("#### 🖥️ 服务器列表")
            
            servers = mcp_config.get("servers", {})
            updated_servers = {}
            
            if servers:
                for server_name, server_config in servers.items():
                    st.markdown(f"##### 📡 {server_name}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        url = st.text_input(
                            "服务器URL",
                            value=server_config.get("url", ""),
                            key=f"{server_name}_url"
                        )
                    
                    with col2:
                        transport = st.selectbox(
                            "传输协议",
                            ["sse", "stdio", "http"],
                            index=["sse", "stdio", "http"].index(server_config.get("transport", "sse")),
                            key=f"{server_name}_transport"
                        )
                    
                    with col3:
                        timeout = st.number_input(
                            "超时时间(秒)",
                            min_value=10,
                            max_value=3600,
                            value=server_config.get("timeout", 600),
                            key=f"{server_name}_timeout"
                        )
                    
                    updated_servers[server_name] = {
                        "url": url,
                        "transport": transport,
                        "timeout": timeout
                    }
                    
                    st.markdown("---")
            else:
                st.info("📝 当前没有配置MCP服务器")
            
            # 新增服务器
            st.markdown("#### ➕ 添加新服务器")
            
            col1, col2 = st.columns(2)
            with col1:
                new_server_name = st.text_input("服务器名称", placeholder="例如: finance-data-server")
            with col2:
                new_server_url = st.text_input("服务器URL", placeholder="例如: http://localhost:3000/sse")
            
            col3, col4 = st.columns(2)
            with col3:
                new_transport = st.selectbox("传输协议", ["sse", "stdio", "http"], key="new_transport")
            with col4:
                new_timeout = st.number_input("超时时间(秒)", min_value=10, max_value=3600, value=600, key="new_timeout")
            
            if new_server_name and new_server_url:
                updated_servers[new_server_name] = {
                    "url": new_server_url,
                    "transport": new_transport,
                    "timeout": new_timeout
                }
            
            # 提交按钮
            submitted = st.form_submit_button("💾 保存MCP配置", use_container_width=True)
            
            if submitted:
                new_config = {"servers": updated_servers}
                if self._save_mcp_config(new_config):
                    st.success("✅ MCP服务器配置已保存！")
                    st.rerun()
                else:
                    st.error("❌ 配置保存失败！")
    
    def _load_env_config(self) -> Dict[str, str]:
        """加载.env配置"""
        config = {}
        if self.env_file.exists():
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        return config
    
    def _save_env_config(self, updates: Dict[str, str]) -> bool:
        """保存.env配置"""
        try:
            for key, value in updates.items():
                set_key(str(self.env_file), key, value)
            return True
        except Exception as e:
            st.error(f"保存配置时出错: {e}")
            return False
    
    def _load_mcp_config(self) -> Dict[str, Any]:
        """加载MCP配置"""
        try:
            if self.mcp_config_file.exists():
                with open(self.mcp_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            st.error(f"加载MCP配置时出错: {e}")
            return {}
    
    def _save_mcp_config(self, config: Dict[str, Any]) -> bool:
        """保存MCP配置"""
        try:
            with open(self.mcp_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"保存MCP配置时出错: {e}")
            return False
