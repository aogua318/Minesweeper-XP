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

    rows: int
    cols: int
    _cells: list[list[Cell]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """初始化全部格子。"""
        self._cells = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def in_bounds(self, coord: Coordinate) -> bool:
        """判断坐标是否在棋盘内。"""
        return 0 <= coord.row < self.rows and 0 <= coord.col < self.cols

    def cell(self, coord: Coordinate) -> Cell:
        """取指定坐标的格子对象。"""
        return self._cells[coord.row][coord.col]

    def all_coords(self) -> Iterator[Coordinate]: # 迭代器
        """遍历棋盘内全部坐标。"""
        for row in range(self.rows):
            for col in range(self.cols):
                yield Coordinate(row, col) #生成器


    def neighbors8(self, coord: Coordinate) -> list[Coordinate]:
        """
        返回 3×3 内 8 个邻居（跳过越界与自身）。
        (-1,-1)  (-1,0)  (-1,1)     左上    上    右上
        (0,-1)   (0,0)   (0,1)  =   左    [当前]   右
        (1,-1)   (1,0)   (1,1)     左下    下    右下
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