"""音效管理：订阅 Core 事件播放对应音效（开发文档 §13、实施文档 §14.2.6）。

原版 WINMINE 的音效（432=点击/滴答、433=胜利、434=失败）在本项目
从 res/sounds/*.wav 播放；滴答频率可配置为每秒/每分钟/关闭。
"""
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

from minesweeper_xp.core.event import CellsRevealed, Event, GameLost, GameWon, TimerTicked


class SoundManager:
    """把 Core 事件映射为音效并负责播放。"""

    def __init__(self, res_dir: Path) -> None:
        """加载音效资源并初始化默认设置。

        参数:
            res_dir: res 资源根目录（音效位于 res/sounds/）。

        返回:
            无。
        """
        self._tick: QSoundEffect = self._load(res_dir / "sounds/tick.wav")  # 点击/滴答声
        self._win: QSoundEffect = self._load(res_dir / "sounds/win.wav")  # 胜利音效
        self._lose: QSoundEffect = self._load(res_dir / "sounds/lose.wav")  # 失败音效
        self.enabled: bool = True  # 音效总开关
        self.volume: float = 0.8  # 音量（0.0~1.0），阶段 6 接入设置
        self.tick_mode: str = "second"  # 滴答频率：second（每秒）/ minute（每分钟）/ off

    def _load(self, path: Path) -> QSoundEffect:
        """从文件加载一个音效。

        参数:
            path: 音效文件路径。

        返回:
            已加载音源的 QSoundEffect 实例。
        """
        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(str(path)))
        effect.setVolume(self.volume)
        return effect

    def handle(self, event: Event) -> None:
        """响应 Core 事件播放音效（作为 Game 的事件监听器注册）。

        参数:
            event: Core 发布的事件。

        返回:
            无。
        """
        if not self.enabled:
            return
        if isinstance(event, GameWon):
            self._win.play()
        elif isinstance(event, GameLost):
            self._lose.play()
        elif isinstance(event, CellsRevealed):
            self._tick.play()
        elif isinstance(event, TimerTicked):
            self._play_tick(event.seconds)

    def _play_tick(self, seconds: int) -> None:
        """按 tick_mode 决定是否播滴答声。

        参数:
            seconds: 当前已计秒数（TimerTicked 事件携带）。

        返回:
            无。
        """
        if self.tick_mode == "second" or (self.tick_mode == "minute" and seconds % 60 == 0):
            self._tick.play()
