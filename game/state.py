import pygame
import os
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING, Tuple
from enum import Enum

"""
Game state management
"""


if TYPE_CHECKING:
    from game.logger import Logger


class GameStateEnum(Enum):
    """游戏状态枚举"""
    MAIN_MENU = "main_menu"     # 主菜单状态
    PLAYING = "playing"         # 正常游戏状态
    PAUSED = "paused"           # 游戏暂停状态
    GAME_OVER = "game_over"     # 游戏结束状态
    RESTART = "restart"         # 重新开始状态


class GameState:
    """Manages the overall game state"""

    def __init__(self, config):
        self.config = config

        # Logger (will be set by Game class)
        self.logger: Optional['Logger'] = None

        # 游戏状态 - 默认从主菜单开始
        self.current_state = GameStateEnum.MAIN_MENU
        # Level state
        self.level = []
        self.width = 0
        self.height = 0
        self.floor_number = 1
        self.exit_pos = None
        # Backwards-compatible alias used by older tests/code
        self.show_exit_indicator = False

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
        # Accept list-of-strings or list-of-list-of-chars
        try:
            self.width = len(level[0]) if level else 0
            self.height = len(level)
        except Exception:
            self.width = 0
            self.height = 0

    def get_level(self):
        """Return the current level structure (alias for tests)"""
        return self.level

    @property
    def floor(self) -> int:
        """Compatibility alias for floor_number"""
        return self.floor_number

    @floor.setter
    def floor(self, v: int):
        self.floor_number = v

    def compute_exit_pos(self):
        """Find the exit position in the current level"""
        try:
            # Debug log for troubleshooting
            if hasattr(self, 'logger') and self.logger:
                level_info = f"{self.width}x{self.height}" if self.level else "empty"
                self.logger.debug(f"Computing exit_pos for level {level_info}", "EXIT")
            
            # Look for 'X' in the level
            found_exits = []
            for y, row in enumerate(self.level):
                for x, ch in enumerate(row):
                    if ch == 'X':
                        found_exits.append((x, y))
            
            if found_exits:
                # Use the first exit found
                self.exit_pos = found_exits[0]
                if hasattr(self, 'logger') and self.logger:
                    self.logger.debug(f"Found exit at {self.exit_pos}, total exits: {len(found_exits)}", "EXIT")
            else:
                self.exit_pos = None
                if hasattr(self, 'logger') and self.logger:
                    x_count = sum(row.count('X') for row in self.level) if self.level else 0
                    self.logger.warning(f"No exit found in level! X count: {x_count}", "EXIT")
                    
        except Exception as e:
            self.exit_pos = None
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Exception computing exit_pos: {e}", "EXIT")
                
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
            'corridor_radius': self.config.corridor_radius,
        }

        self.floor_transition = {'time': 1100, 'text': f'第 {floor_number} 层'}

    def increment_floor(self):
        """Increment the floor number (compatibility for tests)."""
        self.floor_number += 1
        # Keep alias in sync
        try:
            self.floor = self.floor_number
        except Exception:
            pass

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

    def is_screen_shaking(self) -> bool:
        """Compatibility helper: is any screen shake active?"""
        return self.screen_shake > 0

    def add_screen_shake(self):
        """Add screen shake effect"""
        self.screen_shake = self.config.screen_shake_time

    def trigger_screen_shake(self):
        """Backward-compatible alias expected by tests."""
        self.add_screen_shake()

    def update_enemy_flash(self, dt: int):
        """Update enemy flash effects"""
        for ent_id in list(self.enemy_flash.keys()):
            self.enemy_flash[ent_id] -= dt
            if self.enemy_flash[ent_id] <= 0:
                del self.enemy_flash[ent_id]

    def add_enemy_flash(self, entity_id: int):
        """Add enemy flash effect"""
        self.enemy_flash[entity_id] = 200

    # --- Backwards-compatible camera helpers expected by tests ---
    def set_camera(self, x: int, y: int):
        """Set camera position directly (tests expect this)."""
        self.cam_x = x
        self.cam_y = y

    # --- Floating text compatibility ---
    def add_floating_text(self, text: str, x: int, y: int, color=None, duration_ms: int = 1000):
        """Compatibility wrapper used by tests and older code.

        Adds both 'duration' and 'time' keys for compatibility with different consumers.
        """
        entry = {
            'text': text,
            'x': x,
            'y': y,
            'color': color,
            'duration': duration_ms,
            'time': duration_ms,
        }
        self.floating_texts.append(entry)

    def update_floating_texts(self, dt: int):
        """Update floating text durations (compat for tests).

        dt is milliseconds.
        """
        for ft in list(self.floating_texts):
            # Update both duration and time if present
            if 'duration' in ft:
                ft['duration'] -= dt
            if 'time' in ft:
                ft['time'] -= dt

            # If either indicator marks expiry, remove
            dur = ft.get('duration', ft.get('time', 0))
            if dur <= 0:
                try:
                    self.floating_texts.remove(ft)
                except ValueError:
                    pass

    def is_valid_position(self, x: int, y: int) -> bool:
        """Return True if (x,y) is a valid tile coordinate in the current level."""
        if not self.level:
            return False
        if x < 0 or y < 0:
            return False
        if y >= len(self.level):
            return False
        row = self.level[y]
        try:
            return 0 <= x < len(row)
        except Exception:
            return False

    def get_tile(self, x: int, y: int):
        """Return the tile at (x,y) or None if out of bounds. Supports list-of-strings or list-of-lists."""
        if not self.is_valid_position(x, y):
            return None
        row = self.level[y]
        try:
            # row might be a string or list
            return row[x]
        except Exception:
            try:
                return row[x]
            except Exception:
                return None

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

    def set_game_state(self, new_state: GameStateEnum):
        """切换游戏状态"""
        old_state = self.current_state
        self.current_state = new_state
        if self.logger:
            self.logger.info(f"游戏状态切换: {old_state.value} -> {new_state.value}", "STATE")

    def is_main_menu(self) -> bool:
        """检查是否在主菜单"""
        return self.current_state == GameStateEnum.MAIN_MENU

    def is_playing(self) -> bool:
        """检查是否在游戏中"""
        return self.current_state == GameStateEnum.PLAYING

    def is_paused(self) -> bool:
        """检查是否游戏暂停"""
        return self.current_state == GameStateEnum.PAUSED

    def is_game_over(self) -> bool:
        """检查是否游戏结束"""
        return self.current_state == GameStateEnum.GAME_OVER

    def is_restart(self) -> bool:
        """检查是否需要重新开始"""
        return self.current_state == GameStateEnum.RESTART

    def refresh_exit_indicator(self, tile_size: int):
        """刷新方位指示器，指向新楼层的出口"""
        # 如果当前没有开启指示器，则不需要刷新
        if self.pending_target is None:
            return
        
        # 重新计算出口位置
        self.compute_exit_pos()
        
        # 如果找到了新的出口位置，更新指示器目标
        if self.exit_pos is not None:
            ex, ey = self.exit_pos
            self.pending_target = (ex * tile_size + tile_size // 2, ey * tile_size + tile_size // 2)
            if self.logger:
                self.logger.debug(f"方位指示器已刷新，指向新出口位置: {self.exit_pos}", "INDICATOR")
        else:
            # 如果新楼层没有出口，隐藏指示器
            self.pending_target = None
            if self.logger:
                self.logger.warning("新楼层没有出口，已隐藏方位指示器", "INDICATOR")

    def toggle_exit_indicator(self):
        """API expected by tests to toggle the exit indicator on/off."""
        self.show_exit_indicator = not bool(self.show_exit_indicator)
        if self.show_exit_indicator:
            # Refresh to compute a target if possible
            try:
                self.refresh_exit_indicator(self.config.tile_size)
            except Exception:
                pass
