import random
import time

EMPTY = 0

def get_valid_moves(board):
    moves = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                moves.append((i, j))
    return moves


def get_move_mcts_level(board, level=1):
    """
    Dummy MCTS versi awal — hanya pilih langkah random,
    tapi sudah support sistem level agar tidak error saat simulasi.
    """
    config = {
        1: {"simulations": 100, "time_limit": 1.0},
        2: {"simulations": 500, "time_limit": 2.0},
        3: {"simulations": 1000, "time_limit": 3.0},
    }

    c = config.get(level, config[1])
    start = time.time()

    # simulasi pura-pura mikir (pakai sleep)
    time.sleep(c["time_limit"] * 0.1)

    valid_moves = get_valid_moves(board)
    move = random.choice(valid_moves) if valid_moves else (0, 0)

    end = time.time()
    print(f"[MCTS Lv{level}] Time: {end - start:.2f}s | Simulations={c['simulations']} | Move={move}")

    return move