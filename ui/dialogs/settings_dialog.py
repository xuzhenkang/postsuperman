from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QFontComboBox, QApplication, QKeySequenceEdit, QStyledItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.utils.settings_manager import load_settings, save_settings
from ui.utils.i18n import set_language, get_text

class DataDirectoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label_coll = QLabel(get_text('select_json_file') + ':')
        layout.addWidget(self.label_coll)
        self.coll_path_edit = QLineEdit()
        self.coll_choose_btn = QPushButton(get_text('select_file'))
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.coll_path_edit)
        hlayout1.addWidget(self.coll_choose_btn)
        layout.addLayout(hlayout1)
        self.label_log = QLabel(get_text('select_log_file') + ':')
        layout.addWidget(self.label_log)
        self.log_path_edit = QLineEdit()
        self.log_choose_btn = QPushButton(get_text('select_file'))
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.log_path_edit)
        hlayout2.addWidget(self.log_choose_btn)
        layout.addLayout(hlayout2)
        layout.addStretch()
        self.coll_choose_btn.clicked.connect(self.choose_coll_file)
        self.log_choose_btn.clicked.connect(self.choose_log_file)
        self.load_current_settings()
    def choose_coll_file(self):
        f, _ = QFileDialog.getSaveFileName(self, get_text('select_json_file'), self.coll_path_edit.text() or '', 'JSON Files (*.json)')
        if f:
            self.coll_path_edit.setText(f)
    def choose_log_file(self):
        f, _ = QFileDialog.getSaveFileName(self, get_text('select_log_file'), self.log_path_edit.text() or '', get_text('select_log_file_filter'))
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
            return False, get_text('collection_path_invalid')
        if not log_path.lower().endswith('.log'):
            return False, get_text('log_path_invalid')
        return True, ''
    def is_changed(self):
        s = load_settings()
        return (self.coll_path_edit.text().strip() != s.get('collections_path', '')) or (self.log_path_edit.text().strip() != s.get('log_path', ''))
    def refresh_texts(self):
        self.label_coll.setText(get_text('select_json_file') + ':')
        self.coll_choose_btn.setText(get_text('select_file'))
        self.label_log.setText(get_text('select_log_file') + ':')
        self.log_choose_btn.setText(get_text('select_file'))

class ShortcutKeyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QKeySequenceEdit(parent)
        editor.installEventFilter(self)
        return editor
    def setEditorData(self, editor, index):
        seq = index.model().data(index, Qt.EditRole)
        if seq:
            editor.setKeySequence(seq)
    def setModelData(self, editor, model, index):
        model.setData(index, editor.keySequence().toString(), Qt.EditRole)
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QKeyEvent
        if isinstance(obj, QKeySequenceEdit) and event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Tab, Qt.Key_Backtab):
                obj.keyPressEvent(event)
                return True  # 阻止表格处理Tab
            # Ctrl+Tab, Shift+Tab等组合
            if (event.modifiers() & Qt.ControlModifier and key == Qt.Key_Tab) or \
               (event.modifiers() & Qt.ShiftModifier and key == Qt.Key_Tab):
                obj.keyPressEvent(event)
                return True
        return super().eventFilter(obj, event)

class ShortcutKeyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel(get_text('shortcut_key') + '：')
        layout.addWidget(self.label)
        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels([get_text('function'), get_text('shortcut_key')])
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.table.setItemDelegateForColumn(1, ShortcutKeyDelegate(self.table))
        layout.addWidget(self.table)
        layout.addStretch()
        self.load_current_settings()
    def load_current_settings(self):
        from ui.utils.settings_manager import load_settings
        s = load_settings()
        shortcuts = s.get('shortcuts', {
            'send': 'Ctrl+Enter',
            'save': 'Ctrl+S',
            'switch_tab': 'Ctrl+Tab'
        })
        self.table.setRowCount(3)
        self.table.setItem(0, 0, QTableWidgetItem(get_text('send')))
        self.table.setItem(0, 1, QTableWidgetItem(shortcuts.get('send', 'Ctrl+Enter')))
        self.table.setItem(1, 0, QTableWidgetItem(get_text('save')))
        self.table.setItem(1, 1, QTableWidgetItem(shortcuts.get('save', 'Ctrl+S')))
        self.table.setItem(2, 0, QTableWidgetItem(get_text('switch_tab') if 'switch_tab' in get_text.__globals__['_texts'][get_text.__globals__['_language']] else '切换标签'))
        self.table.setItem(2, 1, QTableWidgetItem(shortcuts.get('switch_tab', 'Ctrl+Tab')))
    def get_settings(self):
        return {
            'shortcuts': {
                'send': self.table.item(0, 1).text().strip() if self.table.item(0, 1) else 'Ctrl+Enter',
                'save': self.table.item(1, 1).text().strip() if self.table.item(1, 1) else 'Ctrl+S',
                'switch_tab': self.table.item(2, 1).text().strip() if self.table.item(2, 1) else 'Ctrl+Tab',
            }
        }
    def refresh_texts(self):
        self.label.setText(get_text('shortcut_key') + '：')
        self.table.setHorizontalHeaderLabels([get_text('function'), get_text('shortcut_key')])
        self.table.setItem(0, 0, QTableWidgetItem(get_text('send')))
        self.table.setItem(1, 0, QTableWidgetItem(get_text('save')))
        self.table.setItem(2, 0, QTableWidgetItem(get_text('switch_tab') if 'switch_tab' in get_text.__globals__['_texts'][get_text.__globals__['_language']] else '切换标签'))

class LanguagePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel(get_text('language') + ':')
        layout.addWidget(self.label)
        self.combo = QComboBox()
        self.combo.addItems(['English', '中文'])
        from ui.utils.settings_manager import load_settings
        lang = load_settings().get('ui_language', 'zh')
        self.combo.setCurrentIndex(0 if lang == 'en' else 1)
        layout.addWidget(self.combo)
        layout.addStretch()
    def get_language(self):
        return 'en' if self.combo.currentIndex() == 0 else 'zh'
    def on_language_changed(self, idx):
        lang = 'en' if idx == 0 else 'zh'
        set_language(lang)
        from ui.utils.settings_manager import load_settings, save_settings
        s = load_settings()
        s['ui_language'] = lang
        save_settings(s)
        # 刷新设置窗口所有文字
        self.parent().parent().parent().refresh_texts()  # SettingsDialog.refresh_texts()
    def refresh_texts(self):
        self.label.setText(get_text('language') + ':')
        self.combo.setItemText(0, 'English')
        self.combo.setItemText(1, '中文')

class ThemePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel(get_text('theme') + ':')
        layout.addWidget(self.label)
        self.combo = QComboBox()
        self.combo.addItems(['dark', 'bright'])
        layout.addWidget(self.combo)
        layout.addStretch()
    def refresh_texts(self):
        self.label.setText(get_text('theme') + ':')
        self.combo.setItemText(0, 'dark')
        self.combo.setItemText(1, 'bright')

class AppearanceFontPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel(get_text('font') + ':')
        layout.addWidget(QLabel(get_text('appearance') + get_text('font') + get_text('settings') + ':'))
        self.font_combo = QFontComboBox()
        self.font_combo.setEditable(False)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 32)
        s = load_settings()
        self.font_combo.setCurrentFont(QFont(s.get('ui_font_family', '微软雅黑')))
        self.size_spin.setValue(s.get('ui_font_size', 12))
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.label)
        hlayout.addWidget(self.font_combo)
        hlayout.addWidget(QLabel(get_text('size') if 'size' in dir() else '大小:'))
        hlayout.addWidget(self.size_spin)
        layout.addLayout(hlayout)
        self.preview = QLabel(get_text('font') + get_text('preview') if 'preview' in dir() else '字体预览 Font Preview 123456')
        self.preview.setMinimumHeight(40)
        layout.addWidget(self.preview)
        layout.addStretch()
        self.font_combo.currentFontChanged.connect(self.update_preview)
        self.size_spin.valueChanged.connect(self.update_preview)
        self.update_preview()
    def update_preview(self):
        font = self.font_combo.currentFont()
        font.setPointSize(self.size_spin.value())
        self.preview.setFont(font)
    def get_settings(self):
        return {
            'ui_font_family': self.font_combo.currentFont().family(),
            'ui_font_size': self.size_spin.value()
        }
    def load_current_settings(self):
        s = load_settings()
        self.font_combo.setCurrentFont(QFont(s.get('ui_font_family', '微软雅黑')))
        self.size_spin.setValue(s.get('ui_font_size', 12))
        self.update_preview()
    def refresh_texts(self):
        self.label.setText(get_text('font') + ':')
        self.preview.setText(get_text('font') + get_text('preview') if 'preview' in dir() else '字体预览 Font Preview 123456')

class EditorFontPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel(get_text('font') + ':')
        layout.addWidget(QLabel(get_text('editor') + get_text('font') + get_text('settings') + ':'))
        self.font_combo = QFontComboBox()
        self.font_combo.setEditable(False)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 32)
        from ui.utils.settings_manager import load_settings
        s = load_settings()
        self.font_combo.setCurrentFont(QFont(s.get('editor_font_family', 'Consolas')))
        self.size_spin.setValue(s.get('editor_font_size', 12))
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.label)
        hlayout.addWidget(self.font_combo)
        hlayout.addWidget(QLabel(get_text('size') if 'size' in dir() else '大小:'))
        hlayout.addWidget(self.size_spin)
        layout.addLayout(hlayout)
        self.preview = QLabel(get_text('font') + get_text('preview') if 'preview' in dir() else '字体预览 Font Preview 123456')
        self.preview.setMinimumHeight(40)
        layout.addWidget(self.preview)
        layout.addStretch()
        self.font_combo.currentFontChanged.connect(self.update_preview)
        self.size_spin.valueChanged.connect(self.update_preview)
        self.update_preview()
    def update_preview(self):
        font = self.font_combo.currentFont()
        font.setPointSize(self.size_spin.value())
        self.preview.setFont(font)
    def get_settings(self):
        return {
            'editor_font_family': self.font_combo.currentFont().family(),
            'editor_font_size': self.size_spin.value()
        }
    def load_current_settings(self):
        from ui.utils.settings_manager import load_settings
        s = load_settings()
        self.font_combo.setCurrentFont(QFont(s.get('editor_font_family', 'Consolas')))
        self.size_spin.setValue(s.get('editor_font_size', 12))
        self.update_preview()
    def refresh_texts(self):
        self.label.setText(get_text('font') + ':')
        self.preview.setText(get_text('font') + get_text('preview') if 'preview' in dir() else '字体预览 Font Preview 123456')

class EditorTabPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel(get_text('tab') + ':')
        layout.addWidget(self.label)
        self.tabsize_spin = QSpinBox()
        self.tabsize_spin.setRange(2, 8)
        self.tabsize_spin.setValue(load_settings().get('editor_tab_size', 4))
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel(get_text('tab') + get_text('space_count') if 'space_count' in dir() else 'Tab 替换为空格数:'))
        hlayout.addWidget(self.tabsize_spin)
        layout.addLayout(hlayout)
        layout.addStretch()
    def get_settings(self):
        return {'editor_tab_size': self.tabsize_spin.value()}
    def load_current_settings(self):
        self.tabsize_spin.setValue(load_settings().get('editor_tab_size', 4))
    def refresh_texts(self):
        self.label.setText(get_text('tab') + ':')

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(get_text('settings'))
        self.setMinimumSize(600, 400)
        main_layout = QHBoxLayout()
        # 左侧树
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        # 构建树结构
        general = QTreeWidgetItem(self.tree, [get_text('general')])
        general.setData(0, Qt.UserRole, 'general')
        data_dir = QTreeWidgetItem(general, [get_text('data_directory')])
        data_dir.setData(0, Qt.UserRole, 'data_directory')
        shortcut = QTreeWidgetItem(general, [get_text('shortcut_key')])
        shortcut.setData(0, Qt.UserRole, 'shortcut_key')
        language = QTreeWidgetItem(general, [get_text('language')])
        language.setData(0, Qt.UserRole, 'language')
        appearance = QTreeWidgetItem(self.tree, [get_text('appearance')])
        appearance.setData(0, Qt.UserRole, 'appearance')
        theme = QTreeWidgetItem(appearance, [get_text('theme')])
        theme.setData(0, Qt.UserRole, 'theme')
        font = QTreeWidgetItem(appearance, [get_text('font')])
        font.setData(0, Qt.UserRole, 'font')
        editor = QTreeWidgetItem(self.tree, [get_text('editor')])
        editor.setData(0, Qt.UserRole, 'editor')
        editor_font = QTreeWidgetItem(editor, [get_text('font')])
        editor_font.setData(0, Qt.UserRole, 'font')
        editor_tab = QTreeWidgetItem(editor, [get_text('tab')])
        editor_tab.setData(0, Qt.UserRole, 'tab')
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
        self.btn_ok = QPushButton(get_text('ok'))
        self.btn_cancel = QPushButton(get_text('cancel'))
        self.btn_default = QPushButton(get_text('restore_defaults'))
        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_default)
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        vbox = QVBoxLayout()
        vbox.addLayout(main_layout)
        vbox.addLayout(btn_layout)
        self.setLayout(vbox)
        # 每次弹出都刷新data directory面板内容
        self.panels['data directory'].load_current_settings()
        self.panels['tab_editor'].load_current_settings()  # 新增
    def on_tree_changed(self, current, previous):
        if not current: return
        key = current.data(0, Qt.UserRole)
        parent = current.parent()
        pkey = parent.data(0, Qt.UserRole) if parent else None
        panel_key_map = {
            'data_directory': 'data directory',
            'shortcut_key': 'shortcut key',
            'language': 'language',
            'theme': 'theme',
            'font': 'font_appearance',
            'editor': 'font_editor',
            'tab': 'tab_editor',
        }
        if parent:
            if pkey == 'appearance' and key == 'font':
                self.stack.setCurrentWidget(self.panels['font_appearance'])
            elif pkey == 'editor' and key == 'font':
                self.stack.setCurrentWidget(self.panels['font_editor'])
            elif pkey == 'editor' and key == 'tab':
                self.stack.setCurrentWidget(self.panels['tab_editor'])
            else:
                panel_key = panel_key_map.get(key, key)
                if panel_key in self.panels:
                    self.stack.setCurrentWidget(self.panels[panel_key])
        else:
            if key == 'general':
                self.stack.setCurrentWidget(self.panels['data directory'])
            elif key == 'appearance':
                self.stack.setCurrentWidget(self.panels['theme'])
            elif key == 'editor':
                self.stack.setCurrentWidget(self.panels['font_editor'])
    def on_ok(self):
        data_panel = self.panels['data directory']
        valid, msg = data_panel.validate_paths()
        if not valid:
            QMessageBox.warning(self, get_text('warning'), get_text('collection_path_invalid') if 'collections' in msg else get_text('log_path_invalid'))
            return
        changed = data_panel.is_changed()
        s = load_settings()
        s.update(data_panel.get_settings())
        # 保存Tab设置
        s.update(self.panels['tab_editor'].get_settings())
        # 保存快捷键设置
        s.update(self.panels['shortcut key'].get_settings())
        # 保存Appearance字体设置，并立即生效
        font_settings = self.panels['font_appearance'].get_settings()
        s.update(font_settings)
        font = QFont(font_settings['ui_font_family'], font_settings['ui_font_size'])
        QApplication.setFont(font)
        # 保存编辑器字体设置，并立即生效
        editor_font_settings = self.panels['font_editor'].get_settings()
        s.update(editor_font_settings)
        from ui.widgets.code_editor import CodeEditor
        CodeEditor.apply_global_editor_font(editor_font_settings['editor_font_family'], editor_font_settings['editor_font_size'])
        # 保存Tab宽度设置，并立即生效
        tab_size = self.panels['tab_editor'].tabsize_spin.value()
        CodeEditor.apply_global_tab_size(tab_size)
        # 保存语言设置，并立即生效
        lang = self.panels['language'].get_language()
        s['ui_language'] = lang
        from ui.utils.i18n import set_language
        set_language(lang)
        save_settings(s)
        # 刷新所有面板内容
        for panel in self.panels.values():
            if hasattr(panel, 'load_current_settings'):
                panel.load_current_settings()
            if hasattr(panel, 'refresh_texts'):
                panel.refresh_texts()
        self.panels['language'].combo.setCurrentIndex(0 if lang == 'en' else 1)
        self.refresh_texts()  # 刷新设置窗口自身
        # 主动刷新主窗口字体和多语言
        for w in QApplication.topLevelWidgets():
            if hasattr(w, 'refresh_fonts'):
                w.refresh_fonts()
        for w in QApplication.topLevelWidgets():
            if hasattr(w, 'refresh_texts'):
                w.refresh_texts()
        # 主动刷新主窗口快捷键
        for w in QApplication.topLevelWidgets():
            if hasattr(w, 'refresh_shortcuts'):
                w.refresh_shortcuts()
        if changed:
            QMessageBox.information(self, get_text('info'), get_text('settings_saved') + '\n' + get_text('need_restart'))
        self.accept()

    def refresh_texts(self):
        self.setWindowTitle(get_text('settings'))
        # 刷新左侧树所有节点（递归用data）
        def update_tree_texts(item):
            if item is None:
                return
            key = item.data(0, Qt.UserRole)
            if key:
                item.setText(0, get_text(key))
            for i in range(item.childCount()):
                update_tree_texts(item.child(i))
        for i in range(self.tree.topLevelItemCount()):
            update_tree_texts(self.tree.topLevelItem(i))
        # 底部按钮
        self.btn_ok.setText(get_text('ok'))
        self.btn_cancel.setText(get_text('cancel'))
        self.btn_default.setText(get_text('restore_defaults'))
        # 刷新各面板
        for panel in self.panels.values():
            if hasattr(panel, 'refresh_texts'):
                panel.refresh_texts()
        # 刷新主窗口
        mw = self.parent()
        if hasattr(mw, 'refresh_texts'):
            mw.refresh_texts()

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