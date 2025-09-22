"""
Rendering management for the game
"""
import pygame
import random
from typing import List, Optional, Tuple
from game import ui, utils
from game.debug import DebugOverlay


class Renderer:
    """Manages all rendering operations"""
    
    def __init__(self, config, game_state):
        self.config = config
        self.game_state = game_state
        
        # Initialize display
        view_w_tiles = min(game_state.width, config.view_width)
        view_h_tiles = min(game_state.height, config.view_height)
        self.view_px_w = view_w_tiles * config.tile_size
        self.view_px_h = view_h_tiles * config.tile_size
        
        self.screen = pygame.display.set_mode((self.view_px_w, self.view_px_h))
        pygame.display.set_caption("ASCII Adventure - Pygame 示例")
        
        # Load font
        self.font, self.used_path = utils.load_preferred_font(config.tile_size)
        
        # Initialize debug overlay - always create it but enable/disable based on config
        from game.logging import Logger
        logger = getattr(game_state, 'logger', None)
        if logger:
            self.debug_overlay = DebugOverlay(config, logger)
        else:
            self.debug_overlay = None
    
    def set_debug_clock(self, clock):
        """Set the clock object for FPS calculation in debug overlay"""
        if self.debug_overlay:
            self.debug_overlay.clock = clock
    
    def update_view_size(self, width: int, height: int):
        """Update view size when level changes"""
        view_w_tiles = min(width, self.config.view_width)
        view_h_tiles = min(height, self.config.view_height)
        new_view_px_w = view_w_tiles * self.config.tile_size
        new_view_px_h = view_h_tiles * self.config.tile_size
        
        if new_view_px_w != self.view_px_w or new_view_px_h != self.view_px_h:
            self.view_px_w = new_view_px_w
            self.view_px_h = new_view_px_h
            self.screen = pygame.display.set_mode((self.view_px_w, self.view_px_h))
    
    def render_frame(self, player, entity_mgr, floating_texts, npcs=None):
        """Render a complete frame"""
        # Get screen shake offset
        ox, oy = self.game_state.get_screen_shake_offset()
        
        # Calculate visible tile range
        x0 = max(0, int(self.game_state.cam_x // self.config.tile_size))
        y0 = max(0, int(self.game_state.cam_y // self.config.tile_size))
        x1 = min(self.game_state.width, int((self.game_state.cam_x + self.view_px_w) // self.config.tile_size) + 1)
        y1 = min(self.game_state.height, int((self.game_state.cam_y + self.view_px_h) // self.config.tile_size) + 1)
        
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render level tiles
        self._render_level_tiles(x0, y0, x1, y1, entity_mgr, player, ox, oy)
        
        # Render UI elements
        self._render_ui(player, floating_texts, entity_mgr, ox, oy)
        
        # Render floor transition overlay
        if self.game_state.floor_transition:
            self._render_floor_transition()
        
        # Render debug logs
        if self.config.debug_mode:
            self._render_debug_logs()
        
        # Render debug overlay
        if self.debug_overlay:
            # Update debug mode state in case it was toggled
            self.debug_overlay.update_debug_mode()
            self.debug_overlay.render(self.screen, self.game_state, player, entity_mgr, npcs)
        
        pygame.display.flip()
    
    def _render_level_tiles(self, x0: int, y0: int, x1: int, y1: int, entity_mgr, player, ox: int, oy: int):
        """Render the level tiles"""
        for y in range(y0, y1):
            if y >= len(self.game_state.level):
                continue
            row = self.game_state.level[y]
            
            for x in range(x0, x1):
                if x >= len(row):
                    continue
                
                ch = row[x]
                color = self._get_tile_color(ch, x, y, entity_mgr, player)
                
                surf = self.font.render(ch, True, color)
                px = x * self.config.tile_size - self.game_state.cam_x + ox
                py = y * self.config.tile_size - self.game_state.cam_y + oy
                self.screen.blit(surf, (int(px), int(py)))
    
    def _get_tile_color(self, ch: str, x: int, y: int, entity_mgr, player) -> Tuple[int, int, int]:
        """Get the color for a tile character"""
        if ch == '#':
            return (100, 100, 100)
        elif ch == '@':
            if player.flash_time > 0:
                return (255, 255, 255)
            return (255, 215, 0)
        elif ch == 'X':
            return (150, 255, 150)
        elif ch == 'N':
            return (180, 150, 255)
        elif ch == 'E':
            ent_here = entity_mgr.get_entity_at(x, y) if entity_mgr else None
            if ent_here and self.game_state.enemy_flash.get(getattr(ent_here, 'id', None), 0) > 0:
                return (255, 180, 180)
            return (220, 100, 100)
        else:  # '.' or other
            return (200, 200, 200)
    
    def _render_ui(self, player, floating_texts, entity_mgr, ox: int, oy: int):
        """Render UI elements"""
        # Player HUD
        ui.draw_player_hud(self.screen, player, ox, oy, self.view_px_w, font_path=self.used_path)
        
        # Target indicator
        if self.game_state.pending_target is not None:
            ui.draw_target_indicator(
                self.screen, player, self.game_state.pending_target, 
                self.game_state.cam_x, self.game_state.cam_y, ox, oy, 
                self.view_px_w, self.view_px_h, font_path=self.used_path
            )
        
        # Floating texts
        def position_lookup(ent_id):
            if entity_mgr:
                ent = entity_mgr.get_entity_by_id(ent_id)
                if ent:
                    return (ent.x * self.config.tile_size, ent.y * self.config.tile_size)
            return None
        
        def world_to_screen(wx_px, wy_px):
            sx = wx_px - self.game_state.cam_x + ox
            sy = wy_px - self.game_state.cam_y + oy
            return sx, sy
        
        try:
            ui.draw_floating_texts(
                self.screen, floating_texts, self.config.tile_size, 16,  # dt placeholder
                used_font_path=self.used_path, position_lookup=position_lookup, 
                world_to_screen=world_to_screen
            )
        except Exception:
            pass
        
        # Sprint particles
        try:
            player.update_particles(16, self.config.tile_size)  # dt placeholder
            ui.draw_sprint_particles(self.screen, player, world_to_screen, self.font)
        except Exception:
            pass
        
        # Dialog
        if self.game_state.dialog_active:
            self._render_dialog(ox, oy)
    
    def _render_dialog(self, ox: int, oy: int):
        """Render dialog box"""
        if not self.game_state.dialog_lines:
            return
        
        if self.game_state.dialog_index < 0 or self.game_state.dialog_index >= len(self.game_state.dialog_lines):
            return
        
        pad = 8
        box_h = self.config.tile_size * 3
        box_w = self.view_px_w - pad * 2
        
        if box_w <= 0 or box_h <= 0:
            return
        
        box_x = pad + ox
        box_y = self.view_px_h - box_h - pad + oy
        
        # Dialog background
        s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (box_x, box_y))
        
        # Dialog text
        line_y = box_y + 8
        for i, line in enumerate(self.game_state.dialog_lines[self.game_state.dialog_index].split('\n')):
            surf = self.font.render(line, True, (240, 240, 240))
            self.screen.blit(surf, (box_x + 8, line_y + i * self.config.tile_size))
    
    def _render_floor_transition(self):
        """Render floor transition overlay"""
        try:
            overlay = pygame.Surface((self.view_px_w, self.view_px_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Center text
            big_font = utils.load_preferred_font(36)[0]
            txt = self.game_state.floor_transition.get('text', '')
            surf = big_font.render(txt, True, (240, 240, 240))
            sx = (self.view_px_w - surf.get_width()) // 2
            sy = (self.view_px_h - surf.get_height()) // 2
            self.screen.blit(surf, (sx, sy))
        except Exception:
            pass
    
    def _render_debug_logs(self):
        """Render debug logs in the corner"""
        log_font = utils.load_preferred_font(14)[0]
        lx = 6
        ly = 6
        
        for i, msg in enumerate(self.game_state.game_logs):
            try:
                surf = log_font.render(msg, True, (200, 200, 200))
                self.screen.blit(surf, (lx, ly + i * 16))
            except Exception:
                pass