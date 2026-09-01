"""连开规则（chord）。

对已翻开且周围旗数等于数字的格子，实现中键/双键连开周围格子
（实现见 docs/实施文档.md §7）。
"""
from .reveal import flood_fill
from ..enums import Mark
from ..model.board import Board
from ..model.coordinate import Coordinate


def chord(board: Board, coord: Coordinate) -> tuple[list[Coordinate], bool]:
    """对已翻开的格子执行连开。

    仅当格子已翻开且周围旗数等于其数字（adjacent_mines）时执行；
    逐个翻开周围非旗格子，一旦踩到雷立即中断并返回 True，
    不再翻开其余邻居（终局显示由 UI 层直接读取棋盘完成）。

    参数:
        board: 目标棋盘。
        coord: 已翻开格子的坐标。

    返回:
        (本次翻开的格子列表, 是否踩雷)。
        未满足连开条件时返回 ([], False)；opened 只包含真正翻开的格子，
        雷保持未翻开，其余未翻开的邻居也保持原状（终局由 UI 叠加渲染）。
    """
    cell = board.cell(coord)
    # 当前格子没有被翻开
    if not cell.is_revealed:
        return [], False

    # 判断周围标记的旗子数等于格子自身adjacent_mines
    nb8 = board.neighbors8(coord)
    mark_flags = 0
    for nb in nb8:
        if board.cell(nb).mark is Mark.FLAG:  # 是旗子
            mark_flags += 1
    if mark_flags != cell.adjacent_mines:  # 周围标记的旗子数不等于数字
        return [], False

    # 执行翻开
    coords: list[Coordinate] = []
    for nb in nb8:
        nb_cell = board.cell(nb)
        if nb_cell.is_revealed or nb_cell.mark is Mark.FLAG:  # 邻居已被翻开或标旗
            continue
        if nb_cell.is_mine:  # 踩到雷：立即中断，已翻开的格子一并带回
            return coords, True

        # 翻开并洪水填充
        coords.extend(flood_fill(board, nb))
    return coords, False  # 交给 UI 端渲染
