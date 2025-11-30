import math
import random
import time

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

# --- KONFIGURASI ---
MAX_DEPTH = 3  # Depth 3 biasanya cukup kuat untuk Gomoku di Python tanpa lag parah
SEARCH_RADIUS = 2  # Hanya cari langkah dalam jarak 2 kotak dari bidak yang ada

# Bobot Skor (Pattern Score)
# Kunci: (jumlah_bidak_berurut, jumlah_ujung_terbuka)
SCORE_TABLE = {
    (5, 0): 1000000, (5, 1): 1000000, (5, 2): 1000000, # Menang
    (4, 2): 100000,  # Live 4 (Pasti menang giliran berikutnya)
    (4, 1): 10000,   # Dead 4 (Ancaman serius, harus diblok)
    (3, 2): 5000,    # Live 3 (Bisa jadi Live 4)
    (3, 1): 100,     # Dead 3
    (2, 2): 50,      # Live 2
    (2, 1): 10,      # Dead 2
    (1, 2): 5,
    (1, 1): 1
}

def get_valid_moves_optimized(board):
    """
    Hanya mengembalikan langkah-langkah yang relevan (di sekitar bidak yang sudah ada).
    Mengurangi branching factor dari 225 menjadi ~20-30.
    """
    n = len(board)
    moves = set()
    has_piece = False

    for r in range(n):
        for c in range(n):
            if board[r][c] != EMPTY:
                has_piece = True
                # Cek area sekitar (radius SEARCH_RADIUS)
                r_min = max(0, r - SEARCH_RADIUS)
                r_max = min(n, r + SEARCH_RADIUS + 1)
                c_min = max(0, c - SEARCH_RADIUS)
                c_max = min(n, c + SEARCH_RADIUS + 1)

                for i in range(r_min, r_max):
                    for j in range(c_min, c_max):
                        if board[i][j] == EMPTY:
                            moves.add((i, j))
    
    if not has_piece:
        return [(n // 2, n // 2)]  # Langkah pertama di tengah

    return list(moves)

def evaluate_line(line, player):
    """Menghitung skor untuk satu baris (list of cells)."""
    score = 0
    length = len(line)
    i = 0
    while i < length:
        if line[i] == player:
            count = 0
            start_idx = i
            while i < length and line[i] == player:
                count += 1
                i += 1
            
            # Cek ujung terbuka
            open_ends = 0
            if start_idx > 0 and line[start_idx - 1] == EMPTY:
                open_ends += 1
            if i < length and line[i] == EMPTY:
                open_ends += 1
            
            if count >= 5:
                score += 1000000
            else:
                score += SCORE_TABLE.get((count, open_ends), 0)
        else:
            i += 1
    return score

def evaluate_board(board, player):
    """
    Evaluasi total papan.
    Score = (Score Player) - (Score Lawan * Penalty Factor)
    Kita beri bobot lebih pada skor lawan agar AI bermain defensif (takut kalah).
    """
    n = len(board)
    opponent = PLAYER_X if player == PLAYER_O else PLAYER_O
    
    my_score = 0
    op_score = 0

    # --- Horizontal ---
    for r in range(n):
        row = board[r]
        my_score += evaluate_line(row, player)
        op_score += evaluate_line(row, opponent)

    # --- Vertical ---
    for c in range(n):
        col = [board[r][c] for r in range(n)]
        my_score += evaluate_line(col, player)
        op_score += evaluate_line(col, opponent)

    # --- Diagonals ---
    # Diagonal utama & anti-diagonal
    # Kita kumpulkan semua diagonal ke dalam list
    diags = []
    # Diagonal (kiri-atas ke kanan-bawah)
    for k in range(n * 2 - 1): # k adalah jumlah r+c? bukan, ini untuk diagonal
        # Cara mudah ambil diagonal:
        # diag1: r - c = constant
        # diag2: r + c = constant
        pass 

    # Implementasi manual diagonal loop agar efisien
    # Diagonal \
    for k in range(-n + 1, n):
        d = []
        for r in range(n):
            c = r - k
            if 0 <= c < n:
                d.append(board[r][c])
        if len(d) >= 5:
            my_score += evaluate_line(d, player)
            op_score += evaluate_line(d, opponent)
            
    # Diagonal /
    for k in range(2 * n - 1):
        d = []
        for r in range(n):
            c = k - r
            if 0 <= c < n:
                d.append(board[r][c])
        if len(d) >= 5:
            my_score += evaluate_line(d, player)
            op_score += evaluate_line(d, opponent)

    # Defensif: Jika lawan punya skor tinggi (ancaman), kita harus memprioritaskan block.
    # Faktor 1.2 - 1.5 biasanya cukup.
    return my_score - (op_score * 1.5)

def minimax_ab(board, depth, alpha, beta, is_maximizing, player):
    # Cek terminal state (menang/kalah) tidak perlu di sini secara eksplisit 
    # karena evaluate_board sudah memberi nilai besar jika ada 5 in a row.
    # Tapi untuk optimasi, kita bisa cek winner dulu jika mau.
    
    valid_moves = get_valid_moves_optimized(board)
    
    if depth == 0 or not valid_moves:
        return evaluate_board(board, player), None

    # Move Ordering: (Optional) Bisa sort moves berdasarkan heuristik sederhana agar pruning lebih efektif
    # valid_moves.sort(key=...) # Skip untuk sekarang agar tidak terlalu berat

    opponent = PLAYER_X if player == PLAYER_O else PLAYER_O

    if is_maximizing:
        max_eval = -math.inf
        best_move = random.choice(valid_moves) # Fallback
        
        for move in valid_moves:
            r, c = move
            board[r][c] = player
            eval_val, _ = minimax_ab(board, depth - 1, alpha, beta, False, player)
            board[r][c] = EMPTY
            
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
            
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break # Beta Cutoff
        return max_eval, best_move
    else:
        min_eval = math.inf
        best_move = random.choice(valid_moves)

        for move in valid_moves:
            r, c = move
            board[r][c] = opponent
            eval_val, _ = minimax_ab(board, depth - 1, alpha, beta, True, player)
            board[r][c] = EMPTY
            
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            
            beta = min(beta, eval_val)
            if beta <= alpha:
                break # Alpha Cutoff
        return min_eval, best_move

def get_move_minimax_optimized(board, depth=MAX_DEPTH):
    """
    Fungsi utama yang dipanggil GUI.
    """
    start = time.time()
    
    # Tentukan siapa yang jalan (asumsi fungsi ini dipanggil saat giliran AI)
    # Kita hitung jumlah bidak untuk tahu giliran siapa, atau bisa di-pass argumen.
    # Tapi biar aman, kita anggap AI selalu 'Maximizing' dirinya sendiri.
    # Kita perlu tahu AI itu X atau O.
    # Di gomoku_gui.py, Minimax dipakai sebagai PLAYER_X.
    # Agar fleksibel, kita cek bidak mana yang lebih sedikit (jika O jalan kedua) atau pass argumen.
    # Default code lama: Minimax = Player X.
    
    ai_player = PLAYER_X 
    
    # Panggil Minimax dengan Alpha-Beta Pruning
    score, move = minimax_ab(board, depth, -math.inf, math.inf, True, ai_player)
    
    end = time.time()
    print(f"[Minimax Optimized] Time: {end - start:.3f}s | Depth: {depth} | Score: {score} | Move: {move}")
    
    if move is None:
        # Fallback jika papan penuh atau error
        moves = get_valid_moves_optimized(board)
        return random.choice(moves) if moves else (0,0)
        
    return move
