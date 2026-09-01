"""计时抽象（Clock）。

定义 Core 依赖的计时接口与测试用的 FakeClock，使 Core 不直接依赖
Qt 的 QTimer（实现见 docs/实施文档.md §9）。
"""
from typing import Protocol


class Clock(Protocol):
    """计时接口（Core 依赖的最小契约）。"""

    def start(self) -> None:
        """开始计时。"""
        ...

    def stop(self) -> None:
        """停止计时（终局后调用）。"""
        ...

    def pause(self) -> None:
        """暂停计时（如窗口最小化）。"""
        ...

    def resume(self) -> None:
        """恢复计时。"""
        ...

    def reset(self) -> None:
        """重置为初始状态（未运行、未暂停、0 秒）。"""
        ...

    @property
    def elapsed(self) -> int:
        """当前已计秒数（0~999，999 封顶）。"""
        ...



class FakeClock:
    """手动推进的时钟，供测试使用。"""

    def __init__(self) -> None:
        self._running: bool = False  # 是否运行中
        self._paused: bool = False  # 是否暂停
        self._elapsed: int = 0  # 已计秒数

    def start(self) -> None:
        """开始计时。"""
        self._running = True

    def stop(self) -> None:
        """停止计时。"""
        self._running = False

    def pause(self) -> None:
        """暂停计时。"""
        self._paused = True

    def resume(self) -> None:
        """恢复计时。"""
        self._paused = False

    def reset(self) -> None:
        """重置为初始状态（未运行、未暂停、0 秒）。"""
        self._running = False
        self._paused = False
        self._elapsed = 0

    def tick(self, seconds: int = 1) -> None:
        """手动推进 elapsed。

        参数:
            seconds: 推进的秒数，默认 1。

        返回:
            无。
        """
        if self._running and not self._paused:
            self._elapsed = min(999, self._elapsed + seconds)

    @property
    def elapsed(self) -> int:
        """当前已计秒数。"""
        return self._elapsed
