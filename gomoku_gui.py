import pygame
import sys
from agents.minimax_agent import get_move_minimax
from agents.mcts_agent import get_move_mcts
from agents.minimax_optimized_agent import get_move_minimax_optimized
from agents.mcts_optimized_agent import get_move_mcts_optimized

# --- Inisialisasi ---
pygame.init()

# --- Ambil resolusi layar ---
info = pygame.display.Info()
screen_w, screen_h = info.current_w, info.current_h

# --- Parameter utama ---
BOARD_SIZE = 15
max_height = int(screen_h * 0.85)
MARGIN = int(max_height * 0.05)
CELL_SIZE = int((max_height * 0.9 - MARGIN * 2) / BOARD_SIZE)
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE + MARGIN * 2
OFFSET_Y = int(MARGIN * 2.2)

# --- Warna ---
LINE_COLOR = (50, 50, 50)
BG_COLOR = (230, 200, 150)
X_COLOR = (0, 0, 0)
O_COLOR = (255, 255, 255)

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

# --- Buat window ---
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 100))
pygame.display.set_caption("Gomoku 15x15")

BOARD_WIDTH = (BOARD_SIZE - 1) * CELL_SIZE
BOARD_HEIGHT = (BOARD_SIZE - 1) * CELL_SIZE
BOARD_X = (SCREEN_SIZE - BOARD_WIDTH) // 2
BOARD_Y = ((SCREEN_SIZE + 100) - BOARD_HEIGHT) // 2

# --- Font ---
font = pygame.font.Font(None, int(CELL_SIZE * 1))
title_font = pygame.font.Font(None, int(CELL_SIZE * 1.5))
winner_font = pygame.font.Font(None, int(CELL_SIZE * 1.8))
button_font = pygame.font.Font(None, int(CELL_SIZE * 0.9))

# --- Fungsi dasar ---
def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def draw_board(board):
    screen.fill(BG_COLOR)

    # === Judul ===
    title_text = title_font.render("GOMOKU 15 x 15", True, (100, 0, 0))
    screen.blit(title_text, (SCREEN_SIZE // 2 - title_text.get_width() // 2, int(MARGIN * 0.3)))

    # === Label Player ===
    player1_text = font.render("Minimax Agent", True, (0, 0, 0))
    player2_text = font.render("MCTS Agent", True, (0, 0, 0))
    screen.blit(player1_text, (MARGIN, int(MARGIN * 1.5)))
    screen.blit(player2_text, (SCREEN_SIZE - MARGIN - player2_text.get_width(), int(MARGIN * 1.5)))

    # Lingkaran player sejajar teks
    circle_y = int(MARGIN * 1.5) + player1_text.get_height() // 2
    pygame.draw.circle(screen, X_COLOR,
                       (MARGIN + player1_text.get_width() + 35, circle_y),
                       int(CELL_SIZE / 3))
    pygame.draw.circle(screen, O_COLOR,
                       (SCREEN_SIZE - MARGIN - player2_text.get_width() - 35, circle_y),
                       int(CELL_SIZE / 3))
    pygame.draw.circle(screen, (0, 0, 0),
                       (SCREEN_SIZE - MARGIN - player2_text.get_width() - 35, circle_y),
                       int(CELL_SIZE / 3), 2)

    # === Garis papan ===
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, LINE_COLOR,
                         (BOARD_X, BOARD_Y + i * CELL_SIZE),
                         (BOARD_X + BOARD_WIDTH, BOARD_Y + i * CELL_SIZE))
        pygame.draw.line(screen, LINE_COLOR,
                         (BOARD_X + i * CELL_SIZE, BOARD_Y),
                         (BOARD_X + i * CELL_SIZE, BOARD_Y + BOARD_HEIGHT))

    # === Bidak ===
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            cx = BOARD_X + y * CELL_SIZE
            cy = BOARD_Y + x * CELL_SIZE
            if board[x][y] == PLAYER_X:
                pygame.draw.circle(screen, X_COLOR, (cx, cy), CELL_SIZE // 2 - 2)
            elif board[x][y] == PLAYER_O:
                pygame.draw.circle(screen, O_COLOR, (cx, cy), CELL_SIZE // 2 - 2)
                pygame.draw.circle(screen, (0, 0, 0), (cx, cy), CELL_SIZE // 2 - 2, 2)

    pygame.display.flip()

def get_cell_from_mouse(pos):
    x, y = pos
    col = round((x - BOARD_X) / CELL_SIZE)
    row = round((y - BOARD_Y) / CELL_SIZE)
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row, col
    return None

def check_winner(board, player):
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] == player:
                for dx, dy in directions:
                    count = 1
                    nx, ny = x + dx, y + dy
                    while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == player:
                        count += 1
                        if count == 5:
                            return True
                        nx += dx
                        ny += dy
    return False

def is_full(board):
    return all(cell != EMPTY for row in board for cell in row)

# --- Pesan Menang ---
def show_end_message(winner):
    overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE + 100))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # --- Pesan Menang ---
    if winner == PLAYER_X:
        msg = "Minimax Agent Menang!"
        color = (255, 215, 0)
    elif winner == PLAYER_O:
        msg = "MCTS Agent Menang!"
        color = (255, 215, 0)
    else:
        msg = "Seri!"
        color = (255, 215, 0)

    text = winner_font.render(msg, True, color)
    text_rect = text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 60))
    screen.blit(text, text_rect)

    # --- Tombol Main Lagi & Keluar ---
    button_w, button_h = 180, 60
    spacing = 40
    total_width = button_w * 2 + spacing
    start_x = (SCREEN_SIZE - total_width) // 2
    y_pos = SCREEN_SIZE // 2 + 20

    play_again_rect = pygame.Rect(start_x, y_pos, button_w, button_h)
    quit_rect = pygame.Rect(start_x + button_w + spacing, y_pos, button_w, button_h)

    def draw_button(rect, color, text_str):
        shadow_rect = rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, (40, 40, 40), shadow_rect, border_radius=12)
        pygame.draw.rect(screen, color, rect, border_radius=12)
        btn_text = button_font.render(text_str, True, (255, 255, 255))
        btn_rect = btn_text.get_rect(center=rect.center)
        screen.blit(btn_text, btn_rect)

    draw_button(play_again_rect, (70, 180, 90), "Main Lagi")
    draw_button(quit_rect, (200, 70, 70), "Keluar")

    pygame.draw.line(screen, (255, 255, 255),
                     (SCREEN_SIZE//2 - 120, SCREEN_SIZE//2 - 20),
                     (SCREEN_SIZE//2 + 120, SCREEN_SIZE//2 - 20), 2)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    waiting = False
                    main()
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# --- Main loop ---
def main():
    board = create_board()
    current_player = PLAYER_X
    game_over = False
    winner = None

    while True:
        draw_board(board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # MCTS Agent (Player O) move
        if not game_over and current_player == PLAYER_O:
            x, y = get_move_mcts_optimized(board, iterations=1000)
            board[x][y] = PLAYER_O
            draw_board(board)
            pygame.display.update()
            pygame.time.wait(500)

            if check_winner(board, PLAYER_O):
                game_over = True
                winner = PLAYER_O
            elif is_full(board):
                game_over = True
                winner = 0
            else:
                current_player = PLAYER_X
        
        # Minimax Agent (Player X) move
        elif not game_over and current_player == PLAYER_X:
            x, y = get_move_minimax_optimized(board)
            board[x][y] = PLAYER_X
            draw_board(board)
            pygame.display.update()
            pygame.time.wait(500)

            if check_winner(board, PLAYER_X):
                game_over = True
                winner = PLAYER_X
            elif is_full(board):
                game_over = True
                winner = 0
            else:
                current_player = PLAYER_O
        if game_over:
            show_end_message(winner)

        pygame.display.update()

if __name__ == "__main__":
    main()