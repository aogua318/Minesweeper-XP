"""棋盘控件。

负责把鼠标/键盘输入转换为 Command 交给 Game，并监听事件驱动
棋盘绘制（Vertical Slice 先画色块/数字，后续替换为精灵渲染，
见 docs/实施文档.md §13、§14.1）。
"""
from PySide6.QtCore import Qt, QTimer, Signal, QRect
from PySide6.QtGui import QMouseEvent, QPainter, QColor
from PySide6.QtWidgets import QWidget

from minesweeper_xp.core.command import ChordCell, RevealCell, ToggleMark
from minesweeper_xp.core.enums import Mark
from minesweeper_xp.core.game import Game
from minesweeper_xp.core.model.coordinate import Coordinate


class BoardWidget(QWidget):
    """把鼠标事件转成 Command 交给 Game，再根据事件重绘。"""

    game_changed = Signal()  # 任意 Game 事件触发，驱动重绘

    def __init__(self, game: Game) -> None:
        """初始化控件：绑定 Game、订阅事件、启动计时。

        参数:
            game: 绑定的 Game 实例。

        返回:
            无。
        """
        super().__init__()
        self._game: Game = game  # 绑定的游戏
        self._game.subscribe(lambda _event: self.game_changed.emit())  # 任何事件都触发重绘
        self.game_changed.connect(self.update)  # 信号连接重绘
        self.setMouseTracking(True)  # 跟踪鼠标位置（供后续高亮使用）
        self._tick_timer: QTimer = QTimer(self)  # 每秒驱动 game.tick 的定时器
        self._tick_timer.setInterval(1000)  # 1 秒触发一次
        self._tick_timer.timeout.connect(self._game.tick)  # 每秒推进游戏计时
        self._tick_timer.start()  # 启动定时器

    def cell_size(self) -> int:
        """返回单格像素边长。

        参数:
            无。

        返回:
            单格边长（像素）。
        """
        return 16

    def _coord_at(self, pos) -> Coordinate:
        """把鼠标位置换算成棋盘坐标。

        参数:
            pos: 鼠标位置（QPointF）。

        返回:
            对应的棋盘坐标。
        """
        return Coordinate(pos.y() // self.cell_size(), pos.x() // self.cell_size())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """处理鼠标按下：左键翻开、右键标记、中键连开。

        参数:
            event: 鼠标事件。

        返回:
            无。
        """
        coord = self._coord_at(event.pos())  # 换算坐标
        if not self._game.board.in_bounds(coord):  # 不在棋盘内
            return

        if event.button() is Qt.MouseButton.LeftButton:  # 左键：翻开
            self._game.dispatch(RevealCell(coord))
        elif event.button() is Qt.MouseButton.RightButton:  # 右键：标记
            self._game.dispatch(ToggleMark(coord))
        elif event.button() is Qt.MouseButton.MiddleButton:  # 中键：连开
            self._game.dispatch(ChordCell(coord))

        # elif (event.buttons() & Qt.MouseButton.LeftButton) and (event.buttons() & Qt.MouseButton.RightButton): # 左右键同时按 连开
        #     self._game.dispatch(ChordCell(coord))

    def paintEvent(self, _event) -> None:
        """绘制棋盘：色块/数字的最小实现。

        补充说明:
            棋盘坐标原点在左上角 (0, 0)，9×9 时绘制区域为 0~144 像素。

        参数:
            _event: 绘制事件（未使用）。

        返回:
            无。
        """
        painter = QPainter(self)  # 画笔
        s = self.cell_size()  # 格子边长
        painter.fillRect(0, 0, 144+6, 144+6, QColor(128, 128, 128))
        painter.fillRect(0, 0, 144+6, 144+6, QColor(128, 128, 128))
        # 内容
        painter.setPen(Qt.GlobalColor.black)  # 设置文字颜色

        # 遍历绘制格子
        for coord in self._game.board.all_coords():
            cell = self._game.board.cell(coord)
            x, y = coord.col * s, coord.row * s
            x += 3
            y += 3
            rect = QRect(x, y, s, s)  # 定义矩形

            if cell.is_revealed:  # 翻开的
                # 背景
                painter.fillRect(x, y, s, s, QColor(192, 192, 192))
                painter.fillRect(x , y, 2, s, QColor(128, 128, 128))
                painter.fillRect(x, y , s, 2, QColor(128, 128, 128))
                if cell.is_mine:
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "X")  # 绘制文字：雷
                    continue

                # 非雷逻辑：根据内容自动绘制
                if cell.adjacent_mines != 0:  # 不为 0 才画数字，0 为背景
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(cell.adjacent_mines))

            else:  # 没翻开的
                # 背景
                painter.fillRect(x, y, s, s, QColor(192, 192, 192))


                painter.fillRect(x , y, 2, s, QColor(255, 255, 255))
                painter.fillRect(x, y , s, 2, QColor(255, 255, 255))

                painter.fillRect(x + s - 2, y, 2, s, QColor(128, 128, 128))
                painter.fillRect(x, y + s - 2, s, 2, QColor(128, 128, 128))

                # painter.fillRect(x + 2, y, s, 2, QColor(192, 192, 192))
                # painter.fillRect(x, y + 2, 2, s, QColor(192, 192, 192))

                # 内容
                if cell.mark is Mark.FLAG:
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "F")
                elif cell.mark is Mark.QUESTION:
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "?")
