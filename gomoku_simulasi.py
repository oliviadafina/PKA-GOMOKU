import time
from agents.minimax_optimized_agent import get_move_minimax_level
from agents.mcts_optimized_agent import get_move_mcts_level

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2
BOARD_SIZE = 15


# --- FUNGSI DASAR ---
def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def check_winner(board, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] == player:
                for dx, dy in directions:
                    count = 1
                    nx, ny = x + dx, y + dy
                    while (
                        0 <= nx < BOARD_SIZE
                        and 0 <= ny < BOARD_SIZE
                        and board[nx][ny] == player
                    ):
                        count += 1
                        if count == 5:
                            return True
                        nx += dx
                        ny += dy
    return False


def is_full(board):
    return all(board[x][y] != EMPTY for x in range(BOARD_SIZE) for y in range(BOARD_SIZE))


# --- SIMULASI SATU GAME ---
def play_single_game(minimax_level=1, mcts_level=1, verbose=False):
    board = create_board()
    current_player = PLAYER_X

    while True:
        if current_player == PLAYER_X:
            start = time.time()
            move = get_move_minimax_level(board, level=minimax_level)
            end = time.time()
            if verbose:
                print(f"[Lv{minimax_level}] Minimax pilih {move} dalam {end - start:.2f}s")
        else:
            start = time.time()
            move = get_move_minimax_level(board, level=mcts_level)
            end = time.time()
            if verbose:
                print(f"[Lv{mcts_level}] MCTS pilih {move} dalam {end - start:.2f}s")

        x, y = move
        board[x][y] = current_player

        if check_winner(board, current_player):
            return current_player

        if is_full(board):
            return 0  # draw

        current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X


# --- TURNAMEN ANTAR LEVEL ---
def run_tournament():
    results = []

    pairs = [
        ("Minimax Lv1", "Minimax Lv2", 1, 2, "minimax_vs_minimax"),
        ("Minimax Lv2", "Minimax Lv3", 2, 3, "minimax_vs_minimax"),
        ("MCTS Lv1", "MCTS Lv2", 1, 2, "mcts_vs_mcts"),
        ("MCTS Lv2", "MCTS Lv3", 2, 3, "mcts_vs_mcts"),
        ("Minimax Lv2", "MCTS Lv3", 2, 3, "minimax_vs_mcts"),
    ]

    for name1, name2, lvl1, lvl2, mode in pairs:
        print(f"\n=== {name1} vs {name2} ===")

        x_win, o_win, draws = 0, 0, 0
        n_games = 10  # bisa diubah
        total_time = 0

        for g in range(n_games):
            start_time = time.time()
            if mode == "minimax_vs_minimax":
                result = play_single_game(minimax_level=lvl1, mcts_level=lvl2)
            elif mode == "mcts_vs_mcts":
                result = play_single_game(minimax_level=lvl1, mcts_level=lvl2)
            else:
                result = play_single_game(minimax_level=lvl1, mcts_level=lvl2)
            total_time += time.time() - start_time

            if result == PLAYER_X:
                x_win += 1
            elif result == PLAYER_O:
                o_win += 1
            else:
                draws += 1

            print(f"Game {g+1}/{n_games} selesai. Hasil: {result}")

        avg_time = total_time / n_games
        print("\n======= RINGKASAN =======")
        print(f"{name1} (X) menang: {x_win}")
        print(f"{name2} (O) menang: {o_win}")
        print(f"Seri: {draws}")
        print(f"Rata-rata waktu per game: {avg_time:.2f}s")

        results.append({
            "pair": f"{name1} vs {name2}",
            "X_wins": x_win,
            "O_wins": o_win,
            "draws": draws,
            "avg_time": avg_time
        })

    print("\n=== HASIL AKHIR TURNAMEN ===")
    for r in results:
        print(f"{r['pair']}: X={r['X_wins']}, O={r['O_wins']}, Draw={r['draws']}, Time={r['avg_time']:.2f}s")


if __name__ == "__main__":
    run_tournament()