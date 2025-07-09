#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QColor, QTextFormat, QTextCharFormat, QFont, QPainter, QTextCursor
import json
from ui.utils.settings_manager import load_settings


class LineNumberArea(QWidget):
    """行号区域控件"""
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    """代码编辑器控件，支持行号显示和JSON格式化"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.cursorPositionChanged.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0)
        self.parent_mainwindow = None  # 用于判断是否为json模式
        self.setTabChangesFocus(False)

    def set_mainwindow(self, mw):
        self.parent_mainwindow = mw

    def get_tab_size(self):
        try:
            return int(load_settings().get('editor_tab_size', 4))
        except Exception:
            return 4

    def keyPressEvent(self, event):
        tab_size = self.get_tab_size()
        if self.parent_mainwindow and hasattr(self.parent_mainwindow, 'raw_type_combo'):
            if self.parent_mainwindow.raw_type_combo.currentText() == 'JSON':
                # Ctrl+B 一键美化
                if event.key() == Qt.Key_B and event.modifiers() & Qt.ControlModifier:
                    try:
                        obj = json.loads(self.toPlainText())
                        pretty = json.dumps(obj, ensure_ascii=False, indent=tab_size)
                        self.setPlainText(pretty)
                    except Exception:
                        pass
                    return
                # Tab/Shift+Tab 多行缩进/反缩进
                if event.key() == Qt.Key_Tab:
                    cursor = self.textCursor()
                    if cursor.hasSelection():
                        start = cursor.selectionStart()
                        end = cursor.selectionEnd()
                        doc = self.document()
                        start_block = doc.findBlock(start)
                        end_block = doc.findBlock(end)
                        # 收集所有受影响的block
                        blocks = []
                        block = start_block
                        while True:
                            blocks.append(block)
                            if block == end_block:
                                break
                            block = block.next()
                        # 逐行插入缩进
                        for block in blocks:
                            block_cursor = QTextCursor(block)
                            block_cursor.movePosition(QTextCursor.StartOfBlock)
                            block_cursor.insertText(' ' * tab_size)
                        return
                    else:
                        cursor.insertText(' ' * tab_size)
                        return
                if event.key() == Qt.Key_Backtab:
                    cursor = self.textCursor()
                    if cursor.hasSelection():
                        start = cursor.selectionStart()
                        end = cursor.selectionEnd()
                        doc = self.document()
                        start_block = doc.findBlock(start)
                        end_block = doc.findBlock(end)
                        blocks = []
                        block = start_block
                        while True:
                            blocks.append(block)
                            if block == end_block:
                                break
                            block = block.next()
                        for block in blocks:
                            block_cursor = QTextCursor(block)
                            block_cursor.movePosition(QTextCursor.StartOfBlock)
                            line = block.text()
                            if line.startswith(' ' * tab_size):
                                block_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, tab_size)
                                block_cursor.removeSelectedText()
                            elif line.startswith('\t'):
                                block_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 1)
                                block_cursor.removeSelectedText()
                        return
                # 回车自动缩进
                if event.key() == Qt.Key_Return:
                    cursor = self.textCursor()
                    cursor.insertText('\n')
                    block = cursor.block().previous()
                    text = block.text()
                    indent = ''
                    for c in text:
                        if c == ' ':
                            indent += ' '
                        elif c == '\t':
                            indent += '\t'
                        else:
                            break
                    if text.rstrip().endswith(('{', '[', '(', ':')):
                        indent += ' ' * tab_size
                    cursor.insertText(indent)
                    self.setTextCursor(cursor)
                    return
                # 括号自动补全
                pairs = {'{': '}', '[': ']', '(': ')', '"': '"'}
                text = event.text()
                if text in pairs:
                    cursor = self.textCursor()
                    cursor.insertText(text)
                    cursor.insertText(pairs[text])
                    # 将光标移回中间
                    cursor.movePosition(QTextCursor.Left)
                    self.setTextCursor(cursor)
                    return
        super().keyPressEvent(event)

    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def updateLineNumberArea(self):
        self.lineNumberArea.update(0, 0, self.lineNumberArea.width(), self.lineNumberArea.height())

    def updateLineNumberAreaEvent(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor('#f0f0f0'))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor('#666666'))
                painter.drawText(0, int(top), self.lineNumberArea.width() - 5, self.fontMetrics().height(),
                               Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1 