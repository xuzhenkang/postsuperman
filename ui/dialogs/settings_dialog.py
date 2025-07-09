from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from ui.utils.settings_manager import load_settings, save_settings

class DataDirectoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        # collections.json路径
        layout.addWidget(QLabel('collections.json存储位置:'))
        self.coll_path_edit = QLineEdit()
        self.coll_choose_btn = QPushButton('选择文件')
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.coll_path_edit)
        hlayout1.addWidget(self.coll_choose_btn)
        layout.addLayout(hlayout1)
        # 日志路径
        layout.addWidget(QLabel('日志文件(postsuperman.log)存储位置:'))
        self.log_path_edit = QLineEdit()
        self.log_choose_btn = QPushButton('选择文件')
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.log_path_edit)
        hlayout2.addWidget(self.log_choose_btn)
        layout.addLayout(hlayout2)
        layout.addStretch()
        self.coll_choose_btn.clicked.connect(self.choose_coll_file)
        self.log_choose_btn.clicked.connect(self.choose_log_file)
        self.load_current_settings()
    def choose_coll_file(self):
        f, _ = QFileDialog.getSaveFileName(self, '选择collections.json文件', self.coll_path_edit.text() or '', 'JSON Files (*.json)')
        if f:
            self.coll_path_edit.setText(f)
    def choose_log_file(self):
        f, _ = QFileDialog.getSaveFileName(self, '选择日志文件', self.log_path_edit.text() or '', 'Log Files (*.log);;All Files (*)')
        if f:
            self.log_path_edit.setText(f)
    def load_current_settings(self):
        s = load_settings()
        self.coll_path_edit.setText(s.get('collections_path', ''))
        self.log_path_edit.setText(s.get('log_path', ''))
    def get_settings(self):
        return {
            'collections_path': self.coll_path_edit.text().strip(),
            'log_path': self.log_path_edit.text().strip()
        }
    def validate_paths(self):
        coll_path = self.coll_path_edit.text().strip()
        log_path = self.log_path_edit.text().strip()
        if not coll_path.lower().endswith('.json'):
            return False, 'collections.json路径必须以.json结尾'
        if not log_path.lower().endswith('.log'):
            return False, '日志文件路径必须以.log结尾'
        return True, ''
    def is_changed(self):
        s = load_settings()
        return (self.coll_path_edit.text().strip() != s.get('collections_path', '')) or (self.log_path_edit.text().strip() != s.get('log_path', ''))

class ShortcutKeyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('快捷键设置（示例）：'))
        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels(['功能', '快捷键'])
        self.table.setItem(0, 0, QTableWidgetItem('发送请求'))
        self.table.setItem(0, 1, QTableWidgetItem('Ctrl+Enter'))
        self.table.setItem(1, 0, QTableWidgetItem('保存'))
        self.table.setItem(1, 1, QTableWidgetItem('Ctrl+S'))
        self.table.setItem(2, 0, QTableWidgetItem('切换标签'))
        self.table.setItem(2, 1, QTableWidgetItem('Ctrl+Tab'))
        layout.addWidget(self.table)
        layout.addStretch()

class LanguagePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('语言设置:'))
        self.combo = QComboBox()
        self.combo.addItems(['English', '中文'])
        layout.addWidget(self.combo)
        layout.addStretch()

class ThemePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('主题设置:'))
        self.combo = QComboBox()
        self.combo.addItems(['dark', 'bright'])
        layout.addWidget(self.combo)
        layout.addStretch()

class AppearanceFontPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('界面字体设置:'))
        self.font_combo = QComboBox()
        self.font_combo.addItems(['宋体', '楷体', '微软雅黑', 'Consolas', 'Courier'])
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 32)
        self.size_spin.setValue(12)
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('字体:'))
        hlayout.addWidget(self.font_combo)
        hlayout.addWidget(QLabel('大小:'))
        hlayout.addWidget(self.size_spin)
        layout.addLayout(hlayout)
        layout.addStretch()

class EditorFontPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('编辑器/响应区字体设置:'))
        self.font_combo = QComboBox()
        self.font_combo.addItems(['宋体', '楷体', '微软雅黑', 'Consolas', 'Courier'])
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 32)
        self.size_spin.setValue(12)
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('字体:'))
        hlayout.addWidget(self.font_combo)
        hlayout.addWidget(QLabel('大小:'))
        hlayout.addWidget(self.size_spin)
        layout.addLayout(hlayout)
        layout.addStretch()

class EditorTabPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Tab 设置:'))
        self.tabsize_spin = QSpinBox()
        self.tabsize_spin.setRange(2, 8)
        self.tabsize_spin.setValue(load_settings().get('editor_tab_size', 4))
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('Tab 替换为空格数:'))
        hlayout.addWidget(self.tabsize_spin)
        layout.addLayout(hlayout)
        layout.addStretch()
    def get_settings(self):
        return {'editor_tab_size': self.tabsize_spin.value()}
    def load_current_settings(self):
        self.tabsize_spin.setValue(load_settings().get('editor_tab_size', 4))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Preferences / Settings')
        self.setMinimumSize(600, 400)
        main_layout = QHBoxLayout()
        # 左侧树
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        # 构建树结构
        general = QTreeWidgetItem(self.tree, ['General'])
        data_dir = QTreeWidgetItem(general, ['data directory'])
        shortcut = QTreeWidgetItem(general, ['shortcut key'])
        language = QTreeWidgetItem(general, ['language'])
        appearance = QTreeWidgetItem(self.tree, ['Appearance'])
        theme = QTreeWidgetItem(appearance, ['theme'])
        font = QTreeWidgetItem(appearance, ['font'])
        editor = QTreeWidgetItem(self.tree, ['Editor'])
        editor_font = QTreeWidgetItem(editor, ['font'])
        editor_tab = QTreeWidgetItem(editor, ['tab'])  # 新增Tab设置
        self.tree.expandAll()
        self.tree.setMaximumWidth(180)
        # 右侧stack
        self.stack = QStackedWidget()
        self.panels = {
            'data directory': DataDirectoryPanel(),
            'shortcut key': ShortcutKeyPanel(),
            'language': LanguagePanel(),
            'theme': ThemePanel(),
            'font_appearance': AppearanceFontPanel(),
            'font_editor': EditorFontPanel(),
            'tab_editor': EditorTabPanel(),  # 新增Tab设置
        }
        self.stack.addWidget(self.panels['data directory'])      # 0
        self.stack.addWidget(self.panels['shortcut key'])        # 1
        self.stack.addWidget(self.panels['language'])            # 2
        self.stack.addWidget(self.panels['theme'])               # 3
        self.stack.addWidget(self.panels['font_appearance'])     # 4
        self.stack.addWidget(self.panels['font_editor'])         # 5
        self.stack.addWidget(self.panels['tab_editor'])          # 6 新增
        main_layout.addWidget(self.tree)
        main_layout.addWidget(self.stack, 1)
        # 选项树切换逻辑
        self.tree.currentItemChanged.connect(self.on_tree_changed)
        # 默认选中第一个子项
        self.tree.setCurrentItem(data_dir)
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton('OK')
        btn_cancel = QPushButton('Cancel')
        btn_apply = QPushButton('Apply')
        btn_default = QPushButton('Restore Defaults')
        btn_ok.clicked.connect(self.on_ok)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_default)
        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        vbox = QVBoxLayout()
        vbox.addLayout(main_layout)
        vbox.addLayout(btn_layout)
        self.setLayout(vbox)
        # 每次弹出都刷新data directory面板内容
        self.panels['data directory'].load_current_settings()
        self.panels['tab_editor'].load_current_settings()  # 新增
    def on_tree_changed(self, current, previous):
        if not current: return
        text = current.text(0)
        parent = current.parent()
        if parent:
            ptext = parent.text(0)
            if ptext == 'Appearance' and text == 'font':
                self.stack.setCurrentWidget(self.panels['font_appearance'])
            elif ptext == 'Editor' and text == 'font':
                self.stack.setCurrentWidget(self.panels['font_editor'])
            elif ptext == 'Editor' and text == 'tab':
                self.stack.setCurrentWidget(self.panels['tab_editor'])  # 新增
            else:
                self.stack.setCurrentWidget(self.panels[text])
        else:
            # 点击分组时默认显示第一个子项
            if text == 'General':
                self.stack.setCurrentWidget(self.panels['data directory'])
            elif text == 'Appearance':
                self.stack.setCurrentWidget(self.panels['theme'])
            elif text == 'Editor':
                self.stack.setCurrentWidget(self.panels['font_editor'])
    def on_apply(self):
        data_panel = self.panels['data directory']
        valid, msg = data_panel.validate_paths()
        if not valid:
            QMessageBox.warning(self, '路径校验失败', msg)
            return
        changed = data_panel.is_changed()
        s = load_settings()
        s.update(data_panel.get_settings())
        # 保存Tab设置
        s.update(self.panels['tab_editor'].get_settings())
        save_settings(s)
        data_panel.load_current_settings()
        self.panels['tab_editor'].load_current_settings()
        if changed:
            QMessageBox.information(self, '设置已保存', '部分设置（如数据/日志路径）需重启应用后生效。')
    def on_ok(self):
        self.on_apply()
        self.accept()

        # 示例设置项，可扩展
        # layout.addWidget(QLabel('示例设置项1: ...'))
        # layout.addWidget(QLabel('示例设置项2: ...'))
        # btn_layout = QHBoxLayout()
        # btn_ok = QPushButton('OK')
        # btn_cancel = QPushButton('Cancel')
        # btn_ok.clicked.connect(self.accept)
        # btn_cancel.clicked.connect(self.reject)
        # btn_layout.addStretch()
        # btn_layout.addWidget(btn_ok)
        # btn_layout.addWidget(btn_cancel)
        # layout.addLayout(btn_layout) 