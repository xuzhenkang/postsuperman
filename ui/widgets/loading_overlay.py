#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont


class RespLoadingOverlay(QWidget):
    """响应加载覆盖层"""
    
    def __init__(self, parent=None, mainwin=None):
        super().__init__(parent)
        self.mainwin = mainwin
        self.setVisible(False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # 创建加载界面
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 加载文本
        self.loading_label = QLabel('Sending request...')
        self.loading_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                background: transparent;
                border: none;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_label)
        
        # 停止按钮
        self.stop_btn = QPushButton('Stop Request')
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        layout.addWidget(self.stop_btn)
        
        # 动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.dots_count = 0
        
    def show_loading(self, message="Sending request..."):
        """显示加载状态"""
        self.loading_label.setText(message)
        self.setVisible(True)
        self.animation_timer.start(500)  # 每500ms更新一次
        
    def hide_loading(self):
        """隐藏加载状态"""
        self.setVisible(False)
        self.animation_timer.stop()
        self.dots_count = 0
        
    def update_animation(self):
        """更新动画效果"""
        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        base_text = self.loading_label.text().rstrip('.')
        self.loading_label.setText(base_text + dots)
        
    def on_stop_clicked(self):
        """停止按钮点击事件"""
        try:
            print("LoadingOverlay: Stop按钮被点击")
            if self.mainwin and hasattr(self.mainwin, 'safe_stop_request'):
                print("LoadingOverlay: 调用safe_stop_request")
                self.mainwin.safe_stop_request()
            elif self.mainwin and hasattr(self.mainwin, 'on_stop_request'):
                print("LoadingOverlay: 调用on_stop_request")
                self.mainwin.on_stop_request()
            else:
                print("LoadingOverlay: 未找到停止方法")
            print("LoadingOverlay: Stop按钮处理完成")
        except Exception as e:
            print(f"LoadingOverlay: 停止按钮点击时出错: {e}")
            # 确保遮罩层被隐藏
            self.setVisible(False)
            
    def paintEvent(self, event):
        """绘制半透明背景"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150)) 