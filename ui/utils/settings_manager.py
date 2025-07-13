import os
import sys
import json

def get_default_data_dir():
    if getattr(sys, 'frozen', False):
        # 打包环境，放到exe同级user-data目录
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, 'user-data')
    else:
        # 源码环境
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../user-data"))

DATA_DIR = get_default_data_dir()
DEFAULT_SETTINGS = {
    "collections_path": os.path.join(DATA_DIR, "collections.json"),
    "log_path": os.path.join(DATA_DIR, "postsuperman.log"),
    "editor_tab_size": 4,  # 编辑器Tab空格数
    "ui_font_family": "微软雅黑",  # UI默认字体
    "ui_font_size": 12,  # UI默认字体大小
    "editor_font_family": "Consolas",  # 编辑器默认字体
    "editor_font_size": 12,  # 编辑器默认字号
    "ui_language": "zh",  # UI默认语言
    "shortcuts": {
        "send": "Ctrl+Enter",
        "save": "Ctrl+S",
        "switch_tab": "Ctrl+Tab"
    }
}
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    # 确保目录存在
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False) 