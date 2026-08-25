"""棋盘坐标（Coordinate）。

定义不可变的行列值对象，供棋盘寻址与算法间传递位置
（实现见 docs/实施文档.md §2）。
"""
"""棋盘坐标。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinate:
    """棋盘中的一行一列（不可变值对象）。"""

    row: int
    col: int