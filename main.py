#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能交易分析系统 - 完整整合版
整合所有功能：实时分析、历史会话、辩论展示、报告导出
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web import main

if __name__ == "__main__":
    main()
