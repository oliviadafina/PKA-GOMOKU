import pygame
import sys

# --- Konstanta ---
BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 50
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE + MARGIN * 2
LINE_COLOR = (50, 50, 50)
BG_COLOR = (230, 200, 150)
X_COLOR = (0, 0, 0)
O_COLOR = (255, 255, 255)

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 80))
pygame.display.set_caption("Gomoku 15x15")
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 60)

# --- Fungsi dasar ---
def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def draw_board(board):
    screen.fill(BG_COLOR)

    # === Judul Utama ===
    title_text = title_font.render("GOMOKU 15 x 15", True, (100, 0, 0))
    screen.blit(title_text, (SCREEN_SIZE // 2 - title_text.get_width() // 2, 10))

    # === Label Player 1 dan Player 2 ===
    player1_text = font.render("Player 1", True, (0, 0, 0))
    player2_text = font.render("Player 2", True, (0, 0, 0))
    text_width = player1_text.get_width()
    text_x = SCREEN_SIZE - MARGIN - text_width - 45
    screen.blit(player1_text, (MARGIN, 70))
    text_width = player2_text.get_width()
    text_x = SCREEN_SIZE - MARGIN - text_width - 45
    screen.blit(player2_text, (text_x, 70))

    # Gambar lingkaran hitam (Player 1)
    pygame.draw.circle(screen, X_COLOR, (MARGIN + 100, 85), 12)
    # Gambar lingkaran putih (Player 2)
    pygame.draw.circle(screen, O_COLOR, (SCREEN_SIZE - MARGIN - 30, 85), 12)
    pygame.draw.circle(screen, (0,0,0), (SCREEN_SIZE - MARGIN - 30, 85), 12, 2)

    # === Papan permainan ===
    offset_y = 110  # geser papan ke bawah biar gak nabrak teks
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, LINE_COLOR,
                         (MARGIN, MARGIN + i * CELL_SIZE + offset_y),
                         (MARGIN + (BOARD_SIZE - 1) * CELL_SIZE, MARGIN + i * CELL_SIZE + offset_y))
        pygame.draw.line(screen, LINE_COLOR,
                         (MARGIN + i * CELL_SIZE, MARGIN + offset_y),
                         (MARGIN + i * CELL_SIZE, MARGIN + (BOARD_SIZE - 1) * CELL_SIZE + offset_y))

    # Bidak
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            cx = MARGIN + y * CELL_SIZE
            cy = MARGIN + x * CELL_SIZE + offset_y
            if board[x][y] == PLAYER_X:
                pygame.draw.circle(screen, X_COLOR, (cx, cy), CELL_SIZE // 2 - 2)
            elif board[x][y] == PLAYER_O:
                pygame.draw.circle(screen, O_COLOR, (cx, cy), CELL_SIZE // 2 - 2)
                pygame.draw.circle(screen, (0,0,0), (cx, cy), CELL_SIZE // 2 - 2, 2)
    pygame.display.flip()

def get_cell_from_mouse(pos):
    x, y = pos
    y -= 110  # sesuaikan offset papan
    col = round((x - MARGIN) / CELL_SIZE)
    row = round((y - MARGIN) / CELL_SIZE)
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

# --- Main game loop ---
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

            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                cell = get_cell_from_mouse(event.pos)
                if cell:
                    x, y = cell
                    if board[x][y] == EMPTY:
                        board[x][y] = current_player
                        if check_winner(board, current_player):
                            game_over = True
                            winner = current_player
                        elif is_full(board):
                            game_over = True
                            winner = 0
                        else:
                            current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X

        # Pesan akhir
        if game_over:
            draw_board(board)
            if winner == PLAYER_X:
                text = font.render("Pemain Hitam Menang!", True, (255, 0, 0))
            elif winner == PLAYER_O:
                text = font.render("Pemain Putih Menang!", True, (255, 0, 0))
            else:
                text = font.render("Seri!", True, (255, 0, 0))
            screen.blit(text, (SCREEN_SIZE // 2 - 150, SCREEN_SIZE - 40))
            pygame.display.flip()

        pygame.display.update()

if __name__ == "__main__":
    main()