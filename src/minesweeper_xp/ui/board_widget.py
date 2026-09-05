"""棋盘控件。

负责把鼠标/键盘输入转换为 Command 交给 Game，并用精灵图渲染整个
游戏界面（HUD + 棋盘）；支持 Ctrl+滚轮按档位缩放、窗口拉伸自适应
与终局叠加渲染（实现见 docs/实施文档.md §14.1、§14.2、§14.3，
开发文档 §8、§9、§10）。
"""
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

from minesweeper_xp.core.command import ChordCell, Command, RevealCell, ToggleMark
from minesweeper_xp.core.enums import FaceState, GameStatus
from minesweeper_xp.core.event import Event, GameLost, GameStateChanged
from minesweeper_xp.core.game import Game
from minesweeper_xp.core.model.coordinate import Coordinate
from minesweeper_xp.geometry.board_geometry import (
    BASE_CELL,
    BOARD_LEFT,
    BOARD_TOP,
    ZOOM_STEPS,
    fit_scale,
    widget_pos_to_cell,
    window_size,
)
from minesweeper_xp.rendering.block_renderer import draw_board, draw_loss_overlay
from minesweeper_xp.rendering.hud_renderer import draw_hud, face_rect
from minesweeper_xp.rendering.sprite_loader import SpriteSet, load_sprite_set
from minesweeper_xp.rendering.theme import Theme, load_theme
from minesweeper_xp.ui.face_button import FaceButton


class BoardWidget(QWidget):
    """把鼠标/键盘事件转成 Command 交给 Game，并用精灵图整体重绘。"""

    game_changed = Signal()  # 任意 Game 事件触发，驱动重绘

    def __init__(self, game: Game, res_dir: Path) -> None:
        """初始化控件：加载主题精灵、绑定 Game、订阅事件、启动计时。

        参数:
            game: 绑定的 Game 实例。
            res_dir: res 资源根目录（主题与精灵图所在）。

        返回:
            无。
        """
        super().__init__()
        self._game: Game = game  # 绑定的游戏
        self._game.subscribe(self._on_event)  # 订阅事件（重绘 + 终局叠加）
        self.game_changed.connect(self.update)  # 信号连接重绘
        self.setMouseTracking(True)  # 跟踪鼠标位置（供后续高亮使用）
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # 接收键盘事件（方向键导航）

        # 主题与精灵：彩色/单色两套都加载，按 self._game.color 选用
        self._theme: Theme = load_theme(res_dir / "themes/classic_xp.json")
        self._sprites_color: SpriteSet = load_sprite_set(self._theme.sprites, res_dir)
        self._sprites_mono: SpriteSet = load_sprite_set(self._theme.sprites, res_dir, mono=True)
        self._background_color: str = self._theme.colors["background"]  # 窗口底色

        # 缩放与输入状态
        self._scale: float = 1.0  # 当前缩放系数（Ctrl+滚轮改档，拉伸窗口自适应）
        self._pressed: Coordinate | None = None  # 左键按住的格子（画按下外观）
        self._preview: Coordinate | None = None  # 双键 chord 预览中心
        self._lost: tuple | None = None  # 终局叠加信息 (LostReason, Coordinate)
        self._focus: Coordinate = Coordinate(0, 0)  # 键盘焦点格（初始左上角）
        self._keyboard_mode: bool = False  # 是否处于键盘操作模式（画焦点高亮）
        self._face_override: FaceState | None = None  # UI 瞬态笑脸覆盖（WOW/PRESSED）

        # 笑脸按钮：覆盖在 HUD 笑脸区域上的透明子控件，只管点击
        self._face_button: FaceButton = FaceButton(self)
        self._face_button.face_pressed.connect(self._on_face_pressed)
        self._face_button.face_released.connect(self._on_face_released)
        self._update_face_geometry()

        self._tick_timer: QTimer = QTimer(self)  # 每秒驱动 game.tick 的定时器
        self._tick_timer.setInterval(1000)  # 1 秒触发一次
        self._tick_timer.timeout.connect(self._game.tick)  # 每秒推进游戏计时
        self._tick_timer.start()  # 启动定时器

    # ---------- 事件订阅 ----------

    def _on_event(self, event: Event) -> None:
        """订阅 Game 事件：维护终局叠加信息并广播重绘信号。

        参数:
            event: Core 发布的事件。

        返回:
            无。
        """
        if isinstance(event, GameLost):
            self._lost = (event.reason, event.coord)  # 记录失败原因与触发格
        elif isinstance(event, GameStateChanged) and event.status is not GameStatus.LOST:
            self._lost = None  # 非 LOST 状态（重开/胜利）清除叠加
        self.game_changed.emit()

    # ---------- 坐标换算 ----------

    def _coord_at(self, pos) -> Coordinate | None:
        """把鼠标位置换算成棋盘坐标。

        参数:
            pos: 鼠标位置（QPointF，控件物理像素）。

        返回:
            对应的棋盘坐标；落在棋盘外（HUD/边框区域）时返回 None。
        """
        return widget_pos_to_cell(pos.x(), pos.y(), self._scale,
                                  self._game.board.rows, self._game.board.cols)

    # ---------- 输入分发 ----------

    def _dispatch(self, coord: Coordinate | None, command: Command) -> None:
        """把命令交给 Game（坐标有效且在棋盘内才分发）。

        参数:
            coord: 命令对应的目标格（None 表示无效，不分发）。
            command: 要分发的命令。

        返回:
            无。
        """
        if coord is not None and self._game.board.in_bounds(coord):
            self._game.dispatch(command)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """处理鼠标按下：左键记录按住格（松开时才翻开）、右键标记、
        左+右预览连开、中键直接连开。

        参数:
            event: 鼠标事件。

        返回:
            无。
        """
        self._keyboard_mode = False  # 转入鼠标操作，取消键盘焦点高亮
        coord = self._coord_at(event.position())  # 换算坐标
        if event.button() is Qt.MouseButton.LeftButton:
            self._pressed = coord  # 只记录，松开时在同格才翻开
            if coord is not None:
                self._face_override = FaceState.WOW  # 按住时惊讶脸
        elif event.button() is Qt.MouseButton.RightButton:
            if self._pressed is not None and self._pressed == coord:
                self._preview = coord  # 左键按住后再按右键：chord 预览
            else:
                self._dispatch(coord, ToggleMark(coord))  # 右键在按下时标记
        elif event.button() is Qt.MouseButton.MiddleButton:
            self._dispatch(coord, ChordCell(coord))  # 中键：连开
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """处理鼠标松开：左键同格翻开、双键 chord 执行连开，否则取消。

        参数:
            event: 鼠标事件。

        返回:
            无。
        """
        coord = self._coord_at(event.position())  # 换算坐标
        if event.button() is Qt.MouseButton.LeftButton:
            if self._face_override is FaceState.WOW:  # 松开恢复正常笑脸
                self._face_override = None
            if self._preview is not None:  # 双键 chord：松开左键时执行
                if coord == self._preview:
                    self._dispatch(coord, ChordCell(coord))
                self._preview = None
            elif coord is not None and coord == self._pressed:
                self._dispatch(coord, RevealCell(coord))  # 在按住的格上松开：翻开
            self._pressed = None
        elif event.button() is Qt.MouseButton.RightButton and self._preview is not None:
            self._preview = None  # 先松右键：取消预览
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """处理键盘：方向键移动焦点格、空格翻开、F 标记、回车连开。

        参数:
            event: 键盘事件。

        返回:
            无。
        """
        key = event.key()
        if key == Qt.Key.Key_Up:
            self._move_focus(-1, 0)
        elif key == Qt.Key.Key_Down:
            self._move_focus(1, 0)
        elif key == Qt.Key.Key_Left:
            self._move_focus(0, -1)
        elif key == Qt.Key.Key_Right:
            self._move_focus(0, 1)
        elif key == Qt.Key.Key_Space:
            self._dispatch(self._focus, RevealCell(self._focus))
        elif key == Qt.Key.Key_F:
            self._dispatch(self._focus, ToggleMark(self._focus))
        elif key == Qt.Key.Key_Return:
            self._dispatch(self._focus, ChordCell(self._focus))
        else:
            super().keyPressEvent(event)

    def _move_focus(self, drow: int, dcol: int) -> None:
        """移动键盘焦点格（钳制在棋盘内）。

        参数:
            drow: 行方向增量（-1/0/1）。
            dcol: 列方向增量（-1/0/1）。

        返回:
            无。
        """
        self._keyboard_mode = True  # 进入键盘操作模式（画焦点高亮）
        board = self._game.board
        row = min(max(self._focus.row + drow, 0), board.rows - 1)  # 行钳制
        col = min(max(self._focus.col + dcol, 0), board.cols - 1)  # 列钳制
        self._focus = Coordinate(row, col)
        self.update()

    # ---------- 缩放 ----------

    def resizeEvent(self, event: QEvent) -> None:
        """窗口拉伸时按可用空间自适应缩放（保持比例、不裁切）。

        参数:
            event: 窗口尺寸变化事件。

        返回:
            无。
        """
        super().resizeEvent(event)
        board = self._game.board
        new_scale = fit_scale(board.rows, board.cols, self.width(), self.height())
        if abs(new_scale - self._scale) > 0.01:  # 变化明显才重绘，避免抖动
            self._scale = new_scale
            self._update_face_geometry()
            self.update()
        else:
            self._update_face_geometry()  # 尺寸变了也要同步笑脸按钮位置

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Ctrl+滚轮按档位缩放，并把窗口调整为对应尺寸。

        参数:
            event: 滚轮事件。

        返回:
            无。
        """
        if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            event.ignore()  # 未按 Ctrl：不处理滚轮
            return
        idx = ZOOM_STEPS.index(self._scale) if self._scale in ZOOM_STEPS else 2  # 默认 1.0 档
        idx += 1 if event.angleDelta().y() > 0 else -1  # 向上放大、向下缩小
        self._scale = ZOOM_STEPS[max(0, min(len(ZOOM_STEPS) - 1, idx))]  # 钳制档位
        self._apply_window_size()
        self._update_face_geometry()
        self.update()
        event.accept()

    def _apply_window_size(self) -> None:
        """把顶层窗口调整为当前缩放对应的尺寸（客户区正好放下棋盘）。

        参数:
            无。

        返回:
            无。
        """
        board = self._game.board
        width, height = window_size(board.rows, board.cols, self._scale)
        window = self.window()  # 顶层窗口
        handle = window.windowHandle()
        if handle is not None:  # 补上窗口边框尺寸，保证客户区（而非外框）符合目标
            margins = handle.frameMargins()
            width += margins.left() + margins.right()
            height += margins.top() + margins.bottom()
        window.resize(width, height)

    def _update_face_geometry(self) -> None:
        """按当前缩放更新笑脸按钮子控件的位置与大小。

        参数:
            无。

        返回:
            无。
        """
        width = 22 + self._game.board.cols * BASE_CELL  # 内容区逻辑宽度 W
        rect = face_rect(width)  # 笑脸按钮逻辑矩形
        self._face_button.setGeometry(
            round(rect.x() * self._scale),
            round(rect.y() * self._scale),
            round(rect.width() * self._scale),
            round(rect.height() * self._scale),
        )

    def _on_face_pressed(self) -> None:
        """笑脸按钮按下：切换为 PRESSED 笑脸外观。

        参数:
            无。

        返回:
            无。
        """
        self._face_override = FaceState.PRESSED
        self.update()

    def _on_face_released(self) -> None:
        """笑脸按钮松开：恢复正常笑脸外观（点击重启由 MainWindow 接管）。

        参数:
            无。

        返回:
            无。
        """
        self._face_override = None
        self.update()

    # ---------- 绘制 ----------

    def paintEvent(self, _event: QPaintEvent) -> None:
        """整体绘制：先 HUD 后棋盘，全部按 100% 逻辑坐标画，
        缩放由 painter.scale 统一处理（最近邻，保持像素风清晰）。

        参数:
            _event: 绘制事件（未使用）。

        返回:
            无。
        """
        painter = QPainter(self)
        painter.scale(self._scale, self._scale)

        board = self._game.board
        width = 22 + board.cols * BASE_CELL  # 内容区逻辑宽度 W
        height = 65 + board.rows * BASE_CELL  # 内容区逻辑高度 H
        painter.fillRect(0, 0, width, height, QColor(self._background_color))  # 底色

        sprites = self._sprites_mono if not self._game.color else self._sprites_color
        draw_hud(painter, sprites, self._game.state.remaining_mines,
                 self._game.state.elapsed_seconds, self._face_state(), width)

        # 棋盘：平移到棋盘逻辑起点后逐格绘制
        painter.save()
        painter.translate(BOARD_LEFT, BOARD_TOP)
        draw_board(painter, board, sprites, BASE_CELL, pressed=self._pressed)
        if self._lost is not None:  # 终局叠加（失败显示）
            reason, trigger = self._lost
            draw_loss_overlay(painter, board, sprites, BASE_CELL, reason, trigger)
        self._paint_focus(painter)  # 键盘焦点高亮最后画（不被图块覆盖）
        painter.restore()

    def _face_state(self) -> FaceState:
        """返回当前应绘制的笑脸状态（UI 瞬态覆盖优先于 Core 状态）。

        参数:
            无。

        返回:
            笑脸状态。
        """
        if self._face_override is not None:
            return self._face_override
        return self._game.state.face_state

    def _paint_focus(self, painter: QPainter) -> None:
        """键盘操作模式下给焦点格画高亮边框。

        参数:
            painter: QPainter 绘制目标（已平移到棋盘坐标系）。

        返回:
            无。
        """
        if not self._keyboard_mode:
            return
        painter.setPen(QColor("#FF0000"))  # 红色 1px 边框，与 LED 色一致
        painter.drawRect(
            self._focus.col * BASE_CELL, self._focus.row * BASE_CELL,
            BASE_CELL - 1, BASE_CELL - 1,
        )
