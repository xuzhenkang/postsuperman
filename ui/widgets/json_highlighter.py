#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re


class JsonHighlighter(QSyntaxHighlighter):
    """JSON语法高亮器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyFormat = QTextCharFormat()
        self.keyFormat.setForeground(QColor('#1976d2'))
        self.keyFormat.setFontWeight(QFont.Bold)
        
        self.strFormat = QTextCharFormat()
        self.strFormat.setForeground(QColor('#43a047'))
        
        self.numFormat = QTextCharFormat()
        self.numFormat.setForeground(QColor('#e65100'))
        
        self.boolFormat = QTextCharFormat()
        self.boolFormat.setForeground(QColor('#d84315'))
        
        self.nullFormat = QTextCharFormat()
        self.nullFormat.setForeground(QColor('#757575'))

    def highlightBlock(self, text):
        # key: "key"
        for m in re.finditer(r'"(.*?)"(?=\s*:)', text):
            self.setFormat(m.start(), m.end()-m.start(), self.keyFormat)
        
        # string value: : "value"
        for m in re.finditer(r':\s*"(.*?)"', text):
            self.setFormat(m.start(0)+1, len(m.group(0))-1, self.strFormat)
        
        # number value
        for m in re.finditer(r':\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)', text):
            self.setFormat(m.start(1), len(m.group(1)), self.numFormat)
        
        # bool value
        for m in re.finditer(r':\s*(true|false)', text):
            self.setFormat(m.start(1), len(m.group(1)), self.boolFormat)
        
        # null value
        for m in re.finditer(r':\s*(null)', text):
            self.setFormat(m.start(1), len(m.group(1)), self.nullFormat) 