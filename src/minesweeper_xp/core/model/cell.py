"""Cell 领域对象。

定义单个格子的可变游戏状态：是否雷、是否翻开、右键标记、
邻域雷数（实现见 docs/实施文档.md §2）。
"""
"""Cell 领域对象。"""

from dataclasses import dataclass, field

from ..enums import Mark


@dataclass
class Cell:
    """单个格子的可变游戏状态，位置由 Board 网格承载。"""

    is_mine: bool = False  # 是否为雷
    is_revealed: bool = False  # 是否已翻开
    mark: Mark = Mark.NONE  # 右键标记
    adjacent_mines: int = 0  # 3×3 邻域雷数（翻开后有效）