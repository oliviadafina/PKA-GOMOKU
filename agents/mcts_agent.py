import math
import random
import time

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

# ---------- UTIL DASAR GOMOKU ----------

def get_valid_moves(board):
    moves = []
    n = len(board)
    for i in range(n):
        for j in range(n):
            if board[i][j] == EMPTY:
                moves.append((i, j))
    return moves

def check_winner(board, player):
    """Cek 5 berurutan (horizontal, vertikal, diagonal) untuk player."""
    n = len(board)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for x in range(n):
        for y in range(n):
            if board[x][y] != player:
                continue
            for dx, dy in directions:
                count = 1
                nx, ny = x + dx, y + dy
                while 0 <= nx < n and 0 <= ny < n and board[nx][ny] == player:
                    count += 1
                    if count == 5:
                        return True
                    nx += dx
                    ny += dy
    return False

def is_full(board):
    return all(cell != EMPTY for row in board for cell in row)

def get_game_result(board, root_player):
    """Skor: 1 = root_player menang, 0 = root_player kalah, 0.5 = seri."""
    other = PLAYER_X if root_player == PLAYER_O else PLAYER_O
    if check_winner(board, root_player):
        return 1.0
    if check_winner(board, other):
        return 0.0
    if is_full(board):
        return 0.5
    return None  # belum terminal


# ---------- NODE MCTS (VERSI MIRIP PAPER) ----------

class MCTSNode:
    def __init__(self, board, parent=None, move=None, player_to_move=PLAYER_X):
        # state
        self.board = [row[:] for row in board]
        self.parent = parent
        self.move = move              # langkah yang membawa ke node ini
        self.player_to_move = player_to_move

        # anak / statistik
        self.children = []
        self.untried_moves = get_valid_moves(self.board)
        self.visits = 0
        self.total_reward = 0.0       # sum dari reward (q di paper)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal_node(self):
        # terminal jika sudah ada pemenang atau papan penuh
        return check_winner(self.board, PLAYER_X) or \
               check_winner(self.board, PLAYER_O) or \
               is_full(self.board)

    def ucb1(self, c=0.6):
        """UCB1 seperti di paper (q/n + c * sqrt(ln N / n))."""
        if self.visits == 0:
            return float("inf")
        avg = self.total_reward / self.visits
        parent_visits = self.parent.visits if self.parent else 1
        return avg + c * math.sqrt(math.log(parent_visits) / self.visits)

    def best_child(self, c=0.6):
        return max(self.children, key=lambda child: child.ucb1(c))

    def expand(self):
        """Ambil satu untried move dan buat child node baru."""
        if not self.untried_moves:
            return self

        move = self.untried_moves.pop()
        x, y = move

        new_board = [row[:] for row in self.board]
        new_board[x][y] = self.player_to_move

        next_player = PLAYER_X if self.player_to_move == PLAYER_O else PLAYER_O
        child = MCTSNode(new_board, parent=self, move=move, player_to_move=next_player)
        self.children.append(child)
        return child

    def backpropagate(self, reward):
        """
        reward selalu dari perspektif root player.
        Pada backprop, kita tidak membalik reward (sesuai style umum MCTS di paper).
        """
        node = self
        while node is not None:
            node.visits += 1
            node.total_reward += reward
            node = node.parent


# ---------- ROLLOUT (RANDOM + WINNING MOVE PRIORITY) ----------

def rollout_policy(board, player):
    """
    Rollout ala paper:
    - Jika ada winning move untuk player → mainkan langsung.
    - Jika tidak → random valid move.
    """
    moves = get_valid_moves(board)
    if not moves:
        return None

    # 1) cari winning move
    n = len(board)
    for (x, y) in moves:
        board[x][y] = player
        if check_winner(board, player):
            board[x][y] = EMPTY  # rollback setelah cek
            return (x, y)
        board[x][y] = EMPTY

    # 2) kalau tidak ada, random
    return random.choice(moves)


def simulate_rollout(board, player_to_move, root_player):
    """
    Mainkan game secara acak (dengan prioritas winning move).
    Mengembalikan reward 1 / 0 / 0.5 dari sudut pandang root_player.
    """
    sim_board = [row[:] for row in board]
    current = player_to_move

    while True:
        result = get_game_result(sim_board, root_player)
        if result is not None:
            return result  # 1, 0, atau 0.5

        move = rollout_policy(sim_board, current)
        if move is None:
            # tidak ada langkah & belum ada pemenang → seri
            return 0.5

        x, y = move
        sim_board[x][y] = current
        current = PLAYER_X if current == PLAYER_O else PLAYER_O


# ---------- MCTS SEARCH (VERSI MENDekati PAPER) ----------

def mcts_search(board, iterations=1000):
    """
    MCTS:
    - Select dengan UCB1 (c ≈ 0.6 seperti paper).
    - Expand TIDAK di setiap iterasi → misalnya tiap 3 iterasi (lebih banyak rollout).
    - Rollout random dengan prioritas winning move.
    """
    # misal root selalu giliran PLAYER_O (MCTS agent),
    # sama seperti mcts_agent lama kamu.
    root_player = PLAYER_O
    root = MCTSNode(board, parent=None, move=None, player_to_move=root_player)

    for it in range(iterations):
        node = root

        # ---- 1. SELECT ----
        while not node.is_terminal_node() and node.is_fully_expanded() and node.children:
            node = node.best_child(c=0.6)

        # ---- 2. EXPAND (hanya setiap beberapa iterasi, mirip paper) ----
        if (not node.is_terminal_node()) and (not node.is_fully_expanded()) and (it % 3 == 0):
            node = node.expand()

        # ---- 3. ROLLOUT ----
        reward = simulate_rollout(node.board, node.player_to_move, root_player)

        # ---- 4. BACKPROP ----
        node.backpropagate(reward)

    # Pilih langkah dengan visits terbanyak (robust child)
    if not root.children:
        # fallback random
        moves = get_valid_moves(board)
        return random.choice(moves) if moves else (0, 0)

    best = max(root.children, key=lambda c: c.visits)
    return best.move


# ---------- PUBLIC API ----------

def get_move_mcts(board, iterations=1000):
    """
    Dipanggil dari gomoku_gui.py
    """
    start = time.time()
    move = mcts_search(board, iterations=iterations)
    end = time.time()
    print(f"[MCTS-paper-style] Time: {end - start:.3f}s | Iterations: {iterations} | Move: {move}")

    # Safety check
    if move is not None:
        x, y = move
        if board[x][y] == EMPTY:
            return move

    # fallback kalau ada yang aneh
    moves = get_valid_moves(board)
    return random.choice(moves) if moves else (0, 0)
