"""方块渲染器。

按图块状态 0–15 从 SpriteSet 取对应 pixmap 绘制棋盘，
并支持终局失败叠加渲染（开发文档 §4.3、§4.5、§8）。
"""
from PySide6.QtGui import QPainter

from minesweeper_xp.core.enums import LostReason, Mark
from minesweeper_xp.core.model.board import Board
from minesweeper_xp.core.model.cell import Cell
from minesweeper_xp.core.model.coordinate import Coordinate
from minesweeper_xp.rendering.sprite_loader import SpriteSet


def cell_block_state(cell: Cell, game_over: bool = False, is_hit_mine: bool = False) -> int:
    """计算单格对应的图块状态编号（0–15，开发文档 §4.3）。

    普通状态下：
        未翻开：无标记=15、旗=14、问号=13；
        已翻开：空白=0、数字 1–8 取对应编号。
    终局状态下（game_over=True）：
        未标旗的雷=10、标错的旗=11、踩中的雷=12（is_hit_mine）、
        标对的旗=14、其余格子保持普通状态。

    参数:
        cell: 目标格子。
        game_over: 是否已进入终局。
        is_hit_mine: 该格是否为踩中的雷（仅终局时有效，画 12）。

    返回:
        0–15 的图块编号。
    """
    if not game_over: # 普通状态
        if cell.is_revealed:# 翻开
            return cell.adjacent_mines
        else:# 没翻开
            if cell.mark is Mark.FLAG: # 旗子
                return 14
            if cell.mark is Mark.QUESTION: # 问号
                return 13
            return 15 # 空白
    else: # 终局状态

        if cell.is_mine and cell.mark is Mark.FLAG: # 标对的旗
            return 14
        if not cell.is_mine and cell.mark is Mark.FLAG: # 标错的旗
            return 11
        if cell.is_mine and is_hit_mine: # 是雷 并且 点到了
            return 12
        if cell.is_mine and cell.is_revealed: # 是雷 并且 翻开了
            return 12
        if cell.is_mine: # 是雷 没有点到 也没有旗
            return 10
        if cell.is_revealed:# 翻开
            return cell.adjacent_mines
        if cell.mark is Mark.QUESTION:
            return 13
        return 15 # 空白


def draw_board(
    painter: QPainter,
    board: Board,
    sprites: SpriteSet,
    cell_size: int,
    game_over: bool = False,
    pressed: Coordinate | None = None,
) -> None:
    """绘制整个棋盘：逐格计算状态并画到 (col*cell_size, row*cell_size)。

    参数:
        painter: QPainter 绘制目标。
        board: 当前棋盘（只读，不修改 Game 状态）。
        sprites: 已加载的方块精灵图块。
        cell_size: 单格像素边长。
        game_over: 是否终局（影响雷/旗的显示）。
        pressed: 左键按住的格子（画按下外观：无标记=0、问号=9）；
            None 表示当前没有按住的格子。

    返回:
        无。
    """
    for coord in board.all_coords():
        cell = board.cell(coord)
        if pressed is not None and coord == pressed and not cell.is_revealed:  # 按下外观
            block_state = 9 if cell.mark is Mark.QUESTION else 0
        else:
            block_state = cell_block_state(cell,game_over) # 获取图块位置
        painter.drawPixmap(coord.col * cell_size,coord.row * cell_size,sprites.blocks[block_state])


def draw_loss_overlay(
    painter: QPainter,
    board: Board,
    sprites: SpriteSet,
    cell_size: int,
    reason: LostReason,
    coord: Coordinate,
) -> None:
    """按 GameLost(reason, coord) 绘制失败叠加层（开发文档 §4.5）。

    REVEAL：只把 coord 处踩中的雷画成 12（红底爆炸）。
    CHORD：把 neighbors8(coord) 中未标旗的雷画成 12，
    标对的旗保留 14，标错的旗画 11，其余格子正常显示。

    参数:
        painter: QPainter 绘制目标。
        board: 当前棋盘（只读）。
        sprites: 已加载的方块精灵图块。
        cell_size: 单格像素边长。
        reason: 失败原因（REVEAL=左键踩雷 / CHORD=连开踩雷）。
        coord: 触发坐标（踩中的雷或连开点）。

    返回:
        无。
    """

    if reason is LostReason.REVEAL:# 如果是单雷，则只绘制红雷
        cell = board.cell(coord)
        block_state = cell_block_state(cell, True,cell.is_mine)  # 获取图块位置
        painter.drawPixmap(coord.col * cell_size,coord.row * cell_size, sprites.blocks[block_state])
    else: # 不是单雷 是连开 绘制周围8格
        nb8 = board.neighbors8(coord)
        for nb in nb8:
            cell = board.cell(nb)
            block_state = cell_block_state(cell, True, cell.is_mine)  # 获取图块位置
            painter.drawPixmap(nb.col * cell_size,nb.row * cell_size, sprites.blocks[block_state]) #绘制该8格