"""
Main game class that orchestrates all game systems
"""
import sys
import pygame
import time
import os
from typing import Optional

from game.config import GameConfig
from game.state import GameState
from game.input import InputHandler
from game.floors import FloorManager
from game.renderer import Renderer
from game.player import Player
from game.logging import Logger, ErrorHandler, create_performance_timer
from game.performance import PerformanceOptimizer
from game.memory import MemoryOptimizer, MemoryMonitor, SmartCacheManager
from game.error_handling import get_global_error_handler
from game import entities, dialogs as dialogs_mod, audio as audio_mod


class Game:
    """Main game class that manages the game loop and systems"""
    
    def __init__(self):
        # Initialize systems
        self.config = GameConfig()
        
        # Initialize logging and error handling
        self.logger = Logger(self.config)
        self.error_handler = ErrorHandler(self.logger)
        
        self.logger.info("Initializing game systems", "GAME")
        
        try:
            self.game_state = GameState(self.config)
            self.game_state.logger = self.logger  # Pass logger to game_state
            self.input_handler = InputHandler(self.config, self.game_state)
            self.floor_manager = FloorManager(self.config, self.game_state)
            
            # Initialize pygame
            pygame.init()
            self.logger.debug("Pygame initialized", "GAME")
            
            # Initialize level and entities
            self._initialize_game_world()
            
            # Initialize renderer (after level is set up)
            self.renderer = Renderer(self.config, self.game_state)
            
            # Initialize audio
            self._initialize_audio()
            
            # Initialize performance optimization system
            self.performance_optimizer = PerformanceOptimizer()
            self.logger.debug("Performance optimizer initialized", "GAME")
            
            # Initialize memory management system
            self.memory_monitor = MemoryMonitor(logger=self.logger)
            self.cache_manager = SmartCacheManager()
            self.memory_optimizer = MemoryOptimizer(
                memory_monitor=self.memory_monitor,
                cache_manager=self.cache_manager,
                logger=self.logger
            )
            self.logger.debug("Memory management system initialized", "GAME")
            
            # Initialize global error handling
            self.global_error_handler = get_global_error_handler()
            self.global_error_handler.logger = self.logger
            self.logger.debug("Global error handler initialized", "GAME")
            
            # Game loop variables
            self.clock = pygame.time.Clock()
            self.running = True
            
            # Entity and interaction state
            self.entity_mgr = None
            self.npcs = {}
            
            # Setup initial level
            self._setup_initial_level()
            
            self.logger.info("Game initialization completed successfully", "GAME")
            
        except Exception as e:
            self.logger.error("Failed to initialize game", "GAME", e)
            raise
    
    def _initialize_game_world(self):
        """Initialize the game world (level, player, etc.)"""
        # Generate initial level
        level = self.floor_manager.generate_initial_level()
        self.game_state.set_level(level)
        
        # Find player position
        player_pos = self.floor_manager.find_player(level)
        if not player_pos:
            print("未找到玩家 '@'，请在地图中放置玩家")
            pygame.quit()
            sys.exit(1)
        
        # Create player
        self.player = Player(
            player_pos[0], player_pos[1], 
            hp=10, 
            move_cooldown=self.config.move_cooldown,
            max_stamina=self.config.stamina_max, 
            stamina_regen=self.config.stamina_regen,
            sprint_cost=self.config.sprint_cost, 
            sprint_cooldown_ms=self.config.sprint_cooldown_ms,
            sprint_multiplier=self.config.sprint_multiplier
        )
    
    def _setup_initial_level(self):
        """Setup the initial level with entities and NPCs"""
        self.entity_mgr, self.npcs = self.floor_manager.setup_level(self.game_state.level)
        self.floor_manager.write_initial_snapshot(self.game_state.level)
        
        # Initialize camera
        self.game_state.cam_x = self.player.x * self.config.tile_size - self.renderer.view_px_w // 2
        self.game_state.cam_y = self.player.y * self.config.tile_size - self.renderer.view_px_h // 2
        self.game_state.cam_x = max(0, min(self.game_state.cam_x, max(0, self.game_state.width * self.config.tile_size - self.renderer.view_px_w)))
        self.game_state.cam_y = max(0, min(self.game_state.cam_y, max(0, self.game_state.height * self.config.tile_size - self.renderer.view_px_h)))
    
    def _initialize_audio(self):
        """Initialize audio system"""
        sound_enabled = audio_mod.init_audio()
        self.hit_sound = audio_mod.load_hit_sound() if sound_enabled else None
        self.sprint_sound = audio_mod.load_sprint_sound() if sound_enabled else None
        self.sprint_ready_sound = audio_mod.load_sprint_ready_sound() if sound_enabled else None
        print(f'[Game] sound_enabled={sound_enabled} hit_sound_present={self.hit_sound is not None}')
    
    def run(self):
        """Main game loop with enhanced monitoring and error handling"""
        self.logger.info("Starting main game loop", "GAME")
        frame_count = 0
        
        try:
            while self.running:
                # Start performance monitoring for this frame
                self.performance_optimizer.start_frame()
                
                frame_start = pygame.time.get_ticks()
                render_start = time.perf_counter()
                
                # Tick clock and measure frame time
                dt = self.clock.tick(self.config.fps)
                
                # Handle events
                event_start = time.perf_counter()
                events = pygame.event.get()
                input_results = self.error_handler.safe_call(
                    self.input_handler.handle_events, "input_events", events
                )
                event_time = (time.perf_counter() - event_start) * 1000
                
                if input_results and input_results.get('quit'):
                    self.logger.info("Quit requested by user", "GAME")
                    self.running = False
                    continue
                
                # Process input results
                if input_results:
                    self.error_handler.safe_call(
                        self._process_input_results, "input_processing", input_results, dt
                    )
                
                # Handle continuous input
                continuous_input = self.error_handler.safe_call(
                    self.input_handler.handle_continuous_input, "continuous_input"
                )
                if continuous_input:
                    self.error_handler.safe_call(
                        self._process_continuous_input, "continuous_processing", 
                        continuous_input, dt
                    )
                
                # Update game systems
                update_start = time.perf_counter()
                self.error_handler.safe_call(
                    self._update_game_systems, "game_systems", dt
                )
                update_time = (time.perf_counter() - update_start) * 1000
                self.performance_optimizer.monitor.record_update_time(update_time)
                
                # Process floor transitions
                self.error_handler.safe_call(
                    self._process_floor_transitions, "floor_transitions"
                )
                
                # Render frame
                render_frame_start = time.perf_counter()
                self.error_handler.safe_call(
                    self.renderer.render_frame, "rendering",
                    self.player, self.entity_mgr, 
                    self.game_state.floating_texts, self.npcs
                )
                render_time = (time.perf_counter() - render_frame_start) * 1000
                self.performance_optimizer.monitor.record_render_time(render_time)
                
                # End performance monitoring for this frame
                self.performance_optimizer.end_frame()
                
                frame_count += 1
                
                # Log performance statistics every 300 frames (about 10 seconds at 30 FPS)
                if frame_count % 300 == 0:
                    self._log_performance_stats()
        
        except KeyboardInterrupt:
            self.logger.info("Game interrupted by user (Ctrl+C)", "GAME")
        except Exception as e:
            self.logger.error("Unhandled exception in main game loop", "GAME", e)
            raise
        finally:
            self.logger.info("Shutting down game systems", "GAME")
            pygame.quit()
    
    def _process_input_results(self, input_results, dt):
        """Process discrete input events"""
        # Handle interaction
        if input_results.get('interaction'):
            self._handle_interaction()
        
        # Handle attack
        if input_results.get('attack'):
            self._handle_attack()
        
        # Handle debug
        if input_results.get('debug'):
            self._handle_debug()
        
        # Handle sprint sound
        if input_results.get('sprint_sound') and self.sprint_sound:
            try:
                self.sprint_sound.play()
            except Exception:
                pass
    
    def _process_continuous_input(self, continuous_input, dt):
        """Process continuous input (movement, etc.)"""
        movement = continuous_input.get('continuous_movement')
        is_sprinting = continuous_input.get('sprinting', False)
        
        if movement:
            dx, dy = movement
            moved_result = self.player.attempt_move(
                self.game_state.level, dx, dy, is_sprinting, dt, 
                self.game_state.width, self.game_state.height
            )
            
            if moved_result.get('moved'):
                self._handle_movement_result(moved_result, dt)
        else:
            # No movement: passive stamina regen
            self.player.passive_stamina_update(dt)
    
    def _handle_movement_result(self, moved_result, dt):
        """Handle the result of player movement"""
        px, py = moved_result.get('old')
        nx, ny = moved_result.get('new')
        target = moved_result.get('target')
        
        # Check for exit
        if target == 'X':
            self._trigger_floor_transition()
        
        # Spawn sprint particles
        if moved_result.get('sprinting'):
            dx = nx - px
            dy = ny - py
            self.player.spawn_sprint_particle(px, py, dx, dy)
    
    def _trigger_floor_transition(self):
        """Trigger a floor transition"""
        self.game_state.floor_number += 1
        
        self.game_state.game_log(f'Starting floor transition to {self.game_state.floor_number}')
        
        if self.config.seed is None:
            gen_seed = int(time.time() * 1000)
        else:
            try:
                gen_seed = int(self.config.seed) + self.game_state.floor_number
            except Exception:
                gen_seed = int(time.time() * 1000)
        
        self.game_state.start_floor_transition(self.game_state.floor_number, gen_seed)
        self.game_state.write_exit_log(f'Floor transition triggered: floor {self.game_state.floor_number}, seed {gen_seed}')
    
    def _handle_interaction(self):
        """Handle interaction with NPCs"""
        px, py = self.player.x, self.player.y
        neighbors = [(px+1,py),(px-1,py),(px,py+1),(px,py-1)]
        
        found = None
        for nx, ny in neighbors:
            if (0 <= nx < self.game_state.width and 0 <= ny < self.game_state.height and 
                self.game_state.level[ny][nx] == 'N'):
                found = (nx, ny)
                break
        
        self.game_state.game_log(f'neighbor scan result: {found}')
        
        if found is not None:
            self.game_state.dialog_active = True
            entry = self.npcs.get(found)
            self.game_state.game_log(f'interact found at {found} entry={entry}')
            
            if entry and 'dialog' in entry:
                self.game_state.dialog_lines = entry['dialog'][:]
            else:
                self.game_state.dialog_lines = [
                    "你好，旅行者。欢迎来到字符世界！",
                    "按 E 或 空格 翻页，Esc 关闭对话。",
                ]
            self.game_state.dialog_index = 0
    
    def _handle_attack(self):
        """Handle player attack"""
        px, py = self.player.x, self.player.y
        neighbors = [(px+1,py),(px-1,py),(px,py+1),(px,py-1)]
        
        for nx, ny in neighbors:
            ent = self.entity_mgr.get_entity_at(nx, ny) if self.entity_mgr else None
            if isinstance(ent, entities.Enemy):
                # Deal damage
                ent.hp -= 3
                self.game_state.add_enemy_flash(ent.id)
                print(f'你攻击了敌人 ({nx},{ny})，剩余HP={ent.hp} id={ent.id}')
                
                # Add floating text
                self.game_state.floating_texts.append({
                    'ent_id': ent.id, 'text': f'-3', 'time': 700, 
                    'alpha': 255, 'damage': 3, 
                    'last_pos': (nx * self.config.tile_size, ny * self.config.tile_size)
                })
                
                self.game_state.add_screen_shake()
                
                if self.hit_sound:
                    try:
                        self.hit_sound.play()
                    except Exception:
                        pass
                
                if ent.hp <= 0:
                    # Remove entity
                    self.entity_mgr.remove(ent)
                    if ent.id in self.game_state.enemy_flash:
                        del self.game_state.enemy_flash[ent.id]
                    from game.utils import set_tile
                    set_tile(self.game_state.level, nx, ny, '.')
                break
    
    def _handle_debug(self):
        """Handle debug key press"""
        print('[debug] Entities:')
        if self.entity_mgr:
            for ent in self.entity_mgr.entities_by_id.values():
                ex, ey = ent.x, ent.y
                ch = (self.game_state.level[ey][ex] if 0 <= ey < self.game_state.height and 
                      0 <= ex < self.game_state.width else '?')
                neigh = {}
                for dxn, dyn, name in ((1,0,'R'),(-1,0,'L'),(0,1,'D'),(0,-1,'U')):
                    tx, ty = ex + dxn, ey + dyn
                    if 0 <= ty < self.game_state.height and 0 <= tx < self.game_state.width:
                        neigh[name] = self.game_state.level[ty][tx]
                    else:
                        neigh[name] = None
                print(f'  id={ent.id} pos=({ex},{ey}) hp={getattr(ent,"hp",None)} dir={getattr(ent,"dir",None)} tile={ch} neigh={neigh}')
    
    def _update_game_systems(self, dt):
        """Update all game systems"""
        # Update player
        prev_sprint_cd = getattr(self.player, 'sprint_cooldown', 0)
        self.player.update_timers(dt)
        
        # Play sprint ready sound
        if prev_sprint_cd > 0 and self.player.sprint_cooldown == 0:
            if self.sprint_ready_sound:
                try:
                    self.sprint_ready_sound.play()
                except Exception:
                    pass
        
        # Update entities
        if self.entity_mgr:
            evts = self.entity_mgr.update(
                self.game_state.level, (self.player.x, self.player.y), 
                self.game_state.width, self.game_state.height
            )
            self._process_entity_events(evts)
        
        # Update visual effects
        self.game_state.update_enemy_flash(dt)
        self.game_state.update_screen_shake(dt)
        
        # Update camera
        self.game_state.update_camera(
            self.player.x, self.player.y, 
            self.renderer.view_px_w, self.renderer.view_px_h
        )
        
        # Update floor transition
        if self.game_state.floor_transition:
            self.game_state.update_floor_transition(dt)
    
    def _process_entity_events(self, events):
        """Process events from entity updates"""
        for ev in events:
            if ev.get('type') == 'attack':
                px_ev, py_ev = ev.get('pos')
                dmg = int(ev.get('damage', 1))
                attacker_id = ev.get('attacker_id')
                
                if self.player.i_frames <= 0:
                    damaged = self.player.apply_damage(dmg)
                    if damaged:
                        print(f'敌人攻击了你！ 你的HP={self.player.hp}')
                        
                        # Add floating text
                        if attacker_id is not None:
                            self.game_state.floating_texts.append({
                                'ent_id': attacker_id, 'text': f'-{dmg}', 'time': 700, 
                                'alpha': 255, 'damage': dmg, 
                                'last_pos': (px_ev * self.config.tile_size, py_ev * self.config.tile_size)
                            })
                        else:
                            px_scr = px_ev * self.config.tile_size
                            py_scr = py_ev * self.config.tile_size
                            self.game_state.floating_texts.append({
                                'x': px_scr, 'y': py_scr, 'text': f'-{dmg}', 
                                'time': 700, 'alpha': 255, 'damage': dmg
                            })
                        
                        self.game_state.add_screen_shake()
                        
                        if self.hit_sound:
                            try:
                                self.hit_sound.play()
                            except Exception:
                                pass
                        
                        if self.player.hp <= 0:
                            print('你死了。游戏结束。')
                            self.running = False
    
    def _process_floor_transitions(self):
        """Process floor transitions"""
        result = self.floor_manager.process_floor_transition()
        if result and result[0] is not None:
            level, entity_mgr, npcs, new_pos = result
            
            # Update game state
            self.game_state.set_level(level)
            self.entity_mgr = entity_mgr
            self.npcs = npcs
            
            # Update player position
            if new_pos:
                self.player.x, self.player.y = new_pos
            
            # Update renderer view size
            self.renderer.update_view_size(self.game_state.width, self.game_state.height)
            
            # Reset camera
            self.game_state.cam_x = self.player.x * self.config.tile_size - self.renderer.view_px_w // 2
            self.game_state.cam_y = self.player.y * self.config.tile_size - self.renderer.view_px_h // 2
            self.game_state.cam_x = max(0, min(self.game_state.cam_x, max(0, self.game_state.width * self.config.tile_size - self.renderer.view_px_w)))
            self.game_state.cam_y = max(0, min(self.game_state.cam_y, max(0, self.game_state.height * self.config.tile_size - self.renderer.view_px_h)))
    
    def _log_performance_stats(self):
        """Log performance statistics"""
        # Use the new performance monitor's summary
        self.performance_optimizer.monitor.log_performance_summary()
        
        # Check for performance issues
        stats = self.performance_optimizer.get_stats()
        if stats.get('drop_rate', 0) > 5:  # More than 5% dropped frames
            self.logger.warning(f"High frame drop rate: {stats['drop_rate']:.1f}%", "PERFORMANCE")
        
        if stats.get('avg_frame_time', 0) > 40:  # Worse than 25 FPS
            self.logger.warning(f"Poor frame time: {stats['avg_frame_time']:.1f}ms", "PERFORMANCE")
        
        # Apply optimizations if performance is poor
        if self.config.debug_mode and (stats.get('drop_rate', 0) > 10 or stats.get('avg_frame_time', 0) > 50):
            self.logger.info("Applying performance optimizations...", "PERFORMANCE")
            self.performance_optimizer.optimize_rendering(self.config, self.game_state, pygame.display.get_surface())
        
        # Check for performance issues
        frame_stats = self.logger.get_performance_stats("frame_total")
        if frame_stats and frame_stats['avg'] > 33.0:  # More than 33ms per frame (less than 30 FPS)
            self.logger.warning(
                f"Performance issue detected: average frame time {frame_stats['avg']:.1f}ms", 
                "PERFORMANCE"
            )