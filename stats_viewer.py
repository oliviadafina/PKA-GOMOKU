"""
GUI untuk menampilkan statistik simulasi dengan grafik dan perbandingan
"""
import pygame
import sys
import os
from tkinter import Tk, filedialog
from stats_parser import parse_simulation_file, SimulationStats, compare_stats
from typing import Optional, List


# Inisialisasi pygame
pygame.init()

# Konstanta
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
BG_COLOR = (245, 245, 250)
TEXT_COLOR = (30, 30, 30)
ACCENT_COLOR = (70, 130, 180)
BUTTON_COLOR = (100, 149, 237)
BUTTON_HOVER_COLOR = (65, 105, 225)
GRAPH_BG_COLOR = (255, 255, 255)
GRID_COLOR = (220, 220, 220)
BAR_COLOR_1 = (52, 152, 219)
BAR_COLOR_2 = (231, 76, 60)
BAR_COLOR_3 = (46, 204, 113)
LINE_COLOR_1 = (52, 152, 219)
LINE_COLOR_2 = (231, 76, 60)

# Font
TITLE_FONT = None
NORMAL_FONT = None
SMALL_FONT = None
BUTTON_FONT = None


def init_fonts():
    """Inisialisasi font"""
    global TITLE_FONT, NORMAL_FONT, SMALL_FONT, BUTTON_FONT
    TITLE_FONT = pygame.font.Font(None, 36)
    NORMAL_FONT = pygame.font.Font(None, 24)
    SMALL_FONT = pygame.font.Font(None, 20)
    BUTTON_FONT = pygame.font.Font(None, 28)


class Button:
    """Class untuk tombol interaktif"""
    
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        
    def draw(self, screen):
        """Gambar tombol"""
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=8)
        
        text_surface = BUTTON_FONT.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.callback()
                return True
        return False


class StatsViewer:
    """Main class untuk GUI statistik viewer"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Gomoku - Statistik Viewer")
        self.clock = pygame.time.Clock()
        init_fonts()
        
        # Data
        self.stats1: Optional[SimulationStats] = None
        self.stats2: Optional[SimulationStats] = None
        self.file1_path = ""
        self.file2_path = ""
        
        # UI mode
        self.comparison_mode = False
        self.show_graphs = True
        
        # Buttons
        self.buttons = []
        self.create_buttons()
        
    def create_buttons(self):
        """Buat semua tombol"""
        button_y = 20
        button_height = 45
        button_spacing = 10
        button_width = 180
        
        x = 20
        self.buttons.append(Button(x, button_y, button_width, button_height, 
                                   "Load File 1", self.load_file_1))
        
        x += button_width + button_spacing
        self.buttons.append(Button(x, button_y, button_width, button_height, 
                                   "Load File 2", self.load_file_2))
        
        x += button_width + button_spacing
        self.buttons.append(Button(x, button_y, button_width, button_height, 
                                   "Toggle Mode", self.toggle_comparison_mode))
        
        x += button_width + button_spacing
        self.buttons.append(Button(x, button_y, button_width, button_height, 
                                   "Toggle Grafik", self.toggle_graphs))
        
        x += button_width + button_spacing
        self.buttons.append(Button(x, button_y, button_width, button_height, 
                                   "Clear", self.clear_all))
        
        x += button_width + button_spacing
        self.buttons.append(Button(x, button_y, button_width, button_height, 
                                   "Keluar", self.exit_viewer))
    
    def load_file_1(self):
        """Load file statistik pertama"""
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        initial_dir = os.path.join(os.path.dirname(__file__), "hasil")
        filepath = filedialog.askopenfilename(
            title="Pilih File Simulasi 1",
            initialdir=initial_dir if os.path.exists(initial_dir) else ".",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        root.destroy()
        
        if filepath:
            self.stats1 = parse_simulation_file(filepath)
            self.file1_path = os.path.basename(filepath)
            if self.stats1 is None:
                print(f"Gagal parsing file: {filepath}")
    
    def load_file_2(self):
        """Load file statistik kedua untuk perbandingan"""
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        initial_dir = os.path.join(os.path.dirname(__file__), "hasil")
        filepath = filedialog.askopenfilename(
            title="Pilih File Simulasi 2",
            initialdir=initial_dir if os.path.exists(initial_dir) else ".",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        root.destroy()
        
        if filepath:
            self.stats2 = parse_simulation_file(filepath)
            self.file2_path = os.path.basename(filepath)
            if self.stats2 is None:
                print(f"Gagal parsing file: {filepath}")
    
    def toggle_comparison_mode(self):
        """Toggle antara mode single dan comparison"""
        self.comparison_mode = not self.comparison_mode
    
    def toggle_graphs(self):
        """Toggle tampilan grafik"""
        self.show_graphs = not self.show_graphs
    
    def clear_all(self):
        """Clear semua data"""
        self.stats1 = None
        self.stats2 = None
        self.file1_path = ""
        self.file2_path = ""
        self.comparison_mode = False
    
    def exit_viewer(self):
        """Keluar dari stats viewer"""
        pygame.quit()
        sys.exit()
    
    def draw_bar_chart(self, screen, x, y, width, height, data, labels, colors, title):
        """
        Gambar bar chart
        
        Args:
            screen: Surface pygame
            x, y: Posisi chart
            width, height: Ukuran chart
            data: List of values
            labels: List of labels
            colors: List of colors
            title: Judul chart
        """
        # Background
        pygame.draw.rect(screen, GRAPH_BG_COLOR, (x, y, width, height))
        pygame.draw.rect(screen, GRID_COLOR, (x, y, width, height), 2)
        
        # Title
        title_surface = NORMAL_FONT.render(title, True, TEXT_COLOR)
        screen.blit(title_surface, (x + 10, y + 10))
        
        if not data or sum(data) == 0:
            no_data_text = SMALL_FONT.render("No data", True, TEXT_COLOR)
            screen.blit(no_data_text, (x + width//2 - 30, y + height//2))
            return
        
        # Chart area
        chart_x = x + 50
        chart_y = y + 50
        chart_width = width - 60
        chart_height = height - 100
        
        # Draw bars
        bar_width = chart_width // len(data)
        max_value = max(data) if data else 1
        
        for i, (value, label, color) in enumerate(zip(data, labels, colors)):
            bar_x = chart_x + i * bar_width + 10
            bar_height = int((value / max_value) * chart_height) if max_value > 0 else 0
            bar_y = chart_y + chart_height - bar_height
            
            # Bar
            pygame.draw.rect(screen, color, 
                           (bar_x, bar_y, bar_width - 20, bar_height), 
                           border_radius=4)
            
            # Value text
            value_text = SMALL_FONT.render(str(int(value)), True, TEXT_COLOR)
            text_rect = value_text.get_rect(center=(bar_x + (bar_width - 20)//2, bar_y - 15))
            screen.blit(value_text, text_rect)
            
            # Label
            label_surface = SMALL_FONT.render(label, True, TEXT_COLOR)
            label_rect = label_surface.get_rect(
                center=(bar_x + (bar_width - 20)//2, chart_y + chart_height + 20)
            )
            screen.blit(label_surface, label_rect)
    
    def draw_line_chart(self, screen, x, y, width, height, data, title, color):
        """
        Gambar line chart untuk durasi per game
        
        Args:
            screen: Surface pygame
            x, y: Posisi chart
            width, height: Ukuran chart
            data: List of (game_num, duration) tuples
            title: Judul chart
            color: Warna garis
        """
        # Background
        pygame.draw.rect(screen, GRAPH_BG_COLOR, (x, y, width, height))
        pygame.draw.rect(screen, GRID_COLOR, (x, y, width, height), 2)
        
        # Title
        title_surface = NORMAL_FONT.render(title, True, TEXT_COLOR)
        screen.blit(title_surface, (x + 10, y + 10))
        
        if not data or len(data) < 2:
            no_data_text = SMALL_FONT.render("No data", True, TEXT_COLOR)
            screen.blit(no_data_text, (x + width//2 - 30, y + height//2))
            return
        
        # Chart area
        chart_x = x + 50
        chart_y = y + 50
        chart_width = width - 100
        chart_height = height - 100
        
        # Find max value for scaling
        max_duration = max(d[1] for d in data) if data else 1
        
        # Draw grid lines
        num_grid_lines = 5
        for i in range(num_grid_lines + 1):
            grid_y = chart_y + (chart_height * i // num_grid_lines)
            pygame.draw.line(screen, GRID_COLOR, 
                           (chart_x, grid_y), 
                           (chart_x + chart_width, grid_y), 1)
            
            # Y-axis labels
            value = max_duration * (1 - i / num_grid_lines)
            label = SMALL_FONT.render(f"{value:.0f}s", True, TEXT_COLOR)
            screen.blit(label, (chart_x - 45, grid_y - 8))
        
        # Draw line
        points = []
        for i, (game_num, duration) in enumerate(data):
            px = chart_x + (i * chart_width // (len(data) - 1))
            py = chart_y + chart_height - int((duration / max_duration) * chart_height)
            points.append((px, py))
        
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, 3)
            
            # Draw points
            for px, py in points:
                pygame.draw.circle(screen, color, (px, py), 5)
    
    def draw_comparison_bar_chart(self, screen, x, y, width, height, 
                                  data1, data2, labels, title):
        """
        Gambar bar chart perbandingan (side by side)
        """
        # Background
        pygame.draw.rect(screen, GRAPH_BG_COLOR, (x, y, width, height))
        pygame.draw.rect(screen, GRID_COLOR, (x, y, width, height), 2)
        
        # Title
        title_surface = NORMAL_FONT.render(title, True, TEXT_COLOR)
        screen.blit(title_surface, (x + 10, y + 10))
        
        if not data1 and not data2:
            no_data_text = SMALL_FONT.render("No data", True, TEXT_COLOR)
            screen.blit(no_data_text, (x + width//2 - 30, y + height//2))
            return
        
        # Chart area
        chart_x = x + 50
        chart_y = y + 50
        chart_width = width - 60
        chart_height = height - 100
        
        # Draw bars
        num_categories = len(labels)
        category_width = chart_width // num_categories
        bar_width = (category_width - 20) // 2
        
        max_value = max(max(data1) if data1 else 0, max(data2) if data2 else 0)
        if max_value == 0:
            max_value = 1
        
        for i, label in enumerate(labels):
            cat_x = chart_x + i * category_width
            
            # Bar 1
            if data1:
                value1 = data1[i]
                bar_height1 = int((value1 / max_value) * chart_height)
                bar_y1 = chart_y + chart_height - bar_height1
                pygame.draw.rect(screen, BAR_COLOR_1, 
                               (cat_x + 5, bar_y1, bar_width, bar_height1),
                               border_radius=4)
                # Value
                val_text = SMALL_FONT.render(str(int(value1)), True, TEXT_COLOR)
                screen.blit(val_text, (cat_x + 5, bar_y1 - 20))
            
            # Bar 2
            if data2:
                value2 = data2[i]
                bar_height2 = int((value2 / max_value) * chart_height)
                bar_y2 = chart_y + chart_height - bar_height2
                pygame.draw.rect(screen, BAR_COLOR_2, 
                               (cat_x + bar_width + 10, bar_y2, bar_width, bar_height2),
                               border_radius=4)
                # Value
                val_text = SMALL_FONT.render(str(int(value2)), True, TEXT_COLOR)
                screen.blit(val_text, (cat_x + bar_width + 10, bar_y2 - 20))
            
            # Label
            label_surface = SMALL_FONT.render(label, True, TEXT_COLOR)
            label_rect = label_surface.get_rect(
                center=(cat_x + category_width//2, chart_y + chart_height + 20)
            )
            screen.blit(label_surface, label_rect)
        
        # Legend
        legend_x = x + width - 150
        legend_y = y + 15
        pygame.draw.rect(screen, BAR_COLOR_1, (legend_x, legend_y, 20, 20))
        text1 = SMALL_FONT.render("File 1", True, TEXT_COLOR)
        screen.blit(text1, (legend_x + 25, legend_y))
        
        pygame.draw.rect(screen, BAR_COLOR_2, (legend_x + 70, legend_y, 20, 20))
        text2 = SMALL_FONT.render("File 2", True, TEXT_COLOR)
        screen.blit(text2, (legend_x + 95, legend_y))
    
    def draw_stats_text(self, screen, stats: SimulationStats, x, y, width, height):
        """Gambar statistik dalam bentuk teks"""
        # Background
        pygame.draw.rect(screen, GRAPH_BG_COLOR, (x, y, width, height))
        pygame.draw.rect(screen, GRID_COLOR, (x, y, width, height), 2)
        
        # Draw text
        text_y = y + 15
        line_height = 25
        
        lines = [
            f"Tanggal: {stats.tanggal}",
            f"Player X: {stats.player_x}",
            f"Player O: {stats.player_o}",
            f"Jumlah Game: {stats.jumlah_game}",
            "",
            "=== HASIL ===",
            f"Player X: {stats.x_wins} menang ({stats.x_win_rate:.1f}%)",
            f"Player O: {stats.o_wins} menang ({stats.o_win_rate:.1f}%)",
            f"Draw: {stats.draws} seri ({stats.draw_rate:.1f}%)",
            "",
            "=== WAKTU ===",
            f"Total: {stats.total_waktu:.2f} detik",
            f"Rata-rata: {stats.rata_waktu:.2f} detik/game",
            f"Tercepat: {stats.waktu_tercepat:.2f}s (Game #{stats.game_tercepat_idx})",
            f"Terlambat: {stats.waktu_terlambat:.2f}s (Game #{stats.game_terlambat_idx})",
        ]
        
        for line in lines:
            if line.startswith("==="):
                text_surface = NORMAL_FONT.render(line, True, ACCENT_COLOR)
            else:
                text_surface = SMALL_FONT.render(line, True, TEXT_COLOR)
            screen.blit(text_surface, (x + 15, text_y))
            text_y += line_height
    
    def draw_comparison_text(self, screen, x, y, width, height):
        """Gambar perbandingan dalam bentuk teks"""
        if not self.stats1 or not self.stats2:
            return
        
        # Background
        pygame.draw.rect(screen, GRAPH_BG_COLOR, (x, y, width, height))
        pygame.draw.rect(screen, GRID_COLOR, (x, y, width, height), 2)
        
        text_y = y + 15
        line_height = 25
        
        lines = [
            "=== PERBANDINGAN ===",
            f"File 1: {self.file1_path}",
            f"File 2: {self.file2_path}",
            "",
            "HASIL:",
            f"Games: {self.stats1.jumlah_game} vs {self.stats2.jumlah_game}",
            f"X Wins: {self.stats1.x_wins} ({self.stats1.x_win_rate:.1f}%) vs {self.stats2.x_wins} ({self.stats2.x_win_rate:.1f}%)",
            f"O Wins: {self.stats1.o_wins} ({self.stats1.o_win_rate:.1f}%) vs {self.stats2.o_wins} ({self.stats2.o_win_rate:.1f}%)",
            f"Draws: {self.stats1.draws} vs {self.stats2.draws}",
            "",
            "WAKTU:",
            f"Total: {self.stats1.total_waktu:.1f}s vs {self.stats2.total_waktu:.1f}s",
            f"Rata-rata: {self.stats1.rata_waktu:.1f}s vs {self.stats2.rata_waktu:.1f}s",
            f"Tercepat: {self.stats1.waktu_tercepat:.1f}s vs {self.stats2.waktu_tercepat:.1f}s",
            f"Terlambat: {self.stats1.waktu_terlambat:.1f}s vs {self.stats2.waktu_terlambat:.1f}s",
        ]
        
        for line in lines:
            if line.startswith("===") or line.endswith(":"):
                text_surface = NORMAL_FONT.render(line, True, ACCENT_COLOR)
            else:
                text_surface = SMALL_FONT.render(line, True, TEXT_COLOR)
            screen.blit(text_surface, (x + 15, text_y))
            text_y += line_height
    
    def draw(self):
        """Gambar seluruh UI"""
        self.screen.fill(BG_COLOR)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw file info
        info_y = 80
        if self.file1_path:
            text = SMALL_FONT.render(f"File 1: {self.file1_path}", True, TEXT_COLOR)
            self.screen.blit(text, (20, info_y))
        
        if self.file2_path:
            text = SMALL_FONT.render(f"File 2: {self.file2_path}", True, TEXT_COLOR)
            self.screen.blit(text, (20, info_y + 25))
        
        # Draw mode indicator
        mode_text = "Mode: Perbandingan" if self.comparison_mode else "Mode: Single"
        mode_surface = NORMAL_FONT.render(mode_text, True, ACCENT_COLOR)
        self.screen.blit(mode_surface, (WINDOW_WIDTH - 250, 30))
        
        # Content area starts at y=120
        content_y = 120
        content_height = WINDOW_HEIGHT - content_y - 20
        
        if self.comparison_mode and self.stats1 and self.stats2:
            # Comparison mode
            if self.show_graphs:
                # Top row: comparison bar charts
                chart_height = content_height // 2 - 10
                
                # Win comparison
                self.draw_comparison_bar_chart(
                    self.screen, 20, content_y, 
                    WINDOW_WIDTH//2 - 30, chart_height,
                    [self.stats1.x_wins, self.stats1.o_wins, self.stats1.draws],
                    [self.stats2.x_wins, self.stats2.o_wins, self.stats2.draws],
                    ["X Wins", "O Wins", "Draws"],
                    "Perbandingan Kemenangan"
                )
                
                # Time comparison
                self.draw_comparison_bar_chart(
                    self.screen, WINDOW_WIDTH//2 + 10, content_y,
                    WINDOW_WIDTH//2 - 30, chart_height,
                    [self.stats1.rata_waktu, self.stats1.waktu_tercepat, self.stats1.waktu_terlambat],
                    [self.stats2.rata_waktu, self.stats2.waktu_tercepat, self.stats2.waktu_terlambat],
                    ["Rata-rata", "Tercepat", "Terlambat"],
                    "Perbandingan Waktu (detik)"
                )
                
                # Bottom: comparison text
                text_y = content_y + chart_height + 20
                self.draw_comparison_text(
                    self.screen, 20, text_y,
                    WINDOW_WIDTH - 40, content_height - chart_height - 20
                )
            else:
                # Text only comparison
                self.draw_comparison_text(
                    self.screen, 20, content_y,
                    WINDOW_WIDTH - 40, content_height
                )
        
        elif self.stats1:
            # Single file mode
            if self.show_graphs:
                # Layout: 2 charts on top, stats text on bottom
                chart_width = WINDOW_WIDTH//2 - 30
                chart_height = content_height * 2 // 3 - 10
                
                # Win rate chart
                win_data = [self.stats1.x_wins, self.stats1.o_wins, self.stats1.draws]
                win_labels = ["X Wins", "O Wins", "Draws"]
                win_colors = [BAR_COLOR_1, BAR_COLOR_2, BAR_COLOR_3]
                
                self.draw_bar_chart(
                    self.screen, 20, content_y, chart_width, chart_height,
                    win_data, win_labels, win_colors,
                    "Hasil Pertandingan"
                )
                
                # Duration line chart
                duration_data = [(g['game_num'], g['duration']) 
                                for g in self.stats1.game_details]
                self.draw_line_chart(
                    self.screen, WINDOW_WIDTH//2 + 10, content_y,
                    chart_width, chart_height,
                    duration_data, "Durasi Per Game", LINE_COLOR_1
                )
                
                # Stats text
                text_y = content_y + chart_height + 20
                text_height = content_height - chart_height - 20
                self.draw_stats_text(
                    self.screen, self.stats1, 20, text_y,
                    WINDOW_WIDTH - 40, text_height
                )
            else:
                # Text only
                self.draw_stats_text(
                    self.screen, self.stats1, 20, content_y,
                    WINDOW_WIDTH - 40, content_height
                )
        else:
            # No data loaded
            text = TITLE_FONT.render("Silakan load file simulasi", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle button events
                for button in self.buttons:
                    button.handle_event(event)
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """Entry point"""
    viewer = StatsViewer()
    viewer.run()


if __name__ == "__main__":
    main()
