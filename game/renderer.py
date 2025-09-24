import pygame
from typing import Set, Tuple
from game import ui, utils
from game.debug import DebugOverlay
from game.fov import TileVisibility

"""
Rendering management for the game
"""



class Renderer:
    """Manages all rendering operations"""

    def __init__(self, config, game_state):
        self.config = config
        self.game_state = game_state

        # Initialize display - 在主菜单状态下使用配置的默认尺寸
        if game_state.width == 0 or game_state.height == 0:
            # 主菜单状态，使用配置的视图尺寸
            view_w_tiles = config.view_width
            view_h_tiles = config.view_height
        else:
            # 游戏状态，使用实际地图尺寸限制
            view_w_tiles = min(game_state.width, config.view_width)
            view_h_tiles = min(game_state.height, config.view_height)
            
        self.view_px_w = view_w_tiles * config.tile_size
        self.view_px_h = view_h_tiles * config.tile_size

        self.screen = pygame.display.set_mode((self.view_px_w, self.view_px_h))
        pygame.display.set_caption("ASCII 地牢探险 - v2.2.0")

        # Load font
        self.font, self.used_path = utils.load_preferred_font(config.tile_size)
        
        # Test if the font supports Chinese characters, if not, try to load a Chinese font
        self.chinese_font = None
        try:
            # Test rendering a Chinese character
            test_surface = self.font.render("中", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                # Font supports Chinese
                self.chinese_font = self.font
            else:
                raise Exception("Font doesn't support Chinese")
        except:
            # Font doesn't support Chinese, try to load a Chinese font
            chinese_font, chinese_path = utils.load_chinese_font(config.tile_size)
            if chinese_font:
                self.chinese_font = chinese_font
                logger = getattr(game_state, 'logger', None)
                if logger:
                    logger.info(f"中文字体加载成功: {chinese_path}")
            else:
                # Fallback to the original font
                self.chinese_font = self.font
        
        # Log font loading information
        logger = getattr(game_state, 'logger', None)
        if logger:
            if self.used_path:
                logger.info(f"主字体加载成功: {self.used_path}")
            else:
                logger.info("使用系统默认字体")

        # Initialize debug overlay - always create it but enable/disable based on config
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
        from game.state import GameStateEnum
        
        # 根据游戏状态选择渲染方式
        if self.game_state.current_state == GameStateEnum.MAIN_MENU:
            self._render_main_menu()
        elif self.game_state.current_state == GameStateEnum.GAME_OVER:
            self._render_game_over_screen()
        elif self.game_state.current_state == GameStateEnum.PAUSED:
            # 暂停状态：先渲染游戏画面，再渲染暂停覆盖层
            self._render_playing_game(player, entity_mgr, floating_texts, npcs)
            self._render_pause_overlay()
        else:
            self._render_playing_game(player, entity_mgr, floating_texts, npcs)
        
        # 统一在这里更新显示，避免多次 flip() 造成闪烁
        pygame.display.flip()

    def _render_playing_game(self, player, entity_mgr, floating_texts, npcs=None):
        """渲染正常游戏界面"""
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

        # 不在这里调用 flip()，让主渲染方法统一处理

    def _render_main_menu(self):
        """渲染主菜单界面"""
        # 清屏 - 使用深蓝色背景
        self.screen.fill((20, 30, 50))
        
        # 计算屏幕中心
        center_x = self.view_px_w // 2
        center_y = self.view_px_h // 2
        
        # Debug: 显示屏幕尺寸信息
        debug_text = f"Screen: {self.view_px_w}x{self.view_px_h}"
        debug_surface = self.font.render(debug_text, True, (255, 255, 255))
        self.screen.blit(debug_surface, (10, 10))
        
        # 使用加载的字体，如果太大则缩小尺寸
        menu_font = self.font
        font_size = self.config.tile_size
        
        # 如果字体太大，创建一个较小的版本
        if font_size > 24:
            try:
                # 尝试使用较小的字体大小重新加载
                from game import utils
                menu_font, _ = utils.load_preferred_font(20)  # 使用20像素字体
                if menu_font is None:
                    menu_font = self.font
            except:
                menu_font = self.font
        
        # 游戏标题
        title_text = "ASCII 地牢探险"
        title_color = (255, 255, 150)  # 金黄色
        try:
            title_surface = menu_font.render(title_text, True, title_color)
        except:
            # 如果中文渲染失败，使用英文
            title_surface = menu_font.render("ASCII Dungeon", True, title_color)
        title_rect = title_surface.get_rect(center=(center_x, center_y - 120))
        self.screen.blit(title_surface, title_rect)
        
        # 副标题
        subtitle_text = "Dungeon Adventure"
        subtitle_color = (200, 200, 200)
        subtitle_surface = menu_font.render(subtitle_text, True, subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(center_x, center_y - 80))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # 菜单选项
        try:
            start_text = "开始游戏"
            start_surface = menu_font.render(start_text, True, (220, 255, 220))
        except:
            start_surface = menu_font.render("Start Game", True, (220, 255, 220))
        start_rect = start_surface.get_rect(center=(center_x, center_y - 20))
        self.screen.blit(start_surface, start_rect)
        
        try:
            quit_text = "退出游戏"
            quit_surface = menu_font.render(quit_text, True, (255, 220, 220))
        except:
            quit_surface = menu_font.render("Quit Game", True, (255, 220, 220))
        quit_rect = quit_surface.get_rect(center=(center_x, center_y + 30))
        self.screen.blit(quit_surface, quit_rect)
        
        # 控制提示 - 尝试中文，失败则使用英文
        try:
            controls = [
                "方向键/WASD: 移动  空格: 攻击  E: 交互",
                "Shift: 冲刺  Tab: 显示出口  F12: 调试模式",
                "按 Enter 开始游戏  按 Esc 退出"
            ]
            # 测试第一行是否能正常渲染
            test_surface = menu_font.render(controls[0], True, (150, 150, 150))
        except:
            # 如果中文失败，使用英文
            controls = [
                "WASD/Arrow Keys: Move  Space: Attack  E: Interact",
                "Shift: Sprint  Tab: Show Exit  F12: Debug Mode",
                "Press Enter to Start  Press Esc to Quit"
            ]
        
        for i, text in enumerate(controls):
            y_offset = center_y + 120 + i * 30
            try:
                control_surface = menu_font.render(text, True, (150, 150, 150))
            except:
                # 如果渲染失败，跳过这行
                continue
            control_rect = control_surface.get_rect(center=(center_x, y_offset))
            self.screen.blit(control_surface, control_rect)
        
        # 版本信息
        try:
            version_text = "v2.2.0 - 经验与升级系统"
            version_surface = menu_font.render(version_text, True, (100, 100, 100))
        except:
            version_text = "v2.2.0 - Experience & Leveling System"
            version_surface = menu_font.render(version_text, True, (100, 100, 100))
        version_rect = version_surface.get_rect(center=(center_x, self.view_px_h - 30))
        self.screen.blit(version_surface, version_rect)
        
        # 不在这里调用 flip()，让主渲染方法统一处理

    def _render_game_over_screen(self):
        """渲染游戏结束界面"""
        # 清屏 - 使用深红色背景表示游戏结束
        self.screen.fill((20, 0, 0))
        
        # 计算屏幕中心
        center_x = self.view_px_w // 2
        center_y = self.view_px_h // 2
        
        # 渲染标题 "你死了"
        title_text = "你死了！"
        title_color = (255, 50, 50)  # 红色
        title_surface = self.font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(center_x, center_y - 60))
        self.screen.blit(title_surface, title_rect)
        
        # 渲染操作提示
        restart_text = "按 R 重新开始"
        restart_color = (200, 200, 200)  # 灰白色
        restart_surface = self.font.render(restart_text, True, restart_color)
        restart_rect = restart_surface.get_rect(center=(center_x, center_y + 20))
        self.screen.blit(restart_surface, restart_rect)
        
        quit_text = "按 ESC 退出游戏"
        quit_color = (150, 150, 150)  # 较深灰色
        quit_surface = self.font.render(quit_text, True, quit_color)
        quit_rect = quit_surface.get_rect(center=(center_x, center_y + 60))
        self.screen.blit(quit_surface, quit_rect)
        
        # 添加装饰性元素 - 骷髅符号
        skull_symbols = ["💀", "☠️"]
        try:
            skull_text = skull_symbols[0]  # 使用第一个骷髅符号
            skull_surface = self.font.render(skull_text, True, (255, 100, 100))
            skull_rect = skull_surface.get_rect(center=(center_x, center_y - 120))
            self.screen.blit(skull_surface, skull_rect)
        except Exception:
            # 如果无法渲染emoji，使用ASCII字符
            skull_text = "X_X"
            skull_surface = self.font.render(skull_text, True, (255, 100, 100))
            skull_rect = skull_surface.get_rect(center=(center_x, center_y - 120))
            self.screen.blit(skull_surface, skull_rect)
        
        # 不在这里调用 flip()，让主渲染方法统一处理

    def _render_level_tiles(self, x0: int, y0: int, x1: int, y1: int, entity_mgr, player, ox: int, oy: int):
        """Render the level tiles with FOV support"""
        for y in range(y0, y1):
            if y >= len(self.game_state.level):
                continue
            row = self.game_state.level[y]

            for x in range(x0, x1):
                if x >= len(row):
                    continue

                ch = row[x]
                # If this is an enemy tile, capture entity for glyph/color customization
                ent_here_for_glyph = None
                if ch == 'E' and entity_mgr:
                    try:
                        ent_here_for_glyph = entity_mgr.get_entity_at(x, y)
                    except Exception:
                        ent_here_for_glyph = None

                # Check if FOV is enabled in config
                if hasattr(self.config, 'enable_fov') and self.config.enable_fov:
                    # 获取瓦片可见性状态
                    visibility = TileVisibility.get_visibility_state(x, y, player.fov_system)

                    # 根据可见性状态决定是否渲染和如何渲染
                    if visibility == TileVisibility.HIDDEN:
                        # 完全不可见，不渲染
                        continue
                    elif visibility == TileVisibility.EXPLORED:
                        # 已探索但不可见，用暗色渲染
                        color = self._get_explored_tile_color(ch, x, y, entity_mgr, player)
                    else:  # VISIBLE
                        # 当前可见，正常渲染
                        color = self._get_tile_color(ch, x, y, entity_mgr, player)
                else:
                    # FOV disabled, render all tiles normally
                    color = self._get_tile_color(ch, x, y, entity_mgr, player)

                # Decide glyph+color override for enemies by kind
                render_ch = ch
                render_color = color
                if ch == 'E' and ent_here_for_glyph:
                    try:
                        kind = getattr(ent_here_for_glyph, 'kind', 'basic')
                        glyph_map = {
                            'basic': 'e',
                            'guard': 'G',
                            'scout': 's',
                            'brute': 'B',
                        }
                        kind_color_map = {
                            'basic': (220, 100, 100),
                            'guard': (240, 160, 80),
                            'scout': (180, 140, 240),
                            'brute': (255, 80, 80),
                        }
                        render_ch = glyph_map.get(kind, 'E')
                        # If enemy flash active, keep flash color priority
                        if not (ent_here_for_glyph and self.game_state.enemy_flash.get(getattr(ent_here_for_glyph, 'id', None), 0) > 0):
                            render_color = kind_color_map.get(kind, color)
                    except Exception:
                        render_ch = 'E'
                surf = self.font.render(render_ch, True, render_color)
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

    def _get_explored_tile_color(self, ch: str, x: int, y: int, entity_mgr, player) -> Tuple[int, int, int]:
        """Get the color for an explored but not currently visible tile (fog of war)"""
        # 获取正常颜色然后调暗
        normal_color = self._get_tile_color(ch, x, y, entity_mgr, player)
        # 应用雾化效果：显著降低亮度
        fog_factor = 0.3
        return (int(normal_color[0] * fog_factor), int(normal_color[1] * fog_factor), int(normal_color[2] * fog_factor))

    def _render_ui(self, player, floating_texts, entity_mgr, ox: int, oy: int):
        """Render UI elements"""
        # Player HUD
        ui.draw_player_hud(self.screen, player, ox, oy, self.view_px_w, font_path=self.used_path, tile_size=self.config.tile_size)

        # Target indicator
        if self.game_state.pending_target is not None:
            ui.draw_target_indicator(
                self.screen,
                player,
                self.game_state.pending_target,
                self.game_state.cam_x,
                self.game_state.cam_y,
                ox,
                oy,
                self.view_px_w,
                self.view_px_h,
                font_path=self.used_path,
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
                self.screen,
                floating_texts,
                self.config.tile_size,
                16,  # dt placeholder
                used_font_path=self.used_path,
                position_lookup=position_lookup,
                world_to_screen=world_to_screen,
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

    def _render_pause_overlay(self):
        """渲染暂停覆盖层"""
        try:
            # 创建半透明黑色覆盖层
            overlay = pygame.Surface((self.view_px_w, self.view_px_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # 黑色，50% 透明度
            self.screen.blit(overlay, (0, 0))

            # 计算屏幕中心
            center_x = self.view_px_w // 2
            center_y = self.view_px_h // 2

            # 根据 tile_size 动态调整字体大小
            title_font_size = max(36, int(self.config.tile_size * 1.8))
            menu_font_size = max(24, int(self.config.tile_size * 1.2))
            hint_font_size = max(18, int(self.config.tile_size * 0.9))

            # 暂停标题
            try:
                title_font = self.chinese_font if hasattr(self, 'chinese_font') and self.chinese_font else self.font
                if title_font_size != self.config.tile_size:
                    # 创建指定大小的字体
                    from game import utils
                    title_font = utils.load_preferred_font(title_font_size)[0]
                
                pause_text = "游戏暂停"
                title_surface = title_font.render(pause_text, True, (255, 255, 100))
            except:
                # 如果中文失败，使用英文
                title_font = self.font
                pause_text = "GAME PAUSED"
                title_surface = title_font.render(pause_text, True, (255, 255, 100))
            
            title_rect = title_surface.get_rect(center=(center_x, center_y - 80))
            self.screen.blit(title_surface, title_rect)

            # 菜单选项
            menu_font = self.font
            if menu_font_size != self.config.tile_size:
                from game import utils
                menu_font = utils.load_preferred_font(menu_font_size)[0]

            menu_options = [
                ("继续游戏", "ESC", (180, 255, 180)),
                ("重新开始", "Enter", (255, 255, 180)),
                ("返回主菜单", "M", (180, 180, 255)),
                ("退出游戏", "Q", (255, 180, 180))
            ]

            for i, (text, key, color) in enumerate(menu_options):
                y_offset = center_y - 20 + i * 35
                try:
                    # 尝试渲染中文
                    option_surface = menu_font.render(text, True, color)
                except:
                    # 如果失败，使用英文
                    english_options = ["Continue", "Restart", "Main Menu", "Quit Game"]
                    option_surface = menu_font.render(english_options[i], True, color)
                
                option_rect = option_surface.get_rect(center=(center_x - 50, y_offset))
                self.screen.blit(option_surface, option_rect)

                # 按键提示
                key_surface = menu_font.render(f"[{key}]", True, (200, 200, 200))
                key_rect = key_surface.get_rect(center=(center_x + 80, y_offset))
                self.screen.blit(key_surface, key_rect)

            # 底部操作提示
            hint_font = self.font
            if hint_font_size != self.config.tile_size:
                from game import utils
                hint_font = utils.load_preferred_font(hint_font_size)[0]

            try:
                hint_text = "按 ESC 继续游戏"
                hint_surface = hint_font.render(hint_text, True, (150, 150, 150))
            except:
                hint_surface = hint_font.render("Press ESC to Continue", True, (150, 150, 150))
            
            hint_rect = hint_surface.get_rect(center=(center_x, self.view_px_h - 50))
            self.screen.blit(hint_surface, hint_rect)

            # 不在这里调用 flip()，让主渲染循环统一处理

        except Exception as e:
            # 如果渲染失败，至少显示基本信息
            try:
                basic_font = pygame.font.Font(None, 36)
                basic_text = basic_font.render("PAUSED - Press ESC", True, (255, 255, 255))
                basic_rect = basic_text.get_rect(center=(self.view_px_w // 2, self.view_px_h // 2))
                self.screen.blit(basic_text, basic_rect)
                # 同样不在这里调用 flip()
            except:
                pass
