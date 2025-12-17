import math
import random
import time
import json
import os

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


# Kode ini mengimplementasikan agen kecerdasan buatan untuk permainan Gomoku menggunakan Monte Carlo Tree Search (MCTS).

# 🔹 Game Playing AI
# Permainan papan seperti Gomoku adalah lingkungan kompetitif dua agen, sehingga termasuk:
# Adversarial Search
# Zero-sum game


# ==============================
# LOAD CONFIG
# ==============================
def load_mcts_config():
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config",
        "agent_config.json"
    )
    with open(config_path, "r") as f:
        return json.load(f)

# ==============================
# WIN CHECK (LOCAL)
# ==============================
def check_win_around(board, r, c, player):
    n = len(board)
    directions = [(0,1), (1,0), (1,1), (1,-1)]

    for dr, dc in directions:
        count = 1

        for i in range(1, 5):
            nr, nc = r + dr*i, c + dc*i
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == player:
                count += 1
            else:
                break

        for i in range(1, 5):
            nr, nc = r - dr*i, c - dc*i
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == player:
                count += 1
            else:
                break

        if count >= 5:
            return True

    return False

# ==============================
# MOVE GENERATION
# ==============================
def get_neighboring_moves(board, radius):
    n = len(board)
    moves = set()
    has_piece = False

    for r in range(n):
        for c in range(n):
            if board[r][c] != EMPTY:
                has_piece = True
                for i in range(max(0, r-radius), min(n, r+radius+1)):
                    for j in range(max(0, c-radius), min(n, c+radius+1)):
                        if board[i][j] == EMPTY:
                            moves.add((i, j))

    if not has_piece:
        return [(n//2, n//2)]

    return list(moves)

# ==============================
# MCTS NODE
# ==============================
class MCTSNode:
    def __init__(self, board, config, parent=None, move=None, player_to_move=PLAYER_X):
        self.board = [row[:] for row in board]
        self.config = config
        self.parent = parent
        self.move = move
        self.player_to_move = player_to_move

        self.children = []
        self.untried_moves = get_neighboring_moves(
            self.board, config["neighbor_radius"]
        )

        self.visits = 0
        self.wins = 0.0

    def ucb1(self):
        if self.visits == 0:
            return float("inf")
        c = self.config["uct_c"]
        return (self.wins / self.visits) + c * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

    def expand(self):
        move = self.untried_moves.pop()
        r, c = move

        new_board = [row[:] for row in self.board]
        new_board[r][c] = self.player_to_move

        next_player = PLAYER_X if self.player_to_move == PLAYER_O else PLAYER_O
        child = MCTSNode(new_board, self.config, self, move, next_player)
        self.children.append(child)
        return child

    def is_terminal(self):
        if self.move is None:
            return False
        r, c = self.move
        prev_player = PLAYER_X if self.player_to_move == PLAYER_O else PLAYER_O
        return check_win_around(self.board, r, c, prev_player)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

# ==============================
# ROLLOUT
# ==============================
def simulate_rollout(board, current_player, config):
    sim_board = [row[:] for row in board]
    curr = current_player
    steps = 0

    while steps < config["max_rollout_steps"]:
        moves = get_neighboring_moves(sim_board, config["rollout_radius"])
        if not moves:
            break

        r, c = random.choice(moves)
        sim_board[r][c] = curr

        if check_win_around(sim_board, r, c, curr):
            return 1.0 if curr == PLAYER_O else 0.0

        curr = PLAYER_X if curr == PLAYER_O else PLAYER_O
        steps += 1

    return 0.5

# ==============================
# MCTS SEARCH
# ==============================
def mcts_search(board, config, root_player):
    root = MCTSNode(board, config, player_to_move=root_player)
    start_time = time.time()

    for _ in range(config["num_simulations"]):
        node = root

        # Selection
        while node.is_fully_expanded() and node.children:
            node = max(node.children, key=lambda c: c.ucb1())

        # Expansion
        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()

        # Simulation
        if node.move:
            prev_player = PLAYER_X if node.player_to_move == PLAYER_O else PLAYER_O
            if check_win_around(node.board, node.move[0], node.move[1], prev_player):
                sim_result = 1.0 if prev_player == PLAYER_O else 0.0
            else:
                sim_result = simulate_rollout(node.board, node.player_to_move, config)
        else:
            sim_result = simulate_rollout(node.board, node.player_to_move, config)

        reward = sim_result if root_player == PLAYER_O else 1.0 - sim_result

        # Backpropagation
        while node:
            node.visits += 1
            node.wins += reward
            node = node.parent

    best_child = max(root.children, key=lambda c: c.visits)
    # print(
    #     f"[MCTS] Level: {config} | Move: {best_child.move} | "
    #     f"Time: {time.time()-start_time:.2f}s"
    # )

    return best_child.move

# ==============================
# PUBLIC API
# ==============================
def get_move_mcts(board, level="mcts_"):
    configs = load_mcts_config()
    config = configs["mcts"][level]

    x_count = sum(row.count(PLAYER_X) for row in board)
    o_count = sum(row.count(PLAYER_O) for row in board)

    current_player = PLAYER_X if x_count == o_count else PLAYER_O
    return mcts_search(board, config, current_player)
