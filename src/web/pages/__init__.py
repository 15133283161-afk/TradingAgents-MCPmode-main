#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pages模块
包含Streamlit应用的各个页面
"""

from .real_time_analysis import show_real_time_analysis
from .history_sessions import show_history_sessions
from .debate_timeline import show_debate_timeline
from .analysis_results import show_analysis_results
from .system_overview import show_system_overview

__all__ = [
    'show_real_time_analysis',
    'show_history_sessions',
    'show_debate_timeline',
    'show_analysis_results',
    'show_system_overview',
]
