"""精灵图条加载器。

读取 res/sprites/*.bmp（或主题指定的路径）。BMP 自下而上存储，
先按行翻转，再按规格切成图块列表（实现见 docs/实施文档.md §14.1、
开发文档 §8.2）。
"""
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage, QPixmap


# 图条规格（开发文档 §8.2）
BLOCK_TILE_COUNT = 16  # 方块图块数（状态 0–15）
BLOCK_TILE_SIZE = 16  # 方块边长（像素）
DIGIT_TILE_COUNT = 12  # 数字/符号图块数（0–9、空白 10、负号 11）
DIGIT_TILE_WIDTH = 13  # 数字图块宽（像素）
DIGIT_TILE_HEIGHT = 23  # 数字图块高（像素）
SMILE_TILE_COUNT = 5  # 笑脸图块数
SMILE_TILE_SIZE = 24  # 笑脸边长（像素）


@dataclass(frozen=True)
class SpriteSet:
    """一组已加载的精灵图条（按状态序号索引）。"""

    blocks: list[QPixmap]  # 方块图块 0–15
    digits: list[QPixmap]  # 数字/符号图块 0–11
    smiles: list[QPixmap]  # 笑脸图块 0–4


def _flip_bottom_up(image: QImage) -> QImage:
    """把自下而上存储的 BMP 按行翻转。

    参数:
        image: 原始 QImage。

    返回:
        上下翻转后的新 QImage。
    """
    return image.flipped(Qt.Orientation.Vertical)
    # return image


def _slice_tiles(
    image: QImage,
    tile_count: int,
    tile_width: int,
    tile_height: int,
) -> list[QPixmap]:
    """把图条竖直切成 tile_count 个图块。

    参数:
        image: 已翻转的图条。
        tile_count: 图块数量。
        tile_width: 单块宽度（像素）。
        tile_height: 单块高度（像素）。

    返回:
        按从上到下顺序排列的 QPixmap 列表。
    """
    pixmap: list[QPixmap] = []
    for i in range(tile_count):
        crop_rect = QRect(0, tile_height * i, tile_width, tile_height)  # 裁剪区域
        crop_image = image.copy(crop_rect)  # 裁剪
        # 二次翻转 图像归位
        crop_image = _flip_bottom_up(crop_image)
        pixmap.append(QPixmap.fromImage(crop_image))

    return pixmap


def load_sprite_sheet(
    path: Path,
    tile_count: int,
    tile_width: int,
    tile_height: int,
) -> list[QPixmap]:
    """加载一张 BMP 图条：读文件、按行翻转、切成图块。

    参数:
        path: BMP 文件路径。
        tile_count: 图块数量。
        tile_width: 单块宽度（像素）。
        tile_height: 单块高度（像素）。

    返回:
        按状态序号排列的 QPixmap 列表。
    """
    image = QImage(path)
    if image.isNull():
        raise ValueError("文件加载失败: {path}")

    image = _flip_bottom_up(image)  # 翻转
    return _slice_tiles(image, tile_count, tile_width, tile_height)  # 切块返回


def load_sprite_set(sprites: dict[str, str], res_dir: Path, mono: bool = False) -> SpriteSet:
    """按主题的 sprites 字段加载一套精灵图条（彩色或单色）。

    参数:
        sprites: 主题的 sprites 字典（键如 blocks/blocks_mono、
            digits/digits_mono、smiles/smiles_mono）。
        res_dir: res 资源根目录，用于拼接相对路径。
        mono: True 加载单色图条（*_mono），False 加载彩色图条。

    返回:
        包含方块/数字/笑脸三组图块的 SpriteSet。
    """
    suffix = "_mono" if mono else ""  # 单色模式的键名后缀
    blocks_path = res_dir / sprites["blocks" + suffix]
    digits_path = res_dir / sprites["digits" + suffix]
    smiles_path = res_dir / sprites["smiles" + suffix]

    blocks = load_sprite_sheet(blocks_path, BLOCK_TILE_COUNT, BLOCK_TILE_SIZE, BLOCK_TILE_SIZE)
    digits = load_sprite_sheet(digits_path, DIGIT_TILE_COUNT, DIGIT_TILE_WIDTH, DIGIT_TILE_HEIGHT)
    smiles = load_sprite_sheet(smiles_path, SMILE_TILE_COUNT, SMILE_TILE_SIZE, SMILE_TILE_SIZE)

    return SpriteSet(blocks, digits, smiles)
