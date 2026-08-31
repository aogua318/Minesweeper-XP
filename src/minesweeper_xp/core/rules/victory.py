"""胜负判定规则。

判断所有非雷格是否全部翻开，从而确定是否获胜
（实现见 docs/实施文档.md §8）。
"""
from ..model.board import Board


def is_won(board: Board, mine_count: int) -> bool:
    """判断是否获胜。

    所有非雷格全部翻开即胜（雷是否标旗无关）。

    参数:
        board: 目标棋盘，读取各格子的翻开与雷状态。
        mine_count: 本局雷总数，用于计算应翻开的非雷格数量。

    返回:
        全部非雷格已翻开返回 True，否则返回 False。
    """
    count = 0
    cells_count = board.rows * board.cols
    for coord in board.all_coords():
        if board.cell(coord).is_revealed and not board.cell(coord).is_mine: # 被翻开 并且 不是雷
            count += 1

    if count == cells_count - mine_count:
        return True
    return False

