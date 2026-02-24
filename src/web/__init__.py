#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web前端模块
TradingAgents-MCPmode Streamlit前端组件
"""

__version__ = "1.0.0"
__author__ = "TradingAgents Team"
__description__ = "TradingAgents-MCPmode Web前端"

try:
    from .config_manager import ConfigManager
    from .analysis_monitor import AnalysisMonitor
    from .results_viewer import ResultsViewer
except ImportError as e:
    ConfigManager = None
    AnalysisMonitor = None
    ResultsViewer = None

from .app import main
from .session_manager import SessionManager
from .analysis_engine import AnalysisEngine
from .export_manager import ExportManager
from .sidebar import show_sidebar, get_agent_display_name, get_agent_type

__all__ = [
    'ConfigManager',
    'AnalysisMonitor',
    'ResultsViewer',
    'main',
    'SessionManager',
    'AnalysisEngine',
    'ExportManager',
    'show_sidebar',
    'get_agent_display_name',
    'get_agent_type',
]
