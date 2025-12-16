import math
import random
import time
import json
import os

def load_agent_config():
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config",
        "agent_config.json"
    )
    with open(config_path, "r") as f:
        return json.load(f)

AGENT_CONFIG = load_agent_config()

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

def get_minimax_config(level):
    level_key = f"level_{level}"
    return AGENT_CONFIG["minimax"].get(level_key, AGENT_CONFIG["minimax"]["level_1"])

# --- EVALUASI POLA / SKOR ---
SCORE_TABLE = {
    (5, 0): 1000000, (5, 1): 1000000, (5, 2): 1000000,  # Menang
    (4, 2): 100000,  # Live 4
    (4, 1): 10000,   # Dead 4
    (3, 2): 5000,    # Live 3
    (3, 1): 100,     # Dead 3
    (2, 2): 50,      # Live 2
    (2, 1): 10,      # Dead 2
    (1, 2): 5,
    (1, 1): 1
}


# --- VALID MOVE (OPTIMIZED) ---
def get_valid_moves_optimized(board, radius=2):
    """Cari langkah-langkah di sekitar bidak yang sudah ada (mengurangi branching factor)."""
    n = len(board)
    moves = set()
    has_piece = False

    for r in range(n):
        for c in range(n):
            if board[r][c] != EMPTY:
                has_piece = True
                for i in range(max(0, r - radius), min(n, r + radius + 1)):
                    for j in range(max(0, c - radius), min(n, c + radius + 1)):
                        if board[i][j] == EMPTY:
                            moves.add((i, j))

    if not has_piece:
        return [(n // 2, n // 2)]  # Langkah awal di tengah papan

    return list(moves)


# --- HITUNG SKOR PER GARIS ---
def evaluate_line(line, player):
    score = 0
    i = 0
    length = len(line)
    while i < length:
        if line[i] == player:
            count = 0
            start_idx = i
            while i < length and line[i] == player:
                count += 1
                i += 1

            open_ends = 0
            if start_idx > 0 and line[start_idx - 1] == EMPTY:
                open_ends += 1
            if i < length and line[i] == EMPTY:
                open_ends += 1

            score += SCORE_TABLE.get((count, open_ends), 0)
        else:
            i += 1
    return score


# --- HITUNG SKOR SELURUH PAPAN ---
def evaluate_board(board, player, defense_weight=1.5):
    n = len(board)
    opponent = PLAYER_X if player == PLAYER_O else PLAYER_O
    my_score, op_score = 0, 0

    # Horizontal dan Vertikal
    for i in range(n):
        row = board[i]
        col = [board[r][i] for r in range(n)]
        my_score += evaluate_line(row, player)
        op_score += evaluate_line(row, opponent)
        my_score += evaluate_line(col, player)
        op_score += evaluate_line(col, opponent)

    # Diagonal \
    for k in range(-n + 1, n):
        diag = [board[r][r - k] for r in range(n) if 0 <= r - k < n]
        if len(diag) >= 5:
            my_score += evaluate_line(diag, player)
            op_score += evaluate_line(diag, opponent)

    # Diagonal /
    for k in range(2 * n - 1):
        diag = [board[r][k - r] for r in range(n) if 0 <= k - r < n]
        if len(diag) >= 5:
            my_score += evaluate_line(diag, player)
            op_score += evaluate_line(diag, opponent)

    # Lebih defensif — penalti lawan lebih besar
    return my_score - (op_score * defense_weight)


# --- MINIMAX + ALPHA-BETA PRUNING ---
def minimax_ab(board, depth, alpha, beta, is_maximizing, player, radius, defense_weight):
    valid_moves = get_valid_moves_optimized(board, radius)
    if depth == 0 or not valid_moves:
        return evaluate_board(board, player, defense_weight), None

    opponent = PLAYER_X if player == PLAYER_O else PLAYER_O

    if is_maximizing:
        max_eval, best_move = -math.inf, random.choice(valid_moves)
        for move in valid_moves:
            r, c = move
            board[r][c] = player
            eval_val, _ = minimax_ab(board, depth - 1, alpha, beta, False, player, radius, defense_weight)
            board[r][c] = EMPTY

            if eval_val > max_eval:
                max_eval, best_move = eval_val, move

            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval, best_move = math.inf, random.choice(valid_moves)
        for move in valid_moves:
            r, c = move
            board[r][c] = opponent
            eval_val, _ = minimax_ab(board, depth - 1, alpha, beta, True, player, radius, defense_weight)
            board[r][c] = EMPTY

            if eval_val < min_eval:
                min_eval, best_move = eval_val, move

            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move


# --- UTAMA: DIPANGGIL DARI GUI ATAU SIMULASI ---
def get_move_minimax_level(board, level=1):
    conf = get_minimax_config(level)
    depth = conf["depth"]
    radius = conf["radius"]
    defense_weight = conf["defense_weight"]

    start = time.time()
    ai_player = PLAYER_X
    score, move = minimax_ab(board, depth, -math.inf, math.inf, True, ai_player, radius, defense_weight)
    end = time.time()

    print(f"[Minimax Lv{level}] Time: {end - start:.3f}s | Depth={depth} | Radius={radius} | Move={move}")
    if move is None:
        valid = get_valid_moves_optimized(board)
        return random.choice(valid) if valid else (0, 0)
    return move