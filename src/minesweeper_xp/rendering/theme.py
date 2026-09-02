"""主题数据类与加载（开发文档 §11.2）。"""
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Theme:
    """一个主题：精灵路径、尺寸与颜色。"""

    name: str
    display_name: dict[str, str]
    sprites: dict[str, str]
    sizes: dict[str, object]
    colors: dict[str, str]


def load_theme(path: Path) -> Theme:
    """从 JSON 加载主题。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    return Theme(
        name=data["name"],
        display_name=data["display_name"],
        sprites=data["sprites"],
        sizes=data["sizes"],
        colors=data["colors"],
    )