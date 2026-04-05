#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史会话页面
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json


def clean_empty_session_files():
    """清理空的会话文件（没有agents数据的文件）"""
    try:
        dump_dir = Path("src/dump")
        if not dump_dir.exists():
            return 0
        deleted_count = 0
        for json_file in dump_dir.glob("session_*.json"):
            try:
                # 跳过太大的文件（大于1KB的肯定不是空文件）
                if json_file.stat().st_size > 1024:
                    continue
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 检查是否是空文件（agents为空或agent_execution_history为空）
                agents = data.get('agents', [])
                agent_history = data.get('agent_execution_history', [])
                if not agents and not agent_history:
                    json_file.unlink()
                    deleted_count += 1
            except Exception:
                continue
        return deleted_count
    except Exception:
        return 0


def get_session_files_list():
    """获取会话文件列表"""
    try:
        dump_dir = Path("src/dump")
        if not dump_dir.exists():
            return []
        # 首先清理空文件
        clean_empty_session_files()
        return sorted(dump_dir.glob("session_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    except:
        return []

def load_session_data(file_path: Path):
    """加载会话数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ 加载会话数据失败: {e}")
        return None


def show_history_sessions():
    """历史会话页面"""
    st.markdown('<h2 class="main-title">📚 历史会话</h2>', unsafe_allow_html=True)
    json_files = get_session_files_list()
    if not json_files:
        st.markdown("""
        <div class="info-card" style="text-align:center;padding:3rem;">
            <span style="font-size:4rem;">📭</span>
            <h3 style="color:#ccd6f6;margin:1rem 0;">暂无历史分析数据</h3>
            <p style="color:#8892b0;">开始您的第一次分析吧！</p>
        </div>
        """, unsafe_allow_html=True)
        return
    completed_sessions = []
    for json_file in json_files:
        try:
            data = load_session_data(json_file)
            if data and (data.get('status') or '').lower() == 'completed':
                file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
                completed_sessions.append({
                    'file': json_file,
                    'data': data,
                    'time': file_time,
                    'query': data.get('user_query', '无查询')
                })
        except:
            continue
    if not completed_sessions:
        st.markdown("""
        <div class="info-card" style="text-align:center;padding:3rem;">
            <span style="font-size:4rem;">📝</span>
            <h3 style="color:#ccd6f6;margin:1rem 0;">暂无已完成的历史会话</h3>
        </div>
        """, unsafe_allow_html=True)
        return
    for session in completed_sessions:
        query_preview = session['query'][:60] + "..." if len(session['query']) > 60 else session['query']
        time_str = session['time'].strftime('%Y-%m-%d %H:%M')
        # 使用容器包裹，避免重复渲染
        with st.container():
            st.markdown(f"""
            <div class="report-card">
                <div style="display:flex;align-items:center;gap:1rem;">
                    <span style="font-size:2rem;">💬</span>
                    <div style="flex:1;">
                        <div style="font-weight:600;color:#ccd6f6;margin-bottom:0.25rem;">
                            {query_preview}
                        </div>
                        <div style="font-size:0.85rem;color:#8892b0;">
                            🕒 {time_str}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📄 加载会话", key=f"load_{session['file'].name}", use_container_width=True):
                st.session_state.selected_session_file = str(session['file'])
                st.session_state.current_session_data = session['data']
                st.session_state.analysis_completed = True
                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []
                st.session_state.chat_history.append({
                    'query': session['data'].get('user_query', ''),
                    'timestamp': datetime.now().isoformat(),
                    'result': session['data']
                })
                st.success("✅ 会话加载成功！")
                st.rerun()
