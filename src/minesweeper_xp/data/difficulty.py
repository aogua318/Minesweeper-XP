"""难度数据类与 JSON 加载。

定义难度数据模型，从 res/difficulties.json 加载预设，
并提供自定义难度参数的校验（实现见 docs/实施文档.md §3）。
"""
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Difficulty:
    """一种难度配置。"""

    rows: int
    cols: int
    mines: int


@dataclass(frozen=True)
class DifficultyConfig:
    """全部难度预设与自定义范围。"""

    presets: dict[str, Difficulty]
    min_rows: int
    max_rows: int
    min_cols: int
    max_cols: int
    min_mines: int

    def preset(self, name: str) -> Difficulty:
        """按名字取预设难度。"""
        return self.presets[name]


def load_difficulties(path: Path) -> DifficultyConfig:
    """从 JSON 解析难度配置。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    presets = {
        name: Difficulty(rows=v["rows"], cols=v["cols"], mines=v["mines"])
        for name, v in data.items()
        if name != "custom_limits"
    }
    limits = data["custom_limits"]
    return DifficultyConfig(
        presets=presets,
        min_rows=limits["min_rows"],
        max_rows=limits["max_rows"],
        min_cols=limits["min_cols"],
        max_cols=limits["max_cols"],
        min_mines=limits["min_mines"],
    )


def default_difficulties() -> DifficultyConfig:
    """返回内置默认难度配置（三档预设与自定义范围），不依赖 JSON 文件。

    参数:
        无。

    返回:
        与 res/difficulties.json 默认内容一致的 DifficultyConfig。
    """
    return DifficultyConfig(
        presets={
            "beginner": Difficulty(rows=9, cols=9, mines=10),
            "intermediate": Difficulty(rows=16, cols=16, mines=40),
            "expert": Difficulty(rows=16, cols=30, mines=99),
        },
        min_rows=9,
        max_rows=24,
        min_cols=9,
        max_cols=30,
        min_mines=10,
    )


def validate_custom(rows: int, cols: int, mines: int, cfg: DifficultyConfig) -> None:
    """校验自定义难度，非法抛 ValueError（开发文档 §4.4）。"""
    if not (cfg.min_rows <= rows <= cfg.max_rows):
        raise ValueError(f"行数需在 {cfg.min_rows}~{cfg.max_rows}")
    if not (cfg.min_cols <= cols <= cfg.max_cols):
        raise ValueError(f"列数需在 {cfg.min_cols}~{cfg.max_cols}")
    if not (cfg.min_mines <= mines <= min(999, rows * cols - 9)):
        raise ValueError("雷数不合法")
