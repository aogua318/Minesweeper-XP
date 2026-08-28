"""Board 领域对象单元测试。

覆盖棋盘初始化、越界判断、取格、全坐标遍历与 3×3 邻居查询，
并验证 Cell / Coordinate / Mark 等模型基础约定
（测试清单见 docs/实施文档.md §12）。
"""
import pytest

from minesweeper_xp.core.enums import Mark
from minesweeper_xp.core.model.board import Board
from minesweeper_xp.core.model.cell import Cell
from minesweeper_xp.core.model.coordinate import Coordinate


def test_cell_default_state() -> None:
    """验证新建 Cell 处于默认状态。

    参数:
        无。

    返回:
        无。
    """
    cell = Cell()
    assert cell.is_mine is False
    assert cell.is_revealed is False
    assert cell.mark is Mark.NONE
    assert cell.adjacent_mines == 0


def test_new_board_all_cells_default() -> None:
    """验证新建棋盘上所有格子都处于默认状态。

    参数:
        无。

    返回:
        无。
    """
    board = Board(3, 4)
    for coord in board.all_coords():
        cell = board.cell(coord)
        assert cell.is_mine is False
        assert cell.is_revealed is False
        assert cell.mark is Mark.NONE
        assert cell.adjacent_mines == 0


def test_cell_returns_mutable_cell_instance() -> None:
    """验证 cell() 返回可修改的同一 Cell 实例。

    参数:
        无。

    返回:
        无。
    """
    board = Board(2, 2)
    coord = Coordinate(1, 1)
    cell = board.cell(coord)
    assert isinstance(cell, Cell)
    assert cell is board.cell(coord)
    cell.is_mine = True
    assert board.cell(coord).is_mine is True


def test_in_bounds() -> None:
    """验证越界判断覆盖四边与负坐标。

    参数:
        无。

    返回:
        无。
    """
    board = Board(3, 4)
    assert board.in_bounds(Coordinate(0, 0)) is True
    assert board.in_bounds(Coordinate(2, 3)) is True
    assert board.in_bounds(Coordinate(3, 0)) is False  # 行越界
    assert board.in_bounds(Coordinate(0, 4)) is False  # 列越界
    assert board.in_bounds(Coordinate(-1, 0)) is False  # 负行
    assert board.in_bounds(Coordinate(0, -1)) is False  # 负列


def test_all_coords_row_major() -> None:
    """验证 all_coords 按行优先顺序产出全部坐标。

    参数:
        无。

    返回:
        无。
    """
    board = Board(2, 3)
    coords = list(board.all_coords())
    assert coords == [
        Coordinate(0, 0),
        Coordinate(0, 1),
        Coordinate(0, 2),
        Coordinate(1, 0),
        Coordinate(1, 1),
        Coordinate(1, 2),
    ]


def test_neighbors8_center() -> None:
    """验证中心格返回全部 8 个邻居。

    参数:
        无。

    返回:
        无。
    """
    board = Board(3, 3)
    result = board.neighbors8(Coordinate(1, 1))
    assert len(result) == 8
    assert set(result) == {
        Coordinate(r, c) for r in (0, 1, 2) for c in (0, 1, 2)
    } - {Coordinate(1, 1)}


def test_neighbors8_corner() -> None:
    """验证角落只返回 3 个在界内的邻居。

    参数:
        无。

    返回:
        无。
    """
    board = Board(3, 3)
    result = board.neighbors8(Coordinate(0, 0))
    assert set(result) == {
        Coordinate(0, 1),
        Coordinate(1, 0),
        Coordinate(1, 1),
    }


def test_neighbors8_edge() -> None:
    """验证边缘返回 5 个在界内的邻居。

    参数:
        无。

    返回:
        无。
    """
    board = Board(3, 3)
    result = board.neighbors8(Coordinate(0, 1))
    assert set(result) == {
        Coordinate(0, 0),
        Coordinate(0, 2),
        Coordinate(1, 0),
        Coordinate(1, 1),
        Coordinate(1, 2),
    }


def test_coordinate_is_frozen_value_object() -> None:
    """验证 Coordinate 不可变且可哈希。

    参数:
        无。

    返回:
        无。
    """
    coord = Coordinate(1, 2)
    assert coord == Coordinate(1, 2)
    assert hash(coord) == hash(Coordinate(1, 2))
    with pytest.raises(AttributeError):
        coord.row = 3  # frozen dataclass 赋值应报错
