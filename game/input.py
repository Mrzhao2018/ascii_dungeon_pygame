import pygame
from typing import Any, Callable, Dict, List, Optional

"""
Input handling for the game
"""



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
        self.event_handlers = {pygame.KEYDOWN: self.handle_keydown, pygame.QUIT: self.handle_quit}

    def handle_events(self, events) -> Dict[str, Any]:
        """Handle pygame events and return action results"""
        results = {'quit': False, 'movement': None, 'interaction': None, 'attack': None, 'debug': None}

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
        result: Dict[str, Any] = {}

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

        # Debug key (K) - for debug actions
        if event.key == pygame.K_k:
            result['debug'] = True
            return result

        # Toggle debug mode (F12)
        if event.key == pygame.K_F12:
            result['toggle_debug_mode'] = True
            return result

        # Tab key (toggle exit indicator)
        if event.key == pygame.K_TAB:
            return self._handle_tab_toggle()

        # Debug panel toggles (when debug mode is active)
        if self.config.debug_mode:
            debug_panel_keys = {
                pygame.K_1: 'performance',
                pygame.K_2: 'game_state',
                pygame.K_3: 'player_state',
                pygame.K_4: 'entity_debug',
                pygame.K_5: 'logs',
            }

            if event.key in debug_panel_keys:
                result['toggle_debug_panel'] = debug_panel_keys[event.key]
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
        result: Dict[str, Any] = {}

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

        # Tab indicator (toggle mode - fixed)
        # Note: Tab key handling moved to handle_keydown for proper toggle behavior
        # The continuous check here would clear the indicator when Tab is released

        return result

    def _handle_tab_toggle(self) -> Dict[str, Any]:
        """Handle Tab key press to toggle exit indicator"""
        # Toggle the indicator: if currently showing, hide it; if hidden, show it
        if self.game_state.pending_target is not None:
            # Currently showing indicator, hide it
            self.game_state.pending_target = None
            if hasattr(self.game_state, 'logger') and self.game_state.logger:
                self.game_state.logger.debug("Tab pressed: exit indicator hidden", "TAB")
        else:
            # Currently hidden, show indicator
            # Force recompute exit_pos if it's None but level has 'X'
            if self.game_state.exit_pos is None and self.game_state.level:
                x_count = sum(row.count('X') for row in self.game_state.level)
                if x_count > 0:
                    if hasattr(self.game_state, 'logger') and self.game_state.logger:
                        self.game_state.logger.info(f"Recomputing exit_pos on Tab (found {x_count} 'X')", "TAB")
                    self.game_state.compute_exit_pos()
            
            if self.game_state.exit_pos is not None:
                ex, ey = self.game_state.exit_pos
                tile_size = self.config.tile_size
                self.game_state.pending_target = (ex * tile_size + tile_size // 2, ey * tile_size + tile_size // 2)
                if hasattr(self.game_state, 'logger') and self.game_state.logger:
                    self.game_state.logger.debug(f"Tab pressed: exit indicator shown at {self.game_state.pending_target}", "TAB")
            else:
                self.game_state.pending_target = None
                if hasattr(self.game_state, 'logger') and self.game_state.logger:
                    self.game_state.logger.warning("Tab pressed but no exit_pos available", "TAB")
        
        return {}
