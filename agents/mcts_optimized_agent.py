import math
import random
import time

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

# --- OPTIMISASI 1: Pengecekan Kemenangan Lokal (O(1)) ---
def check_win_around(board, r, c, player):
    """
    Hanya mengecek garis yang melewati titik (r, c) untuk melihat apakah 'player' menang.
    Jauh lebih cepat daripada scan seluruh papan.
    """
    n = len(board)
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        count = 1
        # Cek arah positif
        for i in range(1, 5):
            nr, nc = r + dr * i, c + dc * i
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == player:
                count += 1
            else:
                break
        # Cek arah negatif
        for i in range(1, 5):
            nr, nc = r - dr * i, c - dc * i
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == player:
                count += 1
            else:
                break
        
        if count >= 5:
            return True
    return False

# --- OPTIMISASI 2: Hanya langkah relevan (radius 2) ---
def get_neighboring_moves(board, radius=2):
    """
    Hanya mengembalikan langkah di sekitar bidak yang sudah ada.
    Mengurangi branching factor drastis.
    """
    n = len(board)
    moves = set()
    has_piece = False
    
    for r in range(n):
        for c in range(n):
            if board[r][c] != EMPTY:
                has_piece = True
                r_min = max(0, r - radius)
                r_max = min(n, r + radius + 1)
                c_min = max(0, c - radius)
                c_max = min(n, c + radius + 1)
                
                for i in range(r_min, r_max):
                    for j in range(c_min, c_max):
                        if board[i][j] == EMPTY:
                            moves.add((i, j))
                            
    if not has_piece:
        return [(n // 2, n // 2)]
        
    return list(moves)

class MCTSNodeOpt:
    def __init__(self, board, parent=None, move=None, player_to_move=PLAYER_X):
        self.board = [row[:] for row in board]
        self.parent = parent
        self.move = move
        self.player_to_move = player_to_move
        
        self.children = []
        self.untried_moves = get_neighboring_moves(self.board)
        
        self.visits = 0
        self.wins = 0 
        
    def ucb1(self, c=1.41):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def expand(self):
        move = self.untried_moves.pop()
        r, c = move
        new_board = [row[:] for row in self.board]
        new_board[r][c] = self.player_to_move
        
        next_player = PLAYER_X if self.player_to_move == PLAYER_O else PLAYER_O
        child = MCTSNodeOpt(new_board, parent=self, move=move, player_to_move=next_player)
        self.children.append(child)
        return child

    def is_terminal(self):
        if self.move is None: return False
        r, c = self.move
        prev_player = PLAYER_X if self.player_to_move == PLAYER_O else PLAYER_O
        return check_win_around(self.board, r, c, prev_player) or not any(EMPTY in row for row in self.board)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

def simulate_rollout_opt(board, current_player):
    """
    Rollout cepat:
    - Menggunakan copy board
    - Hanya cek kemenangan di langkah terakhir
    - Batas langkah (max_steps) agar tidak terlalu lama
    Return: 1.0 (O menang), 0.0 (X menang), 0.5 (Seri)
    """
    sim_board = [row[:] for row in board]
    curr = current_player
    
    max_steps = 40 # Batasi kedalaman simulasi random
    steps = 0
    
    while steps < max_steps:
        moves = get_neighboring_moves(sim_board, radius=1) # Radius 1 agar lebih agresif/cepat
        if not moves: break # Papan penuh
        
        r, c = random.choice(moves)
        sim_board[r][c] = curr
        
        if check_win_around(sim_board, r, c, curr):
            return 1.0 if curr == PLAYER_O else 0.0
            
        curr = PLAYER_X if curr == PLAYER_O else PLAYER_O
        steps += 1
        
    return 0.5

def mcts_search_opt(board, iterations=1000, root_player=PLAYER_O):
    root = MCTSNodeOpt(board, player_to_move=root_player)
    
    start_time = time.time()
    
    for i in range(iterations):
        node = root
        
        # 1. Selection
        while node.is_fully_expanded() and node.children:
            node = max(node.children, key=lambda c: c.ucb1())
            
        # 2. Expansion
        if not node.is_fully_expanded() and not node.is_terminal():
            node = node.expand()
            
        # 3. Simulation
        winner = None
        # Cek apakah node yang baru di-expand sudah terminal (menang)
        if node.move:
            prev_player = PLAYER_X if node.player_to_move == PLAYER_O else PLAYER_O
            if check_win_around(node.board, node.move[0], node.move[1], prev_player):
                winner = prev_player
        
        if winner:
            # Jika winner == PLAYER_O, result = 1.0. Jika X, result = 0.0
            sim_result = 1.0 if winner == PLAYER_O else 0.0
        else:
            sim_result = simulate_rollout_opt(node.board, node.player_to_move)
            
        # Konversi result ke reward perspektif root_player
        # Jika root_player O: reward = sim_result
        # Jika root_player X: reward = 1.0 - sim_result
        if root_player == PLAYER_O:
            reward = sim_result
        else:
            reward = 1.0 - sim_result
                
        # 4. Backpropagation
        while node:
            node.visits += 1
            node.wins += reward
            node = node.parent
            
    if not root.children:
        return random.choice(get_neighboring_moves(board))
        
    # Pilih langkah dengan visits terbanyak (Robust Child)
    best_child = max(root.children, key=lambda c: c.visits)
    
    end_time = time.time()
    print(f"[MCTS Optimized] Time: {end_time - start_time:.3f}s | Iterations: {iterations} | Move: {best_child.move}")
    
    return best_child.move

def get_move_mcts_optimized(board, iterations=1000):
    # Tentukan giliran siapa
    x_count = sum(row.count(PLAYER_X) for row in board)
    o_count = sum(row.count(PLAYER_O) for row in board)
    
    # Gomoku: X jalan duluan. Jika jumlah sama, giliran X. Jika X > O, giliran O.
    current_player = PLAYER_X if x_count == o_count else PLAYER_O
    
    return mcts_search_opt(board, iterations=iterations, root_player=current_player)
