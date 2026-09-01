"""主窗口。

负责创建 Game 与棋盘控件、组装主界面、处理窗口级快捷键与重开
（实现见 docs/实施文档.md §13）。
"""
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow

from minesweeper_xp.application.qt_clock import QtClock
from minesweeper_xp.core.command import RestartGame
from minesweeper_xp.core.game import Game
from minesweeper_xp.ui.board_widget import BoardWidget


class MainWindow(QMainWindow):
    """扫雷主窗口（Vertical Slice：Game + 棋盘控件 + F2 重开）。"""

    def __init__(self) -> None:
        """初始化主窗口：创建 Game、棋盘控件并注册快捷键。

        参数:
            无。

        返回:
            无。
        """
        super().__init__()
        self._game: Game = Game(clock=QtClock())  # 游戏实例（真实时钟）
        self._game.new_game("beginner", 9, 9, 10)  # 默认初级开局
        self._board: BoardWidget = BoardWidget(self._game)  # 棋盘控件
        self.setCentralWidget(self._board)  # 棋盘作为中央控件
        self.resize(9 * 16 + 24, 9 * 16 + 65)  # 窗口尺寸（棋盘 + 边框/标题栏余量）
        shortcut = QShortcut(QKeySequence("F2"), self)  # F2 重开本局
        shortcut.activated.connect(lambda: self._game.dispatch(RestartGame()))
