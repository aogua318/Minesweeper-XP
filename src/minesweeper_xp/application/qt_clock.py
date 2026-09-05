"""Qt 环境下的计时实现。

基于 QTimer 驱动 elapsed 递增，接入 Core 的 Clock 接口，
供 UI 层在应用中使用（实现见 docs/实施文档.md §13）。
"""
from PySide6.QtCore import QTimer

from minesweeper_xp.core.clock import Clock


class QtClock(Clock):
    """每 1000ms 递增 elapsed 的时钟。"""

    def __init__(self) -> None:
        """初始化时钟：创建 1 秒定时器并绑定超时回调。

        参数:
            无。

        返回:
            无。
        """
        self._elapsed: int = 0  # 已计秒数（0~999，999 封顶）
        self._started: bool = False  # 本局计时是否已启动（区分"未开局"与"暂停"）
        self._timer: QTimer = QTimer()  # 驱动计时的定时器
        self._timer.setInterval(1000)  # 每 1000ms 触发一次
        self._timer.timeout.connect(self._on_timeout)  # 超时回调

    def _on_timeout(self) -> None:
        """定时器回调：elapsed 递增并封顶 999。

        参数:
            无。

        返回:
            无。
        """
        if self._elapsed >= 999:
            self._elapsed = 999
            self.stop()
        else:
            self._elapsed += 1

    def start(self) -> None:
        """开始计时。"""
        self._started = True
        self._timer.start()

    def stop(self) -> None:
        """停止计时（终局后调用）。"""
        self._started = False
        self._timer.stop()

    def pause(self) -> None:
        """暂停计时（如窗口最小化）。保留 started 状态，恢复时据此继续。"""
        self._timer.stop()

    def resume(self) -> None:
        """恢复计时（仅在计时已启动且未封顶时继续，避免未开局就计时）。"""
        if self._started and self._elapsed < 999:
            self._timer.start()

    def reset(self) -> None:
        """重置为初始状态（停表并归零）。"""
        self.stop()
        self._elapsed = 0

    @property
    def elapsed(self) -> int:
        """当前已计秒数（0~999，999 封顶）。"""
        return self._elapsed
