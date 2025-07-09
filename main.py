from ui.main_window_refactored import MainWindow
from PyQt5.QtWidgets import QApplication
import sys
import traceback
from PyQt5.QtGui import QFont
from ui.utils.settings_manager import load_settings
from ui.utils.i18n import set_language

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    print("=" * 50)
    print("捕获到未处理的异常:")
    print(f"异常类型: {exc_type}")
    print(f"异常信息: {exc_value}")
    print("异常堆栈:")
    traceback.print_tb(exc_traceback)
    print("=" * 50)
    # 不退出程序，让程序继续运行
    return True

if __name__ == '__main__':
    # 设置全局异常处理器
    sys.excepthook = global_exception_handler
    
    # 启动前设置语言
    s = load_settings()
    set_language(s.get('ui_language', 'zh'))
    
    app = QApplication(sys.argv)
    # 应用全局字体设置
    font = QFont(s.get('ui_font_family', '微软雅黑'), s.get('ui_font_size', 12))
    app.setFont(font)
    window = MainWindow()
    window.show()
    
    # 确保程序持续运行，直到用户手动关闭
    print("PostSuperman 启动成功！")
    print("程序将持续运行，直到您手动关闭窗口...")
    
    # 使用exec_()而不是sys.exit()，让程序自然运行
    app.exec_() 