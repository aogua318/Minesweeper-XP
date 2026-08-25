"""程序入口。

通过 ``python -m minesweeper_xp`` 启动应用：创建 QApplication 与
主窗口，并进入 Qt 事件循环（实现见 docs/实施文档.md §0.4、§13）。
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow


def main() -> None:
    """创建应用与主窗口并进入事件循环。"""
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Minesweeper XP")
    window.resize(300, 360)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
