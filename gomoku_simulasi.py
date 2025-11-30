from agents.minimax_agent import get_move_minimax
from agents.mcts_agent import get_move_mcts
from agents.minimax_optimized_agent import get_move_minimax_optimized

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2
BOARD_SIZE = 15

def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def check_winner(board, player):
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] == player:
                for dx, dy in directions:
                    count = 1
                    nx, ny = x+dx, y+dy
                    while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == player:
                        count += 1
                        if count == 5:
                            return True
                        nx += dx
                        ny += dy
    return False

def is_full(board):
    return all(board[x][y] != EMPTY for x in range(BOARD_SIZE) for y in range(BOARD_SIZE))

def play_single_game(iter_mcts=500):
    board = create_board()
    current_player = PLAYER_X

    while True:
        if current_player == PLAYER_X:
            move = get_move_minimax_optimized(board, depth=2)
        else:
            move = get_move_mcts(board, iterations=iter_mcts)

        x, y = move
        board[x][y] = current_player

        # check game over
        if check_winner(board, current_player):
            return current_player

        if is_full(board):
            return 0  # draw

        current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X


def run_benchmark(games=100):
    x_win = 0
    o_win = 0
    draws = 0

    for g in range(games):
        result = play_single_game()
        if result == PLAYER_X:
            x_win += 1
        elif result == PLAYER_O:
            o_win += 1
        else:
            draws += 1

        print(f"Game {g+1}/{games} selesai. Hasil: {result}")

    print("\n======= SUMMARY =======")
    print(f"Minimax (X) wins: {x_win}")
    print(f"MCTS (O) wins: {o_win}")
    print(f"Draws: {draws}")

if __name__ == "__main__":
    run_benchmark(50)  # run 50 dulu, jangan langsung 1000
