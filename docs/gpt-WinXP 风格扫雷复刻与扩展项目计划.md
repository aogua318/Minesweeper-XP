# WinXP 风格扫雷复刻与扩展项目计划

## 1. 项目概述

### 1.1 项目名称

**Minesweeper XP**

暂定项目名，可在项目完成后重新命名。

### 1.2 项目定位

本项目是一个以 Windows XP 经典扫雷为视觉与交互基准的现代化扫雷游戏。

项目不是对原版程序进行机械复制，而是遵循：

> **经典体验保持一致，原版缺陷进行修复，功能在此基础上扩展。**

核心目标：

1. 复刻 WinXP 扫雷的整体视觉风格。
2. 复刻经典扫雷规则和操作方式。
3. 使用现代 GUI 技术重新实现。
4. 支持窗口自由缩放。
5. 支持高 DPI 和不同分辨率。
6. 保持游戏逻辑与 UI 完全解耦。
7. 采用数据驱动方式管理游戏规则和配置。
8. 使用明确类型、分层架构、单元测试和静态检查。
9. 在经典版本完成后逐步增加现代功能。
10. 通过项目系统学习 GUI、游戏架构、软件工程和游戏设计。

---

# 2. 技术目标

## 2.1 技术栈

第一版确定使用：

| 技术 | 用途 |
|---|---|
| Python 3.12+ | 主开发语言 |
| PySide6 | Qt Python 绑定 |
| Qt | GUI、窗口、菜单、事件系统 |
| QPainter | XP 风格游戏区域绘制 |
| pytest | 单元测试 |
| mypy | 静态类型检查 |
| ruff | Lint + Format |
| uv | Python 环境与依赖管理 |
| JSON | 游戏配置与数据 |
| Git | 版本控制 |
| GitHub Actions | CI |
| PyInstaller | Windows 发布 |

原则：

**核心游戏逻辑不依赖 PySide6。**

---

# 3. 学习目标

本项目的主要目的不是快速完成，而是通过项目系统提升编码能力。

## 3.1 Python

重点学习：

- 类型标注
- `dataclass`
- `Enum`
- `Protocol`
- 泛型
- 异常处理
- 模块设计
- 包管理
- 序列化
- 文件系统
- 日志
- 单元测试

要求：

```text
避免使用 Any
避免无意义的动态类型
核心逻辑必须有明确类型
```

---

# 4. Qt / PySide6 学习目标

系统学习：

### 基础

- QApplication
- QMainWindow
- QWidget
- QDialog
- QLabel
- QPushButton
- QMenu
- QAction
- QTimer

### 事件系统

- QMouseEvent
- QKeyEvent
- QResizeEvent
- QPaintEvent
- Event Loop
- Signal / Slot

### 绘制

- QPainter
- QPen
- QBrush
- QFont
- QRect
- QPoint
- QPixmap

### 窗口系统

- Window Size
- Minimum Size
- Maximum Size
- Resize
- DPI
- Device Pixel Ratio

最终目标：

> 能够独立设计一个中小型 Qt 桌面程序，而不是只会调用几个 Widget。

---

# 5. 游戏设计学习目标

通过扫雷学习：

- 游戏状态
- 状态机
- 输入设计
- 随机生成
- 首击保护
- 胜负判定
- 时间系统
- 难度设计
- 游戏反馈
- UX
- 数据驱动
- Replay
- Seed
- 游戏平衡

---

# 6. 软件工程目标

项目必须贯彻以下原则：

## 6.1 单一职责

一个类只负责一个主要职责。

例如：

```text
Board
```

负责棋盘状态。

而不是：

```text
Board
```

同时负责：

- 绘制
- 鼠标
- 文件保存
- 随机生成
- UI
- 菜单

---

## 6.2 依赖方向

推荐：

```text
UI
 ↓
Application
 ↓
Core
```

而不能：

```text
Core
 ↓
PySide6
```

核心逻辑不能依赖 UI。

---

## 6.3 数据与代码分离

游戏参数放在：

```text
config/
```

例如：

```text
config/
├── difficulties.json
├── settings.json
├── themes.json
└── controls.json
```

代码不能大量硬编码：

```python
mines = 99
width = 30
height = 16
```

而应该通过配置系统获得。

---

# 7. 总体架构

推荐采用以下架构：

```text
                    Application
                         │
             ┌───────────┴───────────┐
             │                       │
           UI                    Controller
             │                       │
             └───────────┬───────────┘
                         │
                         ↓
                 Minesweeper Core
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
      Board            Rules             RNG
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                       Tests
```

---

# 8. 推荐目录结构

```text
minesweeper-xp/
│
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
│
├── docs/
│   ├── plan.md
│   ├── architecture.md
│   ├── game-rules.md
│   ├── ui-specification.md
│   ├── rendering.md
│   ├── data-driven.md
│   ├── testing.md
│   ├── save-format.md
│   ├── replay.md
│   └── roadmap.md
│
├── config/
│   ├── difficulties.json
│   ├── settings.json
│   ├── controls.json
│   └── themes.json
│
├── assets/
│   ├── fonts/
│   ├── images/
│   └── sounds/
│
├── src/
│   └── minesweeper/
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── board.py
│       │   ├── cell.py
│       │   ├── game.py
│       │   ├── rules.py
│       │   ├── generator.py
│       │   ├── coordinate.py
│       │   └── enums.py
│       │
│       ├── application/
│       │   ├── controller.py
│       │   ├── game_session.py
│       │   └── state.py
│       │
│       ├── ui/
│       │   ├── main_window.py
│       │   ├── board_widget.py
│       │   ├── menu.py
│       │   ├── dialogs.py
│       │   └── settings_dialog.py
│       │
│       ├── rendering/
│       │   ├── board_renderer.py
│       │   ├── cell_renderer.py
│       │   ├── counter_renderer.py
│       │   ├── face_renderer.py
│       │   └── theme.py
│       │
│       ├── geometry/
│       │   ├── board_geometry.py
│       │   └── layout.py
│       │
│       ├── data/
│       │   ├── config_loader.py
│       │   ├── difficulty.py
│       │   └── settings.py
│       │
│       ├── save/
│       │   ├── save_manager.py
│       │   └── save_model.py
│       │
│       ├── replay/
│       │   ├── recorder.py
│       │   ├── player.py
│       │   └── replay_model.py
│       │
│       └── main.py
│
├── tests/
│   ├── core/
│   ├── application/
│   ├── geometry/
│   ├── data/
│   ├── save/
│   └── replay/
│
├── scripts/
│   ├── validate_config.py
│   └── build.py
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

# 9. 第一阶段：项目初始化

## 目标

建立规范的 Python 项目。

### 工作内容

- 创建 Git 仓库。
- 创建 `pyproject.toml`。
- 配置 uv。
- 配置 Python 版本。
- 安装 PySide6。
- 安装 pytest。
- 安装 mypy。
- 安装 ruff。
- 建立目录结构。
- 创建基础 CI。

### 验收标准

以下命令全部成功：

```text
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

同时：

```text
python -m minesweeper
```

能够启动一个空白 Qt 窗口。

---

# 10. 第二阶段：游戏规则设计

这一阶段禁止开发 UI。

目标：

> **先把扫雷作为一个纯逻辑系统实现。**

---

## 10.1 Cell

定义：

```text
Cell
├── has_mine
├── is_revealed
├── is_flagged
└── adjacent_mines
```

需要明确 Cell 的状态转换。

例如：

```text
Hidden
 ├── LeftClick → Revealed
 └── RightClick → Flagged

Flagged
 └── RightClick → Hidden
```

---

# 11. Board

Board 管理：

```text
width
height
mine_count
cells
```

提供：

```text
get_cell()
neighbors()
place_mines()
calculate_numbers()
reveal()
toggle_flag()
```

Board 不负责：

- 鼠标
- Qt
- 绘画
- 窗口
- 音效

---

# 12. 第三阶段：随机雷区生成

实现：

```text
MineGenerator
```

支持：

- 指定宽度
- 指定高度
- 指定雷数
- 指定随机种子

例如：

```text
Seed
 ↓
Random Generator
 ↓
Mine Layout
```

---

# 13. 首击保护

这是经典扫雷的重要规则。

第一步点击后：

```text
First Click
     ↓
Generate Mines
     ↓
Exclude First Cell
     ↓
Generate Board
```

建议进一步支持：

```text
First Click Safe
First Click + Neighbor Safe
```

但默认保持经典体验。

---

# 14. 第四阶段：数字计算

计算每个格子周围：

```text
8 neighbors
```

的雷数量。

例如：

```text
1 1 1
1 X 1
1 1 1
```

中心 `X` 是雷。

周围数字均为：

```text
1
```

这一部分必须有充分单元测试。

---

# 15. 第五阶段：展开算法

实现：

```text
Reveal
```

如果点击：

```text
数字
```

只展开该格。

如果点击：

```text
0
```

则自动展开相邻空白区域。

推荐使用：

```text
BFS
```

或：

```text
DFS
```

但需要考虑：

- 栈深度
- 大棋盘
- 性能
- 可测试性

建议优先使用 BFS。

---

# 16. 第六阶段：胜负判定

游戏状态：

```text
READY
PLAYING
WON
LOST
```

胜利条件：

> 所有非雷格均已揭开。

注意：

**不要求玩家必须给所有雷插旗。**

这与经典扫雷逻辑一致。

---

# 17. 第七阶段：计时系统

计时器应该属于 Application 层，而不是 Core。

Core：

```text
Game
```

只知道：

```text
READY
PLAYING
WON
LOST
```

Qt：

```text
QTimer
```

负责实际计时。

这样可以避免游戏逻辑依赖系统时间。

---

# 18. 第八阶段：XP UI 规格

核心游戏逻辑完成后，开始 UI。

第一目标不是“漂亮”。

而是：

> **视觉上接近 WinXP 经典扫雷。**

重点复刻：

```text
Window
Menu
Header
Mine Counter
Timer
Face Button
Board
Cell
Number
Flag
Mine
3D Border
```

---

# 19. UI 布局

整体：

```text
┌───────────────────────────────┐
│ 游戏     帮助                 │
├───────────────────────────────┤
│                               │
│  ┌──────┐           ┌──────┐ │
│  │ 010  │           │ 000  │ │
│  └──────┘           └──────┘ │
│                               │
│             ☺                 │
│                               │
│ ┌───────────────────────────┐ │
│ │                           │ │
│ │         Mine Field        │ │
│ │                           │ │
│ └───────────────────────────┘ │
│                               │
└───────────────────────────────┘
```

实际尺寸和间距在 UI 调研阶段确定。

---

# 20. 第九阶段：QPainter 渲染系统

不要为每个 Cell 创建 QWidget。

采用：

```text
QMainWindow
    ↓
MinesweeperBoardWidget
    ↓
QPainter
    ↓
所有 Cell
```

绘制职责：

```text
BoardRenderer
    ↓
CellRenderer
    ├── Hidden
    ├── Revealed
    ├── Flag
    ├── Mine
    └── Number
```

---

# 21. XP 视觉元素

需要实现：

### 未翻开格子

```text
3D Raised
```

### 已翻开格子

```text
Flat / Sunken
```

### 数字

经典扫雷颜色：

```text
1
2
3
...
```

具体颜色应该放入 Theme，而不是散落在 Renderer 中。

---

# 22. 第十阶段：窗口缩放系统

这是本项目与原版的重要区别。

目标：

> **保留 XP 风格，但允许现代窗口自由缩放。**

建立独立模块：

```text
geometry/
└── board_geometry.py
```

负责：

```text
Window Size
      ↓
Available Area
      ↓
Cell Size
      ↓
Board Rect
      ↓
Cell Rect
```

---

# 23. 两种缩放模式

## Classic Mode

保持经典尺寸：

```text
CellSize = OriginalSize
```

窗口不能无限缩放棋盘。

用于：

> 体验经典版本。

---

## Adaptive Mode

根据窗口自动计算：

```text
CellSize
```

窗口越大：

```text
Cell ↑
```

窗口越小：

```text
Cell ↓
```

保持：

```text
Aspect Ratio
```

以及：

```text
Board Center
```

---

# 24. 最小窗口尺寸

必须防止：

```text
CellSize < MinimumCellSize
```

因此：

```text
MinimumWindowSize
```

由：

```text
MinimumCellSize
+
BoardSize
+
UIHeight
+
Margins
```

计算。

不能随意写死。

---

# 25. 高 DPI

重点测试：

```text
100%
125%
150%
175%
200%
```

目标：

- 不模糊
- 不裁剪
- 不错位
- 不出现半像素问题
- 文本清晰
- 棋盘正确缩放

---

# 26. 第十一阶段：鼠标交互

实现：

### 左键

```text
Left Down
    ↓
Pressed State
    ↓
Left Up
    ↓
Reveal
```

### 右键

```text
Right Click
    ↓
Toggle Flag
```

### 双击/Chord

当：

```text
已揭开的数字
```

周围旗帜数量等于数字：

```text
自动展开剩余相邻格
```

这属于经典扫雷的重要操作。

---

# 27. 鼠标视觉状态

需要处理：

```text
Normal
Pressed
Released
Hover
GameOver
Victory
```

尤其是：

> 鼠标按住左键时的视觉效果。

这是 XP 扫雷体验的重要组成部分。

---

# 28. 第十二阶段：菜单系统

实现经典菜单：

```text
游戏
├── 新游戏
├── 初级
├── 中级
├── 高级
├── 自定义
├── 最佳成绩
├── ─────────
└── 退出

帮助
├── 帮助主题
├── 关于扫雷
└── ...
```

具体菜单项目以最终 UI 规格文档为准。

---

# 29. 第十三阶段：难度系统

默认配置：

```text
Beginner
9 × 9
10 Mines

Intermediate
16 × 16
40 Mines

Expert
30 × 16
99 Mines
```

所有参数进入：

```text
config/difficulties.json
```

不要写死在 Core。

---

# 30. 自定义难度

支持：

```text
Width
Height
Mines
```

增加合法性验证：

```text
width > 0
height > 0
mines > 0
mines < width × height
```

进一步考虑：

```text
最大宽度
最大高度
最大雷数
安全区域
```

---

# 31. 第十四阶段：最佳成绩

设计：

```text
BestTimes
```

至少记录：

```text
difficulty
time
date
```

进一步可以增加：

```text
player_name
seed
board_size
mine_count
```

---

# 32. 第十五阶段：存档系统

第一版实现：

```text
Save
Load
```

存储：

```text
difficulty
seed
board state
game state
elapsed time
```

建议 JSON。

但保存格式必须独立于 Core。

---

# 33. 第十六阶段：Seed 系统

这是扩展功能的重要基础。

游戏使用：

```text
seed
```

生成雷区。

例如：

```text
Seed:
381927401
```

其他玩家输入相同：

```text
381927401
```

即可得到相同棋盘。

---

# 34. 第十七阶段：Replay 系统

记录：

```text
timestamp
action
row
column
```

例如：

```text
00:01.250 LeftClick  5  7
00:02.014 RightClick 2  3
00:03.812 LeftClick  6  8
```

Replay：

```text
Replay
 ↓
Event Stream
 ↓
Game Core
 ↓
Renderer
```

Replay 不应该直接记录截图。

---

# 35. 第十八阶段：主题系统

经典主题：

```text
XP Classic
```

之后可以加入：

```text
Dark
Modern
High Contrast
Custom
```

主题数据：

```text
colors
fonts
borders
cell styles
number styles
```

全部进入 Theme 系统。

---

# 36. 第十九阶段：扩展玩法

经典模式完成并稳定后再扩展。

候选：

### Custom Board

```text
任意尺寸
任意雷数
```

### Mega Board

```text
50 × 50
100 × 100
```

### Time Attack

```text
限定时间
```

### Daily Challenge

```text
每日 Seed
```

### Survival

连续棋盘。

### No Guess

保证存在逻辑解。

### Probability Mode

显示概率。

### Hint

提供可解释的提示。

---

# 37. 不建议第一版加入的功能

以下功能全部延后：

```text
联网
账号
排行榜服务器
多人
成就系统
复杂动画
3D
联网对战
```

原因：

> 它们会严重分散项目核心学习目标。

---

# 38. 测试策略

测试重点放在 Core。

---

## 38.1 Board 测试

测试：

```text
创建棋盘
尺寸
Cell 数量
坐标
边界
邻居
```

---

## 38.2 Mine Generator 测试

测试：

```text
雷数正确
雷不越界
Seed 可复现
不同 Seed 能产生不同布局
首击安全
```

---

## 38.3 Reveal 测试

测试：

```text
普通展开
零区域展开
边界
角落
大面积空白
雷格
重复展开
```

---

## 38.4 Flag 测试

测试：

```text
Hidden → Flagged
Flagged → Hidden
Revealed 不能插旗
```

---

## 38.5 Victory 测试

测试：

```text
所有安全格打开 → WIN
只插旗但没有打开 → 不能 WIN
打开雷 → LOSE
```

---

# 39. Geometry 测试

这是本项目非常值得测试的部分。

测试：

```text
Window → Board
Board → Cell
Cell → Pixel
Pixel → Cell
```

包括：

```text
100%
125%
150%
200%
```

以及：

```text
窗口过小
窗口过大
非整数缩放
奇数尺寸
```

---

# 40. UI 测试

UI 不需要像 Core 一样测试得非常细。

重点：

```text
窗口能够启动
菜单存在
新游戏能够工作
点击能够改变 Core 状态
Resize 不崩溃
Dialog 能正常工作
```

---

# 41. 截图回归测试

建议后期增加。

建立：

```text
tests/
└── visual/
```

保存基准截图：

```text
classic_100.png
classic_125.png
classic_150.png
```

以后 UI 修改后进行视觉比对。

目的：

> 防止修改一个绘制细节导致整个 XP UI 变形。

---

# 42. 代码质量标准

每个阶段结束必须：

```text
ruff check
ruff format
mypy
pytest
```

全部通过。

禁止：

```text
# type: ignore
```

除非有明确原因并写注释说明。

避免：

```text
Any
```

---

# 43. 文档要求

项目中至少维护：

```text
docs/
├── plan.md
├── architecture.md
├── game-rules.md
├── ui-specification.md
├── rendering.md
├── data-driven.md
├── testing.md
├── save-format.md
├── replay.md
└── roadmap.md
```

代码不是唯一产物。

---

# 44. Git 提交规范

建议采用：

```text
feat:
fix:
refactor:
test:
docs:
build:
chore:
```

例如：

```text
feat(core): implement board creation
feat(core): implement mine generation
test(core): add reveal tests
feat(ui): implement XP board rendering
fix(ui): correct board scaling
feat(config): add custom difficulty
```

每个 Commit 尽量只完成一个逻辑变化。

---

# 45. CI

GitHub Actions 至少执行：

```text
Python setup
    ↓
uv sync
    ↓
ruff check
    ↓
ruff format --check
    ↓
mypy
    ↓
pytest
```

最终目标：

```text
Pull Request
     ↓
CI
     ↓
全部通过
```

---

# 46. 开发阶段总览

## Phase 0：设计

目标：

```text
需求
架构
UI
数据
测试
```

产物：

```text
docs/
```

---

## Phase 1：工程基础

目标：

```text
Python
uv
PySide6
pytest
mypy
ruff
CI
```

---

## Phase 2：Core

目标：

```text
Cell
Board
MineGenerator
Reveal
Flag
Victory
GameState
```

此阶段：

**无 GUI。**

---

## Phase 3：Core 测试

目标：

```text
核心逻辑覆盖
边界测试
随机测试
Seed 测试
```

---

## Phase 4：Qt 基础

目标：

```text
QApplication
QMainWindow
Menu
Dialog
QTimer
Event
```

---

## Phase 5：XP UI

目标：

```text
窗口
菜单
计数器
计时器
Face
Board
Cell
```

---

## Phase 6：QPainter

目标：

```text
XP 风格完整绘制
```

---

## Phase 7：输入

目标：

```text
Left
Right
Chord
Mouse State
Keyboard
```

---

## Phase 8：Resize / DPI

目标：

```text
Resizable
Adaptive
DPI
```

这是第一版与原版的重要改进。

---

## Phase 9：经典版完成

此时必须做到：

```text
视觉接近 XP
操作接近 XP
规则接近 XP
窗口体验优于 XP
```

形成：

> **MVP 1.0**

---

# 47. MVP 1.0 验收标准

必须满足：

### 游戏

- [ ] 初级
- [ ] 中级
- [ ] 高级
- [ ] 自定义
- [ ] 首击保护
- [ ] 雷生成
- [ ] 数字计算
- [ ] 自动展开
- [ ] 插旗
- [ ] Chord
- [ ] 胜利
- [ ] 失败
- [ ] 计时

### UI

- [ ] XP 风格窗口
- [ ] XP 风格菜单
- [ ] XP 风格棋盘
- [ ] XP 风格数字
- [ ] XP 风格按钮
- [ ] XP 风格雷
- [ ] XP 风格旗帜
- [ ] XP 风格 3D 边框
- [ ] 鼠标按下效果

### 改进

- [ ] 自由调整窗口
- [ ] 自适应棋盘
- [ ] 高 DPI
- [ ] 不变形
- [ ] 不裁剪
- [ ] 不出现明显模糊

### 工程

- [ ] Core 无 Qt 依赖
- [ ] 类型检查通过
- [ ] Lint 通过
- [ ] 测试通过
- [ ] CI 通过
- [ ] 文档完整

---

# 48. MVP 之后

第二阶段才开始：

```text
v1.1
├── Best Times
├── Settings
└── Save

v1.2
├── Seed
└── Replay

v1.3
├── Theme
├── Dark
└── High Contrast

v1.4
├── Hint
├── Statistics
└── Advanced Statistics

v1.5
├── Daily Challenge
└── Challenge Mode
```

---

# 49. 最终产品架构

最终希望形成：

```text
                         Minesweeper
                              │
              ┌───────────────┴───────────────┐
              │                               │
          Application                       UI
              │                               │
              ↓                               ↓
       Game Session                    PySide6 / Qt
              │                               │
              ↓                         QPainter
        Core Engine                            │
              │                               │
      ┌───────┼────────┐                      │
      ↓       ↓        ↓                      │
    Board    Rules     RNG                    │
      │       │        │                      │
      └───────┼────────┘                      │
              ↓                               │
          Game State ─────────────────────────┘
              │
       ┌──────┼─────────┐
       ↓      ↓         ↓
     Save   Replay   Statistics
```

---

# 50. 项目开发原则

整个项目严格遵循以下原则。

## 原则 1：先逻辑，后 UI

不要一开始就画棋盘。

---

## 原则 2：Core 不依赖 Qt

这是最重要的架构原则之一。

---

## 原则 3：数据不硬编码

玩法参数进入配置。

---

## 原则 4：不要过度设计

第一版只解决扫雷。

不要提前设计：

```text
联网
多人
服务器
账号
```

---

## 原则 5：先复刻，再创新

开发顺序必须：

```text
经典规则
 ↓
经典 UI
 ↓
经典交互
 ↓
修复缺陷
 ↓
扩展功能
```

而不是一开始加入大量新功能。

---

## 原则 6：所有重大设计决策记录到 docs

例如为什么：

```text
BFS
```

而不是：

```text
DFS
```

为什么：

```text
QPainter
```

而不是：

```text
QWidget × N
```

都应该留下设计记录。

---

# 51. 最终学习成果

项目完成后，你应该能够回答：

### Python

- 如何设计大型 Python 项目？
- 如何使用类型系统？
- 如何组织 Package？
- 如何进行依赖管理？
- 如何测试？

### Qt

- Event Loop 是什么？
- Signal / Slot 是什么？
- QWidget 生命周期是什么？
- paintEvent 如何工作？
- QPainter 如何工作？
- Resize 如何处理？
- DPI 如何处理？

### 游戏开发

- 游戏状态如何设计？
- 随机地图如何生成？
- Seed 如何实现？
- 游戏胜负如何判断？
- 输入和逻辑如何解耦？
- Replay 如何实现？

### 软件工程

- 如何分层？
- 如何控制依赖？
- 如何测试？
- 如何进行 CI？
- 如何设计配置？
- 如何设计存档格式？
- 如何进行版本演进？

---

# 52. 推荐最终开发顺序

不要跳跃。

严格按照：

```text
01 需求分析
 ↓
02 UI 分析
 ↓
03 架构设计
 ↓
04 项目初始化
 ↓
05 Cell
 ↓
06 Board
 ↓
07 MineGenerator
 ↓
08 Number Calculation
 ↓
09 Reveal
 ↓
10 Flag
 ↓
11 Victory / Lose
 ↓
12 Core Tests
 ↓
13 Qt Window
 ↓
14 Menu
 ↓
15 BoardWidget
 ↓
16 QPainter
 ↓
17 XP Renderer
 ↓
18 Mouse Input
 ↓
19 Timer
 ↓
20 Resize
 ↓
21 DPI
 ↓
22 Classic Mode
 ↓
23 Custom Mode
 ↓
24 Best Times
 ↓
25 Save
 ↓
26 Seed
 ↓
27 Replay
 ↓
28 Theme
 ↓
29 Extended Features
 ↓
30 Packaging
 ↓
31 Release
```

---

# 53. 第一里程碑

第一阶段不要追求“看起来像扫雷”。

第一里程碑应该是：

```text
$ python -m pytest

========================
所有 Core 测试通过
========================
```

并且能够通过代码验证：

```text
创建棋盘
生成雷
计算数字
展开
插旗
胜利
失败
Seed
```

这意味着：

> **扫雷这个游戏本身已经成立，只是还没有 UI。**

---

# 54. 第二里程碑

第二里程碑：

```text
Qt Window
    ↓
QPainter
    ↓
XP 风格棋盘
```

能够完成：

> **不用鼠标，单纯看到一个视觉上接近 XP 扫雷的静态界面。**

---

# 55. 第三里程碑

第三里程碑：

```text
鼠标
 ↓
UI
 ↓
Controller
 ↓
Core
 ↓
Game State
 ↓
UI Repaint
```

此时成为真正可玩的扫雷。

---

# 56. 第四里程碑

完成：

```text
Resize
DPI
Custom Size
Save
Best Time
```

此时：

> **功能已经超过 XP 原版。**

---

# 57. 第五里程碑

完成：

```text
Seed
Replay
Statistics
Themes
Challenge
```

此时项目从：

> “XP 扫雷复刻”

正式变成：

> **“以 XP 扫雷为基础的现代扫雷平台”。**

---

# 58. 项目最终目标

最终项目不是为了证明：

> “我会写一个扫雷。”

而是证明你能够独立完成一个：

```text
小型游戏
    +
桌面 GUI
    +
数据驱动
    +
类型系统
    +
分层架构
    +
随机系统
    +
存档
    +
Replay
    +
测试
    +
CI
    +
Windows 发布
```

的完整软件项目。

**最重要的开发策略是：第一版严格控制范围。**

先做到：

> **XP 经典体验 + 现代可缩放窗口 + 高 DPI + 良好工程结构。**

然后再扩展。

这样可以避免项目从一个 2～3 周可以完成的扫雷，逐渐膨胀成一个永远做不完的“扫雷引擎”。