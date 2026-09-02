"""HUD 渲染器。

绘制顶部状态面板：剩余雷数 LED、笑脸按钮、计时 LED，
以及外框/面板的 3D 边框（开发文档 §8.3、§8.4）。
"""
from PySide6.QtCore import QRect, Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QColor

from minesweeper_xp.core.enums import FaceState
from minesweeper_xp.rendering.sprite_loader import SpriteSet


# HUD 布局常量（开发文档 §8.3，基准 100%）
HUD_LEFT = 9  # HUD 面板左边距
HUD_TOP = 9  # HUD 面板上边距
HUD_RIGHT_MARGIN = 10  # HUD 面板右边距
HUD_HEIGHT = 36  # HUD 面板高度（45 - 9）
DIGIT_WIDTH = 13  # LED 数字图块宽
DIGIT_HEIGHT = 23  # LED 数字图块高
LED_Y = 16  # LED 数字顶部 y
MINE_LED_X_START = 17  # 剩余雷数 LED 起始 x（3 位向右排）
TIMER_LED_X_OFFSETS = (-56, -43, -30)  # 计时 LED 相对右边缘的 x 偏移（右对齐）
SMILE_SIZE = 24  # 笑脸边长
SMILE_Y = 15  # 笑脸顶部 y

_SMILE_INDEX = {
    FaceState.NORMAL: 0,
    FaceState.WOW: 1,
    FaceState.LOST: 2,
    FaceState.WINNER: 3,
    FaceState.PRESSED: 4,
}

def led_indices(value: int) -> tuple[int, int, int]:
    """把数值转换成 3 位 LED 图块索引。

    规则（开发文档 §8.2）：高位补 0；负数在第 1 位用负号（图块 11）；
    计时 999 封顶。空白图块（10）暂不用于数值。

    参数:
        value: 要显示的数值（剩余雷数可为负）。

    返回:
        (第 1 位, 第 2 位, 第 3 位) 的图块索引，范围 0–11。
    """
    if value >= 999:
        value = 999
    if value >= 0:
        return value // 100, value % 100 // 10, value % 10

    if value < -99:
        value = -99
    value = abs(value)  # 取绝对值
    return 11, value % 100 // 10, value % 10


def draw_led_digits(
    painter: QPainter,
    sprites: SpriteSet,
    value: int,
    x: int,
    y: int,
) -> None:
    """在指定位置绘制 3 位 LED 数字。

    参数:
        painter: QPainter 绘制目标。
        sprites: 已加载的精灵图条（digits 组）。
        value: 要显示的数值。
        x: 第 1 位左侧 x 坐标。
        y: 数字顶部 y 坐标。

    返回:
        无。
    """
    led_num = led_indices(value)
    painter.drawPixmap(x, y, sprites.digits[led_num[0]])  # 百位
    painter.drawPixmap(x + DIGIT_WIDTH, y, sprites.digits[led_num[1]])  # 十位
    painter.drawPixmap(x + DIGIT_WIDTH * 2, y, sprites.digits[led_num[2]])  # 个位


def smile_index(face: FaceState) -> int:
    """把笑脸状态映射为精灵图块索引（0–4）。

    映射（开发文档 §4.5）：NORMAL=0、WOW=1、LOST=2、WINNER=3、PRESSED=4。

    参数:
        face: 笑脸状态。

    返回:
        0–4 的图块索引。
    """
    return _SMILE_INDEX[face]


def draw_bevel(
    painter: QPainter,
    rect: QRect,
    sunken: bool,
    light_color: str,
    dark_color: str,
    depth: int = 1,
) -> None:
    """绘制 3D 边框（开发文档 §8.4）。

    用 1px 亮/暗线段组合成边框：凸起 = 左上亮 + 右下暗；
    凹陷 = 左上暗 + 右下亮。按 depth 循环内缩绘制 1–3 层，
    颜色取自主题（外框 3px、HUD 2px、棋盘面板 3px，见 §8.3）。

    参数:
        painter: QPainter 绘制目标。
        rect: 边框所在矩形。
        sunken: True 画凹陷，False 画凸起。
        light_color: 亮色（CSS 颜色字符串）。
        dark_color: 暗色（CSS 颜色字符串）。
        depth: bevel 层数（1–3），默认 1。

    返回:
        无。
    """
    # 保存旧设置
    old_pen = painter.pen()

    if sunken:  # 凹陷：设定颜色
        color_left_top = dark_color
        color_right_bottom = light_color
    else:  # 凸起
        color_left_top = light_color
        color_right_bottom = dark_color

    pen = QPen()
    pen.setWidth(1)  # 1px 大小
    pen.setStyle(Qt.PenStyle.SolidLine)

    # 循环绘制
    for i in range(depth):
        # 矩形缩小
        current_rect = rect.adjusted(i, i, -i, -i)

        # 获取4个角的坐标
        top_left = current_rect.topLeft()
        top_right = current_rect.topRight()
        bottom_left = current_rect.bottomLeft()
        bottom_right = current_rect.bottomRight()

        # 绘制顶边（端点外扩 1px 做圆角过渡）
        pen.setColor(color_left_top)
        painter.setPen(pen)
        # 左上→右上
        painter.drawLine(top_left, top_right)
        # 绘制左边：从左上到左下 (注意：左下角不重复绘制，留给底边)
        painter.drawLine(top_left, bottom_left)

        # 绘制底边
        pen.setColor(color_right_bottom)
        painter.setPen(pen)
        # 左下→右下
        painter.drawLine(bottom_left+QPoint(0,1), bottom_right+QPoint(0,1))
        # 右边：从右上到右下 (注意：右上角不重复绘制，留给顶边)
        painter.drawLine(top_right+QPoint(1,0), bottom_right+QPoint(1,1))

    # 还原风格
    painter.setPen(old_pen)


def draw_hud(
    painter: QPainter,
    sprites: SpriteSet,
    remaining_mines: int,
    seconds: int,
    face: FaceState,
    width: int,
) -> None:
    """绘制整个 HUD 面板：外框、两个 LED、笑脸。
        (9,9)-(W-10,45)，2px 内凹

    参数:
        painter: QPainter 绘制目标。
        sprites: 已加载的精灵图条。
        remaining_mines: 剩余雷数（可为负）。
        seconds: 已计秒数（0–999）。
        face: 笑脸状态。
        width: 窗口宽度，用于面板宽度与元素居中/右对齐。

    返回:
        无。
    """

    # 设置矩形 矩形填充颜色由上层指定
    rect_hud = QRect(HUD_TOP, HUD_LEFT, width - HUD_LEFT - HUD_RIGHT_MARGIN, HUD_HEIGHT)
    painter.drawRect(rect_hud)

    # 绘制边框
    draw_bevel(painter, rect_hud, True, "#ffffff", "#808080", 2)

    # 绘制雷数 LED 矩形：宽 = 3*DIGIT_WIDTH + 2，高 = DIGIT_HEIGHT + 2
    rect_mine_LED = QRect(
        MINE_LED_X_START - 1, LED_Y - 1, DIGIT_WIDTH * 3 + 1, DIGIT_HEIGHT + 1
    )
    painter.drawRect(rect_mine_LED)
    # painter.fillRect(rect_mine_LED, QColor("#000000"))  # 填充黑色底色

    # 绘制边框
    draw_bevel(painter, rect_mine_LED, True, "#ffffff", "#808080", 1)

    # 绘制雷数 LED 数字
    draw_led_digits(painter, sprites, remaining_mines, MINE_LED_X_START, LED_Y)

    # 绘制笑脸
    # 笑脸矩形   最外层有一层四周的暗色矩形  居中
    rect_face_cell = SMILE_SIZE + 2  # 计算边长

    dx = (rect_hud.width() - rect_face_cell) // 2
    rect_face = QRect(rect_hud.x() + dx, SMILE_Y - 1, SMILE_SIZE + 1, SMILE_SIZE + 1)

    painter.drawRect(rect_face)
    # 绘制笑脸图像
    smile_i = smile_index(face)
    painter.drawPixmap(
        rect_face.x() + 1, rect_face.y() + 1, sprites.smiles[smile_i]
    )  # 绘制笑脸

    # 绘制计时 LED 矩形：宽 = 3*DIGIT_WIDTH + 2，高 = DIGIT_HEIGHT + 2
    rect_time_LED = QRect(
        width + TIMER_LED_X_OFFSETS[0] - 1, LED_Y - 1, DIGIT_WIDTH * 3 + 1, DIGIT_HEIGHT + 1
    )

    # painter.fillRect(rect_time_LED, QColor("#000000"))  # 填充黑色底色
    painter.drawRect(rect_time_LED)
    # 绘制边框
    draw_bevel(painter, rect_time_LED, True, "#ffffff", "#808080", 1)
    # 绘制计时 LED 数字
    draw_led_digits(painter, sprites, seconds, width + TIMER_LED_X_OFFSETS[0], LED_Y)
