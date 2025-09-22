"""
Input handling for the game
"""
import pygame
from typing import Dict, Tuple, Optional, Callable, Any


class InputHandler:
    """Handles keyboard input and events"""
    
    def __init__(self, config, game_state):
        self.config = config
        self.game_state = game_state
        
        # Event handlers
        self.event_handlers = {}
        self.setup_default_handlers()
    
    def setup_default_handlers(self):
        """Setup default event handlers"""
        self.event_handlers = {
            pygame.KEYDOWN: self.handle_keydown,
            pygame.QUIT: self.handle_quit
        }
    
    def handle_events(self, events) -> Dict[str, Any]:
        """Handle pygame events and return action results"""
        results = {
            'quit': False,
            'movement': None,
            'interaction': None,
            'attack': None,
            'debug': None
        }
        
        for event in events:
            if event.type in self.event_handlers:
                event_result = self.event_handlers[event.type](event)
                if event_result:
                    results.update(event_result)
        
        return results
    
    def handle_quit(self, event) -> Dict[str, Any]:
        """Handle quit event"""
        return {'quit': True}
    
    def handle_keydown(self, event) -> Dict[str, Any]:
        """Handle keydown events"""
        result = {}
        
        # Skip input during floor transition
        if self.game_state.floor_transition:
            self.game_state.game_log('input ignored during floor transition')
            return result
        
        # Handle dialog input
        if self.game_state.dialog_active:
            return self.handle_dialog_input(event)
        
        # Movement keys
        dx = dy = 0
        if event.key in (pygame.K_UP, pygame.K_w):
            dy = -1
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            dy = 1
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            dx = -1
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            dx = 1
        
        if dx != 0 or dy != 0:
            result['movement'] = (dx, dy)
            return result
        
        # Interaction key (E or Enter)
        if event.key in (pygame.K_e, pygame.K_RETURN):
            self.game_state.game_log('E pressed (interact)')
            result['interaction'] = True
            return result
        
        # Attack key (Space)
        if event.key == pygame.K_SPACE:
            result['attack'] = True
            return result
        
        # Sprint key (Shift) - handled in continuous input
        if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            result['sprint_sound'] = True
            return result
        
        # Debug key (K)
        if event.key == pygame.K_k:
            result['debug'] = True
            return result
        
        return result
    
    def handle_dialog_input(self, event) -> Dict[str, Any]:
        """Handle input during dialog"""
        if event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
            self.game_state.dialog_index += 1
            if self.game_state.dialog_index >= len(self.game_state.dialog_lines):
                self.game_state.dialog_active = False
        elif event.key == pygame.K_ESCAPE:
            self.game_state.dialog_active = False
        
        return {}
    
    def handle_continuous_input(self) -> Dict[str, Any]:
        """Handle continuous key states (movement, sprint, tab)"""
        result = {}
        
        # Skip during dialog or floor transition
        if self.game_state.dialog_active or self.game_state.floor_transition:
            return result
        
        keys = pygame.key.get_pressed()
        
        # Movement
        dx = dy = 0
        kx = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        kx_l = keys[pygame.K_LEFT] or keys[pygame.K_a]
        ky_u = keys[pygame.K_UP] or keys[pygame.K_w]
        ky_d = keys[pygame.K_DOWN] or keys[pygame.K_s]
        
        if kx and not kx_l:
            dx = 1
        elif kx_l and not kx:
            dx = -1
        elif ky_u and not ky_d:
            dy = -1
        elif ky_d and not ky_u:
            dy = 1
        
        if dx != 0 or dy != 0:
            result['continuous_movement'] = (dx, dy)
        
        # Sprint
        is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        result['sprinting'] = is_sprinting
        
        # Tab indicator
        if keys[pygame.K_TAB]:
            if self.game_state.exit_pos is not None:
                ex, ey = self.game_state.exit_pos
                tile_size = self.config.tile_size
                self.game_state.pending_target = (
                    ex * tile_size + tile_size // 2,
                    ey * tile_size + tile_size // 2
                )
            else:
                self.game_state.pending_target = None
        else:
            self.game_state.pending_target = None
        
        return result