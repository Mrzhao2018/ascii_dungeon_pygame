import sys
import pygame
import time
from typing import Optional, Dict, List, cast
from .log_utils import safe_log
from game.config import GameConfig
from game.state import GameState
from game.input import InputHandler
from game.floors import FloorManager
from game.renderer import Renderer
from game.player import Player
from game.logger import Logger, ErrorHandler
from game.performance import PerformanceOptimizer
from game.debug_controls import toggle_debug_mode, toggle_panel
from game.perf_controller import log_performance_stats
from game.memory import MemoryOptimizer, MemoryMonitor, SmartCacheManager
from game.error_handling import get_global_error_handler
from game import entities
from game.audio_controller import initialize_audio
from game.session_controller import (
    initialize_game_world,
    setup_initial_level,
    restart_game as session_restart_game,
    start_game_if_needed,
)
from game.transition_controller import apply_floor_transition, log_transition_triggered, log_transition_summary

"""
Main game class that orchestrates all game systems
"""




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

            # Initialize level and entities (delay until game starts)
            # _initialize_game_world() will be called when user starts game

            # Initialize renderer
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
                memory_monitor=self.memory_monitor, cache_manager=self.cache_manager, logger=self.logger
            )
            self.logger.debug("Memory management system initialized", "GAME")

            # Initialize global error handling
            self.global_error_handler = get_global_error_handler()
            if self.global_error_handler:
                self.global_error_handler.logger = self.logger
            self.logger.debug("Global error handler initialized", "GAME")

            # Game loop variables
            self.clock = pygame.time.Clock()
            self.running = True

            # Set clock for debug overlay FPS calculation
            if self.renderer and hasattr(self.renderer, 'set_debug_clock'):
                self.renderer.set_debug_clock(self.clock)

            # Entity and interaction state
            self.entity_mgr: Optional[entities.EntityManager] = None
            self.npcs: Dict = {}
            self.player: Optional[Player] = None  # Will be created when game starts

            # Don't setup initial level - wait for game start
            # self._setup_initial_level() will be called from _handle_start_game()

            # Sounds (annotated for type clarity)
            self.hit_sound: Optional[pygame.mixer.Sound]
            self.sprint_sound: Optional[pygame.mixer.Sound]
            self.sprint_ready_sound: Optional[pygame.mixer.Sound]

            self.logger.info("Game initialization completed successfully", "GAME")

        except Exception as e:
            self.logger.error("Failed to initialize game", "GAME", e)
            raise

    def _prefer_log(self, msg: str, level: str = 'info') -> None:
        safe_log(getattr(self, 'logger', None), getattr(self, 'game_state', None), msg, level=level, channel='GAME')

    def _initialize_game_world(self):
        """Initialize the game world (level, player, etc.) via session controller."""
        player = initialize_game_world(self.config, self.game_state, self.floor_manager)
        if not player:
            # 使用 logger 记录并优雅退出
            self._prefer_log("未找到玩家 '@'，请在地图中放置玩家", level='error')
            pygame.quit()
            sys.exit(1)
        self.player = player

    def _setup_initial_level(self):
        """Setup the initial level with entities and NPCs"""
        # Player must be initialized by _initialize_game_world before calling this
        if self.player is None:
            return
        self.entity_mgr, self.npcs = setup_initial_level(
            self.config, self.game_state, self.renderer, self.floor_manager, self.player
        )

    def _initialize_audio(self):
        """Initialize audio system via audio controller"""
        sound_enabled, hit, sprint, sprint_ready = initialize_audio(self.logger)
        self.hit_sound = hit
        self.sprint_sound = sprint
        self.sprint_ready_sound = sprint_ready
        self._prefer_log(f'[Game] sound_enabled={sound_enabled} hit_sound_present={self.hit_sound is not None}', level='info')

    def run(self):
        """Main game loop with enhanced monitoring and error handling"""
        self.logger.info("Starting main game loop", "GAME")
        frame_count = 0

        try:
            while self.running:
                # Start performance monitoring for this frame
                self.performance_optimizer.start_frame()

                # Frame timing anchors (collected by performance monitor already)

                # Tick clock and measure frame time
                dt = self.clock.tick(self.config.fps)

                # Handle events
                events = pygame.event.get()
                input_results = self.error_handler.safe_call(self.input_handler.handle_events, "input_events", events)

                if input_results and input_results.get('quit'):
                    self.logger.info("Quit requested by user", "GAME")
                    self.running = False
                    continue

                # Process input results
                if input_results:
                    self.error_handler.safe_call(self._process_input_results, "input_processing", input_results, dt)

                # Handle continuous input
                continuous_input = self.error_handler.safe_call(
                    self.input_handler.handle_continuous_input, "continuous_input"
                )
                if continuous_input:
                    self.error_handler.safe_call(
                        self._process_continuous_input, "continuous_processing", continuous_input, dt
                    )

                # Update game systems
                update_start = time.perf_counter()
                self.error_handler.safe_call(self._update_game_systems, "game_systems", dt)
                update_time = (time.perf_counter() - update_start) * 1000
                self.performance_optimizer.monitor.record_update_time(update_time)

                # Process floor transitions
                self.error_handler.safe_call(self._process_floor_transitions, "floor_transitions")

                # Render frame
                render_frame_start = time.perf_counter()
                # 在主菜单状态下，不传递player和entity参数
                from game.state import GameStateEnum
                if self.game_state.current_state == GameStateEnum.MAIN_MENU:
                    self.error_handler.safe_call(
                        self.renderer.render_frame,
                        "rendering",
                        None,  # player
                        None,  # entity_mgr
                        [],    # floating_texts
                        None,  # npcs
                    )
                else:
                    self.error_handler.safe_call(
                        self.renderer.render_frame,
                        "rendering",
                        self.player,
                        self.entity_mgr,
                        self.game_state.floating_texts,
                        self.npcs,
                    )
                render_time = (time.perf_counter() - render_frame_start) * 1000
                self.performance_optimizer.monitor.record_render_time(render_time)

                # End performance monitoring for this frame
                self.performance_optimizer.end_frame()

                frame_count += 1

                # Log performance statistics every 300 frames (about 10 seconds at 30 FPS)
                if frame_count % 300 == 0:
                    log_performance_stats(self.performance_optimizer, self.logger, self.config, self.game_state)

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
        # Handle pause/resume game
        if input_results.get('pause_game'):
            self._handle_pause_game()
            return  # 暂停后跳过其他输入处理
        
        if input_results.get('resume_game'):
            self._handle_resume_game()
            return  # 恢复后跳过其他输入处理
        
        if input_results.get('goto_main_menu'):
            self._handle_goto_main_menu()
            return  # 返回主菜单后跳过其他输入处理
        
        # Handle start game from main menu
        if input_results.get('start_game'):
            self._handle_start_game()
            return  # 开始游戏后跳过其他输入处理
        
        # Handle restart game
        if input_results.get('restart_game'):
            self._handle_restart_game()
            return  # 重新开始后跳过其他输入处理

        # Handle debug mode toggle
        if input_results.get('toggle_debug_mode'):
            toggle_debug_mode(self.config, self.renderer, self.logger, self.game_state)

        # Handle debug panel toggle
        if input_results.get('toggle_debug_panel'):
            toggle_panel(
                self.renderer,
                input_results.get('toggle_debug_panel'),
                self.logger,
                self.game_state,
                self.config,
            )

        # 以下操作需要玩家存在
        if self.player is None:
            return

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
        if input_results.get('sprint_sound'):
            from game.audio_controller import play_safe
            play_safe(self.sprint_sound)

    def _process_continuous_input(self, continuous_input, dt):
        """Process continuous input (movement, etc.)"""
        # 检查状态与玩家是否存在：仅在 PLAYING 状态下处理连续输入与体力更新
        from game.state import GameStateEnum
        if self.game_state.current_state != GameStateEnum.PLAYING or self.player is None:
            return
            
        movement = continuous_input.get('continuous_movement')
        is_sprinting = continuous_input.get('sprinting', False)

        if movement:
            dx, dy = movement
            moved_result = self.player.attempt_move(
                self.game_state.level, dx, dy, is_sprinting, dt, self.game_state.width, self.game_state.height
            )

            if moved_result.get('moved'):
                self._handle_movement_result(moved_result, dt)
        else:
            # No movement: passive stamina regen（仅在 PLAYING 状态下才会走到这里）
            self.player.passive_stamina_update(dt)

    def _handle_movement_result(self, moved_result, dt):
        """Handle the result of player movement"""
        if self.player is None:
            return
        px, py = moved_result.get('old')
        nx, ny = moved_result.get('new')
        target = moved_result.get('target')

        # Update FOV when player moves
        if self.config.enable_fov:
            self.player.update_fov(self.game_state.level)

        # Check for exit
        if target == 'X':
            self._trigger_floor_transition()

        # Spawn sprint particles
        if moved_result.get('sprinting'):
            dx = nx - px
            dy = ny - py
            self.player.spawn_sprint_particle(px, py, dx, dy, self.config.tile_size)

    def _trigger_floor_transition(self):
        """Trigger a floor transition"""
        if self.player is None:
            return
        # 给予楼层完成经验奖励
        from .experience import EXPERIENCE_CONFIG
        floor_exp = EXPERIENCE_CONFIG["exp_sources"]["floor_completion"]
        leveled_up = self.player.gain_experience(floor_exp)
        
        # 添加楼层完成经验提示
        px, py = self.player.x, self.player.y
        from game.ui import add_floating_text, add_levelup_text
        add_floating_text(
            self.game_state,
            f'Floor Complete! +{floor_exp} EXP',
            0,
            0,
            time_ms=2000,
            floor_complete=True,
            last_pos=(px * self.config.tile_size, py * self.config.tile_size - 30),
        )
        
        # 如果升级了，添加升级提示
        if leveled_up:
            add_levelup_text(
                self.game_state,
                f'LEVEL UP! Lv.{self.player.level}',
                px * self.config.tile_size,
                py * self.config.tile_size - 50,
            )
        
        # 记录楼层完成
        if self.logger:
            self.logger.info(f"完成第 {self.game_state.floor_number} 层, 获得 {floor_exp} 经验, 当前等级: {self.player.level}", "FLOOR")
        
        self.game_state.floor_number += 1

        self.game_state.game_log(f'Starting floor transition to {self.game_state.floor_number}')

        if self.config.seed is None:
            from game.utils import get_seed
            gen_seed = get_seed()
        else:
            try:
                gen_seed = int(self.config.seed) + self.game_state.floor_number
            except Exception:
                from game.utils import get_seed
                gen_seed = get_seed()

        self.game_state.start_floor_transition(self.game_state.floor_number, gen_seed)
        # 统一记录楼层转换触发日志
        log_transition_triggered(self.logger, self.game_state.floor_number, gen_seed)

    def _handle_interaction(self):
        """Handle interaction with NPCs"""
        if self.player is None:
            return
        px, py = self.player.x, self.player.y
        neighbors = [(px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)]

        found = None
        for nx, ny in neighbors:
            if (
                0 <= nx < self.game_state.width
                and 0 <= ny < self.game_state.height
                and self.game_state.level[ny][nx] == 'N'
            ):
                found = (nx, ny)
                break

        self.game_state.game_log(f'neighbor scan result: {found}')

        if found is not None:
            self.game_state.dialog_active = True
            entry = self.npcs.get(found) if self.npcs else None
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
        if self.player is None:
            return
        px, py = self.player.x, self.player.y
        neighbors = [(px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)]

        for nx, ny in neighbors:
            ent = self.entity_mgr.get_entity_at(nx, ny) if self.entity_mgr else None
            if isinstance(ent, entities.Enemy):
                # Deal damage
                ent.hp -= 3
                if ent.id is not None:
                    self.game_state.add_enemy_flash(ent.id)
                # Log the attack to in-game log and persistent logger
                try:
                    if self.game_state:
                        self.game_state.game_log(f'你攻击了敌人 ({nx},{ny})，剩余HP={ent.hp} id={ent.id}')
                except Exception:
                    pass
                self._prefer_log(f'你攻击了敌人 ({nx},{ny})，剩余HP={ent.hp} id={ent.id}', level='info')

                # Add floating text
                self.game_state.floating_texts.append(
                    {
                        'ent_id': ent.id,
                        'text': f'-3',
                        'time': 700,
                        'alpha': 255,
                        'damage': 3,
                        'last_pos': (nx * self.config.tile_size, ny * self.config.tile_size),
                    }
                )

                self.game_state.add_screen_shake()

                from game.audio_controller import play_safe
                play_safe(self.hit_sound)

                if ent.hp <= 0:
                    # 计算经验奖励
                    from .experience import get_enemy_exp_reward
                    enemy_type = getattr(ent, 'kind', 'normal')
                    exp_reward = get_enemy_exp_reward(enemy_type)
                    
                    # 给予玩家经验
                    leveled_up = self.player.gain_experience(exp_reward)
                    
                    # 添加经验获取提示
                    from game.ui import add_exp_text
                    add_exp_text(
                        self.game_state,
                        f'+{exp_reward} EXP',
                        nx * self.config.tile_size,
                        ny * self.config.tile_size + 20,
                    )
                    
                    # 如果升级了，添加升级提示
                    if leveled_up:
                        from game.ui import add_levelup_text
                        add_levelup_text(
                            self.game_state,
                            f'LEVEL UP! Lv.{self.player.level}',
                            nx * self.config.tile_size,
                            ny * self.config.tile_size - 20,
                        )
                    
                    # 生成掉落并应用
                    try:
                        from game.loot import generate_loot_for_enemy, ITEM_DISPLAY_NAME
                        drops = generate_loot_for_enemy(ent)
                    except Exception:
                        drops = []
                    if drops:
                        from game.ui import add_floating_text
                        for item_key, qty in drops:
                            # 应用到玩家
                            try:
                                self.player.apply_loot(item_key, qty)
                            except Exception:
                                pass
                            name = ITEM_DISPLAY_NAME.get(item_key, item_key)
                            add_floating_text(
                                self.game_state,
                                f'+{qty} {name}',
                                0,
                                0,
                                time_ms=1200,
                                last_pos=(nx * self.config.tile_size, ny * self.config.tile_size - 10),
                                experience=False,
                            )

                    # 记录击败敌人（用于调试和统计）
                    if self.logger:
                        loot_summary = ', '.join(f'{k}x{v}' for k, v in drops) if drops else 'no loot'
                        self.logger.info(
                            f"击败敌人 {enemy_type}, 经验 +{exp_reward}, 掉落: {loot_summary}, 等级: {self.player.level}",
                            "COMBAT",
                        )
                    
                    # Remove entity
                    if self.entity_mgr:
                        self.entity_mgr.remove(ent)
                    if ent.id in self.game_state.enemy_flash:
                        del self.game_state.enemy_flash[ent.id]
                    from game.utils import set_tile

                    set_tile(self.game_state.level, nx, ny, '.')
                break

    def _handle_debug(self):
        """Handle debug key press"""
        self._prefer_log('[debug] Entities:', level='debug')
        if self.entity_mgr:
            for ent in self.entity_mgr.entities_by_id.values():
                ex, ey = ent.x, ent.y
                ch = (
                    self.game_state.level[ey][ex]
                    if 0 <= ey < self.game_state.height and 0 <= ex < self.game_state.width
                    else '?'
                )
                neigh = {}
                for dxn, dyn, name in ((1, 0, 'R'), (-1, 0, 'L'), (0, 1, 'D'), (0, -1, 'U')):
                    tx, ty = ex + dxn, ey + dyn
                    if 0 <= ty < self.game_state.height and 0 <= tx < self.game_state.width:
                        neigh[name] = self.game_state.level[ty][tx]
                    else:
                        neigh[name] = None
                msg = (
                    f'  id={ent.id} pos=({ex},{ey}) hp={getattr(ent,"hp",None)} dir={getattr(ent,"dir",None)} tile={ch} neigh={neigh}'
                )
                if self.logger:
                    self.logger.debug(msg, 'DEBUG')
                elif getattr(self, 'game_state', None):
                    try:
                        self.game_state.game_log(msg)
                    except Exception:
                        print(msg)
                else:
                    print(msg)

    def _update_game_systems(self, dt):
        """Update all game systems"""
        # 只在PLAYING状态下更新游戏系统，暂停状态下不更新
        from game.state import GameStateEnum
        if (self.game_state.current_state != GameStateEnum.PLAYING or self.player is None):
            return  # 非游戏状态、暂停状态或玩家未初始化时跳过游戏逻辑更新
        
        # Update player
        prev_sprint_cd = getattr(self.player, 'sprint_cooldown', 0)
        self.player.update_timers(dt)

        # Play sprint ready sound
        if prev_sprint_cd > 0 and self.player.sprint_cooldown == 0:
            from game.audio_controller import play_safe
            play_safe(self.sprint_ready_sound)

        # Update entities
        if self.entity_mgr:
            evts = self.entity_mgr.update(
                self.game_state.level, (self.player.x, self.player.y), self.game_state.width, self.game_state.height
            )
            self._process_entity_events(evts)

        # Update visual effects
        self.game_state.update_enemy_flash(dt)
        self.game_state.update_screen_shake(dt)

        # Update camera
        self.game_state.update_camera(self.player.x, self.player.y, self.renderer.view_px_w, self.renderer.view_px_h)

        # Update floor transition
        if self.game_state.floor_transition:
            self.game_state.update_floor_transition(dt)

    def _process_entity_events(self, events):
        """Process events from entity updates"""
        if self.player is None:
            return
        for ev in events:
            if ev.get('type') == 'attack':
                px_ev, py_ev = ev.get('pos')
                dmg = int(ev.get('damage', 1))
                attacker_id = ev.get('attacker_id')

                if self.player.i_frames <= 0:
                    damaged = self.player.apply_damage(dmg)
                    if damaged:
                        # Log damage to player
                        try:
                            if self.game_state:
                                self.game_state.game_log(f'敌人攻击了你！ 你的HP={self.player.hp}')
                        except Exception:
                            pass
                        self._prefer_log(f'敌人攻击了你！ 你的HP={self.player.hp}', level='info')

                        # Add floating text
                        if attacker_id is not None:
                            self.game_state.floating_texts.append(
                                {
                                    'ent_id': attacker_id,
                                    'text': f'-{dmg}',
                                    'time': 700,
                                    'alpha': 255,
                                    'damage': dmg,
                                    'last_pos': (px_ev * self.config.tile_size, py_ev * self.config.tile_size),
                                }
                            )
                        else:
                            px_scr = px_ev * self.config.tile_size
                            py_scr = py_ev * self.config.tile_size
                            from game.ui import add_floating_text
                            add_floating_text(
                                self.game_state,
                                f'-{dmg}',
                                px_scr,
                                py_scr,
                                time_ms=700,
                                damage=dmg,
                            )

                        self.game_state.add_screen_shake()

                        from game.audio_controller import play_safe
                        play_safe(self.hit_sound)

                        if self.player.hp <= 0:
                            # Player death - log and change state
                            self._prefer_log('你死了。游戏结束。', level='info')
                            # 不再直接退出，而是切换到游戏结束状态
                            from game.state import GameStateEnum
                            self.game_state.set_game_state(GameStateEnum.GAME_OVER)

    def _process_floor_transitions(self):
        """Process floor transitions"""
        if self.player is None:
            return
        result = self.floor_manager.process_floor_transition()
        if result and result[0] is not None:
            level, entity_mgr, npcs, new_pos = result
            # Use transition controller to apply camera/FOV/indicator updates
            if entity_mgr is not None:
                entity_mgr_applied, npcs_dict = apply_floor_transition(
                    self.config,
                    self.game_state,
                    self.renderer,
                    self.player,
                    cast(List[str], level),
                    entity_mgr,
                    npcs,
                    new_pos,
                )
                self.entity_mgr = entity_mgr_applied
                self.npcs = npcs_dict

            # 统一记录楼层转换完成摘要
            log_transition_summary(self.logger, self.game_state, self.entity_mgr)

    def _handle_restart_game(self):
        """处理游戏重新开始"""
        try:
            self.logger.info("重新开始游戏", "GAME")
            from game.state import GameStateEnum
            self.game_state.set_game_state(GameStateEnum.PLAYING)
            # 使用会话控制器进行完整重启
            self.game_state, self.player, self.entity_mgr, self.npcs = session_restart_game(
                self.config, self.logger, self.floor_manager, self.renderer, self.game_state
            )
            
        except Exception as e:
            self.logger.error("重新开始游戏失败", "GAME", e)

    def _handle_start_game(self):
        """处理从主菜单开始游戏"""
        try:
            self.logger.info("从主菜单开始游戏", "GAME")
            
            # 通过会话控制器确保初始化并进入游戏
            player, entity_mgr, npcs = start_game_if_needed(
                self.config, self.logger, self.game_state, self.floor_manager, self.renderer
            )
            if player is not None:
                # 若首次启动，这里需要把新实例赋回
                if self.player is None:
                    self.player = player
                if entity_mgr is not None:
                    self.entity_mgr = entity_mgr
                # 保证为字典类型
                self.npcs = npcs or {}
            self.logger.info("游戏开始成功", "GAME")
            
        except Exception as e:
            self.logger.error("开始游戏失败", "GAME", e)

    def _handle_pause_game(self):
        """处理暂停游戏"""
        from game.state import GameStateEnum
        if self.game_state.current_state == GameStateEnum.PLAYING:
            self.game_state.set_game_state(GameStateEnum.PAUSED)
            self.logger.info("游戏已暂停", "GAME")

    def _handle_resume_game(self):
        """处理恢复游戏"""
        from game.state import GameStateEnum
        if self.game_state.current_state == GameStateEnum.PAUSED:
            self.game_state.set_game_state(GameStateEnum.PLAYING)
            self.logger.info("游戏已恢复", "GAME")

    def _handle_goto_main_menu(self):
        """处理返回主菜单"""
        from game.state import GameStateEnum
        self.game_state.set_game_state(GameStateEnum.MAIN_MENU)
        self.logger.info("返回主菜单", "GAME")
