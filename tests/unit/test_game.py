"""Game 聚合根单元测试。

覆盖命令分发、首击安全、状态迁移、计时与事件发布
（测试清单见 docs/实施文档.md §12）。
"""
from minesweeper_xp.core.command import (
    ChangeDifficulty,
    ChordCell,
    RestartGame,
    RevealCell,
    ToggleMark,
)
from minesweeper_xp.core.enums import FaceState, GameStatus, LostReason, Mark
from minesweeper_xp.core.event import (
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
from minesweeper_xp.core.game import Game
from minesweeper_xp.core.model.coordinate import Coordinate
from minesweeper_xp.core.rules.reveal import calculate_adjacent_mines


def test_new_game_initial_state() -> None:
    """验证新开局处于 READY 状态并发布初始事件。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    events: list[Event] = []
    game.subscribe(events.append)
    game.new_game("beginner", 9, 9, 10)
    assert game.state.status is GameStatus.READY
    assert game.state.remaining_mines == 10
    assert game.state.elapsed_seconds == 0
    assert game.state.face_state is FaceState.NORMAL
    assert (game.state.rows, game.state.cols) == (9, 9)
    assert any(isinstance(e, GameStateChanged) and e.status is GameStatus.READY for e in events)
    assert any(isinstance(e, FlagsChanged) and e.remaining == 10 for e in events)
    assert any(isinstance(e, FaceChanged) and e.face is FaceState.NORMAL for e in events)


def test_first_click_places_mines_and_starts() -> None:
    """验证首击后布雷、状态变 PLAYING、首击格安全（cell 模式）。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    events: list[Event] = []
    game.subscribe(events.append)
    first = Coordinate(4, 4)
    game.dispatch(RevealCell(first))
    assert game.state.status is GameStatus.PLAYING
    assert game.board.cell(first).is_mine is False  # cell 模式首击格必安全
    assert game.board.cell(first).is_revealed is True
    mines = sum(1 for c in game.board.all_coords() if game.board.cell(c).is_mine)
    assert mines == 10
    assert any(isinstance(e, GameStateChanged) and e.status is GameStatus.PLAYING for e in events)
    assert any(isinstance(e, CellsRevealed) for e in events)


def test_first_click_safe_zone3x3() -> None:
    """验证 zone3x3 模式下首击 3×3 范围无雷。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.safe_mode = "zone3x3"
    game.new_game("beginner", 9, 9, 10)
    game.dispatch(RevealCell(Coordinate(4, 4)))
    for row in range(3):
        for col in range(3):
            assert game.board.cell(Coordinate(4 - 1 + row, 4 - 1 + col)).is_mine is False


def test_flag_cycle_and_remaining_mines() -> None:
    """验证右键标记循环（旗→问号→无）并更新剩余雷数。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    events: list[Event] = []
    game.subscribe(events.append)
    target = Coordinate(4, 4)
    game.dispatch(ToggleMark(target))
    assert game.board.cell(target).mark is Mark.FLAG
    assert game.state.remaining_mines == 9
    game.dispatch(ToggleMark(target))
    assert game.board.cell(target).mark is Mark.QUESTION
    assert game.state.remaining_mines == 10
    game.dispatch(ToggleMark(target))
    assert game.board.cell(target).mark is Mark.NONE
    assert game.state.remaining_mines == 10
    assert any(isinstance(e, CellMarked) for e in events)
    assert any(isinstance(e, FlagsChanged) and e.remaining == 9 for e in events)


def test_mark_ignored_on_revealed_cell() -> None:
    """验证已翻开的格子不能标记，剩余雷数不变。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    first = Coordinate(4, 4)
    game.dispatch(RevealCell(first))
    before = game.state.remaining_mines
    game.dispatch(ToggleMark(first))
    assert game.board.cell(first).mark is Mark.NONE
    assert game.state.remaining_mines == before


def test_restart_resets_game() -> None:
    """验证重启命令恢复 READY、清空棋盘与剩余雷数。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    game.dispatch(RevealCell(Coordinate(4, 4)))
    game.dispatch(ToggleMark(Coordinate(1, 1)))
    game.dispatch(RestartGame())
    assert game.state.status is GameStatus.READY
    assert game.state.remaining_mines == 10
    revealed = sum(1 for c in game.board.all_coords() if game.board.cell(c).is_revealed)
    assert revealed == 0


def test_commands_ignored_after_loss() -> None:
    """验证终局后除重启外其他命令被忽略。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    game.dispatch(RevealCell(Coordinate(4, 4)))
    mine_coord = next(c for c in game.board.all_coords() if not game.board.cell(c).is_revealed)
    game.board.cell(mine_coord).is_mine = True
    game.dispatch(RevealCell(mine_coord))
    assert game.state.status is GameStatus.LOST
    before = game.state.remaining_mines
    game.dispatch(ToggleMark(mine_coord))
    assert game.state.remaining_mines == before


def test_restart_works_after_terminal() -> None:
    """验证终局后重启命令仍然有效。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    game.dispatch(RevealCell(Coordinate(4, 4)))
    mine_coord = next(c for c in game.board.all_coords() if not game.board.cell(c).is_revealed)
    game.board.cell(mine_coord).is_mine = True
    game.dispatch(RevealCell(mine_coord))
    assert game.state.status is GameStatus.LOST
    game.dispatch(RestartGame())
    assert game.state.status is GameStatus.READY
    assert game.state.remaining_mines == 10


def test_reveal_mine_loses_with_reason() -> None:
    """验证左键踩雷判负，GameLost 携带 REVEAL 原因与雷坐标。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    events: list[Event] = []
    game.subscribe(events.append)
    game.dispatch(RevealCell(Coordinate(4, 4)))
    mine_coord = next(c for c in game.board.all_coords() if not game.board.cell(c).is_revealed)
    game.board.cell(mine_coord).is_mine = True
    game.dispatch(RevealCell(mine_coord))
    assert game.state.status is GameStatus.LOST
    lost = [e for e in events if isinstance(e, GameLost)][-1]
    assert lost.reason is LostReason.REVEAL
    assert lost.coord == mine_coord


def test_chord_mine_loses_with_reason() -> None:
    """验证连开踩雷判负，GameLost 携带 CHORD 原因与连开点坐标。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 3, 3, 1)
    events: list[Event] = []
    game.subscribe(events.append)
    board = game.board
    # 固定局面（白盒构造，避免随机布雷）：雷在 (1,1)，旗在 (1,0)，(0,0) 已翻开且数字为 1
    game._first_click = Coordinate(0, 0)
    game.state.status = GameStatus.PLAYING
    board.cell(Coordinate(1, 1)).is_mine = True
    calculate_adjacent_mines(board)
    board.cell(Coordinate(0, 0)).is_revealed = True
    board.cell(Coordinate(1, 0)).mark = Mark.FLAG
    game.dispatch(ChordCell(Coordinate(0, 0)))
    assert game.state.status is GameStatus.LOST
    lost = [e for e in events if isinstance(e, GameLost)][-1]
    assert lost.reason is LostReason.CHORD
    assert lost.coord == Coordinate(0, 0)


def test_win_when_all_safe_cells_revealed() -> None:
    """验证所有非雷格翻开后判胜并发布 GameWon。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 3, 3, 1)
    events: list[Event] = []
    game.subscribe(events.append)
    game.dispatch(RevealCell(Coordinate(0, 0)))
    board = game.board
    for c in board.all_coords():
        board.cell(c).is_mine = False
    mine_coord = Coordinate(2, 2)
    board.cell(mine_coord).is_mine = True
    calculate_adjacent_mines(board)
    for c in board.all_coords():
        if c != mine_coord:
            game.dispatch(RevealCell(c))
    assert game.state.status is GameStatus.WON
    assert any(isinstance(e, GameWon) for e in events)


def test_change_difficulty_uses_real_preset() -> None:
    """验证切换难度使用真实预设数据重建棋盘。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    game.dispatch(ChangeDifficulty("expert"))
    assert game.state.difficulty == "expert"
    assert (game.state.rows, game.state.cols, game.state.mine_count) == (16, 30, 99)


def test_tick_emits_timer_only_while_playing() -> None:
    """验证计时事件只在 PLAYING 状态发布，且秒数正确。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    events: list[Event] = []
    game.subscribe(events.append)
    game.new_game("beginner", 9, 9, 10)
    game.tick()
    assert not any(isinstance(e, TimerTicked) for e in events)
    game.dispatch(RevealCell(Coordinate(4, 4)))
    events.clear()
    game._clock.tick(3)
    game.tick()
    timers = [e for e in events if isinstance(e, TimerTicked)]
    assert timers and timers[-1].seconds == 3


def test_new_game_resets_clock() -> None:
    """验证重开一局时钟归零且注入对象不被替换。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    clock = game._clock
    game.dispatch(RevealCell(Coordinate(4, 4)))
    game._clock.tick(7)
    assert game._clock.elapsed == 7
    game.dispatch(RestartGame())
    assert game._clock is clock
    assert game._clock.elapsed == 0


def test_out_of_bounds_command_ignored() -> None:
    """验证越界坐标的翻开命令被忽略。

    参数:
        无。

    返回:
        无。
    """
    game = Game()
    game.new_game("beginner", 9, 9, 10)
    game.dispatch(RevealCell(Coordinate(-1, 0)))
    assert game.state.status is GameStatus.READY
