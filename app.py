"""
项目文件输出工具主程序
用于启动应用程序
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import FileMergeApp


def main():
    """程序入口函数"""
    app = QApplication(sys.argv)
    window = FileMergeApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
