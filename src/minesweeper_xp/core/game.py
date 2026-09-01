"""Game 聚合根。

持有棋盘与游戏状态，接收 Command 并分发处理，对外发布 Event，
包含首次点击布雷、计时控制与胜负判定，不含任何 Qt 依赖
（实现见 docs/实施文档.md §11）。
"""
import random
from dataclasses import dataclass
from typing import Callable

from minesweeper_xp.data import difficulty
from .clock import Clock, FakeClock
from .command import ChangeDifficulty, ChordCell, Command, RestartGame, RevealCell, ToggleMark
from .enums import FaceState, GameStatus, LostReason, Mark
from .event import (
    CellMarked,
    CellsRevealed,
    Event,
    FaceChanged,
    FlagsChanged,
    GameLost,
    GameStateChanged,
    GameWon,
    TimerTicked,
)
from .generation.mine_generator import place_mines
from .model.board import Board
from .model.coordinate import Coordinate
from .rules.chord import chord
from .rules.marking import cycle_mark
from .rules.reveal import calculate_adjacent_mines, flood_fill
from .rules.victory import is_won


@dataclass
class GameState:
    """游戏状态快照（开发文档 §5.4）。"""

    status: GameStatus  # 游戏生命周期状态（READY/PLAYING/WON/LOST）
    difficulty: str  # 当前难度名称
    rows: int  # 棋盘行数
    cols: int  # 棋盘列数
    mine_count: int  # 本局雷总数
    remaining_mines: int  # 剩余雷数（随标记变化）
    elapsed_seconds: int  # 已计秒数（终局后定格）
    face_state: FaceState  # 笑脸按钮状态


class Game:
    """扫雷逻辑核心，不含任何 Qt。"""

    def __init__(
        self,
        clock: Clock | None = None,
        difficulties: difficulty.DifficultyConfig | None = None,
    ) -> None:
        """初始化游戏：创建时钟、棋盘与初始状态。

        参数:
            clock: 计时器实现，默认使用 FakeClock（测试用）。
            difficulties: 难度配置，默认使用内置三档预设。

        返回:
            无。
        """
        self._clock: Clock = clock or FakeClock()  # 计时器
        self._difficulties: difficulty.DifficultyConfig = (
            difficulties or difficulty.default_difficulties()
        )  # 难度配置（ChangeDifficulty 查表用）
        self._listeners: list[Callable[[Event], None]] = []  # 事件监听器列表
        self._board: Board = Board(9, 9)  # 棋盘（开局时按难度重建）
        self._rng: random.Random = random.Random()  # 随机数生成器（布雷用）
        self._first_click: Coordinate | None = None  # 首次点击坐标（布雷锚点）
        self.safe_mode: str = "cell"  # 首击安全区模式（zone3x3 / cell）
        self.marks_enabled: bool = True  # 是否启用问号标记
        self.state: GameState = GameState(
            GameStatus.READY, "beginner", 9, 9, 10, 10, 0, FaceState.NORMAL
        )

    @property
    def board(self) -> Board:
        """对外暴露当前棋盘，供 UI 读取绘制。"""
        return self._board

    def subscribe(self, listener: Callable[[Event], None]) -> None:
        """注册事件监听器。

        参数:
            listener: 接收 Event 的回调函数。

        返回:
            无。
        """
        self._listeners.append(listener)

    def _emit(self, event: Event) -> None:
        """把事件广播给所有已注册的监听器。

        参数:
            event: 要发布的事件对象。

        返回:
            无。
        """
        for listener in self._listeners:
            listener(event)

    def new_game(self, difficulty: str, rows: int, cols: int, mines: int) -> None:
        """开新局：清盘、重置状态，布雷推迟到首次点击。

        参数:
            difficulty: 难度名称。
            rows: 棋盘行数。
            cols: 棋盘列数。
            mines: 雷总数。

        返回:
            无。
        """
        self._clock.reset()  # 停表并清零（重开从 0 计起）
        self._board = Board(rows, cols)  # 棋盘重置
        self._rng = random.Random()  # 随机数重置
        self._first_click = None  # 首次点击坐标（布雷锚点）
        self.state = GameState(
            GameStatus.READY, difficulty, rows, cols, mines, mines, 0, FaceState.NORMAL
        )

        self._emit(GameStateChanged(self.state.status))
        self._emit(FlagsChanged(mines))
        self._emit(FaceChanged(FaceState.NORMAL))

    def dispatch(self, command: Command) -> None:
        """分发命令（终局后仅 Restart 有效，见开发文档 §6.8）。

        参数:
            command: 玩家意图命令。

        返回:
            无。
        """
        if isinstance(command, RestartGame):  # 重启命令第一顺位，保证始终可执行
            self.new_game(
                self.state.difficulty, self.state.rows, self.state.cols, self.state.mine_count
            )
            return

        if self.state.status in (GameStatus.WON, GameStatus.LOST):  # 终局后忽略其他命令
            return

        if isinstance(command, ChangeDifficulty):  # 调整难度等于重开一局
            preset = self._difficulties.preset(command.name)
            self.new_game(command.name, preset.rows, preset.cols, preset.mines)
        elif isinstance(command, RevealCell):  # 翻开命令
            self._reveal(command.coord)
        elif isinstance(command, ToggleMark):  # 标记命令
            self._mark(command.coord)
        elif isinstance(command, ChordCell):  # 连开命令
            self._chord(command.coord)


    def tick(self) -> None:
        """每秒被 UI 的 QTimer 调用，发布计时事件。"""
        if self.state.status is GameStatus.PLAYING:  # 只在游戏中广播
            if self._clock.elapsed >= 999:  # 到顶停表（999 封顶由 Clock 保证，这里负责"停"）
                self._clock.stop()
            self._emit(TimerTicked(self._clock.elapsed))


    def _reveal(self, coord: Coordinate) -> None:
        """处理左键翻开命令：首击布雷、踩雷判负、洪水填充与胜利判定。

        参数:
            coord: 要翻开的格子坐标。

        返回:
            无。
        """
        # 越界防御
        if not self.board.in_bounds(coord):  # 不在棋盘内
            return

        # 判断是不是首击，如果是，则进行首击布雷
        if self._first_click is None:
            # 首击布雷
            place_mines(self.board, self.state.mine_count, coord, self.safe_mode, self._rng)
            # 初始化棋盘
            calculate_adjacent_mines(self.board)
            # 修改首击布雷标志位
            self._first_click = coord
            # 启动棋盘计时
            self._clock.start()
            self.state.status = GameStatus.PLAYING
            self._emit(GameStateChanged(GameStatus.PLAYING))

        # 判断是不是雷
        if self.board.cell(coord).is_mine:  # 是雷
            self._end(GameStatus.LOST, LostReason.REVEAL, coord)  # 左键踩雷：只高亮该雷
            return

        # 该位置点击一次 洪水填充
        coords = flood_fill(self.board, coord)
        # 构造 tuple[tuple[Coordinate, int], ...]
        if coords:  # 只在实际翻开了格子时才发布事件
            event = tuple((x, self.board.cell(x).adjacent_mines) for x in coords)

            self._emit(CellsRevealed(event))

        # 胜利判定
        if is_won(self.board, self.state.mine_count):
            self._end(GameStatus.WON)  # 触发终局事件
            return

    def _mark(self, coord: Coordinate) -> None:
        """处理标记命令：循环切换旗/问号并更新剩余雷数。

        参数:
            coord: 要切换标记的格子坐标。

        返回:
            无。
        """
        # 越界防御
        if not self.board.in_bounds(coord):  # 不在棋盘内
            return

        cell = self.board.cell(coord)

        delta = cycle_mark(cell, self.marks_enabled)
        self.state.remaining_mines += delta

        self._emit(CellMarked(coord, cell.mark))
        self._emit(FlagsChanged(self.state.remaining_mines))


    def _chord(self, coord: Coordinate) -> None:
        """处理连开命令：触发连开、踩雷判负、胜利判定。

        参数:
            coord: 要连开的已翻开格子坐标。

        返回:
            无。
        """
        # 越界防御
        if not self.board.in_bounds(coord):  # 不在棋盘内
            return

        # 执行连开
        coords, mine = chord(self.board, coord)
        # 无论是否踩雷，先发布本次真正翻开的格子（踩雷前已翻开的也通知 UI）
        if coords:
            event = tuple((x, self.board.cell(x).adjacent_mines) for x in coords)
            self._emit(CellsRevealed(event))

        if mine:  # 踩到雷：终局，UI 叠加渲染连开点邻居
            self._end(GameStatus.LOST, LostReason.CHORD, coord)
            return

        # 胜利判定
        if is_won(self.board, self.state.mine_count):
            self._end(GameStatus.WON)


    def _end(
        self,
        status: GameStatus,
        reason: LostReason | None = None,
        coord: Coordinate | None = None,
    ) -> None:
        """进入终局：停表、更新状态、发布终局事件。

        参数:
            status: 终局状态（WON 或 LOST）。
            reason: 失败原因（仅 LOST 需要，REVEAL=左键踩雷 / CHORD=连开踩雷）。
            coord: 触发坐标（仅 LOST 需要，踩中的雷或连开点）。

        返回:
            无。
        """
        self._clock.stop()  # 停表
        self.state.status = status  # 改状态
        if status is GameStatus.WON:  # 改笑脸
            self.state.face_state = FaceState.WINNER
        else:
            self.state.face_state = FaceState.LOST

        self.state.elapsed_seconds = self._clock.elapsed  # 定格最后秒数
        self._emit(FaceChanged(self.state.face_state))  # 笑脸事件
        self._emit(GameStateChanged(status))  # 改状态事件
        if status is GameStatus.WON:  # 胜利事件
            self._emit(GameWon())
        else:  # 失败事件（携带原因与触发坐标，供 UI 终局叠加渲染）
            assert reason is not None and coord is not None
            self._emit(GameLost(reason=reason, coord=coord))
