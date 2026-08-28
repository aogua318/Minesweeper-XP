"""布雷逻辑（点后布雷）。

在首次点击后，于安全区之外的格子中随机放置雷；
安全区规则由 safe_mode（仅首格 / 首格 3×3）决定
（实现见 docs/实施文档.md §4）。
"""
import random

from ..model.board import Board
from ..model.coordinate import Coordinate


def _safe_zone(click: Coordinate, mode: str, rows: int, cols: int) -> set[Coordinate]:
    """计算禁止布雷区。

    参数:
        click: 首次点击的坐标，作为安全区的中心。
        mode: 安全区模式。'cell' 表示仅首格本身禁止布雷，
            'zone3x3' 表示以首格为中心的 3×3 范围禁止布雷。
        rows: 棋盘行数，用于裁剪越界坐标。
        cols: 棋盘列数，用于裁剪越界坐标。

    返回:
        禁止布雷的坐标集合。
    """
    result: set[Coordinate] = set()
    if mode == "cell":
        # 首格禁止布雷
        result.add(click)
    else:
        # 3x3 范围禁止布雷
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                cr = click.row + dr
                cc = click.col + dc
                if 0 <= cr <= rows - 1 and 0 <= cc <= cols - 1:  # 棋盘内
                    result.add(Coordinate(cr, cc))

    return result


def place_mines(
    board: Board,
    mine_count: int,
    first_click: Coordinate,
    safe_mode: str,
    rng: random.Random,
) -> None:
    """在安全区之外的格子中随机放置指定数量的雷。

    参数:
        board: 目标棋盘，布雷结果直接写入其中的格子。
        mine_count: 需要放置的雷总数。
        first_click: 首次点击坐标，用于计算安全区。
        safe_mode: 安全区模式，取值与含义见 _safe_zone。
        rng: 随机数生成器，传入后结果可复现。

    返回:
        无。
    """
    # 获取安全区
    safe_zone: set[Coordinate] = _safe_zone(first_click, safe_mode, board.rows, board.cols)
    if mine_count > board.rows * board.cols - len(safe_zone):
        raise ValueError(
            f"雷的数量({mine_count})不能超过可用格子数"
            f"({board.rows * board.cols - len(safe_zone)})"
        )
    for _ in range(mine_count):
        while True:
            coord: Coordinate = Coordinate(
                rng.randint(0, board.rows - 1),
                rng.randint(0, board.cols - 1),
            )
            if board.cell(coord).is_mine:
                # 是雷
                continue
            if coord in safe_zone:
                # 是安全区
                continue
            # 不是雷
            board.cell(coord).is_mine = True
            break
