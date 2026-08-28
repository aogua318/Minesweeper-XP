"""Board 领域对象。

持有 rows×cols 的 Cell 网格，提供越界判断、取格、遍历
与 3×3 邻居查询等基础操作（实现见 docs/实施文档.md §2）。
"""
from dataclasses import dataclass, field
from typing import Iterator

from .cell import Cell
from .coordinate import Coordinate


@dataclass
class Board:
    """rows×cols 的格子网格。"""

    rows: int  # 棋盘行数
    cols: int  # 棋盘列数
    _cells: list[list[Cell]] = field(init=False, repr=False)  # 内部格子的二维网格（行主序），由 __post_init__ 创建

    def __post_init__(self) -> None:
        """初始化全部格子。

        参数:
            无（该方法由 dataclass 在自动生成的 __init__ 之后调用）。

        返回:
            无。
        """
        self._cells = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def in_bounds(self, coord: Coordinate) -> bool:
        """判断坐标是否在棋盘内。

        参数:
            coord: 待判断的棋盘坐标。

        返回:
            坐标在棋盘范围内返回 True，否则返回 False。
        """
        return 0 <= coord.row < self.rows and 0 <= coord.col < self.cols

    def cell(self, coord: Coordinate) -> Cell:
        """取指定坐标的格子对象。

        参数:
            coord: 目标格子的坐标，调用方需保证其在棋盘内。

        返回:
            该坐标对应的 Cell 对象。
        """
        return self._cells[coord.row][coord.col]

    def all_coords(self) -> Iterator[Coordinate]: # 迭代器
        """遍历棋盘内全部坐标。

        参数:
            无。

        返回:
            按行优先顺序（从上到下、从左到右）产出全部坐标的迭代器。
        """
        for row in range(self.rows):
            for col in range(self.cols):
                yield Coordinate(row, col)  # 生成器


    def neighbors8(self, coord: Coordinate) -> list[Coordinate]:
        """
        返回 3×3 内 8 个邻居（跳过越界与自身）。
        (-1,-1)  (-1,0)  (-1,1)     左上    上    右上
        (0,-1)   (0,0)   (0,1)  =   左    [当前]   右
        (1,-1)   (1,0)   (1,1)     左下    下    右下

        参数:
            coord: 中心格子的坐标。

        返回:
            8 个邻居坐标组成的列表，按 dr/dc 从 (-1,-1) 到 (1,1) 的顺序，
            越界坐标会被跳过。
        """
        result: list[Coordinate] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nxt = Coordinate(coord.row + dr, coord.col + dc)
                if self.in_bounds(nxt):
                    result.append(nxt)
        return result
