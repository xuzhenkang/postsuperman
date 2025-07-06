#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
import psutil  # 添加内存监控
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QMenuBar, QMenu, QAction, QFrame, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QListWidget, QTextEdit,
    QLineEdit, QFileDialog, QMessageBox, QApplication,
    QStyle, QButtonGroup, QRadioButton, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QSpinBox,
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDialogButtonBox,
    QProgressBar, QSlider, QGroupBox, QScrollArea, QGridLayout,
    QSpacerItem, QSizePolicy, QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QMenuBar,
    QMenu, QAction, QFrame, QLabel, QPushButton, QTreeWidget,
    QTreeWidgetItem, QListWidget, QTextEdit, QLineEdit, QFileDialog,
    QMessageBox, QApplication, QStyle, QButtonGroup, QRadioButton,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QSpinBox, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDialogButtonBox, QProgressBar, QSlider, QGroupBox, QScrollArea,
    QGridLayout, QSpacerItem, QSizePolicy, QInputDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QEventLoop
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QClipboard, QPixmap
# from PyQt5.QtWebEngineWidgets import QWebEngineView  # 暂时注释掉，避免导入错误

# 导入自定义模块
from .widgets.code_editor import CodeEditor
from .widgets.json_highlighter import JsonHighlighter
from .widgets.request_editor import RequestEditor
from .widgets.loading_overlay import RespLoadingOverlay
from .utils.request_worker import RequestWorker
from .utils.multiprocess_worker import MultiprocessRequestWorker
from .utils.markdown_converter import MarkdownConverter
from .dialogs.about_dialog import AboutDialog
from .models.collection_manager import CollectionManager
from PyQt5.QtWidgets import QTabWidget
from ui.collection_tree_widget import CollectionTreeWidget


class MainWindow(QWidget):
    """主窗口 - 重构版本"""
    
    def __init__(self):
        super().__init__()
        self._req_thread = None  # 修复首次请求时的线程属性异常
        self._req_worker = None  # 修复首次请求时的工作器属性异常
        self._sending_request = False  # 修复发送状态属性异常
        self._workspace_dir = self.get_workspace_dir()
        self._app_icon = QIcon(self.get_icon_path())
        self.collection_manager = CollectionManager(self._workspace_dir)
        
        # 初始化成员变量
        self.req_tabs = None  # 修复：初始化为None而不是空字典
        self.current_worker = None
        self._unsaved_changes = False
        
        # 设置窗口属性
        self.setWindowTitle('postsuperman')
        self.resize(1440, 900)
        
        # 设置应用图标
        QApplication.setWindowIcon(self._app_icon)
        self.setWindowIcon(self._app_icon)
        
        self.init_logging()
        self.init_ui()
        self.load_collections()
        
    def get_workspace_dir(self):
        """获取工作目录，兼容开发环境和打包后的exe文件"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        
    def get_icon_path(self):
        """获取图标文件路径，兼容开发环境和打包后的exe文件"""
        if getattr(sys, 'frozen', False):
            return None
        else:
            return os.path.join(os.path.dirname(__file__), 'app.ico')
            
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 菜单栏
        self.create_menu_bar(main_layout)
        
        # 顶部导航栏
        self.create_top_bar(main_layout)
        
        # 主体分栏
        self.create_main_splitter(main_layout)
        
    def create_menu_bar(self, main_layout):
        """创建菜单栏"""
        menubar = QMenuBar(self)
        
        # File菜单
        file_menu = menubar.addMenu('File')
        new_request_action = QAction('New Request', self)
        new_collection_action = QAction('New Collection', self)
        open_collection_action = QAction('Open Collection', self)
        save_collection_as_action = QAction('Save Collection As', self)
        save_all_action = QAction('Save All', self)
        exit_action = QAction('Exit', self)
        
        file_menu.addAction(new_request_action)
        file_menu.addAction(new_collection_action)
        file_menu.addSeparator()
        file_menu.addAction(open_collection_action)
        file_menu.addSeparator()
        file_menu.addAction(save_collection_as_action)
        file_menu.addAction(save_all_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Help菜单
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        doc_action = QAction('Documentation', self)
        contact_action = QAction('Contact Me', self)
        
        help_menu.addAction(about_action)
        help_menu.addAction(doc_action)
        help_menu.addAction(contact_action)
        
        # 连接信号
        new_request_action.triggered.connect(self.create_new_request)
        new_collection_action.triggered.connect(self.create_collection)
        open_collection_action.triggered.connect(self.open_collection)
        save_collection_as_action.triggered.connect(self.save_collection_as)
        save_all_action.triggered.connect(self.save_all)
        exit_action.triggered.connect(self.close)
        about_action.triggered.connect(self.show_about)
        doc_action.triggered.connect(self.show_doc)
        contact_action.triggered.connect(self.show_contact)
        
        main_layout.setMenuBar(menubar)
        
    def create_top_bar(self, main_layout):
        """创建顶部导航栏"""
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
        
    def create_main_splitter(self, main_layout):
        """创建主体分割器"""
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)
        
        # 右侧主区
        self.right_widget = self.create_right_panel()
        splitter.addWidget(self.right_widget)
        
        # 设置分割器大小
        splitter.setSizes([260, 1180])
        main_layout.addWidget(splitter)
        
    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # 左侧Tab栏
        self.left_tab = QTabWidget()
        self.left_tab.setTabPosition(QTabWidget.North)
        self.left_tab.setObjectName('LeftTab')
        
        # 图标
        folder_icon = QApplication.style().standardIcon(QStyle.SP_DirClosedIcon)
        file_icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
        self.folder_icon = folder_icon
        self.file_icon = file_icon
        
        # Collections Tab
        collections_panel = self.create_collections_panel()
        self.left_tab.addTab(collections_panel, 'Collections')
        
        # Environments Tab
        self.env_list = QListWidget()
        self.left_tab.addTab(self.env_list, 'Environments')
        
        # History Tab
        self.history_list = QListWidget()
        self.left_tab.addTab(self.history_list, 'History')
        
        left_layout.addWidget(self.left_tab)
        left_widget.setMinimumWidth(200)
        left_widget.setMaximumWidth(500)
        
        return left_widget
        
    def create_collections_panel(self):
        """创建集合面板"""
        collections_panel = QWidget()
        collections_layout = QVBoxLayout(collections_panel)
        collections_layout.setContentsMargins(0, 0, 0, 0)
        collections_layout.setSpacing(4)
        
        self.collection_tree = CollectionTreeWidget()
        self.collection_tree._main_window = self  # 注入主窗口引用
        self.collection_tree.setHeaderHidden(True)
        self.collection_tree.setDragDropMode(self.collection_tree.DragDrop)
        self.collection_tree.setDefaultDropAction(Qt.MoveAction)
        self.collection_tree.setSelectionMode(self.collection_tree.SingleSelection)
        self.collection_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.collection_tree.setDragEnabled(True)
        self.collection_tree.setAcceptDrops(True)
        
        # 默认集合
        root = QTreeWidgetItem(self.collection_tree, ['Default Collection'])
        root.setIcon(0, self.folder_icon)
        demo_req = QTreeWidgetItem(root, ['GET Example Request'])
        demo_req.setIcon(0, self.file_icon)
        
        collections_layout.addWidget(self.collection_tree)
        
        # 连接信号
        self.collection_tree.customContextMenuRequested.connect(self.show_collection_menu)
        self.collection_tree.itemDoubleClicked.connect(self.on_collection_item_double_clicked)
        self.collection_tree.itemClicked.connect(self.on_collection_item_clicked)
        
        return collections_panel
        
    def create_right_panel(self):
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 欢迎页
        self.welcome_page = self.create_welcome_page()
        right_layout.addWidget(self.welcome_page)
        
        return right_widget
        
    def create_welcome_page(self):
        """创建统一的欢迎页"""
        welcome_page = QWidget()
        welcome_page.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: none;
            }
        """)
        
        welcome_vbox = QVBoxLayout(welcome_page)
        welcome_vbox.setAlignment(Qt.AlignCenter)
        welcome_vbox.setSpacing(30)
        welcome_vbox.setContentsMargins(40, 40, 40, 40)
        
        # 应用图标
        icon_label = QLabel()
        icon_pixmap = self._app_icon.pixmap(96, 96)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        welcome_vbox.addWidget(icon_label)
        
        # 主标题
        title_label = QLabel('Welcome to PostSuperman')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                background: transparent;
                border: none;
            }
        """)
        welcome_vbox.addWidget(title_label)
        
        # 描述文本
        desc_label = QLabel('Click on collections or create new requests to start your API debugging journey.\n\nSupports multi-tabs, parameter/header/body editing, cURL import, \n\nresponse highlighting, collection management and other rich features.')
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                background: transparent;
                border: none;
                line-height: 1.6;
            }
        """)
        welcome_vbox.addWidget(desc_label)
        
        return welcome_page
        
    def init_logging(self):
        """初始化日志系统"""
        log_file = os.path.join(self._workspace_dir, 'postsuperman.log')
        
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('postsuperman')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        
        self.logger.info('=' * 50)
        self.logger.info('postsuperman 应用启动')
        self.logger.info(f'工作目录: {self._workspace_dir}')
        self.logger.info(f'日志文件: {log_file}')
        self.logger.info('=' * 50)
        
    def log_info(self, message):
        """记录信息日志"""
        if hasattr(self, 'logger'):
            self.logger.info(message)
            
    def log_warning(self, message):
        """记录警告日志"""
        if hasattr(self, 'logger'):
            self.logger.warning(message)
            
    def log_error(self, message):
        """记录错误日志"""
        if hasattr(self, 'logger'):
            self.logger.error(message)
            
    def log_debug(self, message):
        """记录调试日志"""
        if hasattr(self, '_logger'):
            self._logger.debug(message)
            
    def check_memory_usage(self):
        """检查内存使用情况"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            print(f"内存使用: {memory_mb:.2f} MB")
            return memory_mb
        except Exception as e:
            print(f"检查内存使用出错: {e}")
            return 0
            
    def ensure_req_tabs(self):
        """确保请求Tab区域已创建"""
        # 检查是否需要创建UI
        need_create = False
        if not hasattr(self, 'req_tabs') or self.req_tabs is None:
            need_create = True
        else:
            try:
                _ = self.req_tabs.count()
            except Exception:
                need_create = True
        
        if need_create:
            # 彻底移除并销毁欢迎页，防止QBasicTimer警告
            if hasattr(self, 'welcome_page') and self.welcome_page is not None:
                self.right_widget.layout().removeWidget(self.welcome_page)
                self.welcome_page.deleteLater()
                self.welcome_page = None
            
            # 创建请求Tab和响应区
            vertical_splitter = QSplitter(Qt.Vertical)
            self.req_tabs = QTabWidget()
            self.req_tabs.setObjectName('RequestTabs')
            self.req_tabs.setTabsClosable(True)
            self.req_tabs.currentChanged.connect(self.on_req_tab_changed)
            self.req_tabs.tabCloseRequested.connect(self.on_req_tab_closed)
            # 添加右键菜单支持
            self.req_tabs.setContextMenuPolicy(Qt.CustomContextMenu)
            self.req_tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
            
            # 响应区容器
            self.resp_container = QWidget()
            self.resp_container_layout = QVBoxLayout(self.resp_container)
            self.resp_container_layout.setContentsMargins(0, 0, 0, 0)
            self.resp_container_layout.setSpacing(0)
            
            # 响应区映射表
            self.response_widgets = {}  # tab_index -> response_widget
            
            vertical_splitter.addWidget(self.req_tabs)
            vertical_splitter.addWidget(self.resp_container)
            vertical_splitter.setSizes([500, 300])
            
            # 添加到右侧主区
            layout = self.right_widget.layout()
            layout.addWidget(vertical_splitter)
            self.vertical_splitter = vertical_splitter

    def create_response_widget(self, tab_index):
        """为指定的Tab创建Response区域"""
        # 响应区卡片
        resp_card = QFrame()
        resp_card.setObjectName('ResponseCard')
        resp_card_layout = QVBoxLayout(resp_card)
        resp_card_layout.setContentsMargins(16, 8, 16, 8)
        resp_card_layout.setSpacing(8)
        
        # Response Tabs
        resp_tabs = QTabWidget()
        resp_tabs.setObjectName('RespTabs')
        
        # Body Tab
        resp_body_widget = QWidget()
        resp_body_layout = QVBoxLayout(resp_body_widget)
        resp_body_layout.setContentsMargins(0, 0, 0, 0)
        resp_body_layout.setSpacing(4)
        
        # 状态栏
        resp_status_label = QLineEdit('Click Send to get a response')
        resp_status_label.setReadOnly(True)
        resp_status_label.setFrame(False)
        resp_status_label.setStyleSheet('background: transparent; border: none; font-weight: bold; color: #333;')
        
        status_row = QHBoxLayout()
        status_row.addWidget(resp_status_label)
        status_row.addStretch()
        
        save_resp_btn = QPushButton('Save Response to File')
        clear_resp_btn = QPushButton('Clear Response')
        status_row.addWidget(save_resp_btn)
        status_row.addWidget(clear_resp_btn)
        resp_body_layout.addLayout(status_row)
        
        # Response Body编辑器
        resp_body_edit = CodeEditor()
        resp_body_edit.setReadOnly(True)
        resp_json_highlighter = JsonHighlighter(resp_body_edit.document())
        resp_body_layout.addWidget(resp_body_edit)
        resp_body_widget.setLayout(resp_body_layout)
        resp_tabs.addTab(resp_body_widget, 'Body')
        
        # Headers Tab
        resp_headers_widget = QTextEdit()
        resp_headers_widget.setReadOnly(True)
        resp_tabs.addTab(resp_headers_widget, 'Headers')
        resp_card_layout.addWidget(resp_tabs)
        resp_card.setLayout(resp_card_layout)
        
        # Loading Overlay
        resp_loading_overlay = RespLoadingOverlay(resp_card, mainwin=self)
        
        # 连接按钮事件
        save_resp_btn.clicked.connect(lambda: self.save_response_to_file(tab_index))
        clear_resp_btn.clicked.connect(lambda: self.clear_response(tab_index))
        
        # 返回Response组件字典
        return {
            'card': resp_card,
            'tabs': resp_tabs,
            'status_label': resp_status_label,
            'body_edit': resp_body_edit,
            'headers_widget': resp_headers_widget,
            'loading_overlay': resp_loading_overlay,
            'save_btn': save_resp_btn,
            'clear_btn': clear_resp_btn
        }

    def show_response_for_tab(self, tab_index):
        """显示指定Tab对应的Response区域"""
        if not hasattr(self, 'response_widgets'):
            return
            
        # 清除当前显示的所有Response区域
        for i in range(self.resp_container_layout.count()):
            widget = self.resp_container_layout.itemAt(i).widget()
            if widget:
                self.resp_container_layout.removeWidget(widget)
                widget.hide()
        
        # 显示对应Tab的Response
        if tab_index in self.response_widgets:
            response_widget = self.response_widgets[tab_index]
            self.resp_container_layout.addWidget(response_widget['card'])
            response_widget['card'].show()
        else:
            # 如果该Tab还没有Response，创建一个
            response_widget = self.create_response_widget(tab_index)
            self.response_widgets[tab_index] = response_widget
            self.resp_container_layout.addWidget(response_widget['card'])
            response_widget['card'].show()

    def remove_response_for_tab(self, tab_index):
        """移除指定Tab对应的Response区域"""
        if hasattr(self, 'response_widgets') and tab_index in self.response_widgets:
            response_widget = self.response_widgets[tab_index]
            # 从容器中移除
            self.resp_container_layout.removeWidget(response_widget['card'])
            response_widget['card'].deleteLater()
            # 从映射表中移除
            del self.response_widgets[tab_index]
            
            # 如果还有其他Tab，显示第一个Tab的Response
            if self.req_tabs.count() > 0:
                current_index = self.req_tabs.currentIndex()
                if current_index >= 0:
                    self.show_response_for_tab(current_index)
            else:
                # 没有Tab了，显示欢迎页
                self.check_and_show_welcome_page()

    # 核心功能实现
    def create_new_request(self):
        """从File菜单创建新请求"""
        # 弹出对话框让用户输入Request名称
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        # 获取当前选中的项
        selected_item = self.collection_tree.currentItem()
        
        # 如果选中的是Request节点，弹出提示
        if selected_item and selected_item.childCount() == 0 and selected_item.parent() is not None:
            QMessageBox.information(
                self,
                'Cannot Create Request',
                'Cannot create a request under another request.\n\nPlease select a collection or no item to create a new request.'
            )
            return
        
        request_name, ok = QInputDialog.getText(
            self, 
            'New Request', 
            'Enter request name:',
            text='New Request'
        )
        
        if not ok or not request_name.strip():
            return  # 用户取消或输入为空
        
        # 检查名称是否重复
        def check_name_exists(parent_item, name):
            for i in range(parent_item.childCount()):
                if parent_item.child(i).text(0) == name:
                    return True
            return False
        
        # 获取父Collection
        parent_collection = None
        
        if selected_item:
            # 如果选中的是Collection，直接使用
            if selected_item.childCount() > 0:
                parent_collection = selected_item
            # 如果选中的是Request，使用其父Collection（这种情况不应该发生，因为前面已经检查过了）
            elif selected_item.parent() is not None:
                parent_collection = selected_item.parent()
        
        # 如果没有选中任何Collection，查找或创建默认Collection
        if parent_collection is None:
            for i in range(self.collection_tree.topLevelItemCount()):
                item = self.collection_tree.topLevelItem(i)
                if item.text(0) == 'Default Collection':
                    parent_collection = item
                    break
            
            # 如果没有默认Collection，创建一个
            if parent_collection is None:
                parent_collection = QTreeWidgetItem(['Default Collection'])
                parent_collection.setIcon(0, self.folder_icon)
                self.collection_tree.addTopLevelItem(parent_collection)
        
        # 检查名称是否在父Collection中重复
        if check_name_exists(parent_collection, request_name):
            QMessageBox.warning(
                self, 
                'Duplicate Name', 
                f'A request named "{request_name}" already exists in this collection!'
            )
            return
        
        # 确保请求区域已创建
        self.ensure_req_tabs()
        
        # 生成包含Collection路径的Tab标签
        def get_collection_path(parent_collection):
            path_parts = []
            current = parent_collection
            while current is not None:
                path_parts.insert(0, current.text(0))
                current = current.parent()
            return '/'.join(path_parts)
        
        collection_path = get_collection_path(parent_collection)
        full_request_path = f"{collection_path}/{request_name}"
        
        # 创建新的请求编辑器
        from ui.widgets.request_editor import RequestEditor
        req_editor = RequestEditor(self, req_name=request_name)
        tab_index = self.req_tabs.addTab(req_editor, full_request_path)
        self.req_tabs.setCurrentWidget(req_editor)
        
        # 为新Tab创建Response区域
        self.show_response_for_tab(tab_index)
        
        # 自动保存新请求到collections.json
        self.save_new_request_to_collections(req_editor, request_name, parent_collection)
        
        # 在树中选中新创建的Request
        new_request_item = None
        for i in range(parent_collection.childCount()):
            child = parent_collection.child(i)
            if child.text(0) == request_name:
                new_request_item = child
                break
        
        if new_request_item:
            self.collection_tree.setCurrentItem(new_request_item)
            self.collection_tree.scrollToItem(new_request_item)
        
        self.log_info(f'Create new request "{request_name}" in collection: {parent_collection.text(0)}')

    def save_new_request_to_collections(self, req_editor, request_name, parent_collection):
        self.ensure_req_tabs()
        """将新创建的请求保存到collections.json"""
        # 获取请求数据
        req_data = req_editor.serialize_request()
        
        # 创建树节点
        new_item = QTreeWidgetItem([request_name])
        new_item.setIcon(0, self.file_icon)
        new_item.setData(0, Qt.UserRole, req_data)
        
        if parent_collection:
            # 添加到父集合
            parent_collection.addChild(new_item)
            parent_collection.setExpanded(True)
        else:
            # 这种情况不应该发生，因为前面已经确保了parent_collection存在
            self.log_error('No parent collection found for new request')
            return
        
        # 保存到collections.json
        self.save_all()
        self.log_info(f'Save new request "{request_name}" to collection: {parent_collection.text(0)}')

    def on_collection_item_clicked(self, item, column):
        """集合项单击事件"""
        # 判断是否为Request节点
        if item.childCount() == 0 and item.parent() is not None and item.icon(0).cacheKey() == self.file_icon.cacheKey():
            # 这是Request节点，需要创建Tab
            self.ensure_req_tabs()
            
            # 生成包含Collection路径的唯一标识
            def get_request_path(item):
                path_parts = []
                current = item
                while current is not None:
                    path_parts.insert(0, current.text(0))
                    current = current.parent()
                return '/'.join(path_parts)
            
            request_path = get_request_path(item)
            request_name = item.text(0)
            
            # 检查是否已存在相同路径的Tab
            for i in range(self.req_tabs.count()):
                if self.req_tabs.tabText(i) == request_path:
                    self.req_tabs.setCurrentIndex(i)
                    return
            req_data = self.get_request_data_from_tree(item)
            req_editor = RequestEditor(self, req_name=request_name)
            if req_data:
                req_editor.method_combo.setCurrentText(req_data.get('method', 'GET'))
                req_editor.url_edit.setText(req_data.get('url', ''))
                # Params
                req_editor.params_table.setRowCount(1)
                for i, param in enumerate(req_data.get('params', [])):
                    if i >= req_editor.params_table.rowCount()-1:
                        req_editor.params_table.insertRow(req_editor.params_table.rowCount())
                        req_editor.add_table_row(req_editor.params_table, req_editor.params_table.rowCount()-1)
                    req_editor.params_table.setItem(i, 1, QTableWidgetItem(param.get('key', '')))
                    req_editor.params_table.setItem(i, 2, QTableWidgetItem(param.get('value', '')))
                # Headers
                req_editor.headers_table.setRowCount(1)
                for i, h in enumerate(req_data.get('headers', [])):
                    if i >= req_editor.headers_table.rowCount()-1:
                        req_editor.headers_table.insertRow(req_editor.headers_table.rowCount())
                        req_editor.add_table_row(req_editor.headers_table, req_editor.headers_table.rowCount()-1)
                    req_editor.headers_table.setItem(i, 1, QTableWidgetItem(h.get('key', '')))
                    req_editor.headers_table.setItem(i, 2, QTableWidgetItem(h.get('value', '')))
                req_editor.refresh_table_widgets(req_editor.headers_table)
                # Body
                body_type = req_data.get('body_type', 'none')
                if body_type == 'form-data':
                    req_editor.body_form_radio.setChecked(True)
                    req_editor.form_table.setRowCount(1)
                    for i, item in enumerate(req_data.get('body', [])):
                        if i >= req_editor.form_table.rowCount()-1:
                            req_editor.form_table.insertRow(req_editor.form_table.rowCount())
                            req_editor.add_table_row(req_editor.form_table, req_editor.form_table.rowCount()-1)
                        req_editor.form_table.setItem(i, 1, QTableWidgetItem(item.get('key', '')))
                        req_editor.form_table.setItem(i, 2, QTableWidgetItem(item.get('value', '')))
                elif body_type == 'x-www-form-urlencoded':
                    req_editor.body_url_radio.setChecked(True)
                    req_editor.url_table.setRowCount(1)
                    for i, item in enumerate(req_data.get('body', [])):
                        if i >= req_editor.url_table.rowCount()-1:
                            req_editor.url_table.insertRow(req_editor.url_table.rowCount())
                            req_editor.add_table_row(req_editor.url_table, req_editor.url_table.rowCount()-1)
                        req_editor.url_table.setItem(i, 1, QTableWidgetItem(item.get('key', '')))
                        req_editor.url_table.setItem(i, 2, QTableWidgetItem(item.get('value', '')))
                elif body_type == 'raw':
                    req_editor.body_raw_radio.setChecked(True)
                    req_editor.raw_text_edit.setPlainText(req_data.get('body', ''))
                    req_editor.raw_type_combo.setCurrentText(req_data.get('raw_type', 'JSON'))
                else:
                    req_editor.body_none_radio.setChecked(True)
            self.req_tabs.addTab(req_editor, request_path)
            tab_index = self.req_tabs.count() - 1  # 获取新添加的Tab索引
            self.req_tabs.setCurrentWidget(req_editor)
            
            # 为新Tab创建Response区域
            self.show_response_for_tab(tab_index)
        else:
            # 这是Collection节点，不创建Tab，只展开/折叠
            pass

    def get_request_data_from_tree(self, item):
        """从collections.json结构递归查找对应request数据"""
        # 从collections.json结构递归查找对应request数据
        def find_req(nodes, name):
            for node in nodes:
                if node.get('type') == 'request' and node.get('name') == name:
                    return node.get('request', {})
                elif node.get('type') == 'collection':
                    result = find_req(node.get('children', []), name)
                    if result:
                        return result
            return None
        
        # 加载collections.json数据
        path = os.path.join(self._workspace_dir, 'collections.json')
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return find_req(data, item.text(0))
        except Exception:
            return None

    def send_request(self, editor=None):
        """发送请求 - threading版本"""
        try:
            self.ensure_req_tabs()
            
            # 检查发送状态
            if self._sending_request:
                print("已有请求正在发送中，忽略此次点击")
                return
                
            if editor is None:
                editor = self.req_tabs.currentWidget()
            if editor is None:
                self.log_warning('未找到请求编辑器')
                return
                
            print("开始发送新请求...")
            # 清理之前的请求
            if hasattr(self, '_req_worker') and self._req_worker:
                print("停止之前的请求")
                self._req_worker.stop()
                self._req_worker.cleanup()  # 手动清理资源
            self._req_worker = None
            self._sending_request = True
            
            # 立即更新按钮状态：Send变灰，Stop可用
            if hasattr(editor, 'send_btn'):
                print("立即禁用Send按钮")
                editor.send_btn.setEnabled(False)
            if hasattr(editor, 'stop_btn'):
                print("立即启用Stop按钮")
                editor.stop_btn.setEnabled(True)
                
            self.log_info(f'发送HTTP请求: {editor.method_combo.currentText()} {editor.url_edit.text().strip()}')
            
            # 拼接Params
            params = []
            for i in range(editor.params_table.rowCount()):
                key_item = editor.params_table.item(i, 1)
                value_item = editor.params_table.item(i, 2)
                if key_item and value_item:
                    key = key_item.text().strip()
                    value = value_item.text().strip()
                    if key:
                        params.append({'key': key, 'value': value})
            # 拼接Headers
            headers = []
            for i in range(editor.headers_table.rowCount()):
                key_item = editor.headers_table.item(i, 1)
                value_item = editor.headers_table.item(i, 2)
                if key_item and value_item:
                    key = key_item.text().strip()
                    value = value_item.text().strip()
                    if key:
                        headers.append({'key': key, 'value': value})
            # 处理Body
            data = None
            json_data = None
            files = None
            if editor.body_none_radio.isChecked():
                pass
            elif editor.body_form_radio.isChecked():
                data = {}
                for i in range(editor.form_table.rowCount()):
                    key_item = editor.form_table.item(i, 1)
                    value_item = editor.form_table.item(i, 2)
                    if key_item and value_item:
                        key = key_item.text().strip()
                        value = value_item.text().strip()
                        if key:
                            data[key] = value
            elif editor.body_url_radio.isChecked():
                data = {}
                for i in range(editor.url_table.rowCount()):
                    key_item = editor.url_table.item(i, 1)
                    value_item = editor.url_table.item(i, 2)
                    if key_item and value_item:
                        key = key_item.text().strip()
                        value = value_item.text().strip()
                        if key:
                            data[key] = value
            elif editor.body_raw_radio.isChecked():
                raw_text = editor.raw_text_edit.toPlainText().strip()
                if raw_text:
                    raw_type = editor.raw_type_combo.currentText()
                    if raw_type == 'JSON':
                        try:
                            json_data = json.loads(raw_text)
                        except:
                            data = raw_text
                    else:
                        data = raw_text
            # 显示加载动画
            current_tab_index = self.req_tabs.currentIndex()
            if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                overlay = self.response_widgets[current_tab_index]['loading_overlay']
                overlay.setGeometry(0, 0, overlay.parent().width(), overlay.parent().height())
                overlay.raise_()
                overlay.setVisible(True)
                QApplication.processEvents()
            
            # 创建新的请求工作器
            self._req_worker = RequestWorker(editor.method_combo.currentText(), editor.url_edit.text().strip(), params, headers, data, json_data, files)
            
            # 连接信号
            self._req_worker.finished.connect(self.on_request_finished)
            self._req_worker.error.connect(self.on_request_error)
            self._req_worker.stopped.connect(self.on_request_stopped)
            print("信号连接成功")
            
            # 启动请求线程
            self._req_worker.start()
            self._current_editor = editor
            print("请求已发送，等待服务器响应...")
                
        except Exception as e:
            print(f"send_request 出现异常: {e}")
            # 确保按钮状态恢复
            self._sending_request = False
            if editor and hasattr(editor, 'send_btn'):
                editor.send_btn.setEnabled(True)
            if editor and hasattr(editor, 'stop_btn'):
                editor.stop_btn.setEnabled(False)
            if hasattr(self, 'resp_loading_overlay'):
                self.resp_loading_overlay.setVisible(False)

    def on_request_finished(self, result):
        """请求完成处理 - 最简单版本"""
        try:
            print("处理请求完成")
            self._sending_request = False
            
            # 检查内存使用
            self.check_memory_usage()
            
            # 获取当前Tab索引
            current_tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
            
            # 确保遮罩层被隐藏
            try:
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    overlay = self.response_widgets[current_tab_index]['loading_overlay']
                    overlay.setVisible(False)
            except Exception as e:
                print(f"隐藏遮罩层时出错: {e}")
            
            # 恢复所有可能的Send按钮
            try:
                current_editor = self.req_tabs.currentWidget() if hasattr(self, 'req_tabs') and self.req_tabs else None
                if current_editor and hasattr(current_editor, 'send_btn'):
                    print("恢复当前编辑器的Send按钮")
                    current_editor.send_btn.setEnabled(True)
                if current_editor and hasattr(current_editor, 'stop_btn'):
                    current_editor.stop_btn.setEnabled(False)
                if hasattr(self, '_current_editor') and self._current_editor and hasattr(self._current_editor, 'send_btn'):
                    print("恢复保存的当前编辑器的Send按钮")
                    self._current_editor.send_btn.setEnabled(True)
                if hasattr(self, 'req_tabs') and self.req_tabs:
                    for i in range(self.req_tabs.count()):
                        widget = self.req_tabs.widget(i)
                        if hasattr(widget, 'send_btn'):
                            print(f"恢复标签页 {i} 的Send按钮")
                            widget.send_btn.setEnabled(True)
            except Exception as e:
                print(f"恢复按钮状态时出错: {e}")
            
            # 不清理线程，让它自然结束
            self._req_worker = None
            self._current_editor = None
            
            # 处理 RequestWorker 返回的结果格式
            try:
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    response_widget = self.response_widgets[current_tab_index]
                    status_code = result.get('status_code', 0)
                    status_text = result.get('status_text', 'Unknown')
                    elapsed = result.get('elapsed', 0) * 1000
                    body = result.get('body', '')
                    headers = result.get('headers', {})
                    self._last_response_bytes = body.encode('utf-8') if body else b''
                    status = f'{status_text}   {elapsed:.0f}ms   {len(self._last_response_bytes)/1024:.2f}KB'
                    self.log_info(f'HTTP请求完成: {status_text} - 耗时: {elapsed:.0f}ms - 大小: {len(self._last_response_bytes)/1024:.2f}KB')
                    
                    try:
                        content_type = headers.get('Content-Type', '')
                        if 'application/json' in content_type:
                            obj = json.loads(body)
                            body = json.dumps(obj, ensure_ascii=False, indent=2)
                            # 重新设置JSON高亮
                            from ui.widgets.json_highlighter import JsonHighlighter
                            response_widget['body_edit'].document().setPlainText(body)
                            highlighter = JsonHighlighter(response_widget['body_edit'].document())
                        else:
                            response_widget['body_edit'].setPlainText(body)
                    except Exception:
                        response_widget['body_edit'].setPlainText(body)
                    
                    headers_str = '\n'.join(f'{k}: {v}' for k, v in headers.items())
                    response_widget['status_label'].setText(status)
                    response_widget['headers_widget'].setPlainText(headers_str)
                    response_widget['tabs'].setCurrentIndex(0)
            except Exception as e:
                print(f"处理响应结果时出错: {e}")
        except Exception as e:
            print(f"on_request_finished 出现异常: {e}")
            try:
                self._sending_request = False
                current_tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    overlay = self.response_widgets[current_tab_index]['loading_overlay']
                    overlay.setVisible(False)
                current_editor = self.req_tabs.currentWidget() if hasattr(self, 'req_tabs') and self.req_tabs else None
                if current_editor and hasattr(current_editor, 'send_btn'):
                    current_editor.send_btn.setEnabled(True)
                if current_editor and hasattr(current_editor, 'stop_btn'):
                    current_editor.stop_btn.setEnabled(False)
            except Exception as cleanup_error:
                print(f"清理异常状态时出错: {cleanup_error}")

    def on_request_error(self, msg):
        """请求错误处理 - 最简单版本"""
        try:
            print(f"处理请求错误: {msg}")
            self._sending_request = False
            
            # 获取当前Tab索引
            current_tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
            
            try:
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    overlay = self.response_widgets[current_tab_index]['loading_overlay']
                    overlay.setVisible(False)
            except Exception as e:
                print(f"隐藏遮罩层时出错: {e}")
                
            try:
                current_editor = self.req_tabs.currentWidget() if hasattr(self, 'req_tabs') and self.req_tabs else None
                if current_editor and hasattr(current_editor, 'send_btn'):
                    print("恢复当前编辑器的Send按钮")
                    current_editor.send_btn.setEnabled(True)
                if current_editor and hasattr(current_editor, 'stop_btn'):
                    current_editor.stop_btn.setEnabled(False)
                if hasattr(self, '_current_editor') and self._current_editor and hasattr(self._current_editor, 'send_btn'):
                    print("恢复保存的当前编辑器的Send按钮")
                    self._current_editor.send_btn.setEnabled(True)
                if hasattr(self, 'req_tabs') and self.req_tabs:
                    for i in range(self.req_tabs.count()):
                        widget = self.req_tabs.widget(i)
                        if hasattr(widget, 'send_btn'):
                            print(f"恢复标签页 {i} 的Send按钮")
                            widget.send_btn.setEnabled(True)
            except Exception as e:
                print(f"恢复按钮状态时出错: {e}")
                
            # 不清理线程，让它自然结束
            self._req_worker = None
            self._current_editor = None
            
            try:
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    response_widget = self.response_widgets[current_tab_index]
                    response_widget['status_label'].setText(f'Error: {msg}')
                    response_widget['body_edit'].setPlainText(f'Request failed: {msg}')
                    response_widget['tabs'].setCurrentIndex(0)
            except Exception as e:
                print(f"显示错误信息时出错: {e}")
        except Exception as e:
            print(f"on_request_error 出现异常: {e}")
            try:
                self._sending_request = False
                current_tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    overlay = self.response_widgets[current_tab_index]['loading_overlay']
                    overlay.setVisible(False)
                current_editor = self.req_tabs.currentWidget() if hasattr(self, 'req_tabs') and self.req_tabs else None
                if current_editor and hasattr(current_editor, 'send_btn'):
                    current_editor.send_btn.setEnabled(True)
                if current_editor and hasattr(current_editor, 'stop_btn'):
                    current_editor.stop_btn.setEnabled(False)
            except Exception as cleanup_error:
                print(f"清理异常状态时出错: {cleanup_error}")

    def on_request_stopped(self):
        """请求停止处理 - 最简单版本"""
        try:
            print("处理请求停止")
            self._sending_request = False
            
            # 获取当前Tab索引
            current_tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
            
            # 立即恢复Send按钮状态
            try:
                current_editor = self.req_tabs.currentWidget() if hasattr(self, 'req_tabs') and self.req_tabs else None
                if current_editor and hasattr(current_editor, 'send_btn'):
                    print("立即恢复当前编辑器的Send按钮")
                    current_editor.send_btn.setEnabled(True)
                if current_editor and hasattr(current_editor, 'stop_btn'):
                    current_editor.stop_btn.setEnabled(False)
                    
                # 恢复所有标签页的Send按钮
                if hasattr(self, 'req_tabs') and self.req_tabs:
                    for i in range(self.req_tabs.count()):
                        widget = self.req_tabs.widget(i)
                        if hasattr(widget, 'send_btn'):
                            print(f"立即恢复标签页 {i} 的Send按钮")
                            widget.send_btn.setEnabled(True)
            except Exception as e:
                print(f"恢复按钮状态时出错: {e}")
            
            # 确保遮罩层被隐藏
            try:
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    overlay = self.response_widgets[current_tab_index]['loading_overlay']
                    overlay.setVisible(False)
            except Exception as e:
                print(f"隐藏遮罩层时出错: {e}")
                
            # 不清理线程，让它自然结束
            self._req_worker = None
            self._current_editor = None
            
            print("请求停止处理完成")
            print("Send按钮已立即恢复，可以再次点击")
            print("程序继续运行...")
        except Exception as e:
            print(f"处理请求停止时出错: {e}")
            try:
                current_tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
                if current_tab_index >= 0 and current_tab_index in self.response_widgets:
                    overlay = self.response_widgets[current_tab_index]['loading_overlay']
                    overlay.setVisible(False)
            except Exception as cleanup_error:
                print(f"清理异常状态时出错: {cleanup_error}")

    def save_response_to_file(self, tab_index=None):
        """保存响应到文件"""
        if tab_index is None:
            tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
            
        if tab_index < 0 or tab_index not in self.response_widgets:
            QMessageBox.warning(self, 'No Response', '没有找到对应的响应区域！')
            return
            
        response_widget = self.response_widgets[tab_index]
        body_edit = response_widget['body_edit']
        
        # 获取响应内容
        text = body_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, 'No Response', '响应体为空，无法保存！')
            return
            
        fname, _ = QFileDialog.getSaveFileName(self, 'Save Response', '', 'All Files (*)')
        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.log_info(f'Saved response to file: {fname}')
            except Exception as e:
                QMessageBox.warning(self, 'Save Failed', f'保存失败: {e}')

    def clear_response(self, tab_index=None):
        """清除响应"""
        if tab_index is None:
            tab_index = self.req_tabs.currentIndex() if hasattr(self, 'req_tabs') else -1
            
        if tab_index < 0 or tab_index not in self.response_widgets:
            return
            
        response_widget = self.response_widgets[tab_index]
        body_edit = response_widget['body_edit']
        status_label = response_widget['status_label']
        headers_widget = response_widget['headers_widget']
        tabs = response_widget['tabs']
        
        body_edit.clear()
        status_label.setText('Click Send to get a response')
        tabs.setTabText(0, 'Body')
        headers_widget.setPlainText('')

    def on_req_tab_changed(self, idx):
        self.ensure_req_tabs()
        """请求标签页改变事件"""
        if idx >= 0 and hasattr(self, 'req_tabs'):
            # 切换Response区域
            self.show_response_for_tab(idx)
            
            current_editor = self.req_tabs.widget(idx)
            if current_editor:
                # 在集合树中选中对应的请求
                def find_and_select(item):
                    for i in range(item.childCount()):
                        child = item.child(i)
                        if child.childCount() == 0:  # request
                            if child.text(0) == current_editor.req_name:
                                self.collection_tree.setCurrentItem(child)
                                return True
                        else:  # collection
                            if find_and_select(child):
                                return True
                    return False
                
                for i in range(self.collection_tree.topLevelItemCount()):
                    if find_and_select(self.collection_tree.topLevelItem(i)):
                        break

    def on_req_tab_closed(self, idx):
        """Tab关闭事件"""
        # 移除对应的Response区域
        self.remove_response_for_tab(idx)
        
        # 移除Tab
        self.req_tabs.removeTab(idx)
        
        # 检查是否还有Tab
        if self.req_tabs.count() == 0:
            # 没有Tab了，显示欢迎页
            self.check_and_show_welcome_page()

    def show_tab_context_menu(self, pos):
        self.ensure_req_tabs()
        """显示标签页右键菜单"""
        menu = QMenu(self)
        
        close_action = menu.addAction('Close Tab')
        close_other_action = menu.addAction('Close Other Tabs')
        close_all_action = menu.addAction('Close All Tabs')
        
        action = menu.exec_(self.req_tabs.mapToGlobal(pos))
        
        if action == close_action:
            self.close_tab_with_confirm(self.req_tabs.currentIndex())
        elif action == close_other_action:
            self.close_other_tabs(self.req_tabs.currentIndex())
        elif action == close_all_action:
            self.close_all_tabs()

    def close_tab_with_confirm(self, tab_index):
        self.ensure_req_tabs()
        """确认关闭标签页"""
        if tab_index >= 0:
            self.req_tabs.removeTab(tab_index)

    def close_other_tabs(self, keep_index):
        self.ensure_req_tabs()
        """关闭其他标签页"""
        for i in range(self.req_tabs.count() - 1, -1, -1):
            if i != keep_index:
                self.req_tabs.removeTab(i)

    def close_all_tabs(self):
        self.ensure_req_tabs()
        """关闭所有标签页"""
        self.req_tabs.clear()
        self.check_and_show_welcome_page()

    def check_and_show_welcome_page(self):
        self.ensure_req_tabs()
        """检查并显示欢迎页"""
        if self.req_tabs.count() == 0:
            # 移除请求区和响应区
            if hasattr(self, 'vertical_splitter') and self.vertical_splitter is not None:
                layout = self.right_widget.layout()
                layout.removeWidget(self.vertical_splitter)
                self.vertical_splitter.deleteLater()
                self.vertical_splitter = None
            # 重新显示欢迎页
            if not hasattr(self, 'welcome_page') or self.welcome_page is None:
                self.welcome_page = self.create_welcome_page()
            self.right_widget.layout().addWidget(self.welcome_page)

    def on_stop_request(self):
        """停止请求"""
        try:
            print("停止请求")
            # 调用RequestWorker的stop方法
            if hasattr(self, '_req_worker') and self._req_worker:
                print("调用RequestWorker.stop()")
                self._req_worker.stop()
            # 立即隐藏遮罩层
            if hasattr(self, 'resp_loading_overlay'):
                self.resp_loading_overlay.setVisible(False)
            print("停止请求完成")
        except Exception as e:
            print(f"停止请求时出错: {e}")
            
    def safe_stop_request(self):
        """安全的停止请求方法 - 快速恢复版本"""
        try:
            print("安全停止请求")
            # 立即重置发送状态
            self._sending_request = False
            print("重置发送状态为False")
            
            # 立即恢复Send按钮状态
            try:
                current_editor = self.req_tabs.currentWidget() if hasattr(self, 'req_tabs') and self.req_tabs else None
                if current_editor and hasattr(current_editor, 'send_btn'):
                    print("立即恢复Send按钮")
                    current_editor.send_btn.setEnabled(True)
                if current_editor and hasattr(current_editor, 'stop_btn'):
                    current_editor.stop_btn.setEnabled(False)
            except Exception as e:
                print(f"恢复按钮状态时出错: {e}")
            
            # 调用RequestWorker的stop方法
            if hasattr(self, '_req_worker') and self._req_worker:
                print("调用RequestWorker.stop()")
                self._req_worker.stop()
            # 立即隐藏遮罩层
            if hasattr(self, 'resp_loading_overlay'):
                self.resp_loading_overlay.setVisible(False)
            print("安全停止请求完成")
            print("Send按钮已立即恢复")
        except Exception as e:
            print(f"安全停止请求时出错: {e}")

    # 集合相关功能
    def load_collections(self):
        """加载集合数据"""
        path = os.path.join(self._workspace_dir, 'collections.json')
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.populate_collections(data)
            self.log_info("加载集合数据成功")
        except Exception as e:
            QMessageBox.warning(self, 'Load Failed', f'加载失败: {e}')
            self.log_error(f"加载集合数据失败: {e}")

    def populate_collections(self, data):
        """填充集合树"""
        self.collection_tree.clear()
        
        def add_items(parent, nodes):
            for node in nodes:
                item = QTreeWidgetItem(parent, [node['name']])
                if node.get('type') == 'collection':
                    item.setIcon(0, self.folder_icon)
                    add_items(item, node.get('children', []) or [])
                if node.get('type') == 'request':
                    item.setIcon(0, self.file_icon)
                    item.setData(0, Qt.UserRole, node.get('request', {}))
        
        add_items(self.collection_tree, data)

    def open_collection(self):
        """从File菜单打开集合文件"""
        fname, _ = QFileDialog.getOpenFileName(
            self, 
            'Open Collection', 
            '', 
            'JSON Files (*.json);;All Files (*)'
        )
        
        if not fname:
            return
            
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError('Collection file must contain a list of collections')
            
            choice = QMessageBox.question(
                self, 
                'Open Collection', 
                'Do you want to merge with existing collections or replace them?\n\n'
                'Yes = Merge with existing\n'
                'No = Replace existing',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if choice == QMessageBox.Cancel:
                return
            elif choice == QMessageBox.No:
                self.collection_tree.clear()
                self.populate_collections(data)
                self.log_info(f'Replace collections with: {fname}')
            else:
                self.merge_collections(data)
                self.log_info(f'Merge collections from: {fname}')
            
            self.save_all()
            
            QMessageBox.information(
                self, 
                'Success', 
                f'Successfully loaded collection from: {fname}'
            )
            
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'File not found!')
            self.log_error(f'Open collection failed: File not found - {fname}')
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, 'Error', f'Invalid JSON format: {e}')
            self.log_error(f'Open collection failed: Invalid JSON - {e}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load collection: {e}')
            self.log_error(f'Open collection failed: {e}')

    def merge_collections(self, new_data):
        """合并新集合到现有集合"""
        def add_collection_to_tree(parent, collection_data):
            for item in collection_data:
                if item.get('type') == 'collection':
                    collection_item = QTreeWidgetItem(parent, [item['name']])
                    collection_item.setIcon(0, self.folder_icon)
                    
                    if 'children' in item:
                        add_collection_to_tree(collection_item, item['children'])
                        
                elif item.get('type') == 'request':
                    request_item = QTreeWidgetItem(parent, [item['name']])
                    request_item.setIcon(0, self.file_icon)
                    if 'request' in item:
                        request_item.setData(0, Qt.UserRole, item['request'])
        
        add_collection_to_tree(self.collection_tree, new_data)

    def create_collection(self):
        """从File菜单创建新集合"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        from PyQt5.QtWidgets import QTreeWidgetItem
        from PyQt5.QtCore import Qt
        
        # 检查重复名称
        def is_duplicate(tree, name):
            for i in range(tree.topLevelItemCount()):
                if tree.topLevelItem(i).text(0) == name:
                    return True
            return False
        
        # 获取集合名称
        name, ok = QInputDialog.getText(self, 'Create Collection', 'Enter collection name:')
        if not ok or not name.strip():
            return
        
        name = name.strip()
        
        # 检查重复
        if is_duplicate(self.collection_tree, name):
            QMessageBox.warning(self, 'Error', f'Collection "{name}" already exists!')
            return
        
        # 创建集合节点
        collection_item = QTreeWidgetItem([name])
        collection_item.setIcon(0, self.folder_icon)
        self.collection_tree.addTopLevelItem(collection_item)
        
        # 保存到collections.json
        self.save_all()
        self.log_info(f'Create new collection: {name}')

    def save_collection_as(self):
        """从File菜单另存为集合文件"""
        if not hasattr(self, 'collection_tree') or self.collection_tree.topLevelItemCount() == 0:
            QMessageBox.information(self, 'No Collections', 'No collections to save. Please create some collections first.')
            return
        
        fname, _ = QFileDialog.getSaveFileName(
            self, 
            'Save Collection As', 
            'collections.json', 
            'JSON Files (*.json);;All Files (*)'
        )
        
        if not fname:
            return
            
        try:
            data = self.serialize_collections()
            
            if not data:
                QMessageBox.warning(self, 'No Data', 'No valid collection data to save.')
                return
            
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.log_info(f'Save collection as: {fname}')
            
            QMessageBox.information(
                self, 
                'Success', 
                f'Collection saved successfully to:\n{fname}'
            )
            
        except Exception as e:
            QMessageBox.warning(self, 'Save Failed', f'Failed to save collection: {e}')
            self.log_error(f'Save collection as failed: {e}')

    def serialize_collections(self):
        """序列化集合数据"""
        def serialize_item(item):
            # 用和 is_request 一样的逻辑判断
            def is_request(item):
                return (
                    item is not None and
                    item.childCount() == 0 and
                    item.parent() is not None and
                    item.icon(0).cacheKey() == self.file_icon.cacheKey()
                )
            if is_request(item):
                req_data = item.data(0, Qt.UserRole)
                if not req_data:
                    return None  # 未保存的request不导出
                return {
                    'name': item.text(0),
                    'type': 'request',
                    'request': req_data
                }
            else:
                # Collection节点，即使没有子项也要保存
                children = []
                for i in range(item.childCount()):
                    child_result = serialize_item(item.child(i))
                    if child_result:
                        children.append(child_result)
                return {
                    'name': item.text(0),
                    'type': 'collection',
                    'children': children
                }
        data = []
        for i in range(self.collection_tree.topLevelItemCount()):
            node = serialize_item(self.collection_tree.topLevelItem(i))
            if node:
                data.append(node)
        return data

    def save_all(self):
        """保存所有数据"""
        try:
            data = self.serialize_collections()
            path = os.path.join(self._workspace_dir, 'collections.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._unsaved_changes = False
            self.log_info("保存所有数据成功")
        except Exception as e:
            self.log_error(f"保存数据失败: {e}")

    # 菜单事件处理
    def show_about(self):
        """显示关于对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        from PyQt5.QtCore import QTimer
        from PyQt5.QtGui import QPixmap
        
        dialog = QDialog(self)
        dialog.setWindowTitle('About')
        dialog.setMinimumWidth(450)
        layout = QVBoxLayout(dialog)
        
        # 图标
        icon_label = QLabel()
        icon_path = self.get_icon_path()
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText('🦸')
            icon_label.setStyleSheet('font-size: 48px;')
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 应用信息
        about_text = '''postsuperman

A Postman-like API debugging tool.

Features:
• Multi-tab request management
• Parameter, header, and body editing
• cURL import and export
• Response highlighting and formatting
• Collection management
• Environment support
• Request history

Powered by Python & PyQt5

Developed by xuzhenkang@hotmail.com

https://github.com/xuzhenkang/postsuperman

Version: 1.0.0'''
        
        about_edit = QTextEdit()
        about_edit.setReadOnly(True)
        about_edit.setPlainText(about_text)
        about_edit.setMaximumHeight(300)
        about_edit.setStyleSheet('text-align: left;')
        layout.addWidget(about_edit)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        copy_btn = QPushButton('Copy Info')
        copy_btn.setFixedWidth(120)
        btn_row.addWidget(copy_btn)
        layout.addLayout(btn_row)
        
        def do_copy():
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(about_text)
            
            # 改变按钮文本为"Copied"
            copy_btn.setText('Copied')
            copy_btn.setEnabled(False)
            
            # 2秒后恢复按钮状态
            timer = QTimer(dialog)
            timer.setSingleShot(True)
            def restore_button():
                copy_btn.setText('Copy Info')
                copy_btn.setEnabled(True)
                timer.deleteLater()
            timer.timeout.connect(restore_button)
            timer.start(2000)  # 2000毫秒 = 2秒
        
        copy_btn.clicked.connect(do_copy)
        dialog.exec_()

    def update_tab_title(self, old_name, new_name):
        """更新标签页标题"""
        if hasattr(self, 'req_tabs'):
            for i in range(self.req_tabs.count()):
                if self.req_tabs.tabText(i) == old_name:
                    self.req_tabs.setTabText(i, new_name)
                    break
        
    def show_doc(self):
        """显示用户手册对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QScrollArea, QWidget
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QTextCursor
        
        dialog = QDialog(self)
        dialog.setWindowTitle('PostSuperman 用户手册')
        dialog.setMinimumSize(800, 600)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # 标题
        title_label = QLabel('📖 PostSuperman 用户使用手册')
        title_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #333; margin: 10px;')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 10, 20, 10)
        
        # 读取用户手册内容
        manual_content = self.get_user_manual_content()
        
        # 创建文本编辑器显示手册内容
        manual_edit = QTextEdit()
        manual_edit.setReadOnly(True)
        
        # 将Markdown内容转换为HTML格式
        html_content = self.convert_markdown_to_html(manual_content)
        manual_edit.setHtml(html_content)
        
        manual_edit.setStyleSheet('''
            QTextEdit {
                font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
            }
        ''')
        
        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        manual_edit.setFont(font)
        
        content_layout.addWidget(manual_edit)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # 复制按钮
        copy_btn = QPushButton('📋 复制到剪贴板')
        copy_btn.setFixedWidth(150)
        copy_btn.clicked.connect(lambda: self.copy_manual_to_clipboard(manual_content, copy_btn))
        
        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(dialog.accept)
        
        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()

    def copy_manual_to_clipboard(self, content, button):
        """复制手册内容到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        
        # 改变按钮文本
        original_text = button.text()
        button.setText('已复制')
        button.setEnabled(False)
        
        # 2秒后恢复按钮状态
        timer = QTimer(self)
        timer.setSingleShot(True)
        def restore_button():
            button.setText(original_text)
            button.setEnabled(True)
            timer.deleteLater()
        timer.timeout.connect(restore_button)
        timer.start(2000)

    def show_contact(self):
        """显示联系信息对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        from PyQt5.QtCore import QTimer
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Contact Me')
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        # 联系信息
        contact_text = '''Contact Information

Email: xuzhenkang@hotmail.com

GitHub: https://github.com/xuzhenkang/postsuperman

Issues: https://github.com/xuzhenkang/postsuperman/issues

Features & Bugs: Please report via GitHub issues

Thank you for using PostSuperman!'''
        
        contact_edit = QTextEdit()
        contact_edit.setReadOnly(True)
        contact_edit.setPlainText(contact_text)
        contact_edit.setMaximumHeight(200)
        layout.addWidget(contact_edit)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        copy_btn = QPushButton('Copy Email')
        copy_btn.setFixedWidth(120)
        btn_row.addWidget(copy_btn)
        layout.addLayout(btn_row)
        
        def do_copy():
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText('xuzhenkang@hotmail.com')
            
            # 改变按钮文本为"Copied"
            copy_btn.setText('Copied')
            copy_btn.setEnabled(False)
            
            # 2秒后恢复按钮状态
            timer = QTimer(dialog)
            timer.setSingleShot(True)
            def restore_button():
                copy_btn.setText('Copy Email')
                copy_btn.setEnabled(True)
                timer.deleteLater()
            timer.timeout.connect(restore_button)
            timer.start(2000)  # 2000毫秒 = 2秒
        
        copy_btn.clicked.connect(do_copy)
        dialog.exec_()

    # 集合相关事件处理
    def show_collection_menu(self, pos):
        """显示集合右键菜单"""
        from PyQt5.QtWidgets import QMenu, QMessageBox, QInputDialog
        item = self.collection_tree.itemAt(pos)
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
        new_collection_action = None
        new_req_action = None
        rename_action = None
        delete_action = None
        
        if item is None:
            # 空白处右键菜单
            new_collection_action = menu.addAction('New Collection')
        elif is_collection(item):
            # Collection节点右键菜单
            new_collection_action = menu.addAction('New Collection')
            new_req_action = menu.addAction('New Request')
            menu.addSeparator()
            rename_action = menu.addAction('Rename')
            delete_action = menu.addAction('Delete')
        elif is_request(item):
            # Request节点右键菜单
            rename_action = menu.addAction('Rename')
            delete_action = menu.addAction('Delete')
        
        action = menu.exec_(self.collection_tree.viewport().mapToGlobal(pos))
        
        # 处理空白处的New Collection
        if item is None and action and action.text() == 'New Collection':
            name, ok = QInputDialog.getText(self, 'New Collection', 'Enter collection name:')
            if not ok or not name.strip():
                return
            name = name.strip()
            def is_duplicate(tree, name):
                for i in range(tree.topLevelItemCount()):
                    if tree.topLevelItem(i).text(0) == name:
                        return True
                return False
            if is_duplicate(self.collection_tree, name):
                QMessageBox.warning(self, 'Create Failed', f'A collection named "{name}" already exists!')
                return
            item = QTreeWidgetItem(self.collection_tree, [name])
            item.setIcon(0, self.folder_icon)
            self.save_all()
            self.log_info(f'Create Collection: "{name}"')
            return
            
        # 处理Collection节点的菜单
        if item is not None and is_collection(item) and new_collection_action and action == new_collection_action:
            name, ok = QInputDialog.getText(self, 'New Collection', 'Enter collection name:')
            if not ok or not name.strip():
                return
            name = name.strip()
            # 检查重名（只在该节点下）
            for i in range(item.childCount()):
                sibling = item.child(i)
                if sibling and sibling.text(0) == name:
                    QMessageBox.warning(self, 'Create Failed', f'A collection named "{name}" already exists in this collection!')
                    return
            new_item = QTreeWidgetItem(item, [name])
            new_item.setIcon(0, self.folder_icon)
            item.setExpanded(True)
            self.save_all()
            return
        elif 'new_req_action' in locals() and new_req_action and action == new_req_action:
            # 弹出对话框让用户输入Request名称
            from PyQt5.QtWidgets import QInputDialog, QMessageBox
            
            # 获取当前选中的项（右键点击的Collection）
            selected_collection = item
            
            # 如果选中的是Request节点，弹出提示
            if selected_collection and selected_collection.childCount() == 0 and selected_collection.parent() is not None:
                QMessageBox.information(
                    self,
                    'Cannot Create Request',
                    'Cannot create a request under another request.\n\nPlease select a collection to create a new request.'
                )
                return
            
            request_name, ok = QInputDialog.getText(
                self, 
                'New Request', 
                'Enter request name:',
                text='New Request'
            )
            
            if not ok or not request_name.strip():
                return  # 用户取消或输入为空
            
            # 检查名称是否重复
            def check_name_exists(parent_item, name):
                for i in range(parent_item.childCount()):
                    if parent_item.child(i).text(0) == name:
                        return True
                return False
            
            # 检查名称是否在父Collection中重复
            if check_name_exists(selected_collection, request_name):
                QMessageBox.warning(
                    self, 
                    'Duplicate Name', 
                    f'A request named "{request_name}" already exists in this collection!'
                )
                return
            
            # 确保请求区域已创建
            self.ensure_req_tabs()
            
            # 生成包含Collection路径的Tab标签
            def get_collection_path(parent_collection):
                path_parts = []
                current = parent_collection
                while current is not None:
                    path_parts.insert(0, current.text(0))
                    current = current.parent()
                return '/'.join(path_parts)
            
            collection_path = get_collection_path(selected_collection)
            full_request_path = f"{collection_path}/{request_name}"
            
            # 创建新的请求编辑器
            from ui.widgets.request_editor import RequestEditor
            req_editor = RequestEditor(self, req_name=request_name)
            tab_index = self.req_tabs.addTab(req_editor, full_request_path)
            self.req_tabs.setCurrentWidget(req_editor)
            
            # 为新Tab创建Response区域
            self.show_response_for_tab(tab_index)
            
            # 自动保存新请求到collections.json
            self.save_new_request_to_collections(req_editor, request_name, selected_collection)
            
            # 在树中选中新创建的Request
            new_request_item = None
            for i in range(selected_collection.childCount()):
                child = selected_collection.child(i)
                if child.text(0) == request_name:
                    new_request_item = child
                    break
            
            if new_request_item:
                self.collection_tree.setCurrentItem(new_request_item)
                self.collection_tree.scrollToItem(new_request_item)
            
            self.log_info(f'Create new request "{request_name}" in collection: {selected_collection.text(0)}')
            return
        elif rename_action and action == rename_action:
            name, ok = QInputDialog.getText(self, 'Rename', 'Enter new name:', text=item.text(0))
            if not ok or not name.strip():
                return
            name = name.strip()
            if '*' in name:
                QMessageBox.warning(self, 'Invalid Name', 'Request name cannot contain asterisk (*) character!')
                return
            if item.parent() is None:
                for i in range(self.collection_tree.topLevelItemCount()):
                    if self.collection_tree.topLevelItem(i) != item and self.collection_tree.topLevelItem(i).text(0) == name:
                        QMessageBox.warning(self, 'Rename Failed', f'A collection named "{name}" already exists!')
                        return
            else:
                parent = item.parent()
                for i in range(parent.childCount()):
                    if parent.child(i) != item and parent.child(i).text(0) == name:
                        QMessageBox.warning(self, 'Rename Failed', f'A request named "{name}" already exists in this collection!')
                        return
            old_name = item.text(0)
            item.setText(0, name)
            # 重命名后保持图标
            if item.childCount() == 0:
                item.setIcon(0, self.file_icon)
            else:
                item.setIcon(0, self.folder_icon)
            # 如果是Request节点，同步更新右侧标签页
            if item.childCount() == 0 and item.parent() is not None:
                self.update_tab_title(old_name, name)
                self.log_info(f'Rename Request: "{old_name}" -> "{name}"')
            else:
                # 这是Collection节点，需要更新所有相关的Tab标签
                self.update_tabs_for_collection_rename(old_name, name)
                self.log_info(f'Rename Collection: "{old_name}" -> "{name}"')
            self.save_all()
            return
        elif delete_action and action == delete_action:
            # 判断是否为Collection节点
            if item.childCount() > 0:
                # 这是Collection节点，需要确认删除
                child_count = item.childCount()
                choice = QMessageBox.question(
                    self, 
                    'Delete Collection', 
                    f'Are you sure you want to delete the collection "{item.text(0)}"?\n\n'
                    f'This will also delete all {child_count} child item(s) in this collection.\n\n'
                    'This action cannot be undone.',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if choice == QMessageBox.Yes:
                    # 删除Collection及其所有子节点
                    if item.parent() is None:
                        # 删除顶级集合
                        self.collection_tree.takeTopLevelItem(self.collection_tree.indexOfTopLevelItem(item))
                    else:
                        # 删除子项
                        item.parent().removeChild(item)
                    self.save_all()
                    self.log_info(f'Delete collection "{item.text(0)}" with {child_count} child items')
                return
            else:
                # 这是Request节点，直接删除
                if item.parent() is None:
                    # 删除顶级集合
                    self.collection_tree.takeTopLevelItem(self.collection_tree.indexOfTopLevelItem(item))
                else:
                    # 删除子项
                    item.parent().removeChild(item)
                self.save_all()
                self.log_info(f'Delete request "{item.text(0)}"')
                return
        
    def on_collection_item_double_clicked(self, item, column):
        """集合项双击事件"""
        self.log_info("集合项双击")
        # 实现双击逻辑
        

            
    def get_item_paths_for_tabs(self, item):
        """获取项的所有可能路径，用于Tab更新"""
        paths = []
        
        def get_path(current_item):
            path_parts = []
            current = current_item
            while current is not None:
                path_parts.insert(0, current.text(0))
                current = current.parent()
            return '/'.join(path_parts)
            
        # 获取当前路径
        current_path = get_path(item)
        paths.append(current_path)
        
        # 如果是Collection，获取所有子Request的路径
        if item.childCount() > 0:
            for i in range(item.childCount()):
                child_path = get_path(item.child(i))
                paths.append(child_path)
                
        return paths
        
    def update_tabs_after_drag(self, moved_item, old_paths):
        """拖拽后更新Tab路径"""
        if not hasattr(self, 'req_tabs') or self.req_tabs is None:
            return
            
        # 获取新的路径
        new_paths = self.get_item_paths_for_tabs(moved_item)
        
        # 更新Tab标题
        for i in range(self.req_tabs.count()):
            tab_text = self.req_tabs.tabText(i)
            
            # 检查是否需要更新
            for old_path in old_paths:
                if old_path in tab_text:
                    # 找到对应的新路径
                    for new_path in new_paths:
                        if self.get_request_name_from_path(old_path) == self.get_request_name_from_path(new_path):
                            # 更新Tab标题
                            new_tab_text = tab_text.replace(old_path, new_path)
                            self.req_tabs.setTabText(i, new_tab_text)
                            self.log_info(f'Updated tab after drag: "{tab_text}" -> "{new_tab_text}"')
                            break
                            
    def get_request_name_from_path(self, path):
        """从路径中提取请求名称"""
        if '/' in path:
            return path.split('/')[-1]
        return path

    def closeEvent(self, event):
        """关闭事件处理"""
        # 检查是否有未保存的改动
        has_unsaved_changes = False
        if hasattr(self, 'req_tabs') and self.req_tabs is not None:
            try:
                for i in range(self.req_tabs.count()):
                    tab_text = self.req_tabs.tabText(i)
                    if '*' in tab_text:
                        has_unsaved_changes = True
                        break
            except RuntimeError:
                # req_tabs已被删除，忽略
                pass
        
        if has_unsaved_changes:
            # 有未保存的改动，提示用户
            choice = QMessageBox.question(
                self, 
                'Unsaved Changes', 
                'Detected unsaved changes, do you want to save before exiting?\n\n'
                'Yes = Save all changes and exit\n'
                'No = Discard all unsaved changes and exit\n'
                'Cancel = Cancel exit',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if choice == QMessageBox.Yes:
                # 保存所有更改
                try:
                    self.save_all()
                    event.accept()
                except Exception as e:
                    QMessageBox.warning(self, 'Save Failed', f'Failed to save changes: {e}')
                    event.ignore()
            elif choice == QMessageBox.No:
                # 丢弃未保存的更改
                event.accept()
            else:
                # 取消退出
                event.ignore()
        else:
            # 没有未保存的更改，直接退出
            event.accept()

    def import_request_dialog(self):
        """导入请求对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup, QPushButton, QTextEdit, QFileDialog, QMessageBox
        from PyQt5.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Import Request')
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 导入方式选择
        method_label = QLabel('Import Method:')
        layout.addWidget(method_label)
        
        curl_radio = QRadioButton('From cURL command')
        file_radio = QRadioButton('From file')
        curl_radio.setChecked(True)
        
        method_layout = QHBoxLayout()
        method_layout.addWidget(curl_radio)
        method_layout.addWidget(file_radio)
        method_layout.addStretch()
        layout.addLayout(method_layout)
        
        # cURL输入区域
        curl_label = QLabel('cURL Command:')
        layout.addWidget(curl_label)
        
        curl_text = QTextEdit()
        curl_text.setMaximumHeight(100)
        layout.addWidget(curl_text)
        
        # 文件选择区域
        file_label = QLabel('File Path:')
        file_label.setVisible(False)
        # File选择区
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_select_btn = QPushButton('touch to select file')
        file_select_btn.setFixedHeight(80)
        file_select_btn.setStyleSheet('font-size:18px; color:#1976d2; background: #f5f5f5; border:1px dashed #1976d2;')
        file_layout.addStretch()
        file_layout.addWidget(file_select_btn, alignment=Qt.AlignCenter)
        file_layout.addStretch()
        file_widget.setVisible(False)
        layout.addWidget(file_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        import_btn = QPushButton('Import')
        cancel_btn = QPushButton('Cancel')
        button_layout.addStretch()
        button_layout.addWidget(import_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # 事件处理
        def on_radio_changed():
            if curl_radio.isChecked():
                curl_text.setVisible(True)
                file_widget.setVisible(False)
            else:
                curl_text.setVisible(False)
                file_widget.setVisible(True)
        
        curl_radio.toggled.connect(on_radio_changed)
        file_radio.toggled.connect(on_radio_changed)
        
        def import_curl():
            curl_command = curl_text.toPlainText().strip()
            if not curl_command:
                QMessageBox.warning(dialog, 'Error', 'Please enter a cURL command!')
                return
            
            try:
                # 解析cURL命令
                import shlex
                args = shlex.split(curl_command)
                
                # 提取URL
                url = None
                method = 'GET'
                headers = {}
                data = None
                
                i = 1  # 跳过curl
                while i < len(args):
                    arg = args[i]
                    if arg.startswith('-X') or arg.startswith('--request'):
                        if i + 1 < len(args):
                            method = args[i + 1]
                            i += 2
                        else:
                            i += 1
                    elif arg.startswith('-H') or arg.startswith('--header'):
                        if i + 1 < len(args):
                            header = args[i + 1]
                            if ':' in header:
                                key, value = header.split(':', 1)
                                headers[key.strip()] = value.strip()
                            i += 2
                        else:
                            i += 1
                    elif arg.startswith('-d') or arg.startswith('--data'):
                        if i + 1 < len(args):
                            data = args[i + 1]
                            i += 2
                        else:
                            i += 1
                    elif not arg.startswith('-'):
                        url = arg
                        i += 1
                    else:
                        i += 1
                
                if not url:
                    QMessageBox.warning(dialog, 'Error', 'No URL found in cURL command!')
                    return
                
                # 创建新请求
                self.create_new_request()
                current_editor = self.req_tabs.currentWidget()
                if current_editor:
                    current_editor.method_combo.setCurrentText(method)
                    current_editor.url_edit.setText(url)
                    
                    # 设置headers
                    if headers:
                        current_editor.headers_table.setRowCount(len(headers) + 1)
                        for i, (key, value) in enumerate(headers.items()):
                            current_editor.headers_table.setItem(i, 1, QTableWidgetItem(key))
                            current_editor.headers_table.setItem(i, 2, QTableWidgetItem(value))
                    
                    # 设置body
                    if data:
                        current_editor.body_raw_radio.setChecked(True)
                        current_editor.raw_text_edit.setPlainText(data)
                
                dialog.accept()
                
            except Exception as e:
                QMessageBox.warning(dialog, 'Error', f'Failed to parse cURL command: {e}')
        
        def import_file():
            # 直接打开文件选择对话框
            fname, _ = QFileDialog.getOpenFileName(
                dialog, 
                'Select File', 
                '', 
                'All Files (*);;JSON Files (*.json);;Text Files (*.txt)'
            )
            if not fname:
                return
            
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 尝试解析为JSON
                try:
                    import json
                    data = json.loads(content)
                    
                    # 创建新请求
                    self.create_new_request()
                    current_editor = self.req_tabs.currentWidget()
                    if current_editor:
                        current_editor.method_combo.setCurrentText(data.get('method', 'GET'))
                        current_editor.url_edit.setText(data.get('url', ''))
                        
                        # 设置headers
                        headers = data.get('headers', {})
                        if headers:
                            current_editor.headers_table.setRowCount(len(headers) + 1)
                            for i, (key, value) in enumerate(headers.items()):
                                current_editor.headers_table.setItem(i, 1, QTableWidgetItem(key))
                                current_editor.headers_table.setItem(i, 2, QTableWidgetItem(str(value)))
                        
                        # 设置body
                        body = data.get('body', '')
                        if body:
                            current_editor.body_raw_radio.setChecked(True)
                            current_editor.raw_text_edit.setPlainText(str(body))
                    
                    dialog.accept()
                    
                except json.JSONDecodeError:
                    # 如果不是JSON，尝试作为cURL命令解析
                    import shlex
                    args = shlex.split(content)
                    
                    # 提取URL
                    url = None
                    method = 'GET'
                    headers = {}
                    data = None
                    
                    i = 0
                    while i < len(args):
                        arg = args[i]
                        if arg.startswith('-X') or arg.startswith('--request'):
                            if i + 1 < len(args):
                                method = args[i + 1]
                                i += 2
                            else:
                                i += 1
                        elif arg.startswith('-H') or arg.startswith('--header'):
                            if i + 1 < len(args):
                                header = args[i + 1]
                                if ':' in header:
                                    key, value = header.split(':', 1)
                                    headers[key.strip()] = value.strip()
                                i += 2
                            else:
                                i += 1
                        elif arg.startswith('-d') or arg.startswith('--data'):
                            if i + 1 < len(args):
                                data = args[i + 1]
                                i += 2
                            else:
                                i += 1
                        elif not arg.startswith('-'):
                            url = arg
                            i += 1
                        else:
                            i += 1
                    
                    if not url:
                        QMessageBox.warning(dialog, 'Error', 'No URL found in file content!')
                        return
                    
                    # 创建新请求
                    self.create_new_request()
                    current_editor = self.req_tabs.currentWidget()
                    if current_editor:
                        current_editor.method_combo.setCurrentText(method)
                        current_editor.url_edit.setText(url)
                        
                        # 设置headers
                        if headers:
                            current_editor.headers_table.setRowCount(len(headers) + 1)
                            for i, (key, value) in enumerate(headers.items()):
                                current_editor.headers_table.setItem(i, 1, QTableWidgetItem(key))
                                current_editor.headers_table.setItem(i, 2, QTableWidgetItem(value))
                        
                        # 设置body
                        if data:
                            current_editor.body_raw_radio.setChecked(True)
                            current_editor.raw_text_edit.setPlainText(data)
                    
                    dialog.accept()
                    
            except Exception as e:
                QMessageBox.warning(dialog, 'Error', f'Failed to import file: {e}')
        
        def browse_file():
            fname, _ = QFileDialog.getOpenFileName(
                dialog, 
                'Select File', 
                '', 
                'All Files (*);;JSON Files (*.json);;Text Files (*.txt)'
            )
            if fname:
                file_select_btn.setText(fname)
        
        def on_import():
            if curl_radio.isChecked():
                import_curl()
            else:
                import_file()
        
        import_btn.clicked.connect(on_import)
        cancel_btn.clicked.connect(dialog.reject)
        file_select_btn.clicked.connect(browse_file)
        
        dialog.exec_()

    def _cleanup_previous_request(self):
        """清理之前的请求 - 最简单版本"""
        try:
            print("清理之前的请求")
            # 只设置停止标志，不等待线程
            if hasattr(self, '_req_worker') and self._req_worker:
                print("设置之前请求的停止标志")
                try:
                    self._req_worker._stop_flag = True
                except Exception as e:
                    print(f"设置停止标志时出错: {e}")
                self._req_worker = None
            # 不等待线程，直接清理引用
            self._req_thread = None
            self._sending_request = False
            self._current_editor = None
            print("清理完成")
        except Exception as e:
            print(f"清理之前请求时出错: {e}")
            self._sending_request = False
            self._req_worker = None
            self._req_thread = None
            self._current_editor = None 

    def show_curl_code(self):
        """显示cURL代码对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        from PyQt5.QtGui import QClipboard
        
        dialog = QDialog(self)
        dialog.setWindowTitle('cURL')
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        
        # 获取当前请求编辑器
        current_editor = self.req_tabs.currentWidget()
        if not current_editor:
            QMessageBox.warning(dialog, 'Error', 'No active request editor!')
            return
        
        # 生成cURL命令
        method = current_editor.method_combo.currentText()
        url = current_editor.url_edit.text().strip()
        
        # 构建headers
        headers = []
        for row in range(current_editor.headers_table.rowCount() - 1):
            key_item = current_editor.headers_table.item(row, 1)
            value_item = current_editor.headers_table.item(row, 2)
            if key_item and value_item and key_item.text().strip():
                headers.append(f"-H '{key_item.text().strip()}: {value_item.text().strip()}'")
        
        # 构建cURL命令
        curl_cmd = f"curl -X {method}"
        if headers:
            curl_cmd += f" {' '.join(headers)}"
        curl_cmd += f" '{url}'"
        
        # 添加body数据
        if current_editor.body_raw_radio.isChecked():
            body_data = current_editor.raw_text_edit.toPlainText().strip()
            if body_data:
                curl_cmd += f" -d '{body_data}'"
        
        # 创建UI
        label = QLabel('cURL command:')
        layout.addWidget(label)
        
        curl_edit = QTextEdit()
        curl_edit.setReadOnly(True)
        curl_edit.setPlainText(curl_cmd)
        layout.addWidget(curl_edit)
        
        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        copy_btn = QPushButton('Copy')
        copy_btn.setFixedWidth(80)
        btn_layout.addWidget(copy_btn)
        
        layout.addLayout(btn_layout)
        
        # 复制功能
        def do_copy():
            clipboard = QApplication.clipboard()
            clipboard.setText(curl_cmd)
            QMessageBox.information(dialog, 'Success', 'cURL command copied to clipboard!')
        
        copy_btn.clicked.connect(do_copy)
        dialog.exec_()

    def export_request(self):
        """导出当前请求"""
        current_editor = self.req_tabs.currentWidget()
        if not current_editor:
            QMessageBox.warning(self, 'Error', 'No active request editor!')
            return
        
        # 获取文件名
        fname, _ = QFileDialog.getSaveFileName(
            self, 
            'Export Request', 
            'request.json', 
            'JSON Files (*.json);;All Files (*)'
        )
        if not fname:
            return
        
        try:
            # 序列化请求数据
            request_data = current_editor.serialize_request()
            
            # 保存到文件
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, 'Success', f'Request exported to {fname}')
            
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to export request: {e}') 

    def get_user_manual_content(self):
        """获取用户手册内容"""
        try:
            manual_path = os.path.join(self._workspace_dir, 'docs', 'user_manual.md')
            if os.path.exists(manual_path):
                with open(manual_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "# PostSuperman 用户手册\n\n手册文件未找到。"
        except Exception as e:
            return f"# PostSuperman 用户手册\n\n读取手册文件时出错: {e}"

    def convert_markdown_to_html(self, markdown_text):
        """将Markdown转换为HTML"""
        import re
        
        # 基本的Markdown到HTML转换
        html = markdown_text
        
        # 标题转换
        html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 粗体和斜体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # 代码块
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # 列表
        html = re.sub(r'^\* (.*$)', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^- (.*$)', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 段落
        html = re.sub(r'\n\n', r'</p><p>', html)
        html = f'<p>{html}</p>'
        
        # 清理空段落
        html = re.sub(r'<p></p>', '', html)
        
        return html

    def update_tabs_for_collection_rename(self, old_name, new_name):
        """更新集合重命名后的所有相关标签页标题"""
        if not hasattr(self, 'req_tabs') or self.req_tabs is None:
            return
            
        for i in range(self.req_tabs.count()):
            tab_text = self.req_tabs.tabText(i)
            # 检查Tab标题是否包含旧的Collection名称
            if old_name in tab_text:
                # 替换路径中的Collection名称
                new_tab_text = tab_text.replace(old_name, new_name)
                self.req_tabs.setTabText(i, new_tab_text)
                self.log_info(f'Updated tab title: "{tab_text}" -> "{new_tab_text}"')

    def _get_parent_map(self):
        parent_map = {}
        def recurse(item):
            for i in range(item.childCount()):
                child = item.child(i)
                parent_map[child] = item
                recurse(child)
        for i in range(self.collection_tree.topLevelItemCount()):
            top = self.collection_tree.topLevelItem(i)
            parent_map[top] = None
            recurse(top)
        return parent_map