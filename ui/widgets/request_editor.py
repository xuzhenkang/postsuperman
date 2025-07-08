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
import uuid


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
        self.params_table.setObjectName('params_table')
        self.init_table(self.params_table)
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 0, 0, 0)
        params_layout.setSpacing(0)
        params_layout.addWidget(self.params_table)
        
        # Headers表格
        self.headers_table = QTableWidget()
        self.headers_table.setObjectName('headers_table')
        self.init_table(self.headers_table)
        headers_widget = QWidget()
        headers_layout = QVBoxLayout(headers_widget)
        headers_layout.setContentsMargins(0, 0, 0, 0)
        headers_layout.setSpacing(0)
        headers_layout.addWidget(self.headers_table)
        
        # form-data表格
        self.form_table = QTableWidget()
        self.form_table.setObjectName('form_table')
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
        
        # 设置Beautify按钮的初始可见性
        self.beautify_btn.setVisible(True)  # 默认JSON类型显示
        
        self.setLayout(layout)
        
    def init_table(self, table):
        """初始化表格"""
        from PyQt5.QtWidgets import QComboBox
        is_form = table.objectName() == 'form_table'
        if is_form:
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['', 'Key', 'Type', 'Value', 'Description', 'Operation'])
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.setColumnWidth(2, 100)  # Type列宽度固定100
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        else:
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(['', 'Key', 'Value', 'Description', 'Operation'])
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.setRowCount(1)
        self.add_table_row(table, 0)
        table.cellChanged.connect(lambda row, col, t=table: self.on_table_edit(t, row, col))
        
    def add_table_row(self, table, row):
        """添加表格行"""
        from PyQt5.QtWidgets import QComboBox, QPushButton, QFileDialog
        is_form = table.objectName() == 'form_table'
        if is_form:
            table.setItem(row, 1, QTableWidgetItem(''))
            type_combo = QComboBox()
            type_combo.addItems(['Text', 'File'])
            type_combo.setCurrentIndex(0)
            table.setCellWidget(row, 2, type_combo)
            table.setItem(row, 3, QTableWidgetItem(''))
            table.setItem(row, 4, QTableWidgetItem(''))
            table.setItem(row, 5, QTableWidgetItem(''))
            self.add_row_widgets(table, row)
            def on_type_changed(idx, r=row):
                self.update_row_for_type(table, r)
            type_combo.currentIndexChanged.connect(on_type_changed)
            self.update_row_for_type(table, row)
        else:
            table.setItem(row, 1, QTableWidgetItem(''))
            table.setItem(row, 2, QTableWidgetItem(''))
            table.setItem(row, 3, QTableWidgetItem(''))
            table.setItem(row, 4, QTableWidgetItem(''))
            self.add_row_widgets(table, row)
        
    def add_row_widgets(self, table, row):
        """添加行控件"""
        from PyQt5.QtWidgets import QPushButton, QFileDialog, QComboBox
        is_form = table.objectName() == 'form_table'
        cb = QCheckBox()
        cb.setChecked(True)
        table.setCellWidget(row, 0, cb)
        def remove():
            if table.rowCount() > 1:
                table.removeRow(row)
        remove_btn = QPushButton('Remove')
        remove_btn.setFixedWidth(60)
        remove_btn.clicked.connect(remove)
        if is_form:
            table.setCellWidget(row, 5, remove_btn)
        else:
            table.setCellWidget(row, 4, remove_btn)
        # 文件选择按钮
        if is_form:
            type_combo = table.cellWidget(row, 2)
            if type_combo and type_combo.currentText() == 'File':
                file_btn = QPushButton('Choose File')
                file_btn.setFixedWidth(80)
                def choose_file():
                    fname, _ = QFileDialog.getOpenFileName(self, 'Choose File', '', 'All Files (*)')
                    if fname:
                        table.setItem(row, 3, QTableWidgetItem(fname))
                file_btn.clicked.connect(choose_file)
                table.setCellWidget(row, 3, file_btn)
            else:
                table.removeCellWidget(row, 3)

    def update_row_for_type(self, table, row):
        """更新行以适应类型"""
        from PyQt5.QtWidgets import QPushButton, QFileDialog
        type_combo = table.cellWidget(row, 2)
        if not type_combo:
            return
        if type_combo.currentText() == 'File':
            table.setItem(row, 3, QTableWidgetItem(''))
            table.item(row, 3).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            file_btn = QPushButton('Choose File')
            file_btn.setFixedWidth(80)
            def choose_file():
                fname, _ = QFileDialog.getOpenFileName(self, 'Choose File', '', 'All Files (*)')
                if fname:
                    table.setItem(row, 3, QTableWidgetItem(fname))
            file_btn.clicked.connect(choose_file)
            table.setCellWidget(row, 3, file_btn)
        else:
            table.removeCellWidget(row, 3)
            item = table.item(row, 3)
            if not item:
                table.setItem(row, 3, QTableWidgetItem(''))
            table.item(row, 3).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

    def on_table_edit(self, table, row, col):
        """表格编辑事件"""
        # 自动添加Content-Type: multipart/form-data; boundary=xxx 到Headers表格
        if table.objectName() == 'form_table':
            auto_multipart = False
            for r in range(table.rowCount() - 1):
                type_combo = table.cellWidget(r, 2)
                if type_combo and type_combo.currentText() == 'File':
                    auto_multipart = True
                    break
            headers_table = getattr(self, 'headers_table', None)
            if auto_multipart and headers_table:
                # 检查是否已存在Content-Type
                exists = False
                for i in range(headers_table.rowCount() - 1):
                    key_item = headers_table.item(i, 1)
                    if key_item and key_item.text().strip().lower() == 'content-type':
                        exists = True
                        break
                if not exists:
                    # 生成boundary
                    boundary = uuid.uuid4().hex
                    row_idx = headers_table.rowCount() - 1
                    headers_table.setItem(row_idx, 1, QTableWidgetItem('Content-Type'))
                    headers_table.setItem(row_idx, 2, QTableWidgetItem(f'multipart/form-data; boundary={boundary}'))
                    headers_table.setItem(row_idx, 3, QTableWidgetItem(''))
                    headers_table.setItem(row_idx, 4, QTableWidgetItem(''))
                    self.add_row_widgets(headers_table, row_idx)
        if row == table.rowCount() - 1 and col in [1, 2, 3]:
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
                # 获取当前Tab的完整路径
                idx = mainwin.req_tabs.indexOf(self)
                if idx >= 0:
                    current_tab_text = mainwin.req_tabs.tabText(idx)
                    # 移除星号（如果有）
                    if current_tab_text.endswith('*'):
                        current_tab_text = current_tab_text[:-1]
                    
                    # 保持原有的完整路径，只更新Request名称部分
                    if '/' in current_tab_text:
                        # 有路径的情况：Collection/Request
                        path_parts = current_tab_text.split('/')
                        if len(path_parts) >= 2:
                            collection_path = '/'.join(path_parts[:-1])
                            request_name = sel.text(0)
                            new_tab_text = f"{collection_path}/{request_name}"
                        else:
                            new_tab_text = current_tab_text
                    else:
                        # 没有路径的情况，使用Request名称
                        new_tab_text = sel.text(0)
                    
                    mainwin.req_tabs.setTabText(idx, new_tab_text)
                
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
            
            # 移除星号（如果有）
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
            self.beautify_btn.setVisible(True)
            # 自动美化
            try:
                obj = json.loads(self.raw_text_edit.toPlainText())
                self.raw_text_edit.setPlainText(json.dumps(obj, ensure_ascii=False, indent=2))
            except Exception:
                pass
        else:
            self.beautify_btn.setVisible(False)
                
    def on_send_clicked(self):
        """发送按钮点击"""
        mainwin = self.window()
        if hasattr(mainwin, 'send_request'):
            mainwin.send_request(self)
            
    def on_save_clicked(self):
        """导出按钮点击"""
        mainwin = self.window()
        if hasattr(mainwin, 'export_request'):
            mainwin.export_request()
        
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
            is_form = table.objectName() == 'form_table'
            for row in range(table.rowCount() - 1):
                cb = table.cellWidget(row, 0)
                if cb and cb.isChecked():
                    key_item = table.item(row, 1)
                    if is_form:
                        type_combo = table.cellWidget(row, 2)
                        value_item = table.item(row, 3)
                        type_val = type_combo.currentText() if type_combo else 'Text'
                        file_path = value_item.text() if value_item else ''
                        data.append({
                            'key': key_item.text().strip() if key_item else '',
                            'value': file_path if type_val == 'File' else (value_item.text().strip() if value_item else ''),
                            'type': type_val,
                            'file_path': file_path if type_val == 'File' else ''
                        })
                    else:
                        value_item = table.item(row, 2)
                        data.append({
                            'key': key_item.text().strip() if key_item else '',
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