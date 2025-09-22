"""
Enhanced debug overlay and developer tools
"""
import pygame
from typing import List, Dict, Any, Optional
from game import utils


class DebugOverlay:
    """Enhanced debug overlay showing game state and performance"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.enabled = config.debug_mode
        
        # Font for debug text
        self.font = None
        self.small_font = None
        
        # Debug panels
        self.panels = {}
        self.panel_positions = {
            'performance': (10, 10),
            'game_state': (10, 120),
            'player_state': (250, 10),
            'entity_debug': (250, 120),
            'logs': (10, 250)
        }
        
        # Panel visibility
        self.visible_panels = set(['logs'])  # Only logs visible by default
        
        self._initialize_fonts()
    
    def _initialize_fonts(self):
        """Initialize debug fonts"""
        try:
            self.font = utils.load_preferred_font(16)[0]
            self.small_font = utils.load_preferred_font(12)[0]
        except Exception as e:
            self.logger.warning(f"Failed to load debug fonts: {e}", "DEBUG")
    
    def toggle_panel(self, panel_name: str):
        """Toggle visibility of a debug panel"""
        if panel_name in self.visible_panels:
            self.visible_panels.remove(panel_name)
        else:
            self.visible_panels.add(panel_name)
    
    def render(self, screen, game_state, player, entity_mgr, npcs):
        """Render all enabled debug panels"""
        if not self.enabled or not self.font:
            return
        
        # Performance panel
        if 'performance' in self.visible_panels:
            self._render_performance_panel(screen)
        
        # Game state panel
        if 'game_state' in self.visible_panels:
            self._render_game_state_panel(screen, game_state)
        
        # Player state panel
        if 'player_state' in self.visible_panels:
            self._render_player_state_panel(screen, player)
        
        # Entity debug panel
        if 'entity_debug' in self.visible_panels:
            self._render_entity_debug_panel(screen, entity_mgr, npcs)
        
        # Logs panel (always visible in debug mode)
        if 'logs' in self.visible_panels:
            self._render_logs_panel(screen, game_state)
        
        # FPS counter
        if self.config.show_fps:
            self._render_fps_counter(screen)
        
        # Coordinates
        if self.config.show_coordinates and player:
            self._render_coordinates(screen, player, game_state)
    
    def _render_performance_panel(self, screen):
        """Render performance statistics panel"""
        x, y = self.panel_positions['performance']
        
        # Background
        panel_surf = pygame.Surface((220, 100), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 180))
        screen.blit(panel_surf, (x, y))
        
        # Title
        title_surf = self.font.render("Performance", True, (255, 255, 0))
        screen.blit(title_surf, (x + 5, y + 5))
        
        # Performance stats
        operations = ["frame_total", "rendering", "game_update"]
        line_y = y + 25
        
        for operation in operations:
            stats = self.logger.get_performance_stats(operation)
            if stats:
                text = f"{operation}: {stats['avg']:.1f}ms"
                color = (255, 255, 255)
                
                # Color code performance issues
                if operation == "frame_total" and stats['avg'] > 33:
                    color = (255, 100, 100)  # Red for poor performance
                elif operation == "frame_total" and stats['avg'] > 16:
                    color = (255, 255, 100)  # Yellow for marginal performance
                
                surf = self.small_font.render(text, True, color)
                screen.blit(surf, (x + 5, line_y))
                line_y += 15
    
    def _render_game_state_panel(self, screen, game_state):
        """Render game state information panel"""
        x, y = self.panel_positions['game_state']
        
        # Background
        panel_surf = pygame.Surface((220, 100), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 180))
        screen.blit(panel_surf, (x, y))
        
        # Title
        title_surf = self.font.render("Game State", True, (255, 255, 0))
        screen.blit(title_surf, (x + 5, y + 5))
        
        # Game state info
        info_lines = [
            f"Floor: {game_state.floor_number}",
            f"Level: {game_state.width}x{game_state.height}",
            f"Camera: ({game_state.cam_x:.0f}, {game_state.cam_y:.0f})",
            f"Dialog: {game_state.dialog_active}",
            f"Transition: {game_state.floor_transition is not None}"
        ]
        
        line_y = y + 25
        for line in info_lines:
            surf = self.small_font.render(line, True, (255, 255, 255))
            screen.blit(surf, (x + 5, line_y))
            line_y += 15
    
    def _render_player_state_panel(self, screen, player):
        """Render player state information panel"""
        x, y = self.panel_positions['player_state']
        
        # Background
        panel_surf = pygame.Surface((200, 120), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 180))
        screen.blit(panel_surf, (x, y))
        
        # Title
        title_surf = self.font.render("Player", True, (255, 255, 0))
        screen.blit(title_surf, (x + 5, y + 5))
        
        # Player info
        if player:
            info_lines = [
                f"Pos: ({player.x}, {player.y})",
                f"HP: {player.hp}/10",
                f"Stamina: {player.stamina:.1f}/{player.max_stamina}",
                f"Sprint CD: {player.sprint_cooldown}ms",
                f"Move CD: {player.move_cooldown_timer}ms",
                f"I-Frames: {player.i_frames}ms"
            ]
            
            line_y = y + 25
            for line in info_lines:
                color = (255, 255, 255)
                
                # Color code health
                if "HP:" in line and player.hp <= 3:
                    color = (255, 100, 100)
                elif "Stamina:" in line and player.stamina <= 20:
                    color = (255, 255, 100)
                
                surf = self.small_font.render(line, True, color)
                screen.blit(surf, (x + 5, line_y))
                line_y += 15
    
    def _render_entity_debug_panel(self, screen, entity_mgr, npcs):
        """Render entity debug information panel"""
        x, y = self.panel_positions['entity_debug']
        
        # Background
        panel_surf = pygame.Surface((200, 100), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 180))
        screen.blit(panel_surf, (x, y))
        
        # Title
        title_surf = self.font.render("Entities", True, (255, 255, 0))
        screen.blit(title_surf, (x + 5, y + 5))
        
        # Entity counts
        if entity_mgr:
            enemy_count = len([e for e in entity_mgr.entities_by_id.values() if hasattr(e, 'hp')])
            total_entities = len(entity_mgr.entities_by_id)
        else:
            enemy_count = 0
            total_entities = 0
        
        npc_count = len(npcs) if npcs else 0
        
        info_lines = [
            f"Enemies: {enemy_count}",
            f"NPCs: {npc_count}",
            f"Total Entities: {total_entities}",
        ]
        
        line_y = y + 25
        for line in info_lines:
            surf = self.small_font.render(line, True, (255, 255, 255))
            screen.blit(surf, (x + 5, line_y))
            line_y += 15
    
    def _render_logs_panel(self, screen, game_state):
        """Render game logs panel"""
        x, y = self.panel_positions['logs']
        screen_width = screen.get_width()
        
        # Dynamic width based on screen size
        panel_width = min(600, screen_width - x - 10)
        panel_height = min(150, len(self.logger.game_logs) * 16 + 30)
        
        # Background
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 180))
        screen.blit(panel_surf, (x, y))
        
        # Title
        title_surf = self.font.render("Debug Logs", True, (255, 255, 0))
        screen.blit(title_surf, (x + 5, y + 5))
        
        # Log entries
        line_y = y + 25
        for log_entry in self.logger.game_logs[-8:]:  # Show last 8 entries
            # Truncate long log lines
            if len(log_entry) > 60:
                display_text = log_entry[:57] + "..."
            else:
                display_text = log_entry
            
            # Color code by log level
            color = (255, 255, 255)
            if "[ERROR]" in log_entry:
                color = (255, 100, 100)
            elif "[WARN]" in log_entry:
                color = (255, 255, 100)
            elif "[DEBUG]" in log_entry:
                color = (150, 150, 255)
            
            surf = self.small_font.render(display_text, True, color)
            screen.blit(surf, (x + 5, line_y))
            line_y += 16
    
    def _render_fps_counter(self, screen):
        """Render FPS counter in top-right corner"""
        try:
            fps = pygame.time.Clock().get_fps()
            fps_text = f"FPS: {fps:.1f}"
            
            # Color code FPS
            color = (0, 255, 0)  # Green
            if fps < 20:
                color = (255, 0, 0)  # Red
            elif fps < 25:
                color = (255, 255, 0)  # Yellow
            
            surf = self.font.render(fps_text, True, color)
            x = screen.get_width() - surf.get_width() - 10
            y = 10
            
            # Background
            bg_surf = pygame.Surface((surf.get_width() + 10, surf.get_height() + 5), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 180))
            screen.blit(bg_surf, (x - 5, y - 2))
            
            screen.blit(surf, (x, y))
        except Exception:
            pass  # Silently fail FPS display
    
    def _render_coordinates(self, screen, player, game_state):
        """Render player coordinates"""
        if not player:
            return
        
        coord_text = f"Pos: ({player.x}, {player.y}) | Cam: ({game_state.cam_x:.0f}, {game_state.cam_y:.0f})"
        surf = self.font.render(coord_text, True, (255, 255, 255))
        
        x = screen.get_width() - surf.get_width() - 10
        y = 40
        
        # Background
        bg_surf = pygame.Surface((surf.get_width() + 10, surf.get_height() + 5), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 180))
        screen.blit(bg_surf, (x - 5, y - 2))
        
        screen.blit(surf, (x, y))
    
    def handle_debug_input(self, key):
        """Handle debug-specific input"""
        if not self.enabled:
            return False
        
        # Toggle debug panels with number keys
        debug_keys = {
            pygame.K_1: 'performance',
            pygame.K_2: 'game_state', 
            pygame.K_3: 'player_state',
            pygame.K_4: 'entity_debug',
            pygame.K_5: 'logs'
        }
        
        if key in debug_keys:
            self.toggle_panel(debug_keys[key])
            return True
        
        return False