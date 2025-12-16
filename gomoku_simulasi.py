import time
import json
import os
from datetime import datetime
from agents.minimax_optimized_agent import get_move_minimax_level
from agents.mcts_optimized_agent import get_move_mcts

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2
BOARD_SIZE = 15


# --- CONFIG ---
def load_gui_config():
    config_path = os.path.join(
        os.path.dirname(__file__),
        "agents",
        "config",
        "gui_config.json",
    )
    with open(config_path, "r") as f:
        return json.load(f)


GUI_CONFIG = load_gui_config()


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


def apply_move(board, move, player):
    if move is None:
        return False
    x, y = move
    if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[x][y] == EMPTY:
        board[x][y] = player
        return True
    return False


# --- AGENT HELPERS ---
def describe_agent(conf):
    agent = conf.get("agent", "minimax")
    level = conf.get("level", 1)
    name = "MCTS" if agent == "mcts" else "Minimax"
    return f"{name} Lv{level}"


def get_move_for_agent(board, conf):
    agent = conf.get("agent", "minimax")
    level = conf.get("level", 1)

    mcts_level_map = {1: "mcts_easy", 2: "mcts_medium", 3: "mcts_hard"}

    if agent == "mcts":
        level_key = mcts_level_map.get(level, "mcts_medium")
        return get_move_mcts(board, level=level_key)

    return get_move_minimax_level(board, level=level)


# --- SIMULASI SATU GAME ---
def play_single_game(conf_x=None, conf_o=None, verbose=False):
    conf_x = conf_x or GUI_CONFIG["player_x"]
    conf_o = conf_o or GUI_CONFIG["player_o"]

    board = create_board()
    current_player = PLAYER_X

    while True:
        if current_player == PLAYER_X:
            start = time.time()
            move = get_move_for_agent(board, conf_x)
            end = time.time()
            if verbose:
                print(f"[{describe_agent(conf_x)}] pilih {move} dalam {end - start:.2f}s")
            
            if not apply_move(board, move, PLAYER_X):
                return PLAYER_O  # Invalid move, X kalah
        else:
            start = time.time()
            move = get_move_for_agent(board, conf_o)
            end = time.time()
            if verbose:
                print(f"[{describe_agent(conf_o)}] pilih {move} dalam {end - start:.2f}s")
            
            if not apply_move(board, move, PLAYER_O):
                return PLAYER_X  # Invalid move, O kalah

        if check_winner(board, current_player):
            return current_player

        if is_full(board):
            return 0  # draw

        current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X


# --- SAVE HASIL SIMULASI ---
def save_simulation_result(conf_x, conf_o, num_games, verbose, game_details, x_wins, o_wins, draws, total_time):
    """Simpan hasil simulasi ke file TXT"""
    # Buat folder hasil jika belum ada
    hasil_dir = "hasil"
    if not os.path.exists(hasil_dir):
        os.makedirs(hasil_dir)
    
    timestamp = datetime.now()
    filename = os.path.join(hasil_dir, f"hasil_simulasi_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Cari game tercepat dan terlambat
    if game_details:
        fastest = min(game_details, key=lambda g: g['duration'])
        slowest = max(game_details, key=lambda g: g['duration'])
    else:
        fastest = slowest = None
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(" "*25 + "HASIL SIMULASI GOMOKU\n")
        f.write("="*80 + "\n")
        f.write(f"Tanggal          : {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Player X         : {describe_agent(conf_x)}\n")
        f.write(f"Player O         : {describe_agent(conf_o)}\n")
        f.write(f"Jumlah Game      : {num_games}\n")
        f.write(f"Verbose Mode     : {verbose}\n")
        f.write("\n")
        
        f.write("="*80 + "\n")
        f.write(" "*30 + "RINGKASAN\n")
        f.write("="*80 + "\n")
        f.write(f"Player X ({describe_agent(conf_x)}) : {x_wins} menang  ({x_wins/num_games*100:.1f}%)\n")
        f.write(f"Player O ({describe_agent(conf_o)}) : {o_wins} menang  ({o_wins/num_games*100:.1f}%)\n")
        f.write(f"Draw                   : {draws} seri   ({draws/num_games*100:.1f}%)\n")
        f.write("\n")
        f.write(f"Total Waktu            : {total_time:.2f} detik\n")
        f.write(f"Rata-rata per Game     : {total_time/num_games:.2f} detik\n")
        
        if fastest:
            f.write(f"Game Tercepat          : {fastest['duration']:.2f} detik (Game #{fastest['number']})\n")
        if slowest:
            f.write(f"Game Terlambat         : {slowest['duration']:.2f} detik (Game #{slowest['number']})\n")
        
        f.write("\n")
        f.write("="*80 + "\n")
        f.write(" "*28 + "DETAIL PER GAME\n")
        f.write("="*80 + "\n")
        
        for detail in game_details:
            winner_text = describe_agent(conf_x) if detail['winner'] == 'X' else (
                describe_agent(conf_o) if detail['winner'] == 'O' else 'Draw'
            )
            f.write(f"Game #{detail['number']:<3} | Pemenang: {winner_text:<15} | Durasi: {detail['duration']:>6.2f}s\n")
        
        f.write("="*80 + "\n")
    
    return filename


# --- TURNAMEN ANTAR LEVEL ---
def run_tournament():
    results = []

    pairs = [
        ("Minimax Lv1", "Minimax Lv2", {"agent": "minimax", "level": 1}, {"agent": "minimax", "level": 2}),
        ("Minimax Lv2", "Minimax Lv3", {"agent": "minimax", "level": 2}, {"agent": "minimax", "level": 3}),
        ("MCTS Lv1", "MCTS Lv2", {"agent": "mcts", "level": 1}, {"agent": "mcts", "level": 2}),
        ("MCTS Lv2", "MCTS Lv3", {"agent": "mcts", "level": 2}, {"agent": "mcts", "level": 3}),
        ("Minimax Lv2", "MCTS Lv3", {"agent": "minimax", "level": 2}, {"agent": "mcts", "level": 3}),
    ]

    for name1, name2, lvl1, lvl2, mode in pairs:
        print(f"\n=== {name1} vs {name2} ===")

        x_win, o_win, draws = 0, 0, 0
        n_games = 10  # bisa diubah
        total_time = 0

        for g in range(n_games):
            start_time = time.time()
            result = play_single_game(conf_x=lvl1, conf_o=lvl2)
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
    conf_x = GUI_CONFIG["player_x"]
    conf_o = GUI_CONFIG["player_o"]
    sim_config = GUI_CONFIG.get("simulation", {"num_games": 1, "verbose": True})
    
    num_games = sim_config.get("num_games", 1)
    verbose = sim_config.get("verbose", True)
    
    print(f"=== Simulasi: {describe_agent(conf_x)} vs {describe_agent(conf_o)} ===")
    print(f"Jumlah games: {num_games}\n")
    
    x_wins, o_wins, draws = 0, 0, 0
    total_time = 0
    game_details = []
    
    for i in range(num_games):
        print(f"\n--- Game {i+1}/{num_games} ---")
        start_time = time.time()
        result = play_single_game(conf_x=conf_x, conf_o=conf_o, verbose=verbose)
        game_time = time.time() - start_time
        total_time += game_time
        
        winner_label = None
        if result == PLAYER_X:
            x_wins += 1
            winner_label = 'X'
            print(f"✓ Game {i+1}: {describe_agent(conf_x)} menang (waktu: {game_time:.2f}s)")
        elif result == PLAYER_O:
            o_wins += 1
            winner_label = 'O'
            print(f"✓ Game {i+1}: {describe_agent(conf_o)} menang (waktu: {game_time:.2f}s)")
        else:
            draws += 1
            winner_label = 'Draw'
            print(f"✓ Game {i+1}: Seri (waktu: {game_time:.2f}s)")
        
        game_details.append({
            'number': i + 1,
            'winner': winner_label,
            'duration': game_time
        })
    
    print("\n" + "="*50)
    print("RINGKASAN SIMULASI")
    print("="*50)
    print(f"{describe_agent(conf_x)} (X) menang: {x_wins}/{num_games} ({x_wins/num_games*100:.1f}%)")
    print(f"{describe_agent(conf_o)} (O) menang: {o_wins}/{num_games} ({o_wins/num_games*100:.1f}%)")
    print(f"Seri: {draws}/{num_games} ({draws/num_games*100:.1f}%)")
    print(f"\nTotal waktu: {total_time:.2f}s")
    print(f"Rata-rata per game: {total_time/num_games:.2f}s")
    print("="*50)
    
    # Simpan hasil ke file
    filename = save_simulation_result(
        conf_x, conf_o, num_games, verbose,
        game_details, x_wins, o_wins, draws, total_time
    )
    print(f"\n✓ Hasil simulasi disimpan ke: {filename}")