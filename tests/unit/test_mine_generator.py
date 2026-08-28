"""布雷逻辑单元测试。

覆盖安全区规则（仅首格 / 首格 3×3、边界裁剪）、雷数放置、
随机可复现性与雷数越界拦截
（测试清单见 docs/实施文档.md §12）。
"""
import random

import pytest

from minesweeper_xp.core.generation.mine_generator import _safe_zone, place_mines
from minesweeper_xp.core.model.board import Board
from minesweeper_xp.core.model.coordinate import Coordinate


def _mine_layout(seed: int) -> set[Coordinate]:
    """按指定种子在 9×9 棋盘布 10 颗雷并返回雷的位置集合。

    参数:
        seed: 随机数种子。

    返回:
        布雷完成后雷所在的坐标集合。
    """
    board = Board(9, 9)
    place_mines(board, 10, Coordinate(0, 0), "zone3x3", random.Random(seed))
    return {c for c in board.all_coords() if board.cell(c).is_mine}


def test_safe_zone_cell_mode() -> None:
    """cell 模式只把首格本身列入禁止布雷区。

    参数:
        无。

    返回:
        无。
    """
    click = Coordinate(5, 5)
    assert _safe_zone(click, "cell", 9, 9) == {click}


def test_safe_zone_zone3x3_center() -> None:
    """zone3x3 模式在棋盘中心返回完整 9 格。

    参数:
        无。

    返回:
        无。
    """
    click = Coordinate(4, 4)
    expected = {
        Coordinate(click.row + dr, click.col + dc)
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
    }
    assert _safe_zone(click, "zone3x3", 9, 9) == expected


def test_safe_zone_zone3x3_corner_clipped() -> None:
    """zone3x3 模式在角落按棋盘边界裁剪为 4 格。

    参数:
        无。

    返回:
        无。
    """
    assert _safe_zone(Coordinate(0, 0), "zone3x3", 9, 9) == {
        Coordinate(0, 0),
        Coordinate(0, 1),
        Coordinate(1, 0),
        Coordinate(1, 1),
    }


def test_place_mines_exact_count_outside_safe_zone() -> None:
    """放置指定数量的雷，且首击安全区内无雷。

    参数:
        无。

    返回:
        无。
    """
    board = Board(9, 9)
    first_click = Coordinate(4, 4)
    place_mines(board, 10, first_click, "zone3x3", random.Random(42))
    mine_coords = [c for c in board.all_coords() if board.cell(c).is_mine]
    safe_zone = _safe_zone(first_click, "zone3x3", 9, 9)
    assert len(mine_coords) == 10
    assert all(c not in safe_zone for c in mine_coords)


def test_place_mines_cell_mode_only_protects_first_cell() -> None:
    """cell 模式首击格无雷，且雷数准确。

    参数:
        无。

    返回:
        无。
    """
    board = Board(9, 9)
    first_click = Coordinate(0, 0)
    place_mines(board, 10, first_click, "cell", random.Random(3))
    mine_coords = [c for c in board.all_coords() if board.cell(c).is_mine]
    assert board.cell(first_click).is_mine is False
    assert len(mine_coords) == 10


def test_place_mines_same_seed_same_layout() -> None:
    """相同种子产生相同的布雷结果。

    参数:
        无。

    返回:
        无。
    """
    assert _mine_layout(42) == _mine_layout(42)


def test_place_mines_different_seed_different_layout() -> None:
    """不同种子产生不同布雷结果（概率性断言）。

    参数:
        无。

    返回:
        无。
    """
    assert _mine_layout(1) != _mine_layout(2)


def test_place_mines_raises_when_too_many() -> None:
    """雷数超过可用格子数时抛出 ValueError。

    参数:
        无。

    返回:
        无。
    """
    # 9×9 中心 zone3x3 可用 72 格，73 颗应报错
    with pytest.raises(ValueError):
        place_mines(Board(9, 9), 73, Coordinate(4, 4), "zone3x3", random.Random(1))
    # 角落安全区只有 4 格，可用 77 格，78 颗应报错
    with pytest.raises(ValueError):
        place_mines(Board(9, 9), 78, Coordinate(0, 0), "zone3x3", random.Random(1))


def test_place_mines_can_fill_all_available_cells() -> None:
    """雷数恰好等于可用格子数时允许放满。

    参数:
        无。

    返回:
        无。
    """
    board = Board(9, 9)
    place_mines(board, 72, Coordinate(4, 4), "zone3x3", random.Random(7))
    mine_coords = [c for c in board.all_coords() if board.cell(c).is_mine]
    assert len(mine_coords) == 72
