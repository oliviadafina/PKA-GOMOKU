import pygame
import sys
import json
import os
import time
from agents.minimax_optimized_agent import get_move_minimax_level
from agents.mcts_optimized_agent import get_move_mcts

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

# ==============================
# COLORS
# ==============================
LINE_COLOR = (50, 50, 50)
BG_COLOR = (230, 200, 150)
X_COLOR = (0, 0, 0)
O_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
BUTTON_SELECTED = (50, 100, 150)

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

# Game States
STATE_MENU = "menu"
STATE_SELECT_MODE = "select_mode"
STATE_SELECT_AGENTS = "select_agents"
STATE_SELECT_OPPONENT = "select_opponent"
STATE_GAME = "game"
STATE_END = "end"

# ==============================
# SCREEN
# ==============================
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 100))
pygame.display.set_caption("Gomoku 15x15")

BOARD_WIDTH = (BOARD_SIZE - 1) * CELL_SIZE
BOARD_HEIGHT = (BOARD_SIZE - 1) * CELL_SIZE
BOARD_X = (SCREEN_SIZE - BOARD_WIDTH) // 2
BOARD_Y = ((SCREEN_SIZE + 100) - BOARD_HEIGHT) // 2

# ==============================
# FONT
# ==============================
font = pygame.font.Font(None, int(CELL_SIZE * 0.8))
title_font = pygame.font.Font(None, int(CELL_SIZE * 1.5))
winner_font = pygame.font.Font(None, int(CELL_SIZE * 1.8))
button_font = pygame.font.Font(None, int(CELL_SIZE * 0.9))

button_font = pygame.font.Font(None, int(CELL_SIZE * 0.9))

# ==============================
# BUTTON CLASS
# ==============================
class Button:
    def __init__(self, x, y, width, height, text, value=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.hovered = False
        self.selected = False
    
    def draw(self, surface):
        color = BUTTON_SELECTED if self.selected else (BUTTON_HOVER if self.hovered else BUTTON_COLOR)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=10)
        
        text_surface = button_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# ==============================
# BOARD
# ==============================
def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def draw_board(board, label_x, label_o, title_text):
    screen.fill(BG_COLOR)

    title = title_font.render(title_text, True, (100, 0, 0))
    screen.blit(title, (SCREEN_SIZE//2 - title.get_width()//2, int(MARGIN*0.3)))

    p1 = font.render(label_x, True, (0, 0, 0))
    p2 = font.render(label_o, True, (0, 0, 0))
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
def show_end_message(winner, label_x, label_o):
    overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE + 100))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    if winner == PLAYER_X:
        msg = f"{label_x} Menang"
    elif winner == PLAYER_O:
        msg = f"{label_o} Menang"
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
def describe_agent(agent_type, level):
    name = "MCTS" if agent_type == "mcts" else "Minimax"
    return f"{name} Lv{level}"

def get_move_for_agent(board, agent_type, level):
    mcts_level_map = {1: "mcts_easy", 2: "mcts_medium", 3: "mcts_hard"}
    
    if agent_type == "mcts":
        level_key = mcts_level_map.get(level, "mcts_medium")
        return get_move_mcts(board, level=level_key)
    return get_move_minimax_level(board, level=level)

def draw_menu():
    screen.fill(BG_COLOR)
    title = title_font.render("GOMOKU 15x15", True, (100, 0, 0))
    screen.blit(title, (SCREEN_SIZE//2 - title.get_width()//2, MARGIN * 2))
    
    subtitle = font.render("Pilih Mode Permainan", True, (50, 50, 50))
    screen.blit(subtitle, (SCREEN_SIZE//2 - subtitle.get_width()//2, MARGIN * 4))

def draw_agent_selection_menu(title_text):
    screen.fill(BG_COLOR)
    title = title_font.render(title_text, True, (100, 0, 0))
    screen.blit(title, (SCREEN_SIZE//2 - title.get_width()//2, MARGIN * 2))

def main():
    game_state = STATE_MENU
    mode = None  # "user_vs_agent" or "agent_vs_agent"
    
    # Agent selections
    player_x_agent = None  # "human", "minimax", "mcts"
    player_x_level = 1
    player_o_agent = None
    player_o_level = 1
    
    # Game variables
    board = None
    current_player = PLAYER_X
    game_over = False
    winner = None
    
    # UI Elements
    menu_buttons = [
        Button(SCREEN_SIZE//2 - 150, SCREEN_SIZE//2 - 60, 300, 50, "User vs Agent", "user_vs_agent"),
        Button(SCREEN_SIZE//2 - 150, SCREEN_SIZE//2 + 10, 300, 50, "Agent vs Agent", "agent_vs_agent"),
        Button(SCREEN_SIZE//2 - 150, SCREEN_SIZE//2 + 80, 300, 50, "Keluar", "exit")
    ]
    
    agent_buttons = [
        Button(SCREEN_SIZE//2 - 200, SCREEN_SIZE//2 - 80, 130, 45, "Minimax", "minimax"),
        Button(SCREEN_SIZE//2 - 50, SCREEN_SIZE//2 - 80, 130, 45, "MCTS", "mcts"),
    ]
    
    level_buttons = [
        Button(SCREEN_SIZE//2 - 200, SCREEN_SIZE//2 + 10, 80, 40, "Level 1", 1),
        Button(SCREEN_SIZE//2 - 100, SCREEN_SIZE//2 + 10, 80, 40, "Level 2", 2),
        Button(SCREEN_SIZE//2, SCREEN_SIZE//2 + 10, 80, 40, "Level 3", 3),
    ]
    
    confirm_button = Button(SCREEN_SIZE//2 - 75, SCREEN_SIZE//2 + 100, 150, 45, "Mulai", "confirm")
    back_button = Button(MARGIN, SCREEN_SIZE + 50, 100, 40, "Kembali", "back")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            # === MENU STATE ===
            if game_state == STATE_MENU:
                for btn in menu_buttons:
                    if btn.handle_event(event):
                        if btn.value == "exit":
                            running = False
                        elif btn.value in ["user_vs_agent", "agent_vs_agent"]:
                            mode = btn.value
                            if mode == "user_vs_agent":
                                game_state = STATE_SELECT_OPPONENT
                                player_x_agent = "human"
                            else:
                                game_state = STATE_SELECT_AGENTS
            
            # === SELECT AGENTS (Agent vs Agent) ===
            elif game_state == STATE_SELECT_AGENTS:
                # Select Player X agent
                for btn in agent_buttons:
                    if btn.handle_event(event):
                        player_x_agent = btn.value
                        for b in agent_buttons:
                            b.selected = (b.value == player_x_agent)
                
                # Select Player X level
                for btn in level_buttons:
                    if btn.handle_event(event):
                        player_x_level = btn.value
                        for b in level_buttons:
                            b.selected = (b.value == player_x_level)
                
                # Confirm and go to select Player O
                if confirm_button.handle_event(event) and player_x_agent:
                    game_state = STATE_SELECT_OPPONENT
                
                if back_button.handle_event(event):
                    game_state = STATE_MENU
                    player_x_agent = None
            
            # === SELECT OPPONENT ===
            elif game_state == STATE_SELECT_OPPONENT:
                for btn in agent_buttons:
                    if btn.handle_event(event):
                        player_o_agent = btn.value
                        for b in agent_buttons:
                            b.selected = (b.value == player_o_agent)
                
                for btn in level_buttons:
                    if btn.handle_event(event):
                        player_o_level = btn.value
                        for b in level_buttons:
                            b.selected = (b.value == player_o_level)
                
                if confirm_button.handle_event(event) and player_o_agent:
                    # Start game
                    board = create_board()
                    current_player = PLAYER_X
                    game_over = False
                    winner = None
                    game_state = STATE_GAME
                
                if back_button.handle_event(event):
                    if mode == "user_vs_agent":
                        game_state = STATE_MENU
                    else:
                        game_state = STATE_SELECT_AGENTS
                    player_o_agent = None
            
            # === GAME STATE ===
            elif game_state == STATE_GAME:
                if back_button.handle_event(event):
                    game_state = STATE_MENU
                    board = None
                    continue
                
                # Human player input
                if not game_over and current_player == PLAYER_X and player_x_agent == "human":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        # Check if click is on board
                        if BOARD_X <= mx <= BOARD_X + BOARD_WIDTH and BOARD_Y <= my <= BOARD_Y + BOARD_HEIGHT:
                            grid_x = round((my - BOARD_Y) / CELL_SIZE)
                            grid_y = round((mx - BOARD_X) / CELL_SIZE)
                            
                            if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
                                if apply_move(board, (grid_x, grid_y), PLAYER_X):
                                    if check_winner(board, PLAYER_X):
                                        winner = PLAYER_X
                                        game_over = True
                                    elif is_full(board):
                                        winner = 0
                                        game_over = True
                                    else:
                                        current_player = PLAYER_O
        
        # === RENDER ===
        if game_state == STATE_MENU:
            draw_menu()
            for btn in menu_buttons:
                btn.draw(screen)
        
        elif game_state == STATE_SELECT_AGENTS:
            draw_agent_selection_menu("Pilih Agent untuk Player X")
            
            label = font.render("Pilih Agent:", True, (0, 0, 0))
            screen.blit(label, (SCREEN_SIZE//2 - label.get_width()//2, SCREEN_SIZE//2 - 120))
            
            for btn in agent_buttons:
                btn.draw(screen)
            
            if player_x_agent:
                label2 = font.render("Pilih Level:", True, (0, 0, 0))
                screen.blit(label2, (SCREEN_SIZE//2 - label2.get_width()//2, SCREEN_SIZE//2 - 30))
                for btn in level_buttons:
                    btn.draw(screen)
                confirm_button.draw(screen)
            
            back_button.draw(screen)
        
        elif game_state == STATE_SELECT_OPPONENT:
            title_text = "Pilih Agent Lawan" if mode == "user_vs_agent" else "Pilih Agent untuk Player O"
            draw_agent_selection_menu(title_text)
            
            label = font.render("Pilih Agent:", True, (0, 0, 0))
            screen.blit(label, (SCREEN_SIZE//2 - label.get_width()//2, SCREEN_SIZE//2 - 120))
            
            for btn in agent_buttons:
                btn.draw(screen)
            
            if player_o_agent:
                label2 = font.render("Pilih Level:", True, (0, 0, 0))
                screen.blit(label2, (SCREEN_SIZE//2 - label2.get_width()//2, SCREEN_SIZE//2 - 30))
                for btn in level_buttons:
                    btn.draw(screen)
                confirm_button.draw(screen)
            
            back_button.draw(screen)
        
        elif game_state == STATE_GAME:
            label_x = "Human (X)" if player_x_agent == "human" else f"{describe_agent(player_x_agent, player_x_level)} (X)"
            label_o = f"{describe_agent(player_o_agent, player_o_level)} (O)"
            title_text = f"{label_x} vs {label_o}"
            
            draw_board(board, label_x, label_o, title_text)
            back_button.draw(screen)
            
            # AI moves
            if not game_over:
                if current_player == PLAYER_X and player_x_agent != "human":
                    move = get_move_for_agent(board, player_x_agent, player_x_level)
                    if apply_move(board, move, PLAYER_X):
                        if check_winner(board, PLAYER_X):
                            winner = PLAYER_X
                            game_over = True
                        elif is_full(board):
                            winner = 0
                            game_over = True
                        else:
                            current_player = PLAYER_O
                    pygame.time.wait(300)
                
                elif current_player == PLAYER_O:
                    move = get_move_for_agent(board, player_o_agent, player_o_level)
                    if apply_move(board, move, PLAYER_O):
                        if check_winner(board, PLAYER_O):
                            winner = PLAYER_O
                            game_over = True
                        elif is_full(board):
                            winner = 0
                            game_over = True
                        else:
                            current_player = PLAYER_X
                    pygame.time.wait(300)
            
            if game_over:
                show_end_message(winner, label_x, label_o)
                pygame.time.wait(2000)
                game_state = STATE_MENU
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
