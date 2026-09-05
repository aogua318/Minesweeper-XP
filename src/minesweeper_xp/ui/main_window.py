"""主窗口。

负责创建 Game 与棋盘控件、组装主界面、接音效与笑脸按钮、处理
窗口级快捷键、最小化暂停与初始/最小尺寸（实现见 docs/实施文档.md
§13、§14.2、§14.3）。
"""
from pathlib import Path

from PySide6.QtCore import QEvent
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow

from minesweeper_xp.application.qt_clock import QtClock
from minesweeper_xp.audio.sound_manager import SoundManager
from minesweeper_xp.core.command import RestartGame
from minesweeper_xp.core.game import Game
from minesweeper_xp.geometry.board_geometry import MIN_SCALE, window_size
from minesweeper_xp.ui.board_widget import BoardWidget


class MainWindow(QMainWindow):
    """扫雷主窗口：Game + 棋盘控件 + 音效 + F2 重开 + 最小化暂停。"""

    def __init__(self) -> None:
        """初始化主窗口：创建 Game、棋盘控件、音效并注册快捷键与尺寸。

        参数:
            无。

        返回:
            无。
        """
        super().__init__()
        self._res_dir: Path = Path(__file__).resolve().parents[3] / "res"  # 资源根目录
        self._game: Game = Game(clock=QtClock())  # 游戏实例（真实时钟）
        self._game.new_game("beginner", 9, 9, 10)  # 默认初级开局
        self._board: BoardWidget = BoardWidget(self._game, self._res_dir)  # 棋盘控件
        self.setCentralWidget(self._board)  # 棋盘作为中央控件

        self._sound: SoundManager = SoundManager(self._res_dir)  # 音效管理
        self._game.subscribe(self._sound.handle)  # 订阅 Core 事件播放音效

        # 笑脸按钮点击 → 重开一局（按钮外观由 BoardWidget 事件驱动）
        self._board.face_button.clicked.connect(
            lambda: self._game.dispatch(RestartGame())
        )

        rows, cols = 9, 9  # 当前难度（阶段 6 换难度时同步更新最小/初始尺寸）
        self.setMinimumSize(*window_size(rows, cols, MIN_SCALE))  # 50% 缩放不裁切
        self.resize(*window_size(rows, cols, 1.0))  # 初始 100% 缩放

        shortcut = QShortcut(QKeySequence("F2"), self)  # F2 重开本局
        shortcut.activated.connect(lambda: self._game.dispatch(RestartGame()))

    def changeEvent(self, event: QEvent) -> None:
        """窗口状态变化：最小化暂停计时，恢复显示继续计时。

        参数:
            event: 窗口事件。

        返回:
            无。
        """
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                self._game.pause_timer()
            else:
                self._game.resume_timer()
        super().changeEvent(event)
