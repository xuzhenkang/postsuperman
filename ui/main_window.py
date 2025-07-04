from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QTextEdit, QLineEdit, QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView, QFrame, QTreeWidget, QTreeWidgetItem, QButtonGroup, QRadioButton, QStackedWidget, QCheckBox, QMenuBar, QMenu, QAction, QFileDialog, QMessageBox, QDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QRect, QSize, QTimer
from PyQt5.QtGui import QClipboard, QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor, QIcon
from PyQt5.QtWidgets import QApplication, QStyle
import json
import requests
import time
import shlex
import urllib.parse

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('postsuperman')
        self.resize(1440, 900)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 菜单栏
        menubar = QMenuBar(self)
        file_menu = QMenu('File', self)
        import_action = QAction('Import', self)
        export_action = QAction('Export', self)
        exit_action = QAction('Exit', self)
        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        menubar.addMenu(file_menu)
        help_menu = QMenu('Help', self)
        about_action = QAction('About', self)
        doc_action = QAction('Documentation', self)
        contact_action = QAction('Contact Me', self)
        help_menu.addAction(about_action)
        help_menu.addAction(doc_action)
        help_menu.addAction(contact_action)
        menubar.addMenu(help_menu)
        main_layout.setMenuBar(menubar)
        import_action.triggered.connect(self.import_data)
        export_action.triggered.connect(self.export_data)
        exit_action.triggered.connect(self.close)
        about_action.triggered.connect(self.show_about)
        doc_action.triggered.connect(self.show_doc)
        contact_action.triggered.connect(self.show_contact)

        # 顶部导航栏
        topbar = QFrame()
        topbar.setFixedHeight(48)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(16, 0, 16, 0)
        topbar_layout.setSpacing(16)
        logo = QLabel('🦸')
        logo.setFixedWidth(32)
        title = QLabel('<b>postsuperman</b>')
        title.setStyleSheet('font-size:18px;')
        topbar_layout.addWidget(logo)
        topbar_layout.addWidget(title)
        topbar_layout.addStretch()
        main_layout.addWidget(topbar)

        # 主体分栏
        splitter = QSplitter(Qt.Horizontal)
        # 左侧Tab栏
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        self.left_tab = QTabWidget()
        self.left_tab.setTabPosition(QTabWidget.North)
        self.left_tab.setObjectName('LeftTab')
        # 图标
        folder_icon = QApplication.style().standardIcon(QStyle.SP_DirClosedIcon)
        file_icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
        self.folder_icon = folder_icon
        self.file_icon = file_icon
        # Collections Tab
        collections_panel = QWidget()
        collections_layout = QVBoxLayout(collections_panel)
        collections_layout.setContentsMargins(0, 0, 0, 0)
        collections_layout.setSpacing(4)
        btn_row = QHBoxLayout()
        self.new_collection_btn = QPushButton('New Collection')
        self.new_collection_btn.setToolTip('新建一个请求集合')
        btn_row.addWidget(self.new_collection_btn)
        self.import_collection_btn = QPushButton('Import Collection')
        self.import_collection_btn.setToolTip('导入请求集合')
        btn_row.addWidget(self.import_collection_btn)
        btn_row.addStretch()
        collections_layout.addLayout(btn_row)
        self.collection_tree = QTreeWidget()
        self.collection_tree.setHeaderHidden(True)
        self.collection_tree.setDragDropMode(self.collection_tree.InternalMove)
        self.collection_tree.setDefaultDropAction(Qt.MoveAction)
        self.collection_tree.setSelectionMode(self.collection_tree.SingleSelection)
        self.collection_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.collection_tree.dropEvent = self.collection_drop_event_only_top_level
        collections_layout.addWidget(self.collection_tree)
        root = QTreeWidgetItem(self.collection_tree, ['默认集合'])
        root.setIcon(0, self.folder_icon)
        demo_req = QTreeWidgetItem(root, ['GET 示例请求'])
        demo_req.setIcon(0, self.file_icon)
        self.left_tab.addTab(collections_panel, 'Collections')
        # Environments Tab
        self.env_list = QListWidget()
        self.left_tab.addTab(self.env_list, 'Environments')
        # History Tab
        self.history_list = QListWidget()
        self.left_tab.addTab(self.history_list, 'History')
        left_layout.addWidget(self.left_tab)
        left_widget.setFixedWidth(260)
        splitter.addWidget(left_widget)
        # 右侧主区
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        # 垂直分割：请求区和响应区
        vertical_splitter = QSplitter(Qt.Vertical)
        # 顶部请求Tab
        self.req_tabs = QTabWidget()
        self.req_tabs.setObjectName('RequestTabs')
        self.req_tabs.setTabsClosable(True)
        req_editor = RequestEditor(self, req_name='GET 示例请求')
        self.req_tabs.addTab(req_editor, 'GET 示例请求')
        # 响应区
        resp_card = QFrame()
        resp_card.setObjectName('ResponseCard')
        resp_card_layout = QVBoxLayout(resp_card)
        resp_card_layout.setContentsMargins(16, 8, 16, 8)
        resp_card_layout.setSpacing(8)
        self.resp_tabs = QTabWidget()
        self.resp_tabs.setObjectName('RespTabs')
        # Body Tab
        resp_body_widget = QWidget()
        resp_body_layout = QVBoxLayout(resp_body_widget)
        resp_body_layout.setContentsMargins(0, 0, 0, 0)
        resp_body_layout.setSpacing(4)
        # 响应状态栏和按钮同一行
        self.resp_status_label = QLineEdit('Click Send to get a response')
        self.resp_status_label.setReadOnly(True)
        self.resp_status_label.setFrame(False)
        self.resp_status_label.setStyleSheet('background: transparent; border: none; font-weight: bold; color: #333;')
        status_row = QHBoxLayout()
        status_row.addWidget(self.resp_status_label)
        status_row.addStretch()
        self.save_resp_btn = QPushButton('Save Response to File')
        self.clear_resp_btn = QPushButton('Clear Response')
        status_row.addWidget(self.save_resp_btn)
        status_row.addWidget(self.clear_resp_btn)
        resp_body_layout.addLayout(status_row)
        self.resp_body_edit = QTextEdit()
        self.resp_body_edit.setReadOnly(True)
        resp_body_layout.addWidget(self.resp_body_edit)
        resp_body_widget.setLayout(resp_body_layout)
        self.resp_tabs.addTab(resp_body_widget, 'Body')
        # Headers Tab
        resp_headers_widget = QTextEdit()
        resp_headers_widget.setReadOnly(True)
        self.resp_tabs.addTab(resp_headers_widget, 'Headers')
        resp_card_layout.addWidget(self.resp_tabs)
        resp_card.setLayout(resp_card_layout)
        vertical_splitter.addWidget(self.req_tabs)
        vertical_splitter.addWidget(resp_card)
        vertical_splitter.setSizes([500, 300])
        right_layout.addWidget(vertical_splitter)
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter) 

        self.new_collection_btn.clicked.connect(self.create_collection)
        self.import_collection_btn.clicked.connect(self.import_collection)
        self.collection_tree.customContextMenuRequested.connect(self.show_collection_menu)
        self.collection_tree.itemDoubleClicked.connect(self.on_collection_item_double_clicked)
        self.req_tabs.currentChanged.connect(self.on_req_tab_changed)
        self.req_tabs.tabCloseRequested.connect(self.on_req_tab_closed)

    def init_table(self, table):
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
        table.setItem(row, 1, QTableWidgetItem(''))
        table.setItem(row, 2, QTableWidgetItem(''))
        table.setItem(row, 3, QTableWidgetItem(''))
        table.setItem(row, 4, QTableWidgetItem(''))
        self.add_row_widgets(table, row)

    def add_row_widgets(self, table, row):
        cb = QCheckBox()
        cb.setChecked(True)
        table.setCellWidget(row, 0, cb)
        btn = QPushButton('删除')
        btn.setFixedWidth(48)
        def remove():
            if table.rowCount() > 1:
                table.removeRow(row)
                self.refresh_table_widgets(table)
        btn.clicked.connect(remove)
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0,0,0,0)
        layout.addStretch()
        layout.addWidget(btn)
        table.setCellWidget(row, 4, w)

    def on_table_edit(self, table, row, col):
        last_row = table.rowCount() - 1
        if any(table.item(last_row, c) and table.item(last_row, c).text().strip() for c in [1,2,3]):
            table.insertRow(table.rowCount())
            self.add_table_row(table, table.rowCount()-1)
        self.refresh_table_widgets(table)

    def refresh_table_widgets(self, table):
        for r in range(table.rowCount()):
            is_last = (r == table.rowCount() - 1)
            cb = table.cellWidget(r, 0)
            if cb:
                cb.setVisible(not is_last)
            btn_w = table.cellWidget(r, 4)
            if btn_w:
                btn = btn_w.findChild(QPushButton)
                if btn:
                    btn.setVisible(not is_last)

    def beautify_json(self):
        if self.raw_type_combo.currentText() == 'JSON':
            text = self.raw_text_edit.toPlainText()
            if not text.strip():
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, 'Beautify Error', '请输入JSON内容后再美化！')
                return
            try:
                obj = json.loads(text)
                pretty = json.dumps(obj, ensure_ascii=False, indent=2)
                self.raw_text_edit.setPlainText(pretty)
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, 'Beautify Error', f'Invalid JSON: {e}')

    def show_curl_code(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        from PyQt5.QtGui import QClipboard
        dlg = QDialog(self)
        dlg.setWindowTitle('cURL')
        layout = QVBoxLayout(dlg)
        label = QLabel('cURL command:')
        layout.addWidget(label)
        # 生成当前请求的curl命令
        method = self.method_combo.currentText()
        url = self.url_edit.text().strip()
        headers = []
        for row in range(self.headers_table.rowCount()-1):
            key_item = self.headers_table.item(row, 1)
            value_item = self.headers_table.item(row, 2)
            if key_item and value_item and key_item.text().strip():
                headers.append(f"-H '{key_item.text().strip()}: {value_item.text().strip()}'")
        curl = f"curl -X {method} {' '.join(headers)} '{url}'"
        curl_edit = QTextEdit()
        curl_edit.setReadOnly(True)
        curl_edit.setPlainText(curl)
        layout.addWidget(curl_edit)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        copy_btn = QPushButton('Copy')
        btn_row.addWidget(copy_btn)
        layout.addLayout(btn_row)
        def do_copy():
            clipboard = dlg.clipboard() if hasattr(dlg, 'clipboard') else QApplication.clipboard()
            clipboard.setText(curl)
        copy_btn.clicked.connect(do_copy)
        dlg.exec_()

    def import_curl(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel
        dlg = QDialog(self)
        dlg.setWindowTitle('Import cURL')
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel('Paste your cURL command below:'))
        curl_edit = QTextEdit()
        layout.addWidget(curl_edit)
        btn = QPushButton('Import')
        layout.addWidget(btn)
        def do_import():
            curl_cmd = curl_edit.toPlainText().strip()
            if curl_cmd:
                # TODO: 解析cURL命令并填充请求（预留）
                dlg.accept()
        btn.clicked.connect(do_import)
        dlg.exec_()

    def import_data(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Import Data', '', 'JSON Files (*.json);;All Files (*)')
        if fname:
            # TODO: 实现导入逻辑
            pass

    def export_data(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Export Data', '', 'JSON Files (*.json);;All Files (*)')
        if fname:
            # TODO: 实现导出逻辑
            pass

    def show_about(self):
        QMessageBox.information(self, 'About', 'postsuperman\nA Postman-like API debugging tool.\nPowered by Python & PyQt5. \nDeveloped by xuzhenkang@hotmail.com')

    def show_doc(self):
        QMessageBox.information(self, 'Documentation', 'Visit the official documentation site for usage instructions.')

    def show_contact(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        dlg = QDialog(self)
        dlg.setWindowTitle('Contact Me')
        layout = QVBoxLayout(dlg)
        label = QLabel('For support, contact:')
        layout.addWidget(label)
        contact_edit = QTextEdit()
        contact_edit.setReadOnly(True)
        contact_edit.setPlainText('xuzhenkang@hotmail.com')
        layout.addWidget(contact_edit)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        copy_btn = QPushButton('Copy')
        btn_row.addWidget(copy_btn)
        layout.addLayout(btn_row)
        def do_copy():
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText('xuzhenkang@hotmail.com')
        copy_btn.clicked.connect(do_copy)
        dlg.exec_()

    def send_request(self, editor=None):
        print(f'[DEBUG] MainWindow.send_request called, editor={editor}')
        if editor is None:
            print('[DEBUG] editor is None, return')
            return
        method = editor.method_combo.currentText()
        url = editor.url_edit.text().strip()
        print(f'[DEBUG] method={method}, url={url}')
        # 拼接Params
        params = {}
        for row in range(editor.params_table.rowCount()-1):
            cb = editor.params_table.cellWidget(row, 0)
            if cb and not cb.isChecked():
                continue
            key_item = editor.params_table.item(row, 1)
            value_item = editor.params_table.item(row, 2)
            if key_item and key_item.text().strip():
                params[key_item.text().strip()] = value_item.text().strip() if value_item else ''
        # Headers
        headers = {}
        for row in range(editor.headers_table.rowCount()-1):
            cb = editor.headers_table.cellWidget(row, 0)
            if cb and not cb.isChecked():
                continue
            key_item = editor.headers_table.item(row, 1)
            value_item = editor.headers_table.item(row, 2)
            if key_item and key_item.text().strip():
                headers[key_item.text().strip()] = value_item.text().strip() if value_item else ''
        # Body
        data = None
        json_data = None
        files = None
        if editor.body_form_radio.isChecked():
            # form-data
            data = {}
            for row in range(editor.form_table.rowCount()-1):
                cb = editor.form_table.cellWidget(row, 0)
                if cb and not cb.isChecked():
                    continue
                key_item = editor.form_table.item(row, 1)
                value_item = editor.form_table.item(row, 2)
                if key_item and key_item.text().strip():
                    data[key_item.text().strip()] = value_item.text().strip() if value_item else ''
        elif editor.body_url_radio.isChecked():
            # x-www-form-urlencoded
            data = {}
            for row in range(editor.url_table.rowCount()-1):
                cb = editor.url_table.cellWidget(row, 0)
                if cb and not cb.isChecked():
                    continue
                key_item = editor.url_table.item(row, 1)
                value_item = editor.url_table.item(row, 2)
                if key_item and key_item.text().strip():
                    data[key_item.text().strip()] = value_item.text().strip() if value_item else ''
        elif editor.body_raw_radio.isChecked():
            # raw
            raw_type = editor.raw_type_combo.currentText()
            raw_text = editor.raw_text_edit.toPlainText()
            if raw_type == 'JSON':
                try:
                    json_data = json.loads(raw_text)
                except Exception:
                    json_data = None
            else:
                data = raw_text
        try:
            start = time.time()
            resp = requests.request(method, url, params=params, headers=headers, data=data, json=json_data, files=files)
            elapsed = int((time.time() - start) * 1000)
        except Exception as e:
            status = f'Error: {e}'
            body = ''
            headers_str = ''
            self.resp_status_label.setText(status)
            self.resp_body_edit.setPlainText(body)
            self.resp_tabs.setCurrentIndex(0)
            # 保存到editor
            editor.resp_status = status
            editor.resp_body = body
            editor.resp_headers = headers_str
            return
        # 响应区展示
        status = f'{resp.status_code} {resp.reason}   {elapsed}ms   {len(resp.content)/1024:.2f}KB'
        try:
            body = resp.text
            if 'application/json' in resp.headers.get('Content-Type', ''):
                obj = resp.json()
                body = json.dumps(obj, ensure_ascii=False, indent=2)
        except Exception:
            body = resp.text
        headers_str = '\n'.join(f'{k}: {v}' for k, v in resp.headers.items())
        self.resp_status_label.setText(status)
        self.resp_body_edit.setPlainText(body)
        self.resp_tabs.widget(1).setPlainText(headers_str)
        self.resp_tabs.setCurrentIndex(0)
        # 保存到editor
        editor.resp_status = status
        editor.resp_body = body
        editor.resp_headers = headers_str

    def save_response_to_file(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        text = self.resp_body_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, 'No Response', '响应体为空，无法保存！')
            return
        fname, _ = QFileDialog.getSaveFileName(self, 'Save Response', '', 'Text Files (*.txt);;All Files (*)')
        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                QMessageBox.warning(self, 'Save Failed', f'保存失败: {e}')

    def clear_response(self):
        self.resp_status_label.setText('Click Send to get a response')
        self.resp_body_edit.clear()
        self.resp_tabs.widget(1).setPlainText('')

    def on_raw_type_changed(self, text):
        if text == 'JSON':
            # 自动美化
            try:
                obj = json.loads(self.raw_text_edit.toPlainText())
                pretty = json.dumps(obj, ensure_ascii=False, indent=2)
                self.raw_text_edit.setPlainText(pretty)
            except Exception:
                pass
            self.json_highlighter.setDocument(self.raw_text_edit.document())
        else:
            self.json_highlighter.setDocument(None)

    def create_collection(self):
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        name, ok = QInputDialog.getText(self, '新建 Collection', '请输入集合名称:')
        if not ok or not name.strip():
            return
        name = name.strip()
        def is_duplicate(tree, name):
            for i in range(tree.topLevelItemCount()):
                if tree.topLevelItem(i).text(0) == name:
                    return True
            return False
        if is_duplicate(self.collection_tree, name):
            QMessageBox.warning(self, '新建失败', f'已存在名为"{name}"的集合！')
            return
        item = QTreeWidgetItem(self.collection_tree, [name])
        item.setIcon(0, self.folder_icon)
        QTreeWidgetItem(item, ['GET 示例请求'])
        self.left_tab.addTab(collections_panel, 'Collections')

    def show_collection_menu(self, pos):
        from PyQt5.QtWidgets import QMenu, QMessageBox, QInputDialog
        item = self.collection_tree.itemAt(pos)
        if not item:
            return  # 空白处不弹菜单
        menu = QMenu(self)
        # 判断节点类型
        def is_request(item):
            return (
                item is not None and
                item.childCount() == 0 and
                item.parent() is not None and
                item.icon(0).cacheKey() == self.file_icon.cacheKey()
            )
        def is_collection(item):
            return item is not None and not is_request(item)
        # 菜单生成
        if is_collection(item):
            new_collection_action = menu.addAction('New Collection')
            new_req_action = menu.addAction('新建 Request')
            menu.addSeparator()
            rename_action = menu.addAction('重命名')
            delete_action = menu.addAction('删除')
        elif is_request(item):
            new_collection_action = None
            rename_action = menu.addAction('重命名')
            delete_action = menu.addAction('删除')
        else:
            new_collection_action = None
            rename_action = None
            delete_action = None
        action = menu.exec_(self.collection_tree.viewport().mapToGlobal(pos))
        if new_collection_action and action == new_collection_action:
            name, ok = QInputDialog.getText(self, 'New Collection', '请输入集合名称:')
            if not ok or not name.strip():
                return
            name = name.strip()
            # 检查重名（只在该节点下）
            for i in range(item.childCount()):
                sibling = item.child(i)
                if sibling and sibling.text(0) == name:
                    QMessageBox.warning(self, '新建失败', f'该集合下已存在名为"{name}"的集合！')
                    return
            new_item = QTreeWidgetItem(item, [name])
            new_item.setIcon(0, self.folder_icon)
            item.setExpanded(True)
            return
        elif 'new_req_action' in locals() and new_req_action and action == new_req_action:
            name, ok = QInputDialog.getText(self, '新建 Request', '请输入请求名称:')
            if not ok or not name.strip():
                return
            name = name.strip()
            # 检查重名（只在该集合下）
            for i in range(item.childCount()):
                sibling = item.child(i)
                if sibling and sibling.text(0) == name:
                    QMessageBox.warning(self, '新建失败', f'该集合下已存在名为"{name}"的请求！')
                    return
            new_item = QTreeWidgetItem(item, [name])
            new_item.setIcon(0, self.file_icon)
            item.setExpanded(True)
            return
        elif rename_action and action == rename_action:
            name, ok = QInputDialog.getText(self, '重命名', '请输入新名称:', text=item.text(0))
            if not ok or not name.strip():
                return
            name = name.strip()
            if item.parent() is None:
                for i in range(self.collection_tree.topLevelItemCount()):
                    if self.collection_tree.topLevelItem(i) != item and self.collection_tree.topLevelItem(i).text(0) == name:
                        QMessageBox.warning(self, '重命名失败', f'已存在名为"{name}"的集合！')
                        return
            else:
                parent = item.parent()
                for i in range(parent.childCount()):
                    if parent.child(i) != item and parent.child(i).text(0) == name:
                        QMessageBox.warning(self, '重命名失败', f'该集合下已存在名为"{name}"的请求！')
                        return
            item.setText(0, name)
            # 重命名后保持图标
            if item.parent() is None:
                item.setIcon(0, self.folder_icon)
            else:
                item.setIcon(0, self.file_icon)
        elif delete_action and action == delete_action:
            if item.parent() is None:
                reply = QMessageBox.question(self, '删除集合', f'确定要删除集合"{item.text(0)}"吗？', QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    idx = self.collection_tree.indexOfTopLevelItem(item)
                    self.collection_tree.takeTopLevelItem(idx)
            else:
                reply = QMessageBox.question(self, '删除请求', f'确定要删除请求"{item.text(0)}"吗？', QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    parent = item.parent()
                    parent.removeChild(item)

    def import_collection(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, 'Import Collection', '导入集合功能待实现。')

    def collection_drop_event_only_top_level(self, event):
        # Collection节点可无限层级，Request只能是Collection的子节点，Request/Collection同级可排序，Request不能变成顶层或Request的子节点
        from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget
        source = self.collection_tree.currentItem()
        target_pos = event.pos()
        target_item = self.collection_tree.itemAt(target_pos)
        if source is None:
            event.ignore()
            return
        # 判断节点类型
        def is_request(item):
            return (
                item is not None and
                item.childCount() == 0 and
                item.parent() is not None and
                item.icon(0).cacheKey() == self.file_icon.cacheKey()
            )
        def is_collection(item):
            return item is not None and not is_request(item)
        # 拖拽Collection节点
        if is_collection(source):
            # 拖到根部或Collection节点下，允许
            if target_item is None or is_collection(target_item):
                QTreeWidget.dropEvent(self.collection_tree, event)
                return
            # 拖到Request节点下，禁止
            if is_request(target_item):
                event.ignore()
                return
        # 拖拽Request节点
        if is_request(source):
            # 只能在同一Collection下排序
            if target_item is not None and target_item.parent() == source.parent() and is_request(target_item):
                QTreeWidget.dropEvent(self.collection_tree, event)
                return
            # 拖到Collection节点，允许作为其子节点（即跨Collection移动）
            if is_collection(target_item):
                QTreeWidget.dropEvent(self.collection_tree, event)
                return
            # 拖到根部或Request节点下，禁止
            event.ignore()
            return

    def on_collection_item_double_clicked(self, item, column):
        # 判断是否为Request节点
        if item.childCount() == 0 and item.parent() is not None and item.icon(0).cacheKey() == self.file_icon.cacheKey():
            # 查找请求Tab中是否有同名Tab，有则切换，没有则新建
            name = item.text(0)
            for i in range(self.req_tabs.count()):
                if self.req_tabs.tabText(i) == name:
                    self.req_tabs.setCurrentIndex(i)
                    return
            req_editor = RequestEditor(self, req_name=name)
            self.req_tabs.addTab(req_editor, name)
            self.req_tabs.setCurrentWidget(req_editor)

    def on_req_tab_changed(self, idx):
        editor = self.req_tabs.widget(idx)
        if hasattr(editor, 'resp_status'):
            self.resp_status_label.setText(editor.resp_status)
            self.resp_body_edit.setPlainText(editor.resp_body)
            self.resp_tabs.widget(1).setPlainText(editor.resp_headers)
        else:
            self.resp_status_label.setText('')
            self.resp_body_edit.setPlainText('')
            self.resp_tabs.widget(1).setPlainText('')

    def on_req_tab_closed(self, idx):
        self.req_tabs.removeTab(idx)
        # 如果没有Tab或当前Tab不是RequestEditor，清空响应区
        if self.req_tabs.count() == 0 or not hasattr(self.req_tabs.currentWidget(), 'resp_status'):
            self.resp_status_label.setText('')
            self.resp_body_edit.setPlainText('')
            self.resp_tabs.widget(1).setPlainText('')

class JsonHighlighter(QSyntaxHighlighter):
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
        import re
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

# 行号区域控件
from PyQt5.QtWidgets import QWidget, QPlainTextEdit
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor
    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)
    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
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
    def keyPressEvent(self, event):
        if self.parent_mainwindow and hasattr(self.parent_mainwindow, 'raw_type_combo'):
            if self.parent_mainwindow.raw_type_combo.currentText() == 'JSON':
                # Ctrl+B 一键美化
                if event.key() == Qt.Key_B and event.modifiers() & Qt.ControlModifier:
                    try:
                        obj = json.loads(self.toPlainText())
                        pretty = json.dumps(obj, ensure_ascii=False, indent=2)
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
                            block_cursor.insertText('    ')
                        return
                    else:
                        cursor.insertText('    ')
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
                            if line.startswith('    '):
                                block_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 4)
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
                        indent += '    '
                    cursor.insertText(indent)
                    self.setTextCursor(cursor)
                    return
                # 括号自动补全
                pairs = {'{': '}', '[': ']', '(': ')', '"': '"'}
                text = event.text()
                if text in pairs:
                    cursor = self.textCursor()
                    cursor.insertText(text + pairs[text])
                    cursor.movePosition(cursor.Left)
                    self.setTextCursor(cursor)
                    return
        super().keyPressEvent(event)
    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().width('9') * digits
    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
    def updateLineNumberArea(self):
        rect = self.viewport().rect()
        dy = 0
        self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
    def updateLineNumberAreaEvent(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    def lineNumberAreaPaintEvent(self, event):
        from PyQt5.QtGui import QPainter
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.gray)
                painter.drawText(0, top, self.lineNumberArea.width()-2, self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
    def paintEvent(self, event):
        super().paintEvent(event)
        self.lineNumberArea.update() 

# 在MainWindow类外部添加RequestEditor类
class RequestEditor(QWidget):
    def __init__(self, parent=None, req_name=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QComboBox, QLineEdit, QPushButton, QTabWidget, QWidget, QLabel, QStackedWidget, QRadioButton, QButtonGroup, QTableWidget
        from PyQt5.QtCore import Qt
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
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
        req_line_layout.addWidget(self.method_combo)
        req_line_layout.addWidget(self.url_edit)
        self.send_btn = QPushButton('Send')
        self.send_btn.setFixedWidth(80)
        self.send_btn.setStyleSheet('''QPushButton {background-color: #1976d2; color: white; font-weight: bold; border-radius: 6px; padding: 8px 0; font-size: 16px;} QPushButton:pressed {background-color: #115293;}''')
        req_line_layout.addWidget(self.send_btn)
        self.layout.addWidget(req_line)
        # Code/Import/Save按钮
        code_import_row = QHBoxLayout()
        code_import_row.setContentsMargins(16, 0, 16, 0)
        code_import_row.setSpacing(8)
        code_import_row.addStretch()
        self.code_btn = QPushButton('Code')
        self.import_btn = QPushButton('Import')
        self.save_btn = QPushButton('Save')
        code_import_row.addWidget(self.code_btn)
        code_import_row.addWidget(self.import_btn)
        code_import_row.addWidget(self.save_btn)
        self.layout.addLayout(code_import_row)
        # Params表格
        self.params_table = QTableWidget()
        self.init_table(self.params_table)
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0,0,0,0)
        params_layout.setSpacing(0)
        params_layout.addWidget(self.params_table)
        # Headers表格
        self.headers_table = QTableWidget()
        self.init_table(self.headers_table)
        headers_widget = QWidget()
        headers_layout = QVBoxLayout(headers_widget)
        headers_layout.setContentsMargins(0,0,0,0)
        headers_layout.setSpacing(0)
        headers_layout.addWidget(self.headers_table)
        # form-data表格
        self.form_table = QTableWidget()
        self.init_table(self.form_table)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0,0,0,0)
        form_layout.setSpacing(0)
        form_layout.addWidget(self.form_table)
        # x-www-form-urlencoded表格
        self.url_table = QTableWidget()
        self.init_table(self.url_table)
        url_widget = QWidget()
        url_layout = QVBoxLayout(url_widget)
        url_layout.setContentsMargins(0,0,0,0)
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
        self.raw_type_combo.currentTextChanged.connect(self.on_raw_type_changed)
        self.body_none_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(0))
        self.body_form_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(1))
        self.body_url_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(2))
        self.body_raw_radio.toggled.connect(lambda checked: checked and self.body_stack.setCurrentIndex(3))
        self.beautify_btn.clicked.connect(self.beautify_json)
        body_tab_layout.addWidget(self.body_stack)
        self.req_tab = QTabWidget()
        self.req_tab.setObjectName('ReqTab')
        self.req_tab.addTab(params_widget, 'Params')
        self.req_tab.addTab(headers_widget, 'Headers')
        self.req_tab.addTab(body_tab, 'Body')
        self.layout.addWidget(self.req_tab)
        if req_name:
            self.url_edit.setText(f'https://api.example.com/{req_name}')
        self.send_btn.clicked.connect(self.on_send_clicked)
        self.save_btn.clicked.connect(self.on_save_clicked)
        self.import_btn.clicked.connect(self.on_import_clicked)
        self.code_btn.clicked.connect(self.on_code_clicked)
        # 添加响应内容属性
        self.resp_status = ''
        self.resp_body = ''
        self.resp_headers = ''
    def init_table(self, table):
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['', 'Key', 'Value', 'Description', 'Operation'])
        from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QCheckBox, QPushButton, QWidget, QHBoxLayout
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.setRowCount(1)
        self.add_table_row(table, 0)
        table.cellChanged.connect(lambda row, col, t=table: self.on_table_edit(t, row, col))
    def add_table_row(self, table, row):
        table.setItem(row, 1, QTableWidgetItem(''))
        table.setItem(row, 2, QTableWidgetItem(''))
        table.setItem(row, 3, QTableWidgetItem(''))
        table.setItem(row, 4, QTableWidgetItem(''))
        cb = QCheckBox()
        cb.setChecked(True)
        table.setCellWidget(row, 0, cb)
        btn = QPushButton('删除')
        btn.setFixedWidth(48)
        def remove():
            if table.rowCount() > 1:
                table.removeRow(row)
        btn.clicked.connect(remove)
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0,0,0,0)
        layout.addStretch()
        layout.addWidget(btn)
        table.setCellWidget(row, 4, w)
    def on_table_edit(self, table, row, col):
        last_row = table.rowCount() - 1
        if any(table.item(last_row, c) and table.item(last_row, c).text().strip() for c in [1,2,3]):
            table.insertRow(table.rowCount())
            self.add_table_row(table, table.rowCount()-1)
    def beautify_json(self):
        if self.raw_type_combo.currentText() == 'JSON':
            text = self.raw_text_edit.toPlainText()
            if not text.strip():
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, 'Beautify Error', '请输入JSON内容后再美化！')
                return
            try:
                import json
                obj = json.loads(text)
                pretty = json.dumps(obj, ensure_ascii=False, indent=2)
                self.raw_text_edit.setPlainText(pretty)
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, 'Beautify Error', f'Invalid JSON: {e}')
    def on_raw_type_changed(self, text):
        if text == 'JSON':
            self.json_highlighter.setDocument(self.raw_text_edit.document())
        else:
            self.json_highlighter.setDocument(None)
    def on_send_clicked(self):
        print('[DEBUG] RequestEditor.on_send_clicked called')
        mainwin = self.window()
        if hasattr(mainwin, 'send_request'):
            print('[DEBUG] Calling mainwin.send_request(self)')
            mainwin.send_request(self)
        else:
            print('[DEBUG] mainwin has no send_request')
    def on_save_clicked(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import json
        # 收集请求数据
        req_data = {
            'name': self.url_edit.text().strip(),
            'method': self.method_combo.currentText(),
            'url': self.url_edit.text().strip(),
            'params': [],
            'headers': [],
            'body_type': None,
            'body': None
        }
        # Params
        for row in range(self.params_table.rowCount()-1):
            key_item = self.params_table.item(row, 1)
            value_item = self.params_table.item(row, 2)
            if key_item and key_item.text().strip():
                req_data['params'].append({
                    'key': key_item.text().strip(),
                    'value': value_item.text().strip() if value_item else ''
                })
        # Headers
        for row in range(self.headers_table.rowCount()-1):
            key_item = self.headers_table.item(row, 1)
            value_item = self.headers_table.item(row, 2)
            if key_item and key_item.text().strip():
                req_data['headers'].append({
                    'key': key_item.text().strip(),
                    'value': value_item.text().strip() if value_item else ''
                })
        # Body
        if self.body_form_radio.isChecked():
            req_data['body_type'] = 'form-data'
            body = []
            for row in range(self.form_table.rowCount()-1):
                key_item = self.form_table.item(row, 1)
                value_item = self.form_table.item(row, 2)
                if key_item and key_item.text().strip():
                    body.append({'key': key_item.text().strip(), 'value': value_item.text().strip() if value_item else ''})
            req_data['body'] = body
        elif self.body_url_radio.isChecked():
            req_data['body_type'] = 'x-www-form-urlencoded'
            body = []
            for row in range(self.url_table.rowCount()-1):
                key_item = self.url_table.item(row, 1)
                value_item = self.url_table.item(row, 2)
                if key_item and key_item.text().strip():
                    body.append({'key': key_item.text().strip(), 'value': value_item.text().strip() if value_item else ''})
            req_data['body'] = body
        elif self.body_raw_radio.isChecked():
            req_data['body_type'] = 'raw'
            req_data['body'] = self.raw_text_edit.toPlainText()
            req_data['raw_type'] = self.raw_type_combo.currentText()
        # 保存到文件
        fname, _ = QFileDialog.getSaveFileName(self, '保存请求', '', 'JSON Files (*.json);;All Files (*)')
        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    json.dump(req_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, '保存成功', f'请求已保存到 {fname}')
            except Exception as e:
                QMessageBox.warning(self, '保存失败', f'保存请求失败: {e}')
    def on_import_clicked(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import json
        fname, _ = QFileDialog.getOpenFileName(self, '导入请求', '', 'JSON Files (*.json);;All Files (*)')
        if not fname:
            return
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                req_data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, '导入失败', f'读取文件失败: {e}')
            return
        # 填充请求内容
        self.method_combo.setCurrentText(req_data.get('method', 'GET'))
        self.url_edit.setText(req_data.get('url', ''))
        # Params
        self.params_table.setRowCount(1)
        for i, param in enumerate(req_data.get('params', [])):
            if i >= self.params_table.rowCount()-1:
                self.params_table.insertRow(self.params_table.rowCount())
            self.params_table.setItem(i, 1, QTableWidgetItem(param.get('key', '')))
            self.params_table.setItem(i, 2, QTableWidgetItem(param.get('value', '')))
        # Headers
        self.headers_table.setRowCount(1)
        for i, header in enumerate(req_data.get('headers', [])):
            if i >= self.headers_table.rowCount()-1:
                self.headers_table.insertRow(self.headers_table.rowCount())
            self.headers_table.setItem(i, 1, QTableWidgetItem(header.get('key', '')))
            self.headers_table.setItem(i, 2, QTableWidgetItem(header.get('value', '')))
        # Body
        body_type = req_data.get('body_type', 'none')
        if body_type == 'form-data':
            self.body_form_radio.setChecked(True)
            self.form_table.setRowCount(1)
            for i, item in enumerate(req_data.get('body', [])):
                if i >= self.form_table.rowCount()-1:
                    self.form_table.insertRow(self.form_table.rowCount())
                self.form_table.setItem(i, 1, QTableWidgetItem(item.get('key', '')))
                self.form_table.setItem(i, 2, QTableWidgetItem(item.get('value', '')))
        elif body_type == 'x-www-form-urlencoded':
            self.body_url_radio.setChecked(True)
            self.url_table.setRowCount(1)
            for i, item in enumerate(req_data.get('body', [])):
                if i >= self.url_table.rowCount()-1:
                    self.url_table.insertRow(self.url_table.rowCount())
                self.url_table.setItem(i, 1, QTableWidgetItem(item.get('key', '')))
                self.url_table.setItem(i, 2, QTableWidgetItem(item.get('value', '')))
        elif body_type == 'raw':
            self.body_raw_radio.setChecked(True)
            self.raw_text_edit.setPlainText(req_data.get('body', ''))
            self.raw_type_combo.setCurrentText(req_data.get('raw_type', 'JSON'))
        else:
            self.body_none_radio.setChecked(True)
        QMessageBox.information(self, '导入成功', '请求已导入！')
    def on_code_clicked(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        from PyQt5.QtCore import QTimer
        from PyQt5.QtGui import QClipboard
        dlg = QDialog(self)
        dlg.setWindowTitle('cURL')
        layout = QVBoxLayout(dlg)
        label = QLabel('cURL command:')
        layout.addWidget(label)
        # 生成cURL命令
        method = self.method_combo.currentText()
        url = self.url_edit.text().strip()
        # Params
        params = []
        for row in range(self.params_table.rowCount()-1):
            key_item = self.params_table.item(row, 1)
            value_item = self.params_table.item(row, 2)
            if key_item and key_item.text().strip():
                params.append((key_item.text().strip(), value_item.text().strip() if value_item else ''))
        # 拼接URL参数
        if params:
            url_parts = urllib.parse.urlsplit(url)
            query = urllib.parse.parse_qsl(url_parts.query)
            query += params
            url = urllib.parse.urlunsplit((url_parts.scheme, url_parts.netloc, url_parts.path, urllib.parse.urlencode(query), url_parts.fragment))
        # Headers
        headers = []
        for row in range(self.headers_table.rowCount()-1):
            key_item = self.headers_table.item(row, 1)
            value_item = self.headers_table.item(row, 2)
            if key_item and key_item.text().strip():
                headers.append((key_item.text().strip(), value_item.text().strip() if value_item else ''))
        # Body
        body = None
        body_type = None
        if self.body_form_radio.isChecked():
            body_type = 'form-data'
            form = []
            for row in range(self.form_table.rowCount()-1):
                key_item = self.form_table.item(row, 1)
                value_item = self.form_table.item(row, 2)
                if key_item and key_item.text().strip():
                    form.append((key_item.text().strip(), value_item.text().strip() if value_item else ''))
            if form:
                # --form 'key=value'
                body = ' '.join([f"--form {shlex.quote(f'{k}={v}')}" for k, v in form])
        elif self.body_url_radio.isChecked():
            body_type = 'x-www-form-urlencoded'
            urlencoded = []
            for row in range(self.url_table.rowCount()-1):
                key_item = self.url_table.item(row, 1)
                value_item = self.url_table.item(row, 2)
                if key_item and key_item.text().strip():
                    urlencoded.append((key_item.text().strip(), value_item.text().strip() if value_item else ''))
            if urlencoded:
                # --data 'key1=val1&key2=val2'
                body = f"--data {shlex.quote('&'.join(f'{k}={v}' for k, v in urlencoded))}"
        elif self.body_raw_radio.isChecked():
            body_type = 'raw'
            raw = self.raw_text_edit.toPlainText()
            if raw:
                body = f"--data-raw {shlex.quote(raw)}"
        # 组装cURL命令
        parts = ["curl", "-X", shlex.quote(method)]
        for k, v in headers:
            parts.append(f"-H {shlex.quote(f'{k}: {v}')}")
        if body:
            parts.append(body)
        parts.append(shlex.quote(url))
        curl_cmd = ' '.join(parts)
        # 弹窗展示
        curl_edit = QTextEdit()
        curl_edit.setReadOnly(True)
        curl_edit.setPlainText(curl_cmd)
        layout.addWidget(curl_edit)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        copy_btn = QPushButton('Copy to Clipboard')
        btn_row.addWidget(copy_btn)
        layout.addLayout(btn_row)
        def do_copy():
            clipboard = dlg.clipboard() if hasattr(dlg, 'clipboard') else self.clipboard() if hasattr(self, 'clipboard') else QApplication.clipboard()
            clipboard.setText(curl_cmd)
            copy_btn.setText('Copied')
            copy_btn.setEnabled(False)
            QTimer.singleShot(2000, lambda: (copy_btn.setText('Copy to Clipboard'), copy_btn.setEnabled(True)))
        copy_btn.clicked.connect(do_copy)
        dlg.exec_() 