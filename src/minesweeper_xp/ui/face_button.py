"""笑脸按钮控件。

独立子控件，覆盖在 BoardWidget 绘制的 HUD 笑脸区域上，负责处理
鼠标按下/松开并发出信号；笑脸的精灵图块仍由 BoardWidget 按
FaceState 绘制（实现见 docs/实施文档.md §14.2.3）。
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget


class FaceButton(QWidget):
    """笑脸按钮：按下显示 PRESSED，松开时若在按钮内则触发新游戏。"""

    clicked = Signal()  # 按下后在按钮范围内松开（视为点击，触发新游戏）
    face_pressed = Signal()  # 鼠标按下（BoardWidget 据此画 PRESSED 笑脸）
    face_released = Signal()  # 鼠标松开（BoardWidget 据此恢复正常笑脸）

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化笑脸按钮。

        参数:
            parent: 父控件（BoardWidget）。

        返回:
            无。
        """
        super().__init__(parent)
        self._is_pressed: bool = False  # 鼠标是否按在按钮上

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """处理鼠标按下：左键记录按下状态并通知父控件切换笑脸外观。

        参数:
            event: 鼠标事件。

        返回:
            无。
        """
        if event.button() is Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.face_pressed.emit()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """处理鼠标松开：松开位置在按钮内才视为点击（触发新游戏）。

        参数:
            event: 鼠标事件。

        返回:
            无。
        """
        inside = self.rect().contains(event.position().toPoint())  # 是否在按钮内松开
        if self._is_pressed and inside:
            self.clicked.emit()
        self._is_pressed = False
        self.face_released.emit()
