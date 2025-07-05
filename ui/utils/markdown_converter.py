#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re


class MarkdownConverter:
    """Markdown转HTML转换器"""
    
    @staticmethod
    def convert_markdown_to_html(markdown_text):
        """将Markdown文本转换为HTML"""
        html = markdown_text
        
        # 处理标题
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 处理粗体和斜体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # 处理代码块
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # 处理列表
        html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 处理表格
        html = MarkdownConverter._process_tables(html)
        
        # 处理ASCII表格
        html = MarkdownConverter._process_ascii_tables(html)
        
        # 处理换行
        html = html.replace('\n', '<br>')
        
        return html
    
    @staticmethod
    def _process_tables(html):
        """处理Markdown表格"""
        def process_table(match):
            lines = match.group(1).strip().split('\n')
            if len(lines) < 2:
                return match.group(0)
            
            # 解析表头
            header_line = lines[0]
            headers = [h.strip() for h in header_line.split('|')[1:-1]]
            
            # 跳过分隔行
            data_lines = lines[2:]
            
            # 构建HTML表格
            table_html = '<table border="1" style="border-collapse: collapse; width: 100%;">'
            
            # 表头
            table_html += '<thead><tr>'
            for header in headers:
                table_html += f'<th style="padding: 8px; text-align: left;">{header}</th>'
            table_html += '</tr></thead>'
            
            # 表体
            table_html += '<tbody>'
            for line in data_lines:
                if line.strip():
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    table_html += '<tr>'
                    for cell in cells:
                        table_html += f'<td style="padding: 8px;">{cell}</td>'
                    table_html += '</tr>'
            table_html += '</tbody></table>'
            
            return table_html
        
        return re.sub(r'\|(.*?)\|', process_table, html, flags=re.DOTALL)
    
    @staticmethod
    def _process_ascii_tables(html):
        """处理ASCII表格"""
        def process_ascii_table(match):
            table_text = match.group(1)
            lines = table_text.strip().split('\n')
            
            if len(lines) < 3:
                return match.group(0)
            
            # 解析表格结构
            table_html = '<table border="1" style="border-collapse: collapse; width: 100%;">'
            
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('+'):
                    # 解析行数据
                    cells = []
                    parts = line.split('|')
                    for part in parts[1:-1]:
                        cells.append(part.strip())
                    
                    if cells:
                        if i == 1:  # 第一行数据作为表头
                            table_html += '<thead><tr>'
                            for cell in cells:
                                table_html += f'<th style="padding: 8px; text-align: left;">{cell}</th>'
                            table_html += '</tr></thead><tbody>'
                        else:
                            table_html += '<tr>'
                            for cell in cells:
                                table_html += f'<td style="padding: 8px;">{cell}</td>'
                            table_html += '</tr>'
            
            table_html += '</tbody></table>'
            return table_html
        
        return re.sub(r'\+.*?\+(.*?)\+.*?\+', process_ascii_table, html, flags=re.DOTALL) 