from matplotlib.pyplot import title
import pygame
import sys
import json
import os
import time
import subprocess
from datetime import datetime
from agents.minimax_optimized_agent import get_move_minimax_level
from agents.mcts_optimized_agent import get_move_mcts
from gomoku_simulasi import play_single_game, save_simulation_result, describe_agent as sim_describe_agent

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

LABEL_AGENT_Y = SCREEN_SIZE // 2 - 120
LABEL_LEVEL_Y = SCREEN_SIZE // 2 + 10
LEVEL_BUTTON_OFFSET_Y = 35
CONFIRM_BUTTON_Y = LABEL_LEVEL_Y + 35 + 60

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
STATE_SETUP_SIMULATION = "setup_simulation"
STATE_RUNNING_SIMULATION = "running_simulation"

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
def create_menu_buttons():
    button_w = 300
    button_h = 55
    gap = 20

    total_height = 5 * button_h + 4 * gap
    start_y = SCREEN_SIZE // 2 - total_height // 2 + 40

    center_x = SCREEN_SIZE // 2 - button_w // 2

    return [
        Button(center_x, start_y, button_w, button_h, "User vs Agent", "user_vs_agent"),
        Button(center_x, start_y + (button_h + gap), button_w, button_h, "Agent vs Agent", "agent_vs_agent"),
        Button(center_x, start_y + 2 * (button_h + gap), button_w, button_h, "Simulasi", "simulation"),
        Button(center_x, start_y + 3 * (button_h + gap), button_w, button_h, "Lihat Statistik", "stats_viewer"),
        Button(center_x, start_y + 4 * (button_h + gap), button_w, button_h, "Keluar", "exit"),
    ]

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

class InputField:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = "10"
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 4:
                self.text += event.unicode
    
    def draw(self, surface):
        # Background
        color = (255, 255, 255) if self.active else (240, 240, 240)
        pygame.draw.rect(surface, color, self.rect)
        border_color = (52, 152, 219) if self.active else (100, 100, 100)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Text
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Cursor
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer % 60 < 30:  # Blink every 30 frames
                cursor_x = text_x + text_surface.get_width() + 2
                cursor_y = self.rect.y + 5
                pygame.draw.line(surface, (0, 0, 0), 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + self.rect.height - 10), 2)
    
    def get_value(self):
        try:
            return int(self.text) if self.text else 10
        except:
            return 10

# ==============================
# BOARD
# ==============================

def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def draw_board(board, label_x, label_o, title_text):
    screen.fill(BG_COLOR)

    title = title_font.render(title_text, True, (100, 0, 0))
    TITLE_Y = int(MARGIN * 0.6)
    
    title_rect = title.get_rect(
        center=(SCREEN_SIZE // 2, TITLE_Y + title.get_height() // 2)
)
    screen.blit(title, title_rect)

    # LABEL PLAYER
    p1 = font.render(label_x, True, (0, 0, 0))
    p2 = font.render(label_o, True, (0, 0, 0))

    LABEL_Y = TITLE_Y + title.get_height() + 15 

    screen.blit(p1, (MARGIN, LABEL_Y))
    screen.blit(p2, (SCREEN_SIZE - MARGIN - p2.get_width(), LABEL_Y))

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

def launch_stats_viewer(file_path=None):
    """Launch the statistics viewer in a new process"""
    try:
        stats_viewer_path = os.path.join(os.path.dirname(__file__), "stats_viewer.py")
        if os.path.exists(stats_viewer_path):
            if file_path:
                subprocess.Popen([sys.executable, stats_viewer_path, file_path])
            else:
                subprocess.Popen([sys.executable, stats_viewer_path])
        else:
            print(f"Stats viewer not found at: {stats_viewer_path}")
    except Exception as e:
        print(f"Error launching stats viewer: {e}")

def run_simulation_gui(agent_x_type, agent_x_level, agent_o_type, agent_o_level, num_games, 
                       callback_progress=None):
    """Run simulation using gomoku_simulasi functions with GUI callback"""
    conf_x = {"agent": agent_x_type, "level": agent_x_level}
    conf_o = {"agent": agent_o_type, "level": agent_o_level}
    
    x_wins, o_wins, draws = 0, 0, 0
    total_time = 0
    game_details = []
    
    for i in range(num_games):
        start_time = time.time()
        result = play_single_game(conf_x=conf_x, conf_o=conf_o, verbose=False)
        game_time = time.time() - start_time
        total_time += game_time
        
        winner_label = None
        if result == 1:  # PLAYER_X
            x_wins += 1
            winner_label = 'X'
        elif result == 2:  # PLAYER_O
            o_wins += 1
            winner_label = 'O'
        else:
            draws += 1
            winner_label = 'Draw'
        
        game_details.append({
            'number': i + 1,
            'winner': winner_label,
            'duration': game_time
        })
        
        # Call progress callback if provided
        if callback_progress:
            callback_progress(i + 1, num_games, x_wins, o_wins, draws, total_time)
    
    # Save results using gomoku_simulasi function
    filename = save_simulation_result(
        conf_x, conf_o, num_games, False,
        game_details, x_wins, o_wins, draws, total_time
    )
    
    return filename

def draw_menu():
    screen.fill(BG_COLOR)

    title = title_font.render("GOMOKU 15x15", True, (120, 49, 20))
    subtitle = font.render("Pilih Mode Permainan", True, (60, 60, 60))

    title_rect = title.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 250))
    subtitle_rect = subtitle.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 180))

    screen.blit(title, title_rect)
    screen.blit(subtitle, subtitle_rect)


def draw_agent_selection_menu(title_text):
    screen.fill(BG_COLOR)
    title = title_font.render(title_text, True, (100, 0, 0))
    screen.blit(title, (SCREEN_SIZE//2 - title.get_width()//2, MARGIN * 2))

def draw_simulation_setup():
    screen.fill(BG_COLOR)
    title = title_font.render("Setup Simulasi", True, (100, 0, 0))
    screen.blit(title, (SCREEN_SIZE//2 - title.get_width()//2, MARGIN * 2))

def draw_simulation_running(current_game, total_games, player_x_name, player_o_name, 
                            x_wins, o_wins, draws, elapsed_time):
    screen.fill(BG_COLOR)
    
    y = 100
    line_spacing = 35
    
    # Title
    title = title_font.render("SIMULASI BERJALAN...", True, (120, 20, 20))
    screen.blit(title, (SCREEN_SIZE//2 - title.get_width()//2, y))
    y += 80
    
    # Match info
    match_text = font.render(f"{player_x_name} vs {player_o_name}", True, (0, 0, 0))
    screen.blit(match_text, (SCREEN_SIZE//2 - match_text.get_width()//2, y))
    y += line_spacing + 20
    
    # Progress
    progress_text = font.render(f"Game {current_game} / {total_games}", True, (0, 0, 0))
    screen.blit(progress_text, (SCREEN_SIZE//2 - progress_text.get_width()//2, y))
    y += line_spacing
    
    # Progress bar
    bar_width = 400
    bar_height = 30
    bar_x = SCREEN_SIZE//2 - bar_width//2
    bar_y = y
    
    pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
    if total_games > 0:
        progress = current_game / total_games
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, (52, 152, 219), (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)
    
    y += bar_height + 30
    
    # Current results
    results_title = font.render("Hasil Sementara:", True, (0, 0, 0))
    screen.blit(results_title, (SCREEN_SIZE//2 - results_title.get_width()//2, y))
    y += line_spacing + 10
    
    x_text = font.render(f"Player X: {x_wins} menang", True, (0, 0, 0))
    screen.blit(x_text, (SCREEN_SIZE//2 - 150, y))
    y += line_spacing
    
    o_text = font.render(f"Player O: {o_wins} menang", True, (0, 0, 0))
    screen.blit(o_text, (SCREEN_SIZE//2 - 150, y))
    y += line_spacing
    
    draw_text = font.render(f"Draw: {draws} seri", True, (0, 0, 0))
    screen.blit(draw_text, (SCREEN_SIZE//2 - 150, y))
    y += line_spacing + 20
    
    # Time
    time_text = font.render(f"Waktu: {elapsed_time:.1f}s", True, (0, 0, 0))
    screen.blit(time_text, (SCREEN_SIZE//2 - time_text.get_width()//2, y))
    
    pygame.display.flip()

def center_buttons_x(num_buttons, button_width, gap):
    total_width = num_buttons * button_width + (num_buttons - 1) * gap
    start_x = SCREEN_SIZE // 2 - total_width // 2
    return start_x

def main():
    game_state = STATE_MENU
    mode = None  # "user_vs_agent" or "agent_vs_agent"
    
    # Agent selections
    player_x_agent = None  # "human", "minimax", "mcts"
    player_x_level = None
    player_o_agent = None
    player_o_level = None
    
    # Game variables
    board = None
    current_player = PLAYER_X
    game_over = False
    winner = None
    
    # Simulation variables
    sim_num_games = 10
    sim_current_game = 0
    sim_results = []
    sim_durations = []
    sim_start_time = 0
    sim_output_file = ""
    
    # UI Elements
    menu_buttons = create_menu_buttons()

    agent_btn_w = 130
    agent_btn_h = 45
    agent_gap = 20

    agent_start_x = center_buttons_x(2, agent_btn_w, agent_gap)
    agent_y = SCREEN_SIZE // 2 - 80

    agent_buttons = [
        Button(agent_start_x, agent_y, agent_btn_w, agent_btn_h, "Minimax", "minimax"),
        Button(agent_start_x + agent_btn_w + agent_gap, agent_y, agent_btn_w, agent_btn_h, "MCTS", "mcts"),
    ]
    
    level_btn_w = 100
    level_btn_h = 40
    level_gap = 20

    level_start_x = center_buttons_x(3, level_btn_w, level_gap)
    level_y = SCREEN_SIZE // 2 + 10

    level_buttons = [
        Button(level_start_x, level_y, level_btn_w, level_btn_h, "Level 1", 1),
        Button(level_start_x + (level_btn_w + level_gap), level_y, level_btn_w, level_btn_h, "Level 2", 2),
        Button(level_start_x + 2 * (level_btn_w + level_gap), level_y, level_btn_w, level_btn_h, "Level 3", 3),
    ]
    
    confirm_button = Button(SCREEN_SIZE//2 - 75, SCREEN_SIZE//2 + 100, 150, 45, "Mulai", "confirm")
    back_button = Button(MARGIN, SCREEN_SIZE + 50, 100, 40, "Kembali", "back")
    
    # Simulation input field
    num_games_input = InputField(SCREEN_SIZE//2 - 75, SCREEN_SIZE//2 + 80, 150, 40)
    
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
                        elif btn.value == "stats_viewer":
                            launch_stats_viewer()
                        elif btn.value == "simulation":
                            game_state = STATE_SETUP_SIMULATION
                            player_x_agent = None
                            player_x_level = None
                            player_o_agent = None
                            player_o_level = None
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
                        player_x_level = None
                        for b in agent_buttons:
                            b.selected = (b.value == player_x_agent)
                
                # Select Player X level
                for btn in level_buttons:
                    if btn.handle_event(event):
                        player_x_level = btn.value
                        for b in level_buttons:
                            b.selected = (b.value == player_x_level)
                
                # Confirm and go to select Player O
                if confirm_button.handle_event(event) and player_x_agent and player_x_level is not None:
                    game_state = STATE_SELECT_OPPONENT

                
                if back_button.handle_event(event):
                    game_state = STATE_MENU
                    player_x_agent = None
            
            # === SELECT OPPONENT ===
            elif game_state == STATE_SELECT_OPPONENT:
                for btn in agent_buttons:
                    if btn.handle_event(event):
                        player_o_agent = btn.value
                        player_o_level = None
                        for b in agent_buttons:
                            b.selected = (b.value == player_o_agent)
                
                for btn in level_buttons:
                    if btn.handle_event(event):
                        player_o_level = btn.value
                        for b in level_buttons:
                            b.selected = (b.value == player_o_level)
                
                if confirm_button.handle_event(event) and player_o_agent and player_o_level is not None:
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
            
            # === SETUP SIMULATION STATE ===
            elif game_state == STATE_SETUP_SIMULATION:
                num_games_input.handle_event(event)
                
                # Select Player X agent
                for btn in agent_buttons:
                    if btn.handle_event(event):
                        player_x_agent = btn.value
                        player_x_level = None
                        for b in agent_buttons:
                            b.selected = (b.value == player_x_agent)
                
                # Select Player X level
                for btn in level_buttons:
                    if btn.handle_event(event):
                        player_x_level = btn.value
                        for b in level_buttons:
                            b.selected = (b.value == player_x_level)
                
                # Continue to Player O selection if X is complete
                if confirm_button.handle_event(event) and player_x_agent and player_x_level is not None:
                    # Move to select Player O
                    for b in agent_buttons:
                        b.selected = False
                    for b in level_buttons:
                        b.selected = False
                    player_o_agent = None
                    player_o_level = None
                    game_state = "setup_simulation_player_o"
                
                if back_button.handle_event(event):
                    game_state = STATE_MENU
                    player_x_agent = None
                    player_x_level = None
            
            # === SETUP SIMULATION PLAYER O ===
            elif game_state == "setup_simulation_player_o":
                num_games_input.handle_event(event)
                
                for btn in agent_buttons:
                    if btn.handle_event(event):
                        player_o_agent = btn.value
                        player_o_level = None
                        for b in agent_buttons:
                            b.selected = (b.value == player_o_agent)
                
                for btn in level_buttons:
                    if btn.handle_event(event):
                        player_o_level = btn.value
                        for b in level_buttons:
                            b.selected = (b.value == player_o_level)
                
                if confirm_button.handle_event(event) and player_o_agent and player_o_level is not None:
                    # Start simulation
                    sim_num_games = num_games_input.get_value()
                    sim_current_game = 0
                    sim_results = []
                    sim_durations = []
                    sim_start_time = time.time()
                    game_state = STATE_RUNNING_SIMULATION
                
                if back_button.handle_event(event):
                    game_state = STATE_SETUP_SIMULATION
                    player_o_agent = None
                    player_o_level = None
                    for b in agent_buttons:
                        b.selected = (b.value == player_x_agent)
                    for b in level_buttons:
                        b.selected = (b.value == player_x_level)
            
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
            screen.blit(label, (SCREEN_SIZE//2 - label.get_width()//2, SCREEN_SIZE//2 - 180))
            
            for btn in agent_buttons:
                btn.draw(screen)
            
            if player_x_agent:
                label2_y = LABEL_LEVEL_Y
                label2 = font.render("Pilih Level:", True, (0, 0, 0))
                screen.blit(
                    label2,
                    (SCREEN_SIZE // 2 - label2.get_width() // 2, label2_y)
                )
                for i, btn in enumerate(level_buttons):
                    btn.rect.y = label2_y + 35
                    btn.draw(screen)
                
                confirm_button.draw(screen)
            back_button.draw(screen)
        
        elif game_state == STATE_SELECT_OPPONENT:
            title_text = "Pilih Agent Lawan" if mode == "user_vs_agent" else "Pilih Agent untuk Player O"
            draw_agent_selection_menu(title_text)
            
            label = font.render("Pilih Agent:", True, (0, 0, 0))
            screen.blit(label, (SCREEN_SIZE//2 - label.get_width()//2, SCREEN_SIZE//2 - 180))
            
            for btn in agent_buttons:
                btn.draw(screen)
            
            if player_o_agent:
                label2 = font.render("Pilih Level:", True, (0, 0, 0))
                screen.blit(label2, (SCREEN_SIZE//2 - label2.get_width()//2, LABEL_LEVEL_Y))

                for btn in level_buttons:
                    btn.rect.y = LABEL_LEVEL_Y + LEVEL_BUTTON_OFFSET_Y
                    btn.draw(screen)
                confirm_button.rect.y = CONFIRM_BUTTON_Y
                confirm_button.draw(screen)
            
            back_button.draw(screen)
        
        elif game_state == STATE_SETUP_SIMULATION:
            draw_simulation_setup()
            
            label = font.render("Pilih Agent Player X:", True, (0, 0, 0))
            screen.blit(label, (SCREEN_SIZE//2 - label.get_width()//2, SCREEN_SIZE//2 - 180))
            
            for btn in agent_buttons:
                btn.rect.y = SCREEN_SIZE // 2 - 120
                btn.draw(screen)
            
            if player_x_agent:
                label2 = font.render("Pilih Level Player X:", True, (0, 0, 0))
                screen.blit(label2, (SCREEN_SIZE//2 - label2.get_width()//2, SCREEN_SIZE//2 - 30))
                
                for btn in level_buttons:
                    btn.rect.y = SCREEN_SIZE // 2 + 10
                    btn.draw(screen)
                
                # Input jumlah game
                label3 = font.render("Jumlah Game:", True, (0, 0, 0))
                screen.blit(label3, (SCREEN_SIZE//2 - label3.get_width()//2, SCREEN_SIZE//2 + 60))
                num_games_input.draw(screen)
                
                confirm_button.rect.y = SCREEN_SIZE//2 + 140
                confirm_button.text = "Lanjut"
                confirm_button.draw(screen)
            
            back_button.draw(screen)
        
        elif game_state == "setup_simulation_player_o":
            draw_simulation_setup()
            
            label = font.render("Pilih Agent Player O:", True, (0, 0, 0))
            screen.blit(label, (SCREEN_SIZE//2 - label.get_width()//2, SCREEN_SIZE//2 - 180))
            
            for btn in agent_buttons:
                btn.rect.y = SCREEN_SIZE // 2 - 120
                btn.draw(screen)
            
            if player_o_agent:
                label2 = font.render("Pilih Level Player O:", True, (0, 0, 0))
                screen.blit(label2, (SCREEN_SIZE//2 - label2.get_width()//2, SCREEN_SIZE//2 - 30))
                
                for btn in level_buttons:
                    btn.rect.y = SCREEN_SIZE // 2 + 10
                    btn.draw(screen)
                
                # Show configuration summary
                label3 = font.render(f"Jumlah Game: {num_games_input.get_value()}", True, (0, 0, 0))
                screen.blit(label3, (SCREEN_SIZE//2 - label3.get_width()//2, SCREEN_SIZE//2 + 80))
                
                label4 = font.render(f"Player X: {describe_agent(player_x_agent, player_x_level)}", True, (0, 0, 0))
                screen.blit(label4, (SCREEN_SIZE//2 - label4.get_width()//2, SCREEN_SIZE//2 + 110))
                
                confirm_button.rect.y = SCREEN_SIZE//2 + 150
                confirm_button.text = "Mulai"
                confirm_button.draw(screen)
            
            back_button.draw(screen)
        
        elif game_state == STATE_RUNNING_SIMULATION:
            # Initialize simulation if just started
            if sim_current_game == 0 and not sim_results:
                sim_start_time = time.time()
            
            # Run one game at a time
            if sim_current_game < sim_num_games:
                # Define progress callback
                def update_progress(current, total, x_w, o_w, d, elapsed):
                    player_x_name = describe_agent(player_x_agent, player_x_level)
                    player_o_name = describe_agent(player_o_agent, player_o_level)
                    draw_simulation_running(current, total, player_x_name, player_o_name,
                                          x_w, o_w, d, elapsed)
                
                # Run the entire simulation
                sim_output_file = run_simulation_gui(
                    player_x_agent, player_x_level,
                    player_o_agent, player_o_level,
                    sim_num_games,
                    callback_progress=update_progress
                )
                
                # Mark as complete
                sim_current_game = sim_num_games
                
                # Show completion message
                screen.fill(BG_COLOR)
                complete_text = title_font.render("SIMULASI SELESAI!", True, (0, 150, 0))
                screen.blit(complete_text, (SCREEN_SIZE//2 - complete_text.get_width()//2, SCREEN_SIZE//2 - 50))
                
                info_text = font.render(f"Hasil disimpan: {os.path.basename(sim_output_file)}", True, (0, 0, 0))
                screen.blit(info_text, (SCREEN_SIZE//2 - info_text.get_width()//2, SCREEN_SIZE//2 + 20))
                
                wait_text = font.render("Membuka visualisasi statistik...", True, (0, 0, 0))
                screen.blit(wait_text, (SCREEN_SIZE//2 - wait_text.get_width()//2, SCREEN_SIZE//2 + 60))
                
                pygame.display.flip()
                pygame.time.wait(2000)
                
                # Launch stats viewer with the result file
                launch_stats_viewer(sim_output_file)
                pygame.time.wait(1000)
                
                # Return to menu
                game_state = STATE_MENU
                sim_current_game = 0
                sim_results = []
                sim_durations = []
        
        elif game_state == STATE_GAME:
            label_x = (
                "Human (X)"
                if player_x_agent == "human"
                else f"{describe_agent(player_x_agent, player_x_level)} (X)"
                if player_x_level is not None
                else "Agent (X)"
            )
            label_o = (
                f"{describe_agent(player_o_agent, player_o_level)} (O)"
                if player_o_level is not None
                else "Agent (O)"
            )

            draw_board(board, label_x, label_o, "")

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
        
        # Only flip if not in running simulation (it has its own flip)
        if game_state != STATE_RUNNING_SIMULATION:
            pygame.display.flip()

if __name__ == "__main__":
    main()