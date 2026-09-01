"""程序入口。

通过 ``python -m minesweeper_xp`` 启动应用：创建 QApplication 与
主窗口，并进入 Qt 事件循环（实现见 docs/实施文档.md §13）。
"""
import sys

from PySide6.QtWidgets import QApplication

from minesweeper_xp.ui.main_window import MainWindow


def main() -> None:
    """创建应用与主窗口并进入事件循环。

    参数:
        无。

    返回:
        无。
    """
    app = QApplication(sys.argv)
    MainWindow().show()  # 显示扫雷主窗口
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
