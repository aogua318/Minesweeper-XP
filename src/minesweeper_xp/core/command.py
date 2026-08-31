"""玩家意图命令（Command）。

定义 UI 发往 Game 的命令基类与各命令数据类（翻开、标记、连开、
重开、换难度），是 UI 与 Core 之间的解耦接口
（实现见 docs/实施文档.md §10）。
"""
from dataclasses import dataclass

from .model.coordinate import Coordinate


class Command:
    """命令基类，所有命令的公共父类型。"""


@dataclass(frozen=True)
class RevealCell(Command):
    """左键翻开命令。"""

    coord: Coordinate  # 要翻开的格子坐标


@dataclass(frozen=True)
class ToggleMark(Command):
    """右键标记命令（旗/问号循环）。"""

    coord: Coordinate  # 要切换标记的格子坐标


@dataclass(frozen=True)
class ChordCell(Command):
    """连开命令（中键/双键）。"""

    coord: Coordinate  # 要连开的已翻开格子坐标


@dataclass(frozen=True)
class RestartGame(Command):
    """重开本局命令（F2）。"""


@dataclass(frozen=True)
class ChangeDifficulty(Command):
    """切换难度命令。"""

    name: str  # 难度名称（beginner/intermediate/expert 等）
