"""
Game state management
"""
import pygame
import os
from typing import Optional, Dict, List, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.logging import Logger


class GameState:
    """Manages the overall game state"""
    
    def __init__(self, config):
        self.config = config
        
        # Logger (will be set by Game class)
        self.logger: Optional['Logger'] = None
        
        # Level state
        self.level = []
        self.width = 0
        self.height = 0
        self.floor_number = 1
        self.exit_pos = None
        
        # Dialog state
        self.dialog_active = False
        self.dialog_lines = []
        self.dialog_index = 0
        
        # Floor transition state
        self.floor_transition = None  # dict {time: ms_remaining, text: str}
        self.pending_floor = None  # dict with generation params when transition finishes
        
        # Visual effects state
        self.enemy_flash = {}  # id -> ms remaining
        self.floating_texts = []
        self.screen_shake = 0
        self.pending_target = None  # for Tab indicator
        
        # Game logs for debug display
        self.game_logs = []
        
        # Camera state
        self.cam_x = 0
        self.cam_y = 0
    
    def set_level(self, level: List[str]):
        """Set the current level and update dimensions"""
        self.level = level
        self.width = len(level[0]) if level else 0
        self.height = len(level)
    
    def compute_exit_pos(self):
        """Find the exit position in the current level"""
        try:
            for y, row in enumerate(self.level):
                x = row.find('X')
                if x != -1:
                    self.exit_pos = (x, y)
                    return self.exit_pos
            self.exit_pos = None
        except Exception:
            self.exit_pos = None
        return self.exit_pos
    
    def start_floor_transition(self, floor_number: int, gen_seed: int):
        """Start a floor transition with given parameters"""
        self.exit_pos = None  # Clear previous exit
        self.floor_number = floor_number
        
        # Set pending floor parameters
        self.pending_floor = {
            'seed': gen_seed,
            'floor': floor_number,
            'width': self.config.map_width,
            'height': self.config.map_height,
            'rooms': self.config.rooms,
            'enemies': self.config.enemies,
            'min_room': self.config.min_room,
            'max_room': self.config.max_room,
            'corridor_radius': self.config.corridor_radius
        }
        
        self.floor_transition = {'time': 1100, 'text': f'第 {floor_number} 层'}
    
    def update_floor_transition(self, dt: int) -> bool:
        """Update floor transition timer. Returns True if transition completed."""
        if not self.floor_transition:
            return False
        
        self.floor_transition['time'] -= dt
        return self.floor_transition['time'] <= 0
    
    def complete_floor_transition(self):
        """Complete the floor transition and clean up state"""
        self.floor_transition = None
        self.pending_floor = None
        
        # Reset visual state
        self.enemy_flash = {}
        self.floating_texts = []
        self.dialog_active = False
        self.dialog_lines = []
        self.dialog_index = 0
    
    def update_screen_shake(self, dt: int):
        """Update screen shake effect"""
        if self.screen_shake > 0:
            self.screen_shake -= dt
            if self.screen_shake < 0:
                self.screen_shake = 0
    
    def add_screen_shake(self):
        """Add screen shake effect"""
        self.screen_shake = self.config.screen_shake_time
    
    def update_enemy_flash(self, dt: int):
        """Update enemy flash effects"""
        for ent_id in list(self.enemy_flash.keys()):
            self.enemy_flash[ent_id] -= dt
            if self.enemy_flash[ent_id] <= 0:
                del self.enemy_flash[ent_id]
    
    def add_enemy_flash(self, entity_id: int):
        """Add enemy flash effect"""
        self.enemy_flash[entity_id] = 200
    
    def game_log(self, msg: str):
        """Add a debug log message"""
        if not self.config.debug_mode:
            return
        
        try:
            ts = pygame.time.get_ticks()
        except Exception:
            ts = 0
        
        entry = f"[{ts}] {msg}"
        self.game_logs.append(entry)
        
        if len(self.game_logs) > self.config.game_log_max:
            del self.game_logs[0]
        
        # Also append to disk log
        try:
            log_path = os.path.join(os.path.dirname(__file__), '..', 'game.log')
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(entry + "\n")
        except Exception:
            pass
    
    def write_exit_log(self, msg: str):
        """Write to the persistent exit log"""
        try:
            dbg_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'session')
            try:
                os.makedirs(dbg_dir, exist_ok=True)
            except Exception:
                pass
            p = os.path.join(dbg_dir, 'exit_log.txt')
            with open(p, 'a', encoding='utf-8') as lf:
                ts = pygame.time.get_ticks() if 'pygame' in globals() else 0
                lf.write(f'[{ts}] {msg}\n')
        except Exception:
            pass
    
    def update_camera(self, player_x: int, player_y: int, view_px_w: int, view_px_h: int):
        """Update camera position with smooth following"""
        tile_size = self.config.tile_size
        
        # Target camera position
        target_px = (player_x * tile_size + tile_size // 2, player_y * tile_size + tile_size // 2)
        world_px_w = self.width * tile_size
        world_px_h = self.height * tile_size
        target_cam_x = target_px[0] - view_px_w // 2
        target_cam_y = target_px[1] - view_px_h // 2
        
        # Clamp target
        target_cam_x = max(0, min(target_cam_x, max(0, world_px_w - view_px_w)))
        target_cam_y = max(0, min(target_cam_y, max(0, world_px_h - view_px_h)))
        
        # Smooth camera with deadzone
        deadzone_px = self.config.cam_deadzone * tile_size
        
        dx_cam = target_cam_x - self.cam_x
        if abs(dx_cam) > deadzone_px:
            self.cam_x = self.cam_x + dx_cam * self.config.cam_lerp
        
        dy_cam = target_cam_y - self.cam_y
        if abs(dy_cam) > deadzone_px:
            self.cam_y = self.cam_y + dy_cam * self.config.cam_lerp
        
        # Final clamp
        self.cam_x = max(0, min(self.cam_x, max(0, world_px_w - view_px_w)))
        self.cam_y = max(0, min(self.cam_y, max(0, world_px_h - view_px_h)))
    
    def get_screen_shake_offset(self):
        """Get current screen shake offset"""
        if self.screen_shake <= 0:
            return 0, 0
        
        import random
        amp = int(self.config.screen_shake_amplitude * (self.screen_shake / self.config.screen_shake_time))
        try:
            ox = random.randint(-amp, amp)
            oy = random.randint(-amp, amp)
        except Exception:
            ox = oy = 0
        
        return ox, oy