"""难度数据与配置加载单元测试。

覆盖预设加载、custom_limits 解析、预设查询与自定义难度校验
（对应 docs/实施文档.md §3 与开发文档 §4.4）。
"""
import json
from pathlib import Path

import pytest

from minesweeper_xp.data.difficulty import (
    Difficulty,
    DifficultyConfig,
    load_difficulties,
    validate_custom,
)


def _make_config() -> DifficultyConfig:
    """构造一份与 res/difficulties.json 一致的测试配置。

    参数:
        无。

    返回:
        包含三档预设与默认自定义范围的 DifficultyConfig。
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


def test_load_difficulties_from_json(tmp_path: Path) -> None:
    """验证从 JSON 文件解析出预设与自定义范围。

    参数:
        tmp_path: pytest 提供的临时目录路径，用于放置测试 JSON。

    返回:
        无。
    """
    data = {
        "beginner": {"rows": 9, "cols": 9, "mines": 10},
        "expert": {"rows": 16, "cols": 30, "mines": 99},
        "custom_limits": {
            "min_rows": 9,
            "max_rows": 24,
            "min_cols": 9,
            "max_cols": 30,
            "min_mines": 10,
        },
    }
    path = tmp_path / "difficulties.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    cfg = load_difficulties(path)
    assert cfg.presets["beginner"] == Difficulty(rows=9, cols=9, mines=10)
    assert cfg.presets["expert"] == Difficulty(rows=16, cols=30, mines=99)
    assert cfg.min_rows == 9
    assert cfg.max_rows == 24
    assert cfg.min_cols == 9
    assert cfg.max_cols == 30
    assert cfg.min_mines == 10


def test_preset_returns_difficulty() -> None:
    """验证 preset() 按名字返回预设难度。

    参数:
        无。

    返回:
        无。
    """
    cfg = _make_config()
    assert cfg.preset("beginner") == Difficulty(rows=9, cols=9, mines=10)


def test_validate_custom_accepts_valid() -> None:
    """验证合法自定义难度通过校验。

    参数:
        无。

    返回:
        无。
    """
    validate_custom(9, 9, 10, _make_config())


def test_validate_custom_accepts_maximum() -> None:
    """验证最大尺寸与最大雷数边界通过校验。

    参数:
        无。

    返回:
        无。
    """
    cfg = _make_config()
    validate_custom(24, 30, min(999, 24 * 30 - 9), cfg)


@pytest.mark.parametrize(
    "rows, cols, mines",
    [
        (8, 9, 10),  # 行过小
        (25, 9, 10),  # 行过大
        (9, 8, 10),  # 列过小
        (9, 31, 10),  # 列过大
        (9, 9, 9),  # 雷过少
        (9, 9, 100),  # 雷过多（超过 rows*cols-9）
    ],
)
def test_validate_custom_rejects_invalid(rows: int, cols: int, mines: int) -> None:
    """验证非法自定义难度抛出 ValueError。

    参数:
        rows: 自定义行数。
        cols: 自定义列数。
        mines: 自定义雷数。

    返回:
        无。
    """
    with pytest.raises(ValueError):
        validate_custom(rows, cols, mines, _make_config())
