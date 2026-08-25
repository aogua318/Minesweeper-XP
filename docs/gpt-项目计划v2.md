可以。下面给你一份可以**直接作为项目 `docs/project-plan-v2.md` 使用的正式计划文档**。我把前面讨论的内容整理成了项目文档形式，而不是继续用分析说明的方式。

# Minesweeper-XP 项目计划 v2

> Windows XP 风格扫雷复刻与现代化扩展项目计划

- 文档版本：v2.0
- 项目状态：Planning
- 技术栈：Python + PySide6 / Qt
- 项目类型：桌面游戏 / 软件工程学习项目
- 目标平台：Windows
- 核心目标：完整复刻 Windows XP 经典扫雷的 UI 与核心交互，并在此基础上修复窗口缩放、DPI 等现代环境下的问题，同时建立数据驱动、可测试、可扩展的软件架构。

---

# 目录

1. [项目概述](#1-项目概述)
2. [项目目标](#2-项目目标)
3. [设计原则](#3-设计原则)
4. [XP 兼容性基准](#4-xp-兼容性基准)
5. [现代化改进](#5-现代化改进)
6. [功能范围](#6-功能范围)
7. [技术选型](#7-技术选型)
8. [系统架构](#8-系统架构)
9. [核心领域模型](#9-核心领域模型)
10. [Command / Event 设计](#10-command--event-设计)
11. [渲染系统](#11-渲染系统)
12. [Geometry / Scale / DPI](#12-geometry--scale--dpi)
13. [UI 系统](#13-ui-系统)
14. [数据驱动设计](#14-数据驱动设计)
15. [资源管理与版权策略](#15-资源管理与版权策略)
16. [音频系统](#16-音频系统)
17. [存档系统](#17-存档系统)
18. [国际化](#18-国际化)
19. [测试体系](#19-测试体系)
20. [代码质量与工程规范](#20-代码质量与工程规范)
21. [CI/CD](#21-cicd)
22. [项目目录结构](#22-项目目录结构)
23. [开发阶段](#23-开发阶段)
24. [MVP 1.0](#24-mvp-10)
25. [后续扩展](#25-后续扩展)
26. [Definition of Done](#26-definition-of-done)
27. [版本规划](#27-版本规划)
28. [风险与应对措施](#28-风险与应对措施)
29. [最终验收标准](#29-最终验收标准)

---

# 1. 项目概述

## 1.1 项目名称

**Minesweeper-XP**

---

## 1.2 项目定位

Minesweeper-XP 是一个基于 Python + PySide6 开发的 Windows XP 风格扫雷复刻项目。

项目不是简单实现一个扫雷算法，而是以 Windows XP 经典扫雷作为参考对象，完整研究并复刻：

- 用户界面
- 游戏规则
- 鼠标交互
- 键盘交互
- 游戏状态
- 计时系统
- 菜单系统
- 音效
- 资源表现
- 难度系统

同时针对现代 Windows 环境，对原版存在的显示和窗口限制进行改进。

---

## 1.3 项目核心定位

项目遵循：

> **Original Compatibility First**

即：

> 原版行为优先，现代化改进其次，扩展功能最后。

项目最终形成：

```text
                    Minesweeper-XP
                          │
             ┌────────────┴────────────┐
             │                         │
       XP Compatibility          Modern Improvements
             │                         │
       经典 UI / 规则              Resize / DPI
             │                         │
             └────────────┬────────────┘
                          │
                    Extensible Core
                          │
              Theme / Save / Replay / ...
```

------

# 2. 项目目标

## 2.1 第一目标：XP 风格复刻

尽可能保持 Windows XP 经典扫雷的视觉和交互体验。

包括：

- 主窗口
- 菜单栏
- HUD
- 雷区
- 数字显示
- 笑脸按钮
- 经典颜色
- 棋盘边框
- 单元格样式
- 旗帜
- 问号
- 雷
- 爆炸效果

------

## 2.2 第二目标：完整复刻经典玩法

必须实现：

- Beginner
- Intermediate
- Expert
- Custom
- 左键翻开
- 右键标记
- 旗帜
- 问号
- Chord
- 雷区生成
- 空白区域扩散
- 胜利判定
- 失败判定
- 计时
- 重启

------

## 2.3 第三目标：修复现代环境问题

原版扫雷存在窗口尺寸固定、现代 DPI 适配不足等问题。

Minesweeper-XP 必须支持：

- 窗口 Resize
- 自适应布局
- 高 DPI
- 多种 UI Scale
- 像素风资源缩放
- 最小窗口尺寸
- 窗口状态保存

------

## 2.4 第四目标：建立良好的软件工程架构

项目必须具备：

- 明确的模块边界
- 类型标注
- 数据驱动
- 单元测试
- 集成测试
- 兼容性测试
- CI
- 静态检查
- 可维护代码
- 可扩展架构

------

# 3. 设计原则

## 3.1 Core 与 UI 解耦

Core 不允许依赖 PySide6。

```text
Core
  X
  │
  └── PySide6
```

Core 应能够脱离 Qt 单独运行和测试。

------

## 3.2 UI 不实现游戏规则

UI 负责：

- 输入
- 显示
- 布局
- 绘制

Core 负责：

- 游戏状态
- 棋盘
- 雷
- 翻开
- 标记
- 胜负

禁止：

```text
BoardWidget
    ↓
直接修改 Cell
```

推荐：

```text
Mouse
  ↓
Command
  ↓
Game
  ↓
Event
  ↓
UI
```

------

## 3.3 数据驱动参数，代码驱动行为

适合数据驱动：

- 难度
- 棋盘尺寸
- 雷数量
- 主题
- 本地化字符串
- UI 参数
- 配置

不适合数据驱动：

- Reveal 算法
- Chord 算法
- 胜利判定
- 状态机
- 雷生成逻辑

原则：

> **Data defines parameters; Code defines behavior.**

------

## 3.4 XP 兼容和现代改进必须分离

所有与 XP 不一致的设计必须明确记录。

分成：

```text
Original Behavior
Intentional Deviation
Known Difference
```

避免随着项目发展失去复刻目标。

------

## 3.5 扩展功能不得污染 Core

例如：

- Replay
- AI
- Hint
- Probability

都不能让基础：

```text
Board
Cell
Reveal
```

变得复杂。

------

# 4. XP 兼容性基准

## 4.1 基准来源

以 Windows XP 经典扫雷实际行为、界面和资源作为参考。

项目需要建立正式兼容性文档：

```text
docs/
└── compatibility/
    ├── original-behavior.md
    ├── ui-specification.md
    ├── menu-specification.md
    ├── intentional-deviations.md
    └── known-differences.md
```

------

## 4.2 UI 基准

经典 XP 扫雷的重要视觉元素：

```text
Cell
16 × 16

Smile
24 × 24

HUD
经典 XP 布局

LED
3 位数字显示
```

具体：

- 坐标
- 尺寸
- 边框
- 字体
- 颜色
- 资源状态

必须记录到 UI Specification。

------

## 4.3 游戏状态

至少：

```text
READY
PLAYING
WON
LOST
```

状态转换：

```text
READY
  │
  │ first reveal
  ▼
PLAYING
  │
  ├───────────────┐
  │               │
 victory          mine
  │               │
  ▼               ▼
 WON             LOST
```

------

# 5. 现代化改进

## 5.1 Resize

窗口允许用户自由调整大小。

Resize 后：

- 棋盘保持正方形
- HUD 保持比例
- 笑脸保持比例
- 数字保持比例
- 边框保持正确
- 棋盘完整显示

------

## 5.2 DPI

支持现代 Windows：

```text
100%
125%
150%
175%
200%
```

目标：

- 无明显模糊
- 无布局错位
- 无棋盘变形
- 无字体异常

------

## 5.3 Scale

逻辑尺寸：

```text
Cell = 16 × 16
```

支持：

```text
1×
2×
3×
```

优先使用整数缩放。

无法满足窗口尺寸时才使用 Fractional Scale。

------

# 6. 功能范围

## 6.1 P0：必须实现

```text
XP 风格 UI
经典扫雷规则
Beginner
Intermediate
Expert
Custom
鼠标
键盘
Chord
Timer
Victory
Lost
Restart
Resize
DPI
```

------

## 6.2 P1：应该实现

```text
Best Time
Sound
Theme
Settings
中文
英文
Save / Load
```

------

## 6.3 P2：可以实现

```text
Seed
Statistics
Replay
```

------

## 6.4 P3：实验功能

```text
Hint
Probability
No Guess
Daily Challenge
AI
特殊模式
```

P3 不得阻塞 v1.0。

------

# 7. 技术选型

## 7.1 Python

使用 Python 作为主要开发语言。

原因：

- 类型标注完善
- 开发效率高
- 适合游戏逻辑开发
- 适合快速实验
- 便于测试
- 与已有开发经验衔接

------

## 7.2 PySide6

使用 PySide6 / Qt。

主要使用：

```text
QMainWindow
QWidget
QPainter
QPixmap
QTimer
QMenu
QDialog
QSettings
```

------

## 7.3 开发工具

```text
Python
uv
PySide6
pytest
ruff
mypy
Git
GitHub Actions
```

后期可加入：

```text
Hypothesis
```

------

# 8. 系统架构

总体架构：

```text
┌───────────────────────────────┐
│              UI               │
│            PySide6            │
└───────────────┬───────────────┘
                │
          Qt Adapter
                │
┌───────────────▼───────────────┐
│         Application           │
│       Controller / Session    │
└───────────────┬───────────────┘
                │
        Command / Event
                │
┌───────────────▼───────────────┐
│             Core              │
│         Game / Rules          │
└───────────────┬───────────────┘
                │
       ┌────────┼────────┐
       │        │        │
     Model    Rules     RNG
       │        │        │
       └────────┼────────┘
                │
              State
```

------

# 9. 核心领域模型

## 9.1 Cell

Cell 表示单个格子。

属性：

```text
is_mine
adjacent_mines
visibility
mark
```

可见状态：

```text
Hidden
Revealed
```

标记：

```text
None
Flag
Question
```

------

# 9.2 Coordinate

用于表达：

```text
row
column
```

提供：

- 邻居计算
- 边界处理
- 坐标转换

------

# 9.3 Board

Board 负责：

- 宽度
- 高度
- 雷数量
- Cell 管理
- 邻居查询
- 边界判断

Board 不负责：

- Qt
- 绘制
- 音效
- 菜单

------

# 9.4 Game

Game 负责：

- 生命周期
- 游戏状态
- 操作入口
- 胜利
- 失败
- 重启

------

# 9.5 MineGenerator

负责：

- 雷生成
- Random
- Seed
- 首次点击规则

------

# 9.6 Reveal

使用 BFS / Queue 实现空白区域扩散。

避免深度递归造成：

```text
RecursionError
```

------

# 10. Command / Event 设计

## 10.1 Command

统一玩家操作：

```text
RevealCell
ToggleMark
ChordCell
RestartGame
```

输入来源：

```text
Mouse
Keyboard
Replay
AI
```

都转换成 Command。

------

## 10.2 Event

Core 产生：

```text
GameStarted
CellRevealed
CellMarked
GameWon
GameLost
TimerStarted
TimerStopped
```

流程：

```text
Core
 ↓
Event
 ↓
Application
 ↓
Qt Signal
 ↓
UI
```

------

# 11. Timer

Core 不依赖 QTimer。

使用：

```text
Clock
```

Core 只处理：

```text
start
stop
elapsed
```

Qt 层使用：

```text
QTimer
```

负责定期刷新。

测试环境使用：

```text
FakeClock
```

------

# 12. 渲染系统

结构：

```text
Game State
    ↓
Render Model
    ↓
Renderer
    ↓
QPainter
```

Renderer 只负责：

> 将状态转换为视觉表现。

Renderer 不修改 Game。

------

# 13. Geometry / Scale / DPI

使用三层坐标：

```text
Logical Coordinate
        ↓
Scale
        ↓
Device Coordinate
```

例如：

```text
Logical Cell = 16 × 16

1× → 16 × 16
2× → 32 × 32
3× → 48 × 48
```

------

# 14. UI 系统

目录：

```text
ui/
├── windows/
│   └── main_window.py
│
├── widgets/
│   ├── board_widget.py
│   ├── hud_widget.py
│   └── face_button.py
│
├── dialogs/
│   ├── options_dialog.py
│   └── about_dialog.py
│
└── controllers/
    └── game_controller.py
```

------

# 15. MainWindow

负责：

- 主窗口
- 菜单
- Dialog
- 主布局
- Window State

不负责：

- 雷生成
- 游戏规则
- 胜负判定

------

# 16. BoardWidget

负责：

- 鼠标输入
- 坐标转换
- Rendering

输入流程：

```text
Mouse Position
      ↓
Device Coordinate
      ↓
Logical Coordinate
      ↓
Board Coordinate
      ↓
Command
```

------

# 17. HUD

显示：

```text
Mine Counter
Timer
Face
```

HUD 不负责计时。

------

# 18. 数据驱动

目录：

```text
data/
├── difficulties.json
├── themes/
│   └── classic_xp.json
└── locales/
    ├── zh_CN.json
    └── en_US.json
```

------

## 18.1 Difficulty

示例：

```json
{
    "beginner": {
        "width": 9,
        "height": 9,
        "mines": 10
    },
    "intermediate": {
        "width": 16,
        "height": 16,
        "mines": 40
    },
    "expert": {
        "width": 30,
        "height": 16,
        "mines": 99
    }
}
```

------

# 19. 配置错误处理

用户配置：

```text
读取失败
 ↓
记录 warning
 ↓
恢复默认
```

内置资源：

```text
读取失败
 ↓
明确报错
 ↓
停止启动
```

禁止静默吞掉开发资源错误。

------

# 20. Theme

Theme 负责：

- 视觉参数
- Sprite
- UI 参数
- Scale 参数

例如：

```text
Classic XP
Modern
Custom
```

Theme 不负责：

- 游戏规则
- 游戏状态

------

# 21. 资源管理

使用：

```text
AssetProvider
```

UI 不直接访问：

```text
blocks.bmp
```

而访问：

```text
cell_closed
cell_open
mine
flag
question
smile_normal
smile_pressed
smile_won
smile_lost
```

------

# 22. 资源版权策略

开发环境：

```text
可以使用原版资源进行本地研究和验证
```

公开 GitHub：

```text
不提交未经许可的微软原版资源
```

项目必须提供：

```text
assets/README.md
```

说明：

- 资源来源
- 使用范围
- 版权状态
- 公共发行方案

最终公开版本使用：

- 自制资源
- 或具有明确再分发许可的资源

------

# 23. 音频系统

Core 不依赖音频库。

Core 只产生事件：

```text
CellRevealed
FlagPlaced
GameWon
GameLost
```

Audio 层根据事件播放声音。

------

# 24. 国际化

第一版本支持：

```text
zh_CN
en_US
```

所有界面文字必须来自 Localization。

禁止：

```python
menu.setTitle("游戏")
```

推荐：

```text
Localization
      ↓
Translated String
      ↓
Qt UI
```

------

# 25. Save / Load

保存格式必须带版本：

```json
{
    "format_version": 1,
    "game_version": "...",
    "difficulty": "...",
    "width": 9,
    "height": 9,
    "mine_count": 10,
    "seed": null,
    "state": "...",
    "elapsed_time": 0,
    "cells": []
}
```

未来格式变化必须支持版本迁移。

------

# 26. 测试体系

```text
tests/
├── unit/
├── integration/
├── compatibility/
├── property/
└── performance/
```

------

## 26.1 Unit Test

覆盖：

```text
Cell
Board
Coordinate
MineGenerator
Reveal
Mark
Chord
Victory
Game
```

------

## 26.2 Integration Test

测试：

```text
Command
 ↓
Game
 ↓
Event
```

确保完整业务流程正确。

------

## 26.3 Compatibility Test

针对 XP 行为：

```text
左键
右键
旗帜
问号
Chord
Restart
Timer
Victory
Lost
```

逐项验证。

------

## 26.4 Property Test

后期使用 Hypothesis。

例如：

```text
实际雷数量 == 配置雷数量
adjacent_mines ==
实际邻居雷数量
```

------

## 26.5 Performance Test

测试：

```text
9×9
16×16
30×16
100×100
500×500
```

重点测试：

- 雷生成
- Reveal
- 空白区域扩散
- 渲染

------

# 27. 代码质量

代码必须：

- 使用类型标注
- 避免隐式类型
- 保持单一职责
- 减少全局状态
- 避免循环依赖
- 避免过度继承
- 使用明确的数据结构

------

# 28. 工具规范

## Ruff

负责：

- Lint
- Import
- 基础代码规范

------

## Mypy

负责：

- 静态类型检查

------

## Pytest

负责：

- 单元测试
- 集成测试
- 回归测试

------

# 29. CI

GitHub Actions：

```text
Push / Pull Request
        ↓
Ruff
        ↓
Mypy
        ↓
Pytest
        ↓
Build
```

任何关键检查失败：

```text
CI = Failed
```

------

# 30. 项目目录结构

```text
Minesweeper-XP/
│
├── src/
│   └── minesweeper/
│       │
│       ├── core/
│       │   ├── model/
│       │   │   ├── board.py
│       │   │   ├── cell.py
│       │   │   └── coordinate.py
│       │   │
│       │   ├── rules/
│       │   │   ├── reveal.py
│       │   │   ├── marking.py
│       │   │   ├── chord.py
│       │   │   └── victory.py
│       │   │
│       │   ├── generation/
│       │   │   ├── mine_generator.py
│       │   │   └── seed.py
│       │   │
│       │   ├── command.py
│       │   ├── event.py
│       │   ├── clock.py
│       │   └── game.py
│       │
│       ├── application/
│       │   └── controllers/
│       │
│       ├── ui/
│       │   ├── windows/
│       │   ├── widgets/
│       │   └── dialogs/
│       │
│       ├── rendering/
│       │   ├── renderer/
│       │   ├── sprite/
│       │   └── theme/
│       │
│       ├── geometry/
│       │
│       ├── audio/
│       │
│       ├── persistence/
│       │
│       └── localization/
│
├── data/
│   ├── difficulties.json
│   ├── themes/
│   └── locales/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── compatibility/
│   ├── property/
│   └── performance/
│
├── docs/
│   ├── compatibility/
│   ├── architecture/
│   ├── development/
│   └── design/
│
├── assets/
│   └── README.md
│
├── local-assets/
│   └── .gitkeep
│
├── scripts/
│
├── .github/
│   └── workflows/
│
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

------

# 31. 开发阶段

## Phase 0：需求与原版基准

### 目标

确定：

> Windows XP 扫雷究竟需要复刻什么。

### 工作

- 分析原版 UI
- 分析资源
- 分析菜单
- 分析鼠标行为
- 分析键盘行为
- 分析游戏规则
- 记录特殊行为
- 建立截图基准

### 产物

```text
docs/compatibility/
```

------

# 32. Phase 1：工程基础

建立：

```text
Git
uv
pyproject.toml
pytest
ruff
mypy
GitHub Actions
```

验收：

```text
pytest
ruff
mypy
build
```

全部能够运行。

------

# 33. Phase 2：Core

实现：

```text
Cell
Coordinate
Board
Game
MineGenerator
Reveal
Mark
Chord
Victory
Clock
Command
Event
```

目标：

> 不依赖 Qt 完成完整扫雷逻辑。

------

# 34. Phase 3：Core 测试

完成：

- Unit Tests
- Boundary Tests
- Integration Tests
- Property Tests

目标：

> Core 可以独立运行并稳定通过测试。

------

# 35. Phase 4：XP UI Prototype

实现：

```text
MainWindow
Menu
HUD
Face
Board
```

暂时不要求完整游戏。

目标：

> 验证 XP UI 的布局和视觉表现。

------

# 36. Phase 5：Rendering / Geometry

实现：

```text
QPainter
Sprite
AssetProvider
Theme
Logical Coordinate
Scale
DPI
Resize
```

目标：

> 在不同窗口尺寸和 DPI 下正确显示。

------

# 37. Phase 6：Input Integration

实现：

```text
Mouse
Keyboard
Command
Game
Event
UI
Timer
Audio
```

目标：

> 完成完整可玩的 XP 风格扫雷。

------

# 38. Phase 7：XP Compatibility

建立 Compatibility Checklist。

逐项验证：

```text
Beginner
Intermediate
Expert
Custom

Reveal
Flag
Question
Chord

Victory
Lost
Restart
Timer
```

------

# 39. Phase 8：Modernization

实现：

```text
Resize
Adaptive Layout
DPI
Scale
Window State
Minimum Size
```

目标：

> 保持 XP 风格，同时解决原版窗口和现代显示环境的问题。

------

# 40. Phase 9：MVP 1.0

必须具备：

```text
XP 风格 UI
经典玩法
三档难度
自定义难度
鼠标
键盘
Chord
计时
胜利
失败
重启
Resize
DPI
音效
```

------

# 41. Phase 10：扩展功能

按照：

```text
Theme
 ↓
Localization
 ↓
Settings
 ↓
Best Time
 ↓
Save
 ↓
Seed
 ↓
Statistics
```

顺序开发。

------

# 42. Phase 11：高级功能

只有核心稳定后才开发：

```text
Replay
Hint
Probability
No Guess
Challenge
AI
```

------

# 43. Phase 12：Release

完成：

```text
测试
CI
Build
打包
README
CHANGELOG
LICENSE
Asset Policy
用户文档
开发文档
```

最终发布：

```text
v1.0.0
```

------

# 44. Definition of Done

一个功能只有满足以下条件才算完成：

```text
[ ] 需求明确
[ ] 设计完成
[ ] 实现完成
[ ] 类型标注
[ ] Unit Test
[ ] Integration Test（如需要）
[ ] Compatibility Test（如需要）
[ ] Ruff
[ ] Mypy
[ ] 手动验证
[ ] 文档更新
```

------

# 45. 版本规划

## v0.1

```text
Core Prototype
```

完成：

- Board
- Cell
- MineGenerator
- Reveal
- Mark
- Victory

------

## v0.2

```text
XP UI Prototype
```

完成：

- MainWindow
- HUD
- BoardWidget
- Face
- XP Layout

------

## v0.3

```text
Playable
```

完成：

- Mouse
- Keyboard
- Chord
- Timer
- Victory
- Lost

------

## v0.4

```text
XP Compatibility
```

完成：

- XP UI 对照
- XP 行为对照
- 资源系统
- Theme

------

## v0.5

```text
Modernization
```

完成：

- Resize
- DPI
- Scale
- Adaptive Layout

------

## v0.6

```text
Engineering
```

完成：

- Test
- CI
- Type Check
- Lint
- Performance

------

## v0.7

```text
Persistence
```

完成：

- Settings
- Best Time
- Save / Load

------

## v0.8

```text
Localization / Theme
```

完成：

- 中文
- 英文
- Theme

------

## v0.9

```text
Release Candidate
```

完成：

- 全面测试
- UI 修复
- 性能优化
- 文档
- 打包

------

## v1.0

```text
Minesweeper-XP
```

达到正式版本标准。

------

# 46. 风险与应对

## 46.1 UI 复刻困难

### 风险

Qt 默认控件与 XP 原生控件视觉存在差异。

### 对策

重要视觉组件使用：

```text
QWidget
+
QPainter
```

自行绘制。

------

## 46.2 DPI 导致像素模糊

### 对策

采用：

```text
Logical Coordinate
+
Integer Scale
+
Nearest Neighbor
```

------

## 46.3 Core 与 UI 耦合

### 对策

强制：

```text
Core
X
Qt
```

通过：

```text
Command
Event
Adapter
```

通信。

------

## 46.4 项目范围失控

### 对策

严格执行：

```text
P0
P1
P2
P3
```

P3 不得影响 v1.0。

------

## 46.5 原版资源版权

### 对策

开发环境与公开发布资源分离。

------

## 46.6 过度设计

### 对策

遵循：

> **需要时创建模块，而不是为了未来可能需要而提前实现。**

架构预留边界，但不提前实现全部功能。

------

# 47. 最终验收标准

## 47.1 游戏功能

```text
[ ] Beginner
[ ] Intermediate
[ ] Expert
[ ] Custom
[ ] Reveal
[ ] Flag
[ ] Question
[ ] Chord
[ ] Victory
[ ] Lost
[ ] Restart
[ ] Timer
```

------

## 47.2 XP UI

```text
[ ] Main Window
[ ] Menu
[ ] HUD
[ ] LED
[ ] Face
[ ] Board
[ ] Cell
[ ] Mine
[ ] Flag
[ ] Question
[ ] Number
```

------

## 47.3 Modern UI

```text
[ ] Resize
[ ] Scale
[ ] DPI
[ ] Minimum Size
[ ] Window State
[ ] 不变形
[ ] 不明显模糊
```

------

## 47.4 工程质量

```text
[ ] Core 不依赖 Qt
[ ] 类型标注
[ ] Unit Test
[ ] Integration Test
[ ] Compatibility Test
[ ] Ruff
[ ] Mypy
[ ] CI
```

------

## 47.5 数据驱动

```text
[ ] Difficulty
[ ] Theme
[ ] Localization
[ ] Configuration
```

------

## 47.6 发布

```text
[ ] README
[ ] CHANGELOG
[ ] LICENSE
[ ] Asset Policy
[ ] Build
[ ] Package
[ ] Release
```

------

# 48. 项目成功标准

Minesweeper-XP 不以“功能数量”作为成功标准。

最终成功标准为：

```text
┌──────────────────────────────────────┐
│          Minesweeper-XP v1.0         │
├──────────────────────────────────────┤
│                                      │
│  XP UI 复刻       ✓                  │
│  XP 游戏规则      ✓                  │
│  鼠标/键盘        ✓                  │
│  Chord            ✓                  │
│  Resize           ✓                  │
│  DPI              ✓                  │
│  数据驱动         ✓                  │
│  Core/UI 解耦     ✓                  │
│  自动化测试       ✓                  │
│  CI               ✓                  │
│  可扩展架构       ✓                  │
│                                      │
└──────────────────────────────────────┘
```

最终目标不是：

> “写出了一个能玩的扫雷。”

而是：

> **完整经历一次从原版软件分析、需求规格化、领域建模、算法实现、GUI 开发、2D 渲染、数据驱动、测试、CI 到发布的软件工程流程。**

------

# 49. 后续开发原则

在后续开发过程中，如果出现：

> “这个功能要不要加？”

优先按照以下顺序判断：

```text
是否属于 XP 复刻？
        │
        ├── 是 → P0
        │
        └── 否
             │
             ↓
是否解决现代环境问题？
             │
             ├── 是 → P0/P1
             │
             └── 否
                  │
                  ↓
是否有明确学习价值？
                  │
                  ├── 是 → P1/P2
                  │
                  └── 否 → 暂不实现
```

项目始终遵循：

> **先完成一个优秀的 XP 风格扫雷，再逐步把它发展成一个现代化、可扩展的扫雷游戏框架。**

------

# 50. 当前第一步

项目正式开始后，不立即编写游戏代码。

首先完成：

```text
Phase 0
```

建立：

```text
docs/compatibility/
├── original-behavior.md
├── ui-specification.md
├── menu-specification.md
├── intentional-deviations.md
└── known-differences.md
```

然后建立：

```text
Phase 1
```

完成：

```text
pyproject.toml
pytest
ruff
mypy
GitHub Actions
```

最后才进入：

```text
Phase 2
Core
```

**第一份实际代码应该从 `core/model/cell.py`、`coordinate.py`、`board.py` 这些领域模型开始，而不是从 `MainWindow` 开始。**

```
这份可以直接作为 **`docs/project-plan-v2.md`**。其中我特意把“**XP 复刻**、**现代化修复**、**工程学习**、**未来扩展**”四条线分开，避免后续开发时因为不断加功能导致项目失控。
```