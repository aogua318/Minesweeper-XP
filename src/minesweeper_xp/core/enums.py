"""Core 使用的枚举类型。

集中定义格子的右键标记状态（Mark）、游戏生命周期状态（GameStatus）
与笑脸按钮状态（FaceState），供 Core 各模块与 UI 共享
（实现见 docs/实施文档.md §1）。
"""

"""Core 使用的枚举类型。"""
from enum import Enum, auto


class Mark(Enum):
    """格子的右键标记状态。"""

    NONE = auto()  # 无
    FLAG = auto()  # 旗
    QUESTION = auto()  # 问号


class GameStatus(Enum):
    """游戏生命周期状态（开发文档 §6.8）。"""

    READY = auto()  # 开始，还没点第一下
    PLAYING = auto()  # 游戏中 计时
    WON = auto()  # 胜利
    LOST = auto()  # 失败


class FaceState(Enum):
    """笑脸按钮状态。"""

    NORMAL = auto()  # 平常
    WOW = auto()  # 在棋盘上按住鼠标
    LOST = auto()  # 失败
    WINNER = auto()  # 胜利
    PRESSED = auto()  # 按住笑脸
