#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出管理器
处理报告导出功能
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class ExportManager:
    """导出管理器"""
    # 静态计数器，用于生成唯一 key
    _export_button_counter = 0
    @staticmethod
    def export_report_markdown(session_data: dict, output_path: str = None) -> Optional[str]:
        """导出报告为Markdown格式"""
        try:
            from src.dumptools.json_to_markdown import JSONToMarkdownConverter

            converter = JSONToMarkdownConverter()
            markdown_content = converter.convert(session_data)

            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path("exports")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"report_{timestamp}.md"

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return str(output_path)
        except Exception as e:
            st.error(f"❌ Markdown导出失败: {e}")
            return None

    @staticmethod
    def export_report_pdf(session_data: dict) -> Optional[str]:
        """导出报告为PDF格式"""
        try:
            from src.dumptools.json_to_markdown import JSONToMarkdownConverter
            from src.dumptools.md2pdf import MarkdownToPDFConverter

            markdown_path = ExportManager.export_report_markdown(session_data)

            if not markdown_path:
                return None

            converter = MarkdownToPDFConverter()
            pdf_path = converter.convert(markdown_path)

            return pdf_path
        except Exception as e:
            st.error(f"❌ PDF导出失败: {e}")
            return None

    @staticmethod
    def export_report_docx(session_data: dict) -> Optional[str]:
        """导出报告为Word格式"""
        try:
            from src.dumptools.json_to_markdown import JSONToMarkdownConverter
            from src.dumptools.md2docx import MarkdownToDocxConverter

            markdown_path = ExportManager.export_report_markdown(session_data)

            if not markdown_path:
                return None

            converter = MarkdownToDocxConverter()
            docx_path = converter.convert(markdown_path)

            return docx_path
        except Exception as e:
            st.error(f"❌ Word导出失败: {e}")
            return None

    @staticmethod
    def show_export_buttons(session_data: dict):
        """显示导出按钮"""
        st.markdown("---")
        st.markdown("### 📥 导出报告")

        # 使用 session_data 的 session_id 作为唯一标识
        session_id = session_data.get('session_id', datetime.now().strftime("%Y%m%d_%H%M%S"))
        page_suffix = st.session_state.get('active_page', 'main')  # 区分不同页面

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 导出 Markdown", use_container_width=True, key=f"export_md_{session_id}_{page_suffix}"):
                with st.spinner("正在生成Markdown文件..."):
                    path = ExportManager.export_report_markdown(session_data)
                    if path:
                        st.success(f"✅ Markdown文件已导出到: {path}")
                        with open(path, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label="💾 下载文件",
                                data=f.read(),
                                file_name=Path(path).name,
                                mime="text/markdown",
                                key=f"download_md_{session_id}_{page_suffix}"
                            )

        with col2:
            if st.button("📋 导出 PDF", use_container_width=True, key=f"export_pdf_{session_id}_{page_suffix}"):
                with st.spinner("正在生成PDF文件..."):
                    path = ExportManager.export_report_pdf(session_data)
                    if path:
                        st.success(f"✅ PDF文件已导出到: {path}")
                        with open(path, 'rb') as f:
                            st.download_button(
                                label="💾 下载文件",
                                data=f.read(),
                                file_name=Path(path).name,
                                mime="application/pdf",
                                key=f"download_pdf_{session_id}_{page_suffix}"
                            )

        with col3:
            if st.button("📝 导出 Word", use_container_width=True, key=f"export_docx_{session_id}_{page_suffix}"):
                with st.spinner("正在生成Word文件..."):
                    path = ExportManager.export_report_docx(session_data)
                    if path:
                        st.success(f"✅ Word文件已导出到: {path}")
                        with open(path, 'rb') as f:
                            st.download_button(
                                label="💾 下载文件",
                                data=f.read(),
                                file_name=Path(path).name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"download_docx_{session_id}_{page_suffix}"
                            )
