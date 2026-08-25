# Minesweeper-XP 项目计划（合并版）

> 说明：本文档为项目唯一权威计划，合并自 `docs/deepseek-项目计划.md`（精确规格、资源落地）与 `docs/gpt-WinXP 风格扫雷复刻与扩展项目计划.md`（工程规范、学习路线、长远规划）。两份原始文档保留在 docs/ 供追溯。
>
> 更新日期：2026-08-25　状态：计划定稿，等待按阶段实施

## 1. 项目概述

### 1.1 项目定位

以 Windows XP 扫雷（WINMINE 5.1）为视觉与交互基准的现代化扫雷游戏，遵循「经典体验一致、原版缺陷修复、功能在此基础上扩展」。

### 1.2 核心目标

1. 像素级复刻 XP 视觉与操作（直接使用从原版提取的位图、图标、音效资源）。
2. 修复原版“窗口不可缩放”缺陷，支持自适应缩放与高 DPI。
3. Core（游戏逻辑）与 UI 完全解耦，核心逻辑不依赖 Qt。
4. 数据驱动：规则、主题、文案、用户配置全部使用 JSON。
5. 工程规范：类型明确（mypy）、代码规范（ruff）、分层架构、单元测试（手动运行）、详细注释（AGENTS.md）。
6. v1 扩展：高分记录、音效开关、键盘操作、主题数据文件、语言切换（默认中文）。
7. 学习目标：通过完整项目掌握 Python 类型系统与包管理、Qt 事件与绘制、游戏状态机/随机生成/首击保护、软件工程分层/测试/配置设计。

## 2. 技术栈与环境

| 项目 | 决策 |
| --- | --- |
| Python | 3.14.7（本机已装） |
| GUI | PySide6 ≥ 6.10（需安装；若 cp314 轮子缺失则回退 Python 3.13） |
| 依赖管理 | pyproject.toml + venv + pip（可选用 uv） |
| 质量工具 | pytest（仅手动运行）、mypy、ruff |
| 版本控制 | Git，Conventional Commits |
| CI | GitHub Actions（后置可选，Phase 8 或 v1.1；仅远端执行，不违反本地“不自动测试”约定） |
| 发布 | PyInstaller（v1.3） |
| 原则 | Core 不依赖 PySide6；核心逻辑类型明确；避免无理由的 `Any` 与 `# type: ignore` |

## 3. 资源提取与资产清单（已完成）

### 3.1 提取方式

- 源文件：`other/WINMINE.EXE`（仅本地参考，不入 Git；`.gitignore` 已排除 `other/`）。
- 提取脚本：`other/extract_resources.py`（纯标准库解析 PE 资源，可随时重跑）。
- 完整产物：`other/extracted/`（共 26 项资源）；`strings.txt` 提供原版英文文案，作为 `en_US` 语言包基准。
- 已确认快捷键（原版加速键表）：F1=帮助主题、F2=新游戏。

### 3.2 游戏资产（`res/`）

| 文件 | 说明 |
| --- | --- |
| `res/sprites/blocks_color.bmp` | 方块 16 态精灵条（彩色，位图 410） |
| `res/sprites/blocks_mono.bmp` | 方块 16 态精灵条（单色，位图 411） |
| `res/sprites/digits_color.bmp` | LED 数字条 13×23×12（0–9、负号、空白，位图 420） |
| `res/sprites/digits_mono.bmp` | LED 数字条（单色，位图 421） |
| `res/sprites/smiles_color.bmp` | 笑脸 5 态 24×24（正常/惊讶/失败/胜利/按下，位图 430） |
| `res/sprites/smiles_mono.bmp` | 笑脸 5 态（单色，位图 431） |
| `res/icons/app.ico` | 窗口与任务栏图标（16/32/48 多尺寸） |
| `res/sounds/tick.wav` | 音效：滴答（资源 432） |
| `res/sounds/win.wav` | 音效：胜利（资源 433） |
| `res/sounds/lose.wav` | 音效：失败（资源 434） |

### 3.3 方块状态 ↔ 图块映射（已确认）

位图条按状态 0–15 顺序排列，存储为自下而上（BMP 正高度），加载时需垂直翻转：

| 状态值 | 含义 | 图块内容 |
| --- | --- | --- |
| 0 | 翻开空格 | 平灰格 |
| 1–8 | 数字 1–8 | 蓝/绿/红/深蓝/深红/青/黑/灰 |
| 9 | 按下的问号 | 平灰 + 黑色问号 |
| 10 | 黑雷 | 普通地雷 |
| 11 | 错旗雷 | 地雷 + 红色叉 |
| 12 | 红底雷 | 红底 + 地雷 |
| 13 | 问号 | 凸起 + 黑色问号 |
| 14 | 旗帜 | 凸起 + 红旗 |
| 15 | 未翻开 | 纯凸起灰格 |

### 3.4 版权说明

提取资源来自微软原版程序，仅供个人学习与本地使用；仓库若公开分发需替换为自绘资源或另行授权。架构通过主题文件预留替换点，不影响整体设计。

## 4. 复刻规格（UI 与玩法基准）

### 4.1 窗口与 HUD（常量以原版为准）

- 标题：中文“扫雷” / 英文 “Minesweeper”；背景 #C0C0C0；外框 3px 内凹。
- HUD 面板 (9,9)-(W-10,45)，棋盘面板 (9,52)-(W-10,H-10)，均 3px 内凹。
- 左上 3 位 LED 计数器（数字位 13×23，x=17/30/43，y=16）；中间 24×24 笑脸（居中，y=15）；右上 3 位计时器。
- 方块 16×16，棋盘从 (12,55) 起、每格 +16；等价公式 col×16−4、row×16+39。
- 窗口尺寸由棋盘反推：宽 = 22 + 16×列数，高 = 65 + 16×行数（基准 100%，不含菜单栏高度差异）。

### 4.2 菜单（原版结构，默认中文）

- 游戏：新游戏(F2) / 初级 / 中级 / 高级 / 自定义… / 声音☑ / 标记☑ / 颜色☑ / 最佳时间… / 退出
- 帮助：帮助主题(F1) / 搜索帮助 / 使用帮助 / 关于扫雷
- v1 行为：帮助主题 → 弹出当前语言包的玩法说明对话框；搜索帮助、使用帮助置灰；关于显示署名（Robert Donner & Curt Johnson）。

### 4.3 玩法规则

- 左键翻开；右键循环“无→旗→问号→无”（“标记”关闭时仅旗→无）；中键或左右键同按对数字格做 3×3 chord（旗数=数字才触发，旗错引爆）。
- 首击保证其 3×3 邻域无雷：首击后才布雷（懒生成），计时同时开始。
- 难度：初级 9×9/10、中级 16×16/40、高级 16×30/99；自定义行 9–24、列 9–30、雷 10 至 rows×cols−9，非法值拒绝。
- 计时：0–999 封顶（3 位 LED）；沿用原版“最小化时暂停、恢复继续”；胜负停止。
- 雷数显示：剩余雷 = 雷数 − 旗数，可为负（使用数字条负号字形 index 11）。
- 胜负表现：失败显示红底雷、其余雷与错旗、哭脸；胜利全翻开、墨镜脸；刷新纪录弹输入名字对话框。

### 4.4 对话框

- 自定义：行/列/雷数三个输入（含范围校验与错误提示）。
- 最佳时间：三档难度各 Top 5（时间/名字/日期）+ 重置按钮；对话框中注明“Top 5 为现代扩展”。
- 输入名字：新纪录时弹出，默认“匿名”。
- 关于：程序名、版本、署名。

### 4.5 缩放修复（统一模型）

- 基础格子 16px，缩放范围 50%–300%（8–48px），最近邻插值保持像素风。
- 自适应：窗口 resize 时 scale = min(可用宽/列数, 可用高/行数) 反推，保持宽高比、不拉伸、不裁剪。
- 缩放档：Ctrl+滚轮 / 视图菜单（50/75/100/125/150/200/300%）。
- 最小窗口：由最小格子（8px）+ HUD + 边框反推，不得随意写死。
- 高 DPI：依赖 Qt devicePixelRatio，绘制用逻辑像素；重点测试 100/125/150/200%。

## 5. 总体架构

### 5.1 分层与依赖方向

```text
UI（PySide6） → Application（Controller / GameSession） → Core（Board / Rules / RNG）
```

依赖只允许从上向下；Core 不 import 任何 Qt 模块。

### 5.2 目录结构（v1）

```text
minesweeper-xp/
├── pyproject.toml / README.md / CHANGELOG.md / LICENSE
├── docs/            # 开发规范、游戏设计、架构、数据 schema、测试策略、ADR
├── res/             # 精灵、图标、音效、主题、语言包、难度配置（已有）
├── src/minesweeper_xp/
│   ├── main.py
│   ├── core/        # cell / board / game / difficulty / enums / generator
│   ├── application/ # controller / game_session
│   ├── ui/          # main_window / board_widget / hud_widget / menu / dialogs
│   ├── rendering/   # sprite_loader / block_renderer / hud_renderer / theme
│   ├── geometry/    # board_geometry（窗口↔棋盘↔格子坐标换算）
│   ├── data/        # config_loader / difficulty / settings / locales
│   └── audio/       # sound_manager
├── tests/           # core / geometry / data
└── scripts/         # validate_config.py 等辅助脚本
```

### 5.3 事件流（Core ↔ UI 解耦）

Core 不依赖 Qt，通过事件对象/回调暴露状态变化；Application 层桥接为 Qt Signal：

- `cell_changed(row, col, state)` / `board_reset`
- `flags_changed(remaining)` / `timer_ticked(seconds)`
- `game_state_changed(READY/PLAYING/WON/LOST)`
- `best_time_updated(difficulty, entry)`

UI 只监听信号并局部重绘，不轮询 Core。

## 6. 数据驱动设计（JSON schema，字段级）

### 6.1 `res/difficulties.json`

```json
{
  "beginner":      { "rows": 9,  "cols": 9,  "mines": 10 },
  "intermediate":  { "rows": 16, "cols": 16, "mines": 40 },
  "expert":        { "rows": 16, "cols": 30, "mines": 99 },
  "custom_limits": { "min_rows": 9, "max_rows": 24, "min_cols": 9, "max_cols": 30, "min_mines": 10 }
}
```

校验规则：自定义雷数 ≤ rows×cols−9；所有字段缺省回退三档预设。

### 6.2 `res/themes/classic_xp.json`

字段：`name`、`display_name`、`sprites`（blocks/blocks_mono/digits/digits_mono/smiles/smiles_mono/icon 路径）、`sizes`（cell:16、digit:[13,23]、smile:24）、`colors`（背景、面板、LED 背景/前景、数字 1–8）。加载失败时回退内置默认主题。

### 6.3 `res/locales/zh_CN.json` 与 `en_US.json`

键值对语言包：`app_title`、`menu_game/new/beginner/intermediate/expert/custom/sound/marks/color/best_times/exit`、`menu_help/contents/about`、`custom_dialog.*`、`best_times.*`、`winner_name.*`、`about.*`、`help_text.*` 等。切换语言后全 UI 立即重绘并持久化。

### 6.4 用户配置 `config.json`（QStandardPaths.AppDataLocation/minesweeper_xp/）

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `language` | string | `zh_CN` | 界面语言 |
| `theme` | string | `classic_xp` | 当前主题 |
| `sound` | bool | true | 音效总开关 |
| `volume` | float | 0.8 | 音量 0.0–1.0 |
| `marks` | bool | true | 问号标记开关 |
| `color` | bool | true | 颜色/单色模式 |
| `window` | object | — | 宽、高、缩放比例 |
| `best_times` | object | 空 | 每难度 Top 5（name/time/date） |

### 6.5 校验与回退

`data` 层将 JSON 解析为 dataclass 并校验；字段缺失或非法时回退默认值并输出警告日志。

## 7. 扩展功能（v1）

- 高分记录：每难度 Top 5 + 最佳时间对话框（可重置）；新纪录输入名字（默认“匿名”）。
- 音效开关与音量：对应原版“声音”菜单项，音量持久化。
- 键盘操作：方向键移动焦点、空格翻开、F 标记循环、Enter 3×3 chord、F2 新游戏、Ctrl+滚轮缩放。
- 主题数据文件：v1 内置 `classic_xp`，菜单即时切换。
- 语言切换：zh_CN（默认）/ en_US，即时切换并持久化。

## 8. 分阶段实施与验收

| 阶段 | 内容 | 验收标准 |
| --- | --- | --- |
| P0 设计 | docs 全套（00-开发规范 / 01-游戏设计 / 02-架构 / 03-数据 schema / 04-测试策略）+ 本文档 | schema 字段级定稿，无未决项 |
| P1 工程骨架 | pyproject、venv、安装 PySide6/pytest/mypy/ruff、包结构、空窗口 | ruff check、mypy src、手动 pytest 通过；`python -m minesweeper_xp` 启动空窗口 |
| P2 Core | Cell/Board/Generator/Game/Difficulty + 单测 | 手动 pytest 全绿；Core 无 Qt import |
| P3 资源加载验证 | SpriteLoader（翻转、单色）、16 态映射核对 | 加载并渲染精灵条，映射表逐项核对 |
| P4 渲染层 | BoardWidget/HudWidget 静态 XP 界面 | 静态界面与原版截图接近 |
| P5 交互与状态机 | 鼠标（按下/拖出/双键 chord）、键盘、计时、胜负、表情/音效 | 可完整对局；999 封顶、最小化暂停、负雷数显示 |
| P6 缩放与 DPI | 统一缩放模型、最小窗口、125/150/200% | 50–300% 不变形不裁剪；高 DPI 清晰 |
| P7 扩展功能 | 高分/最佳时间、音效开关、主题、语言切换 | 各项手工验收清单通过 |
| P8 收尾 | 菜单完整（F1/F2、置灰项）、关于、ADR×3、README/CHANGELOG、（可选 CI） | MVP 验收清单全勾 |

## 9. 测试与验收

### 9.1 Core 单元测试（pytest，手动运行）

- 布雷数量与随机种子可复现；不同种子产生不同布局。
- 首击 3×3 安全；翻开扩散与边界（角落、大面积空白、重复展开）。
- chord 规则（旗数=数字才触发、旗错引爆）；旗/问号循环（含“标记”关闭时）。
- 胜负判定（全开安全格即胜、插旗不翻不开不算胜、踩雷即败）；计时起止与 999 封顶。
- 自定义难度边界（9×9/10、24×30/668、非法值拒绝）。

### 9.2 Geometry 测试

- 窗口↔棋盘↔格子↔像素双向换算；50/125/150/200/300%。
- 窗口过小、过大、非整数缩放、奇数尺寸不崩溃不错位。

### 9.3 UI 手工验收

- 三档难度各完整对局；左/右/中键全部交互；单色/颜色切换。
- 缩放 50%–300% 无变形；高 DPI 清晰；主题与语言即时切换；键盘全操作；音效开关与音量。

### 9.4 视觉对照与截图回归

- 本地运行 `other/WINMINE.EXE` 截图，与游戏逐项对比窗口布局、配色、方块与笑脸造型。
- 后期建立 `tests/visual/` 基准截图（classic_100/125/150.png），UI 修改后自动比对，防止绘制细节回归。

### 9.5 MVP 验收清单（v1 完成标准）

- 游戏：初级/中级/高级/自定义、首击保护、雷生成、数字计算、自动展开、插旗、chord、胜负、计时 ☐
- UI：XP 风格窗口/菜单/棋盘/数字/笑脸/雷/旗帜/3D 边框、鼠标按下效果 ☐
- 改进：自由缩放、自适应棋盘、高 DPI、不变形不裁剪不明显模糊 ☐
- 工程：Core 无 Qt、类型检查、lint、测试、文档完整 ☐

## 10. 版本路线图

- **v1（本文档）**：经典复刻 + 缩放修复 + 高分/音效/键盘/主题/语言扩展。
- **v1.1**：存档系统（Save/Load，JSON，格式独立于 Core）+ Seed 系统（同种子同棋盘）。
- **v1.2**：Replay（事件流回放，不记录截图）+ 统计。
- **v1.3**：主题扩展（Dark / High Contrast）+ PyInstaller 发布。
- **明确不做**：联网、账号、排行榜服务器、多人、成就系统、3D、复杂动画。

## 11. 工程规范

- 注释：遵循 AGENTS.md——所有函数有作用与参数说明，类字段注明含义；仅修改注释不触发代码审查。
- 质量门：mypy 与 ruff 通过；禁止无理由的 `Any` 和 `# type: ignore`。
- Git：Conventional Commits（feat/fix/refactor/test/docs/build/chore），一次提交只做一个逻辑变更。
- ADR：渲染资源方案（P3 末）、缩放模型（P6 末）、i18n 方案（P7 末）、存档格式（v1.1）各记一份。
- 测试纪律：本地不自动运行测试（AGENTS.md）；CI 若启用仅在远端执行。

## 12. 风险与对策

| 风险 | 对策 |
| --- | --- |
| PySide6 暂无 cp314 轮子 | 回退 Python 3.13 环境 |
| 位图加载失败/缺失 | 主题回退 + 错误提示，不崩溃 |
| 非整数缩放锯齿 | 最近邻插值，优先整数/半档缩放 |
| 中文字体渲染异常 | 系统字体回退（如微软雅黑） |
| 计时行为与原版有偏差 | 以逆向源码为准（999 封顶、最小化暂停） |
| 资源版权 | 仅本地学习使用；公开分发前替换资产 |

## 13. 假设与默认决策

- 界面文案默认中文（zh_CN），v1 支持 zh_CN/en_US，JSON 语言包。
- 渲染直接使用提取的原版位图（颜色/单色两套），QPainter 仅负责 3D 边框、HUD 面板与缩放合成。
- 缩放采用“自适应 + 缩放档”统一模型；最小窗口由最小格子反推。
- 高分记录 Top 5（现代扩展，对话框注明）。
- 帮助主题 = 玩法说明对话框；搜索/使用帮助置灰。
- 初始默认难度：初级；最小化暂停计时（沿用原版）。
- CI 后置可选；工具链 mypy + ruff；pytest 仅手动运行。
- 配置/语言/主题全 JSON；Python 3.14.7 + PySide6≥6.10。
