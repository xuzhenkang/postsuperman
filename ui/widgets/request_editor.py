#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QLineEdit, QTableWidget, QTableWidgetItem,
                             QRadioButton, QButtonGroup, QPushButton, QTextEdit,
                             QGroupBox, QCheckBox, QHeaderView, QMessageBox,
                             QFileDialog, QDialog, QTextEdit as QTextEditWidget,
                             QTabWidget, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from .code_editor import CodeEditor
from .json_highlighter import JsonHighlighter
import json
import os


class RequestEditor(QWidget):
    """请求编辑器控件"""
    
    def __init__(self, parent=None, req_name=None):
        super().__init__(parent)
        self.parent_mainwindow = parent
        self.req_name = req_name
        self.is_dirty = False
        self._dirty = False
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 请求行
        req_line = QFrame()
        req_line.setObjectName('RequestLine')
        req_line_layout = QHBoxLayout(req_line)
        req_line_layout.setContentsMargins(16, 16, 16, 0)
        req_line_layout.setSpacing(8)
        
        self.method_combo = QComboBox()
        self.method_combo.setObjectName('MethodCombo')
        self.method_combo.addItems(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        
        self.url_edit = QLineEdit()
        self.url_edit.setObjectName('UrlEdit')
        self.url_edit.setPlaceholderText('Enter request URL...')
        
        self.send_btn = QPushButton('Send')
        self.send_btn.setFixedWidth(80)
        self.send_btn.setStyleSheet('''QPushButton {background-color: #1976d2; color: white; font-weight: bold; border-radius: 6px; padding: 8px 0; font-size: 16px;} QPushButton:pressed {background-color: #115293;}''')
        
        req_line_layout.addWidget(self.method_combo)
        req_line_layout.addWidget(self.url_edit)
        req_line_layout.addWidget(self.send_btn)
        
        layout.addWidget(req_line)
        
        # Code/Import/Save按钮
        code_import_row = QHBoxLayout()
        code_import_row.setContentsMargins(16, 0, 16, 0)
        code_import_row.setSpacing(8)
        code_import_row.addStretch()
        
        self.code_btn = QPushButton('Code')
        self.import_btn = QPushButton('Import')
        self.save_btn = QPushButton('Export Current Request')
        self.save_to_tree_btn = QPushButton('Save')
        
        code_import_row.addWidget(self.code_btn)
        code_import_row.addWidget(self.import_btn)
        code_import_row.addWidget(self.save_btn)
        code_import_row.addWidget(self.save_to_tree_btn)
        
        layout.addLayout(code_import_row)
        
        # Params表格
        self.params_table = QTableWidget()
        self.init_table(self.params_table)
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 0, 0, 0)
        params_layout.setSpacing(0)
        params_layout.addWidget(self.params_table)
        
        # Headers表格
        self.headers_table = QTableWidget()
        self.init_table(self.headers_table)
        headers_widget = QWidget()
        headers_layout = QVBoxLayout(headers_widget)
        headers_layout.setContentsMargins(0, 0, 0, 0)
        headers_layout.setSpacing(0)
        headers_layout.addWidget(self.headers_table)
        
        # form-data表格
        self.form_table = QTableWidget()
        self.init_table(self.form_table)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)
        form_layout.addWidget(self.form_table)
        
        # x-www-form-urlencoded表格
        self.url_table = QTableWidget()
        self.init_table(self.url_table)
        url_widget = QWidget()
        url_layout = QVBoxLayout(url_widget)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(0)
        url_layout.addWidget(self.url_table)
        
        # Body Tab内容
        body_tab = QWidget()
        body_tab_layout = QVBoxLayout(body_tab)
        body_tab_layout.setContentsMargins(0, 0, 0, 0)
        body_tab_layout.setSpacing(8)
        
        self.body_type_group = QButtonGroup(body_tab)
        body_type_row = QHBoxLayout()
        
        self.body_none_radio = QRadioButton('none')
        self.body_form_radio = QRadioButton('form-data')
        self.body_url_radio = QRadioButton('x-www-form-urlencoded')
        self.body_raw_radio = QRadioButton('raw')
        
        self.body_type_group.addButton(self.body_none_radio)
        self.body_type_group.addButton(self.body_form_radio)
        self.body_type_group.addButton(self.body_url_radio)
        self.body_type_group.addButton(self.body_raw_radio)
        
        body_type_row.addWidget(self.body_none_radio)
        body_type_row.addWidget(self.body_form_radio)
        body_type_row.addWidget(self.body_url_radio)
        body_type_row.addWidget(self.body_raw_radio)
        body_type_row.addStretch()
        
        body_tab_layout.addLayout(body_type_row)
        
        self.body_stack = QStackedWidget()
        self.body_none_label = QLabel('This request does not have a body')
        self.body_none_label.setAlignment(Qt.AlignCenter)
        self.body_stack.addWidget(self.body_none_label)
        self.body_stack.addWidget(form_widget)
        self.body_stack.addWidget(url_widget)
        
        # raw内容
        raw_widget = QWidget()
        raw_main_layout = QVBoxLayout(raw_widget)
        raw_main_layout.setContentsMargins(0, 0, 0, 0)
        raw_main_layout.setSpacing(4)
        
        raw_top_layout = QHBoxLayout()
        raw_top_layout.setContentsMargins(0, 0, 0, 0)
        raw_top_layout.setSpacing(8)
        
        self.raw_type_combo = QComboBox()
        self.raw_type_combo.addItems(['JSON', 'TEXT'])
        raw_top_layout.addWidget(self.raw_type_combo)
        
        self.beautify_btn = QPushButton('Beautify')
        self.beautify_btn.setToolTip('格式化/美化 JSON (快捷键 Ctrl+B)')
        raw_top_layout.addWidget(self.beautify_btn)
        raw_top_layout.addStretch()
        
        raw_main_layout.addLayout(raw_top_layout)
        
        self.raw_text_edit = CodeEditor()
        self.raw_text_edit.set_mainwindow(self)
        raw_main_layout.addWidget(self.raw_text_edit)
        
        raw_widget.setLayout(raw_main_layout)
        self.body_stack.addWidget(raw_widget)
        
        self.json_highlighter = JsonHighlighter(self.raw_text_edit.document())
        
        # 连接Body类型切换信号
        self.raw_type_combo.currentTextChanged.connect(self.on_raw_type_changed)
        self.body_none_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(0))
        self.body_form_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(1))
        self.body_url_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(2))
        self.body_raw_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(3))
        self.beautify_btn.clicked.connect(self.beautify_json)
        
        body_tab_layout.addWidget(self.body_stack)
        
        # 创建TabWidget
        self.req_tab = QTabWidget()
        self.req_tab.setObjectName('ReqTab')
        self.req_tab.addTab(params_widget, 'Params')
        self.req_tab.addTab(headers_widget, 'Headers')
        self.req_tab.addTab(body_tab, 'Body')
        
        layout.addWidget(self.req_tab)
        
        # 设置默认URL
        if self.req_name:
            self.url_edit.setText(f'https://api.example.com/{self.req_name}')
        
        # 连接按钮信号
        self.send_btn.clicked.connect(self.on_send_clicked)
        self.save_btn.clicked.connect(self.on_save_clicked)
        self.import_btn.clicked.connect(self.on_import_clicked)
        self.code_btn.clicked.connect(self.on_code_clicked)
        self.save_to_tree_btn.clicked.connect(self.save_to_tree)
        
        # 添加响应内容属性
        self.resp_status = ''
        self.resp_body = ''
        self.resp_headers = ''
        
        # 连接编辑信号
        for widget in [self.method_combo, self.url_edit, self.params_table, self.headers_table, self.form_table, self.url_table, self.raw_text_edit]:
            if hasattr(widget, 'textChanged'):
                widget.textChanged.connect(self.mark_dirty)
            elif hasattr(widget, 'currentTextChanged'):
                widget.currentTextChanged.connect(self.mark_dirty)
            elif hasattr(widget, 'cellChanged'):
                widget.cellChanged.connect(lambda *_: self.mark_dirty())
        
        # 添加快捷键
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        QShortcut(QKeySequence('Ctrl+S'), self, self.save_to_tree)
        
        self.setLayout(layout)
        
    def init_table(self, table):
        """初始化表格"""
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['', 'Key', 'Value', 'Description', 'Operation'])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.setRowCount(1)
        self.add_table_row(table, 0)
        # 只连接一次cellChanged
        table.cellChanged.connect(lambda row, col, t=table: self.on_table_edit(t, row, col))
        
    def add_table_row(self, table, row):
        """添加表格行"""
        table.setItem(row, 1, QTableWidgetItem(''))
        table.setItem(row, 2, QTableWidgetItem(''))
        table.setItem(row, 3, QTableWidgetItem(''))
        table.setItem(row, 4, QTableWidgetItem(''))
        self.add_row_widgets(table, row)
        # 不要在这里连接cellChanged，避免递归
        
    def add_row_widgets(self, table, row):
        """添加行控件"""
        cb = QCheckBox()
        cb.setChecked(True)
        table.setCellWidget(row, 0, cb)
        
        def remove():
            if table.rowCount() > 1:
                table.removeRow(row)
        
        remove_btn = QPushButton('Remove')
        remove_btn.setFixedWidth(60)
        remove_btn.clicked.connect(remove)
        table.setCellWidget(row, 4, remove_btn)
        
    def on_table_edit(self, table, row, col):
        """表格编辑事件"""
        if row == table.rowCount() - 1 and col in [1, 2, 3]:
            # 在最后一行编辑时，添加新行
            table.blockSignals(True)
            table.insertRow(table.rowCount())
            self.add_table_row(table, table.rowCount() - 1)
            table.blockSignals(False)
        
    def refresh_table_widgets(self, table):
        """刷新表格控件"""
        for r in range(table.rowCount()):
            is_last = (r == table.rowCount() - 1)
            if not is_last:
                # 非最后一行，添加删除按钮
                def remove():
                    if table.rowCount() > 1:
                        table.removeRow(r)
                
                remove_btn = QPushButton('Remove')
                remove_btn.setFixedWidth(60)
                remove_btn.clicked.connect(remove)
                table.setCellWidget(r, 4, remove_btn)
        
    def mark_dirty(self):
        """标记为已修改"""
        mainwin = self.window()
        if hasattr(mainwin, 'req_tabs'):
            idx = mainwin.req_tabs.indexOf(self)
            if idx >= 0 and not mainwin.req_tabs.tabText(idx).endswith('*'):
                mainwin.req_tabs.setTabText(idx, mainwin.req_tabs.tabText(idx) + '*')
        self._dirty = True
        
    def save_to_tree(self):
        """保存到树"""
        from PyQt5.QtCore import Qt
        mainwin = self.window()
        if hasattr(mainwin, 'collection_tree'):
            sel = mainwin.collection_tree.currentItem()
            if sel and sel.childCount() == 0:
                name = sel.text(0)
                idx = mainwin.req_tabs.indexOf(self)
                if idx >= 0:
                    mainwin.req_tabs.setTabText(idx, name)
                # 保存内容到树节点
                sel.setData(0, Qt.UserRole, self.serialize_request())
            else:
                from PyQt5.QtWidgets import QTreeWidgetItem
                name = self.url_edit.text() or 'New Request'
                item = QTreeWidgetItem([name])
                item.setIcon(0, mainwin.file_icon)
                item.setData(0, Qt.UserRole, self.serialize_request())
                mainwin.collection_tree.addTopLevelItem(item)
                idx = mainwin.req_tabs.indexOf(self)
                if idx >= 0:
                    mainwin.req_tabs.setTabText(idx, name)
            idx = mainwin.req_tabs.indexOf(self)
            if idx >= 0:
                t = mainwin.req_tabs.tabText(idx)
                if t.endswith('*'):
                    mainwin.req_tabs.setTabText(idx, t[:-1])
        self._dirty = False
        mainwin.save_all()
        
    def beautify_json(self):
        """美化JSON"""
        try:
            text = self.raw_text_edit.toPlainText()
            if text.strip():
                obj = json.loads(text)
                self.raw_text_edit.setPlainText(json.dumps(obj, ensure_ascii=False, indent=2))
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Invalid JSON: {e}')
            
    def on_raw_type_changed(self, text):
        """原始类型改变"""
        if text == 'JSON':
            # 自动美化
            try:
                obj = json.loads(self.raw_text_edit.toPlainText())
                self.raw_text_edit.setPlainText(json.dumps(obj, ensure_ascii=False, indent=2))
            except Exception:
                pass
                
    def on_send_clicked(self):
        """发送按钮点击"""
        mainwin = self.window()
        if hasattr(mainwin, 'send_request'):
            mainwin.send_request(self)
            
    def on_save_clicked(self):
        """保存按钮点击"""
        self.save_to_tree()
        
    def on_import_clicked(self):
        """导入按钮点击"""
        mainwin = self.window()
        if hasattr(mainwin, 'import_request_dialog'):
            mainwin.import_request_dialog()
            
    def on_code_clicked(self):
        """代码按钮点击"""
        mainwin = self.window()
        if hasattr(mainwin, 'show_curl_code'):
            mainwin.show_curl_code()
            
    def serialize_request(self):
        """序列化请求数据"""
        def get_table_data(table):
            data = []
            for row in range(table.rowCount() - 1):
                cb = table.cellWidget(row, 0)
                if cb and cb.isChecked():
                    key_item = table.item(row, 1)
                    value_item = table.item(row, 2)
                    if key_item and key_item.text().strip():
                        data.append({
                            'key': key_item.text().strip(),
                            'value': value_item.text().strip() if value_item else ''
                        })
            return data
        
        # 确定body类型
        body_type = 'none'
        body_data = ''
        if self.body_form_radio.isChecked():
            body_type = 'form-data'
            body_data = get_table_data(self.form_table)
        elif self.body_url_radio.isChecked():
            body_type = 'x-www-form-urlencoded'
            body_data = get_table_data(self.url_table)
        elif self.body_raw_radio.isChecked():
            body_type = 'raw'
            body_data = self.raw_text_edit.toPlainText()
        
        return {
            'method': self.method_combo.currentText(),
            'url': self.url_edit.text(),
            'params': get_table_data(self.params_table),
            'headers': get_table_data(self.headers_table),
            'body_type': body_type,
            'body': body_data,
            'raw_type': self.raw_type_combo.currentText() if body_type == 'raw' else 'JSON'
        } 