#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能交易分析系统
整合所有功能：实时分析、历史会话、辩论展示、报告导出
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    if os.environ.get("STREAMLIT_LAUNCHED") == "1":
        from src.web import main
        main()
    else:
        import subprocess
        env = os.environ.copy()
        env["STREAMLIT_LAUNCHED"] = "1"
        script_path = os.path.abspath(__file__)
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", script_path],
            env=env,
            check=True
        )
