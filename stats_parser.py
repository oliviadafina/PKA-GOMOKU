"""
Module untuk parsing file hasil simulasi Gomoku
"""
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class SimulationStats:
    """Class untuk menyimpan statistik simulasi"""
    
    def __init__(self):
        self.tanggal = ""
        self.player_x = ""
        self.player_o = ""
        self.jumlah_game = 0
        self.verbose_mode = False
        
        # Ringkasan
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        self.x_win_rate = 0.0
        self.o_win_rate = 0.0
        self.draw_rate = 0.0
        
        # Waktu
        self.total_waktu = 0.0
        self.rata_waktu = 0.0
        self.waktu_tercepat = 0.0
        self.waktu_terlambat = 0.0
        self.game_tercepat_idx = 0
        self.game_terlambat_idx = 0
        
        # Detail per game
        self.game_details: List[Dict] = []
        
    def get_summary_text(self) -> str:
        """Generate summary text"""
        return f"""
=== STATISTIK SIMULASI ===
Tanggal: {self.tanggal}
Player X: {self.player_x}
Player O: {self.player_o}
Jumlah Game: {self.jumlah_game}

=== HASIL ===
Player X: {self.x_wins} menang ({self.x_win_rate:.1f}%)
Player O: {self.o_wins} menang ({self.o_win_rate:.1f}%)
Draw: {self.draws} seri ({self.draw_rate:.1f}%)

=== WAKTU ===
Total Waktu: {self.total_waktu:.2f} detik
Rata-rata: {self.rata_waktu:.2f} detik/game
Tercepat: {self.waktu_tercepat:.2f} detik (Game #{self.game_tercepat_idx})
Terlambat: {self.waktu_terlambat:.2f} detik (Game #{self.game_terlambat_idx})
"""


def parse_simulation_file(filepath: str) -> Optional[SimulationStats]:
    """
    Parse file hasil simulasi dan return SimulationStats object
    
    Args:
        filepath: Path ke file txt hasil simulasi
        
    Returns:
        SimulationStats object atau None jika parsing gagal
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stats = SimulationStats()
        
        # Parse header info
        tanggal_match = re.search(r'Tanggal\s*:\s*(.+)', content)
        if tanggal_match:
            stats.tanggal = tanggal_match.group(1).strip()
        
        player_x_match = re.search(r'Player X\s*:\s*(.+)', content)
        if player_x_match:
            stats.player_x = player_x_match.group(1).strip()
        
        player_o_match = re.search(r'Player O\s*:\s*(.+)', content)
        if player_o_match:
            stats.player_o = player_o_match.group(1).strip()
        
        jumlah_game_match = re.search(r'Jumlah Game\s*:\s*(\d+)', content)
        if jumlah_game_match:
            stats.jumlah_game = int(jumlah_game_match.group(1))
        
        verbose_match = re.search(r'Verbose Mode\s*:\s*(\w+)', content)
        if verbose_match:
            stats.verbose_mode = verbose_match.group(1).strip().lower() == 'true'
        
        # Parse ringkasan
        x_wins_match = re.search(r'Player X[^:]*:\s*(\d+)\s*menang\s*\(([0-9.]+)%\)', content)
        if x_wins_match:
            stats.x_wins = int(x_wins_match.group(1))
            stats.x_win_rate = float(x_wins_match.group(2))
        
        o_wins_match = re.search(r'Player O[^:]*:\s*(\d+)\s*menang\s*\(([0-9.]+)%\)', content)
        if o_wins_match:
            stats.o_wins = int(o_wins_match.group(1))
            stats.o_win_rate = float(o_wins_match.group(2))
        
        draw_match = re.search(r'Draw\s*:\s*(\d+)\s*seri\s*\(([0-9.]+)%\)', content)
        if draw_match:
            stats.draws = int(draw_match.group(1))
            stats.draw_rate = float(draw_match.group(2))
        
        # Parse waktu
        total_waktu_match = re.search(r'Total Waktu\s*:\s*([0-9.]+)\s*detik', content)
        if total_waktu_match:
            stats.total_waktu = float(total_waktu_match.group(1))
        
        rata_waktu_match = re.search(r'Rata-rata per Game\s*:\s*([0-9.]+)\s*detik', content)
        if rata_waktu_match:
            stats.rata_waktu = float(rata_waktu_match.group(1))
        
        tercepat_match = re.search(r'Game Tercepat\s*:\s*([0-9.]+)\s*detik\s*\(Game\s*#(\d+)\)', content)
        if tercepat_match:
            stats.waktu_tercepat = float(tercepat_match.group(1))
            stats.game_tercepat_idx = int(tercepat_match.group(2))
        
        terlambat_match = re.search(r'Game Terlambat\s*:\s*([0-9.]+)\s*detik\s*\(Game\s*#(\d+)\)', content)
        if terlambat_match:
            stats.waktu_terlambat = float(terlambat_match.group(1))
            stats.game_terlambat_idx = int(terlambat_match.group(2))
        
        # Parse detail per game
        game_pattern = r'Game\s*#(\d+)\s*\|\s*Pemenang:\s*(.+?)\s*\|\s*Durasi:\s*([0-9.]+)s'
        for match in re.finditer(game_pattern, content):
            game_num = int(match.group(1))
            winner = match.group(2).strip()
            duration = float(match.group(3))
            
            stats.game_details.append({
                'game_num': game_num,
                'winner': winner,
                'duration': duration
            })
        
        return stats
        
    except Exception as e:
        print(f"Error parsing file {filepath}: {e}")
        return None


def compare_stats(stats1: SimulationStats, stats2: SimulationStats) -> str:
    """
    Generate comparison text antara dua statistik
    
    Args:
        stats1: Statistik pertama
        stats2: Statistik kedua
        
    Returns:
        String berisi perbandingan
    """
    comparison = f"""
=== PERBANDINGAN STATISTIK ===

FILE 1: {stats1.player_x} vs {stats1.player_o}
FILE 2: {stats2.player_x} vs {stats2.player_o}

=== HASIL PERTANDINGAN ===
                    File 1          File 2
Jumlah Game:        {stats1.jumlah_game:>3}             {stats2.jumlah_game:>3}
Player X Wins:      {stats1.x_wins:>3} ({stats1.x_win_rate:>5.1f}%)    {stats2.x_wins:>3} ({stats2.x_win_rate:>5.1f}%)
Player O Wins:      {stats1.o_wins:>3} ({stats1.o_win_rate:>5.1f}%)    {stats2.o_wins:>3} ({stats2.o_win_rate:>5.1f}%)
Draws:              {stats1.draws:>3} ({stats1.draw_rate:>5.1f}%)    {stats2.draws:>3} ({stats2.draw_rate:>5.1f}%)

=== PERFORMA WAKTU ===
                    File 1          File 2          Selisih
Total Waktu:        {stats1.total_waktu:>7.2f}s        {stats2.total_waktu:>7.2f}s        {stats1.total_waktu - stats2.total_waktu:>7.2f}s
Rata-rata:          {stats1.rata_waktu:>7.2f}s        {stats2.rata_waktu:>7.2f}s        {stats1.rata_waktu - stats2.rata_waktu:>7.2f}s
Tercepat:           {stats1.waktu_tercepat:>7.2f}s        {stats2.waktu_tercepat:>7.2f}s        {stats1.waktu_tercepat - stats2.waktu_tercepat:>7.2f}s
Terlambat:          {stats1.waktu_terlambat:>7.2f}s        {stats2.waktu_terlambat:>7.2f}s        {stats1.waktu_terlambat - stats2.waktu_terlambat:>7.2f}s
"""
    return comparison
