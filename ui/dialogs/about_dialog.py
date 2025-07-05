#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About PostSuperman')
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel('PostSuperman')
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 版本信息
        version_label = QLabel('Version 1.0.0')
        version_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
            }
        """)
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # 描述
        desc_label = QLabel(
            'A powerful API testing tool built with Python and PyQt5.\n\n'
            'Features:\n'
            '• Multi-tab request management\n'
            '• cURL import support\n'
            '• Collection organization\n'
            '• Response highlighting\n'
            '• Request history\n'
            '• Environment variables'
        )
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #2c3e50;
                line-height: 1.5;
            }
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 复制按钮
        copy_btn = QPushButton('Copy Info')
        copy_btn.clicked.connect(self.copy_info)
        button_layout.addWidget(copy_btn)
        
        # 关闭按钮
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def copy_info(self):
        """复制信息到剪贴板"""
        info = """PostSuperman v1.0.0
A powerful API testing tool built with Python and PyQt5.

Features:
• Multi-tab request management
• cURL import support
• Collection organization
• Response highlighting
• Request history
• Environment variables"""
        
        clipboard = self.parent().window().clipboard()
        clipboard.setText(info)
        
        # 临时改变按钮文本
        sender = self.sender()
        original_text = sender.text()
        sender.setText('Copied!')
        sender.setEnabled(False)
        
        # 2秒后恢复
        from PyQt5.QtCore import QTimer
        timer = QTimer()
        timer.singleShot(2000, lambda: self.restore_button(sender, original_text))
        
    def restore_button(self, button, text):
        """恢复按钮状态"""
        button.setText(text)
        button.setEnabled(True) 