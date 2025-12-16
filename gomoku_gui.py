import pygame
import sys
import json
import os
from agents.minimax_optimized_agent import get_move_minimax_level

def load_gui_config():
    config_path = os.path.join(
        os.path.dirname(__file__),
        "agents",
        "config",
        "gui_config.json"
    )
    with open(config_path, "r") as f:
        return json.load(f)

GUI_CONFIG = load_gui_config()


# ==============================
# INIT
# ==============================
pygame.init()
info = pygame.display.Info()
screen_w, screen_h = info.current_w, info.current_h

BOARD_SIZE = 15
max_height = int(screen_h * 0.85)
MARGIN = int(max_height * 0.05)
CELL_SIZE = int((max_height * 0.9 - MARGIN * 2) / BOARD_SIZE)
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE + MARGIN * 2
OFFSET_Y = int(MARGIN * 2.2)

# ==============================
# COLORS
# ==============================
LINE_COLOR = (50, 50, 50)
BG_COLOR = (230, 200, 150)
X_COLOR = (0, 0, 0)
O_COLOR = (255, 255, 255)

EMPTY = 0
PLAYER_X = 1   # Minimax A
PLAYER_O = 2   # Minimax B

# ==============================
# SCREEN
# ==============================
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 100))
pygame.display.set_caption("Gomoku 15x15 - Minimax vs Minimax")

BOARD_WIDTH = (BOARD_SIZE - 1) * CELL_SIZE
BOARD_HEIGHT = (BOARD_SIZE - 1) * CELL_SIZE
BOARD_X = (SCREEN_SIZE - BOARD_WIDTH) // 2
BOARD_Y = ((SCREEN_SIZE + 100) - BOARD_HEIGHT) // 2

# ==============================
# FONT
# ==============================
font = pygame.font.Font(None, int(CELL_SIZE * 1))
title_font = pygame.font.Font(None, int(CELL_SIZE * 1.5))
winner_font = pygame.font.Font(None, int(CELL_SIZE * 1.8))

# ==============================
# BOARD
# ==============================
def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def draw_board(board):
    screen.fill(BG_COLOR)

    title = title_font.render("MINIMAX vs MINIMAX", True, (100, 0, 0))
    screen.blit(title, (SCREEN_SIZE//2 - title.get_width()//2, int(MARGIN*0.3)))

    p1 = font.render("Minimax A (X)", True, (0, 0, 0))
    p2 = font.render("Minimax B (O)", True, (0, 0, 0))
    screen.blit(p1, (MARGIN, int(MARGIN * 1.5)))
    screen.blit(p2, (SCREEN_SIZE - MARGIN - p2.get_width(), int(MARGIN * 1.5)))

    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, LINE_COLOR,
                         (BOARD_X, BOARD_Y + i * CELL_SIZE),
                         (BOARD_X + BOARD_WIDTH, BOARD_Y + i * CELL_SIZE))
        pygame.draw.line(screen, LINE_COLOR,
                         (BOARD_X + i * CELL_SIZE, BOARD_Y),
                         (BOARD_X + i * CELL_SIZE, BOARD_Y + BOARD_HEIGHT))

    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            cx = BOARD_X + y * CELL_SIZE
            cy = BOARD_Y + x * CELL_SIZE
            if board[x][y] == PLAYER_X:
                pygame.draw.circle(screen, X_COLOR, (cx, cy), CELL_SIZE//2 - 2)
            elif board[x][y] == PLAYER_O:
                pygame.draw.circle(screen, O_COLOR, (cx, cy), CELL_SIZE//2 - 2)
                pygame.draw.circle(screen, (0,0,0), (cx, cy), CELL_SIZE//2 - 2, 2)

    pygame.display.flip()

# ==============================
# LOGIC
# ==============================
def check_winner(board, player):
    dirs = [(1,0),(0,1),(1,1),(1,-1)]
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] == player:
                for dx, dy in dirs:
                    cnt = 1
                    nx, ny = x+dx, y+dy
                    while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == player:
                        cnt += 1
                        if cnt == 5:
                            return True
                        nx += dx
                        ny += dy
    return False

def is_full(board):
    return all(cell != EMPTY for row in board for cell in row)

def apply_move(board, move, player):
    if move is None:
        return False
    x, y = move
    if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[x][y] == EMPTY:
        board[x][y] = player
        return True
    return False

# ==============================
# END
# ==============================
def show_end_message(winner):
    overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE + 100))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    if winner == PLAYER_X:
        msg = "Minimax A (X) Menang"
    elif winner == PLAYER_O:
        msg = "Minimax B (O) Menang"
    else:
        msg = "Seri"

    text = winner_font.render(msg, True, (255, 215, 0))
    rect = text.get_rect(center=(SCREEN_SIZE//2, SCREEN_SIZE//2))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(2500)

# ==============================
# MAIN
# ==============================
def main():
    board = create_board()
    current_player = PLAYER_X
    game_over = False
    winner = None
    clock = pygame.time.Clock()

    while not game_over:
        clock.tick(60)
        draw_board(board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # === MINIMAX A ===
        if current_player == PLAYER_X:
            conf_x = GUI_CONFIG["player_x"]
            move = get_move_minimax_level(board, level=conf_x["level"])
            if not apply_move(board, move, PLAYER_X):
                winner = PLAYER_O
                break

            if check_winner(board, PLAYER_X):
                winner = PLAYER_X
                game_over = True
            elif is_full(board):
                winner = 0
                game_over = True
            else:
                current_player = PLAYER_O

        # === MINIMAX B ===
        else:
            conf_o = GUI_CONFIG["player_o"]
            move = get_move_minimax_level(board, level=conf_o["level"])

            if not apply_move(board, move, PLAYER_O):
                winner = PLAYER_X
                break

            if check_winner(board, PLAYER_O):
                winner = PLAYER_O
                game_over = True
            elif is_full(board):
                winner = 0
                game_over = True
            else:
                current_player = PLAYER_X

        pygame.time.wait(300)

    show_end_message(winner)

if __name__ == "__main__":
    main()
