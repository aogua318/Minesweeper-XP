"""翻开规则单元测试。

覆盖邻域雷数统计与预计算、单格翻开、洪水填充展开与边界阻挡
（对应 docs/实施文档.md §5）。
"""
from minesweeper_xp.core.enums import Mark
from minesweeper_xp.core.model.board import Board
from minesweeper_xp.core.model.coordinate import Coordinate
from minesweeper_xp.core.rules.reveal import (
    calculate_adjacent_mines,
    count_adjacent_mines,
    flood_fill,
    reveal_cell,
)


def _board_with_mines(mine_coords: list[Coordinate], rows: int = 5, cols: int = 5) -> Board:
    """构造指定雷位的棋盘并预计算邻域雷数。

    参数:
        mine_coords: 需要布雷的坐标列表。
        rows: 棋盘行数，默认 5。
        cols: 棋盘列数，默认 5。

    返回:
        已布雷并调用 calculate_adjacent_mines 预计算好的 Board。
    """
    board = Board(rows, cols)
    for coord in mine_coords:
        board.cell(coord).is_mine = True

    calculate_adjacent_mines(board)
    return board


def test_count_adjacent_mines_center() -> None:
    """验证中心格子的邻域雷数统计正确（含 8 个方向）。

    参数:
        无。

    返回:
        无。
    """
    # 无雷时计数为 0
    assert count_adjacent_mines(_board_with_mines([]), Coordinate(2, 2)) == 0

    # 8 个邻居全部布雷，计数为 8
    board = _board_with_mines(
        [
            Coordinate(1, 1),
            Coordinate(1, 2),
            Coordinate(1, 3),
            Coordinate(2, 1),
            Coordinate(2, 3),
            Coordinate(3, 1),
            Coordinate(3, 2),
            Coordinate(3, 3),
        ]
    )
    center = Coordinate(2, 2)
    assert count_adjacent_mines(board, center) == 8

    # 移走一颗雷后计数减少
    board.cell(Coordinate(3, 3)).is_mine = False
    assert count_adjacent_mines(board, center) == 7

    # 中心自身是雷不应计入（只统计邻居）
    board.cell(center).is_mine = True
    assert count_adjacent_mines(board, center) == 7


def test_count_adjacent_mines_at_edge() -> None:
    """验证边缘/角落格子统计不越界、不崩溃。

    参数:
        无。

    返回:
        无。
    """
    # 角落无雷时计数为 0
    assert count_adjacent_mines(_board_with_mines([]), Coordinate(0, 0)) == 0

    # 边缘无雷时计数为 0
    assert count_adjacent_mines(_board_with_mines([]), Coordinate(2, 0)) == 0
    assert count_adjacent_mines(_board_with_mines([]), Coordinate(0, 2)) == 0

    # 构造雷区
    board = _board_with_mines(
        [
            Coordinate(0, 1),
            Coordinate(0, 3),
            Coordinate(1, 0),
            Coordinate(1, 1),
            Coordinate(1, 2),
            Coordinate(1, 3),
            Coordinate(2, 1),
            Coordinate(3, 0),
            Coordinate(3, 1),
            Coordinate(4, 0),
            Coordinate(4, 1),
        ]
    )
    # 角落 3 个邻居全部布雷，计数为 3
    cell00 = Coordinate(0, 0)
    assert count_adjacent_mines(board, cell00) == 3

    # 顶部 5 个邻居全部布雷，计数为 5
    cell02 = Coordinate(0, 2)
    assert count_adjacent_mines(board, cell02) == 5

    # 侧部 5 个邻居全部布雷，计数为 5
    cell20 = Coordinate(2, 0)
    assert count_adjacent_mines(board, cell20) == 5

    # 移走一颗雷后计数减少
    board.cell(Coordinate(1, 1)).is_mine = False
    assert count_adjacent_mines(board, cell00) == 2
    assert count_adjacent_mines(board, cell02) == 4
    assert count_adjacent_mines(board, cell20) == 4

    # 中心自身是雷不应计入（只统计邻居）
    board.cell(cell00).is_mine = True
    assert count_adjacent_mines(board, cell00) == 2

    board.cell(cell02).is_mine = True
    assert count_adjacent_mines(board, cell02) == 4

    board.cell(cell20).is_mine = True
    assert count_adjacent_mines(board, cell20) == 4


def test_calculate_adjacent_mines_writes_all_cells() -> None:
    """验证预计算后每个格子的 adjacent_mines 都等于实际邻居雷数。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines(
        [
            Coordinate(0, 0),
            Coordinate(2, 2),
            Coordinate(4, 4),
        ]
    )
    for coord in board.all_coords():
        assert board.cell(coord).adjacent_mines == count_adjacent_mines(board, coord)


def test_reveal_cell_success() -> None:
    """验证普通未翻开格子可被翻开且返回 True。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([])
    coord = Coordinate(2, 2)
    assert reveal_cell(board, coord) is True
    assert board.cell(coord).is_revealed is True


def test_reveal_cell_skips_already_revealed() -> None:
    """验证已翻开的格子不重复翻开，返回 False。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([])
    coord = Coordinate(2, 2)
    assert reveal_cell(board, coord) is True
    assert reveal_cell(board, coord) is False
    assert board.cell(coord).is_revealed is True


def test_reveal_cell_skips_mine() -> None:
    """验证雷格不会被翻开，返回 False。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([Coordinate(2, 2)])
    coord = Coordinate(2, 2)
    assert reveal_cell(board, coord) is False
    assert board.cell(coord).is_revealed is False


def test_reveal_cell_skips_flag() -> None:
    """验证标旗的格子不会被翻开，返回 False。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([])
    coord = Coordinate(2, 2)
    board.cell(coord).mark = Mark.FLAG
    assert reveal_cell(board, coord) is False
    assert board.cell(coord).is_revealed is False


def test_reveal_cell_out_of_bounds() -> None:
    """验证越界坐标不会被翻开，返回 False。

    参数:
        无。

    返回:
        无。
    """
    board = Board(5, 5)
    assert reveal_cell(board, Coordinate(-1, 0)) is False
    assert reveal_cell(board, Coordinate(0, -1)) is False
    assert reveal_cell(board, Coordinate(5, 0)) is False
    assert reveal_cell(board, Coordinate(0, 5)) is False


def test_flood_fill_expands_zero_region() -> None:
    """验证空白格会向 8 个方向扩散，数字格被翻开但不扩散。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([Coordinate(4, 4)])
    mine = Coordinate(4, 4)
    result = flood_fill(board, Coordinate(0, 0))
    expected = {c for c in board.all_coords()} - {mine}
    assert set(result) == expected
    assert len(result) == 24
    assert board.cell(mine).is_revealed is False
    assert all(board.cell(c).is_revealed for c in result)


def test_flood_fill_stops_at_mine() -> None:
    """验证雷是扩散边界，雷本身及雷后方的格子不会被翻开。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([Coordinate(1, 1)], rows=3, cols=3)
    result = flood_fill(board, Coordinate(0, 0))
    assert result == [Coordinate(0, 0)]
    assert board.cell(Coordinate(0, 1)).is_revealed is False
    assert board.cell(Coordinate(1, 0)).is_revealed is False
    assert board.cell(Coordinate(1, 1)).is_revealed is False


def test_flood_fill_stops_at_flag() -> None:
    """验证旗子是扩散边界，旗子及其后方的格子不会被翻开。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([Coordinate(2, 4)], rows=3, cols=5)
    for col in range(5):
        board.cell(Coordinate(1, col)).mark = Mark.FLAG  # 整行旗形成隔离墙
    result = flood_fill(board, Coordinate(0, 0))
    expected = {Coordinate(0, col) for col in range(5)}
    assert set(result) == expected
    assert all(board.cell(Coordinate(1, col)).is_revealed is False for col in range(5))
    assert all(board.cell(Coordinate(2, col)).is_revealed is False for col in range(5))


def test_flood_fill_returns_revealed_coords() -> None:
    """验证返回值包含本次翻开的全部坐标（含起点）。

    参数:
        无。

    返回:
        无。
    """
    board = _board_with_mines([], rows=3, cols=3)
    result = flood_fill(board, Coordinate(0, 0))
    assert len(result) == 9
    assert Coordinate(0, 0) in result
    assert set(result) == {c for c in board.all_coords()}
    assert all(board.cell(c).is_revealed for c in result)
