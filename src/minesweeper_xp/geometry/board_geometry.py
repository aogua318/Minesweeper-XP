"""棋盘几何换算（纯函数，开发文档 §9、实施文档 §14.3.1）。

本模块不含任何 Qt 依赖，只做数值换算：
- 由缩放系数推出格子边长与窗口尺寸；
- 由可用空间反推自适应缩放系数；
- 窗口坐标与棋盘坐标互转。

坐标系约定（与开发文档 §8.3 的 HUD 布局一致）：
- 窗口逻辑坐标原点在客户区左上角；
- 棋盘逻辑起点为 (BOARD_LEFT, BOARD_TOP)，每格 BASE_CELL 像素；
- "逻辑像素"指 100% 缩放下的像素，绘制时由 QPainter.scale 统一放大。
"""
from minesweeper_xp.core.model.coordinate import Coordinate

BASE_CELL = 16  # 基准格子边长（像素，100% 缩放下）
BOARD_LEFT = 12  # 棋盘逻辑起点 x（棋盘面板左侧留白）
BOARD_TOP = 55  # 棋盘逻辑起点 y（HUD 面板高度 + 留白）
MIN_SCALE = 0.5  # 最小缩放系数
MAX_SCALE = 3.0  # 最大缩放系数
ZOOM_STEPS = (0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)  # Ctrl+滚轮的缩放档位


def cell_size(scale: float) -> int:
    """按缩放系数返回格子边长。

    参数:
        scale: 缩放系数（MIN_SCALE~MAX_SCALE）。

    返回:
        格子边长（像素，四舍五入）。
    """
    return round(BASE_CELL * scale)


def window_size(rows: int, cols: int, scale: float) -> tuple[int, int]:
    """按缩放系数返回窗口逻辑尺寸（宽、高）。

    尺寸 = 棋盘区域 + HUD 区域 + 边框留白：
    - 宽 = cols * 16 + 22（左右各约 11px 留白）；
    - 高 = rows * 16 + 65（顶部 HUD 约 55px + 底部约 10px 留白）。

    参数:
        rows: 棋盘行数。
        cols: 棋盘列数。
        scale: 缩放系数。

    返回:
        (窗口宽度, 窗口高度) 元组（客户区逻辑像素）。
    """
    return round((cols * BASE_CELL + 22) * scale), round((rows * BASE_CELL + 65) * scale)


def fit_scale(rows: int, cols: int, avail_w: int, avail_h: int) -> float:
    """由可用尺寸反推自适应缩放系数（夹在 MIN/MAX 之间）。

    用于窗口被手动拉伸时，让棋盘按可用空间等比缩放、不变形不裁切。

    参数:
        rows: 棋盘行数。
        cols: 棋盘列数。
        avail_w: 可用宽度（控件当前宽度，逻辑像素）。
        avail_h: 可用高度（控件当前高度，逻辑像素）。

    返回:
        自适应缩放系数，范围 [MIN_SCALE, MAX_SCALE]。
    """
    s = min(avail_w / (cols * BASE_CELL + 22), avail_h / (rows * BASE_CELL + 65))
    return max(MIN_SCALE, min(MAX_SCALE, s))


def widget_pos_to_cell(
    px: float, py: float, scale: float, rows: int, cols: int
) -> Coordinate | None:
    """窗口逻辑坐标 → 棋盘坐标；越界返回 None。

    先除以缩放系数还原成 100% 逻辑坐标，再减去棋盘起点并整除格子边长。

    参数:
        px: 窗口逻辑坐标 x。
        py: 窗口逻辑坐标 y。
        scale: 当前缩放系数。
        rows: 棋盘行数（用于越界判断）。
        cols: 棋盘列数（用于越界判断）。

    返回:
        对应的棋盘坐标；落在棋盘外（HUD/边框区域）时返回 None。
    """
    col = int((px / scale - BOARD_LEFT) / BASE_CELL)
    row = int((py / scale - BOARD_TOP) / BASE_CELL)
    if 0 <= row < rows and 0 <= col < cols:
        return Coordinate(row, col)
    return None
