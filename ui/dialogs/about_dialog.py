#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QApplication
import sys
import os


class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About PostSuperman')
        self.setFixedSize(500, 400)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #f7f9fa;
                border-radius: 12px;
            }
        """)
        vbox = QVBoxLayout(self)
        vbox.setSpacing(12)
        # 艺术字应用名称（顶部）
        self.art_label = QLabel('postsuperman')
        self.art_label.setAlignment(Qt.AlignCenter)
        self.art_label.setStyleSheet('''
            QLabel {
                font-size: 28px;
                font-family: "Arial Black", "微软雅黑", Arial, sans-serif;
                font-weight: bold;
                letter-spacing: 1px;
                color: #1976d2;
            }
        ''')
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(1, 2)
        self.art_label.setGraphicsEffect(shadow)
        vbox.addWidget(self.art_label)
        # Logo/Icon
        icon_label = QLabel()
        # 兼容 PyInstaller 路径
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'app.ico')
        else:
            icon_path = os.path.join('ui', 'app.ico')
        icon_pix = QPixmap(icon_path)
        if not icon_pix.isNull():
            icon_label.setPixmap(icon_pix.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(icon_label)
        # 分割线
        line1 = QLabel()
        line1.setFixedHeight(2)
        line1.setStyleSheet('background: #e0e0e0; margin: 0 20px;')
        vbox.addWidget(line1)
        # 描述区（可滚动）
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setTextFormat(Qt.RichText)
        self.desc_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.desc_label.setStyleSheet("font-size: 13px; color: #2c3e50; line-height: 1.7;")
        scroll = QScrollArea()
        scroll.setWidget(self.desc_label)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(170)
        scroll.setFrameShape(QScrollArea.NoFrame)
        vbox.addWidget(scroll)
        # 再加一条分割线
        line2 = QLabel()
        line2.setFixedHeight(2)
        line2.setStyleSheet('background: #e0e0e0; margin: 0 20px;')
        vbox.addWidget(line2)
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.copy_btn = QPushButton('Copy Info')
        self.copy_btn.setObjectName('copyInfoBtn')
        self.copy_btn.setStyleSheet('''
            QPushButton#copyInfoBtn {
                min-width: 90px;
                padding: 6px 18px;
                border-radius: 6px;
                background: #1976d2;
                color: white;
                font-weight: bold;
            }
            QPushButton#copyInfoBtn:pressed {
                background: #115293;
            }
            QPushButton#copyInfoBtn:disabled {
                background: #b0bec5;
                color: #ececec;
            }
        ''')
        self.copy_btn.clicked.connect(self.copy_info)
        button_layout.addWidget(self.copy_btn)
        self.close_btn = QPushButton('Close')
        self.close_btn.setStyleSheet('''
            QPushButton {
                min-width: 90px;
                padding: 6px 18px;
                border-radius: 6px;
                background: #1976d2;
                color: white;
                font-weight: bold;
            }
            QPushButton:pressed {
                background: #115293;
            }
        ''')
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        button_layout.addStretch()
        vbox.addLayout(button_layout)
        self.refresh_texts()
        
    def copy_info(self):
        """复制信息到剪贴板"""
        print("copy_info called")
        try:
            info = (
                "PostSuperman v1.0.0\n"
                "A powerful API testing tool built with Python and PyQt5.\n\n"
                "Features:\n"
                "• Multi-tab request management\n"
                "• cURL import support\n"
                "• Collection organization\n"
                "• Response highlighting\n"
                "• Request history\n"
                "• Environment variables\n"
                "\nPowered by Python & PyQt5\n"
                "Developed by xuzhenkang@hotmail.com\n"
                "https://github.com/xuzhenkang/postsuperman\n"
                "Version: 1.0.0"
            )
            clipboard = QApplication.clipboard()
            clipboard.setText(info)
            self.copy_btn.setText('Copied!')
            self.copy_btn.setEnabled(False)
            self.copy_btn.setStyleSheet(self.copy_btn.styleSheet())
            from PyQt5.QtCore import QTimer
            if hasattr(self, '_copy_timer') and self._copy_timer is not None:
                self._copy_timer.stop()
                self._copy_timer.deleteLater()
            self._copy_timer = QTimer(self)
            self._copy_timer.setSingleShot(True)
            self._copy_timer.timeout.connect(self.restore_copy_btn)
            self._copy_timer.start(2000)
        except Exception as e:
            print("copy_info error:", e)

    def restore_copy_btn(self):
        """恢复复制按钮"""
        try:
            print("restore_copy_btn called")
            self.copy_btn.setText('Copy Info')
            self.copy_btn.setEnabled(True)
            self.copy_btn.setStyleSheet(self.copy_btn.styleSheet())
            if hasattr(self, '_copy_timer') and self._copy_timer is not None:
                self._copy_timer.deleteLater()
                self._copy_timer = None 
        except Exception as e:
            print("restore_copy_btn error:", e) 

    def refresh_texts(self):
        from ui.utils.i18n import get_text
        self.setWindowTitle(get_text('about_title'))
        self.art_label.setText(get_text('app_title'))
        # 英文/中文描述
        lang = getattr(self, '_lang', None)
        if not lang:
            from ui.utils.settings_manager import load_settings
            lang = load_settings().get('ui_language', 'zh')
        if lang == 'en':
            desc_html = (
                '<div style="text-align:center;">'
                '<span style="font-size:13px; color:#34495e;">A powerful API testing tool built with Python and PyQt5.</span><br><br>'
                '<b>Features:</b><br>'
                '<ul style="margin:0; padding-left:20px; text-align:left; display:inline-block;">'
                '<li>Multi-tab request management</li>'
                '<li>cURL import support</li>'
                '<li>Collection organization</li>'
                '<li>Response highlighting</li>'
                '<li>Request history</li>'
                '<li>Environment variables</li>'
                '</ul>'
                '<br>Powered by Python & PyQt5<br>'
                'Developed by xuzhenkang@hotmail.com<br>'
                '<a href="https://github.com/xuzhenkang/postsuperman">https://github.com/xuzhenkang/postsuperman</a><br>'
                'Version: 1.0.0'
                '</div>'
            )
            self.copy_btn.setText('Copy Info')
            self.close_btn.setText('Close')
        else:
            desc_html = (
                '<div style="text-align:center;">'
                '<span style="font-size:13px; color:#34495e;">一款基于 Python 和 PyQt5 的强大 API 测试工具。</span><br><br>'
                '<b>主要功能：</b><br>'
                '<ul style="margin:0; padding-left:20px; text-align:left; display:inline-block;">'
                '<li>多标签请求管理</li>'
                '<li>cURL 导入支持</li>'
                '<li>集合分组管理</li>'
                '<li>响应高亮显示</li>'
                '<li>请求历史记录</li>'
                '<li>环境变量支持</li>'
                '</ul>'
                '<br>Powered by Python & PyQt5<br>'
                '开发者: xuzhenkang@hotmail.com<br>'
                '<a href="https://github.com/xuzhenkang/postsuperman">https://github.com/xuzhenkang/postsuperman</a><br>'
                '版本: 1.0.0'
                '</div>'
            )
            self.copy_btn.setText('复制信息')
            self.close_btn.setText('关闭')
        self.desc_label.setText(desc_html) 