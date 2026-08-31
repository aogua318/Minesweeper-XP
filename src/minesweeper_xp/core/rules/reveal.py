"""翻开与 BFS 洪水填充（邻域雷数在布雷后预计算）。

实现单格翻开、邻域雷数统计与预计算、空白区域自动展开
（实现见 docs/实施文档.md §5）。
"""
from collections import deque

from ..enums import Mark
from ..model.board import Board
from ..model.coordinate import Coordinate


def count_adjacent_mines(board: Board, coord: Coordinate) -> int:
    """统计 3×3 邻域内的雷数。

    参数:
        board: 目标棋盘，用于读取邻居格子的状态。
        coord: 中心格子的坐标。

    返回:
        邻域内雷的数量（0~8）。
    """
    flags: int = 0
    nb8: list[Coordinate] = board.neighbors8(coord)
    for nb in nb8:
        if board.cell(nb).is_mine:  # 有雷
            flags += 1
    return flags


def calculate_adjacent_mines(board: Board) -> None:
    """布雷后预计算棋盘上每个格子的邻域雷数。

    遍历全部格子，把计算结果写入各格子的 adjacent_mines 字段，
    后续翻开/连开阶段只读取该值，不再逐格统计。

    参数:
        board: 目标棋盘，计算结果直接写入其中的格子。

    返回:
        无。
    """
    for coord in board.all_coords():  # 遍历棋盘
        board.cell(coord).adjacent_mines = count_adjacent_mines(board, coord)



def reveal_cell(board: Board, coord: Coordinate) -> bool:
    """翻开单格。

    越界、已翻开、是雷或标旗的格子不执行翻开并返回 False。

    参数:
        board: 目标棋盘。
        coord: 要翻开的格子坐标。

    返回:
        翻开返回 True，否则返回 False。
    """
    if not board.in_bounds(coord):  # 越界
        return False

    cell = board.cell(coord)

    if cell.is_revealed:  # 已经翻开
        return False
    if cell.is_mine:  # 是雷
        return False
    if cell.mark is Mark.FLAG:  # 是旗子
        return False

    # 执行翻开
    cell.is_revealed = True
    return True


def flood_fill(board: Board, start: Coordinate) -> list[Coordinate]:
    """从 start 展开空白区域（BFS 洪水填充）。

    参数:
        board: 目标棋盘。
        start: 起始格子坐标。

    返回:
        本次被翻开的全部格子坐标列表（含 start）。

    补充说明:
        以 start 为起点，沿 8 个方向 BFS 扩散。
        当前格周围没有雷（adjacent_mines == 0）时继续扩散，
        并把 8 个邻居入列；当前格周围有雷（数字格）时只翻开
        当前格、不再扩散。
        雷、旗子、越界或已翻开的格子会被 reveal_cell 拒绝并跳过
    """
    coords: list[Coordinate] = []
    queue_coords = deque()
    queue_coords.append(start)  # 入列
    while queue_coords:  # 队列非空则继续处理
        coord = queue_coords.popleft()  # 出列
        cell = board.cell(coord)
        if not reveal_cell(board, coord):  # 雷/旗/越界/已翻开：跳过，不扩散
            continue

        # 当前格已被 reveal_cell 翻开，记录坐标
        coords.append(coord)

        if cell.adjacent_mines == 0:  # 周围没有雷，继续扩散
            # 把 8 个邻居一次性入列（extend 添加多个元素）
            queue_coords.extend(board.neighbors8(coord))

    return coords
