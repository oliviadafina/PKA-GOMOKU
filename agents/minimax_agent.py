import math
import random
import time

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

# MENILAI POSISI
def evaluate(board):
    SCORE_TABLE  = {
        1: 10,
        2: 50,
        3: 200,
        4: 1000,
        5: 100000
    }
    def count_sequence(line, player):
        max_count = 0
        count = 0
        for cell in line:
            if cell == player:
                count += 1
                max_count = max(max_count, count)
            else:
                count = 0
        return max_count
    def score_for_player(board, player):
        total = 0
        n = len(board)
        for i in range(n):
            total += SCORE_TABLE.get(count_sequence(board[i], player), 0)
            column = [board[r][i] for r in range(n)]
            total += SCORE_TABLE.get(count_sequence(column, player), 0)
        for x in range(n - 4):
            for y in range(n - 4):
                diag = [board[x+i][y+i] for i in range(5)]
                total += SCORE_TABLE.get(count_sequence(diag, player), 0)
        for x in range(n - 4):
            for y in range (4, n):
                diag = [board[x+i][y-i] for i in range(5)]
                total += SCORE_TABLE.get(count_sequence(diag, player), 0)
        return total
    player_score = score_for_player(board, PLAYER_X)
    enemy_score = score_for_player(board, PLAYER_O)

    return player_score - enemy_score

def get_valid_moves(board):
    moves = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                moves.append((i, j))
    return moves

def minimax(board, depth, is_maximizing):
    valid_moves = get_valid_moves(board)
    if depth == 0 or len(valid_moves) == 0:
        return evaluate(board), None
    if is_maximizing:
        best_score = -math.inf
        best_move = None
        for move in valid_moves:
            x, y = move
            board[x][y] = PLAYER_X
            score, _ = minimax(board, depth -1, False)
            board[x][y] = EMPTY
            if score > best_score:
                best_score = score
                best_move = move
        return best_score, best_move
    else: 
        best_score = math.inf
        best_move = None
        for move in valid_moves:
            x, y = move
            board[x][y] = PLAYER_O
            score, _ = minimax(board, depth -1, True)
            board[x][y] = EMPTY
            if score < best_score:
                best_score = score
                best_move = move
        return best_score, best_move
    
def get_move_minimax(board, depth=2):
    start = time.time()
    _, move = minimax(board, depth, True)
    end = time.time()
    print(f"[Minimax] Time: {end - start: .3f}s | Move: {move}")
    if move is None or board[move[0]][move[1]] != EMPTY:
        return random.choice(get_valid_moves(board))
    return move