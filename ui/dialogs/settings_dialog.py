from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Preferences / Settings')
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('应用设置（可扩展更多选项）'))
        # 示例设置项，可扩展
        # layout.addWidget(QLabel('示例设置项1: ...'))
        # layout.addWidget(QLabel('示例设置项2: ...'))
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton('OK')
        btn_cancel = QPushButton('Cancel')
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout) 