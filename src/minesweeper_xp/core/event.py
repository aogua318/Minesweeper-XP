"""Core 对外发布的事件（Event）。

定义事件基类与各类状态变更事件（翻开、标记、计时、笑脸、胜负等），
供 UI 订阅后驱动重绘与音效（实现见 docs/实施文档.md §10）。
"""
from dataclasses import dataclass

from .enums import FaceState, GameStatus, Mark
from .model.coordinate import Coordinate


class Event:
    """事件基类，所有事件的公共父类型。"""


@dataclass(frozen=True)
class GameStateChanged(Event):
    """游戏状态切换事件（READY/PLAYING/WON/LOST）。"""

    status: GameStatus  # 切换后的游戏状态


@dataclass(frozen=True)
class CellRevealed(Event):
    """单格翻开事件。"""

    coord: Coordinate  # 被翻开的格子坐标
    number: int  # 该格邻域雷数（0~8）


@dataclass(frozen=True)
class CellsRevealed(Event):
    """批量翻开事件（洪水填充/连开一次翻多格）。"""

    cells: tuple[tuple[Coordinate, int], ...]  # (坐标, 邻域雷数) 元组序列


@dataclass(frozen=True)
class CellMarked(Event):
    """格子标记变化事件。"""

    coord: Coordinate  # 标记变化的格子坐标
    mark: Mark  # 变化后的标记状态


@dataclass(frozen=True)
class FlagsChanged(Event):
    """剩余雷数变化事件。"""

    remaining: int  # 当前剩余雷数


@dataclass(frozen=True)
class TimerTicked(Event):
    """计时事件（每秒触发）。"""

    seconds: int  # 当前已计秒数


@dataclass(frozen=True)
class FaceChanged(Event):
    """笑脸按钮状态变化事件。"""

    face: FaceState  # 新的笑脸状态


@dataclass(frozen=True)
class GameWon(Event):
    """胜利事件。"""


@dataclass(frozen=True)
class GameLost(Event):
    """失败事件。"""
