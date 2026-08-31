"""标记规则（右键循环）。

实现「无标记 → 旗 → 问号 → 无标记」的循环切换，
并返回剩余雷数变化量（实现见 docs/实施文档.md §6）。
"""
from ..enums import Mark
from ..model.cell import Cell


def cycle_mark(cell: Cell, marks_enabled: bool) -> int:
    """循环切换右键标记状态。

    无标记 → 旗；旗 → 问号（marks_enabled 为 True）或直接回到无标记；
    问号 → 无标记。已翻开的格子不改变标记。

    注意: marks_enabled 在一局内固定（开局时由配置决定，游戏中不可变），
    问号只会在其开启时产生，因此「问号格 + marks_enabled=False」在
    实际流程中不会出现。

    参数:
        cell: 目标格子，标记状态直接写入其中。
        marks_enabled: 是否启用问号标记；为 False 时旗直接回到无标记。

    返回:
        剩余雷数的变化量：标旗 -1，去旗 +1，问号 0。
    """
    if cell.is_revealed:  # 如果已经被翻开
        return 0
    if marks_enabled:
        if cell.mark is Mark.NONE:  # 如果是空 变旗
            cell.mark = Mark.FLAG
            return -1
        if cell.mark is Mark.FLAG:  # 如果是旗 变问号
            cell.mark = Mark.QUESTION
            return 1
        cell.mark = Mark.NONE  # 是问号 变空
        return 0
    else:
        if cell.mark is Mark.NONE:  # 如果是空 变旗
            cell.mark = Mark.FLAG
            return -1
        # 如果是旗 变空
        cell.mark = Mark.NONE
        return 1
