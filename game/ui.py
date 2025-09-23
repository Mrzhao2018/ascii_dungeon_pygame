import pygame
import pygame
import math
from typing import Dict, Optional, Tuple, Callable, Any


def add_floating_text(game_state, text: str, x_px: int, y_px: int, time_ms: int = 1000, alpha: int = 255, **flags):
    """Add a generic floating text entry with optional flags (damage, experience, level_up, floor_complete, etc.)."""
    entry = {
        'ent_id': flags.pop('ent_id', None),
        'text': text,
        'time': time_ms,
        'alpha': alpha,
    }
    entry.update(flags)
    # Support legacy keys 'x'/'y' or 'last_pos'
    if 'last_pos' in flags:
        entry['last_pos'] = flags['last_pos']
    else:
        entry['x'] = x_px
        entry['y'] = y_px
    game_state.floating_texts.append(entry)


def add_exp_text(game_state, text: str, x_px: int, y_px: int):
    add_floating_text(game_state, text, x_px, y_px, time_ms=1000, experience=True)


def add_levelup_text(game_state, text: str, x_px: int, y_px: int):
    add_floating_text(game_state, text, x_px, y_px, time_ms=2000, level_up=True)

# 简单字体缓存，避免重复创建 Font 对象
# Font cache to avoid reloading fonts
_font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}


def get_font(path_or_none, size):
    key = (path_or_none, size)
    if key in _font_cache:
        return _font_cache[key]
    try:
        f = pygame.font.Font(path_or_none, size) if path_or_none else pygame.font.SysFont(None, size)
    except Exception:
        f = pygame.font.SysFont(None, size)
    _font_cache[key] = f
    return f


def draw_floating_texts(
    surface,
    texts,
    base_tile_size,
    dt,
    used_font_path=None,
    position_lookup: Optional[Callable] = None,
    world_to_screen: Optional[Callable] = None,
):
    # texts supports two formats:
    # - legacy: {'x','y','text','time','alpha','damage'} (x/y in pixels)
    # - ent-based: {'ent_id', 'text','time','alpha','damage','last_pos':(x_px,y_px)}
    FLOAT_TOTAL = 700
    for ft in list(texts):
        ft['time'] -= dt
        # position update: legacy moves by y, ent-based uses last_pos and follows entity if available
        if 'ent_id' in ft and position_lookup is not None:
            pos = position_lookup(ft['ent_id'])
            if pos:
                ft['last_pos'] = pos
        else:
            # legacy behavior
            ft['y'] -= dt * 0.03

        if ft['time'] <= 0:
            try:
                texts.remove(ft)
            except ValueError:
                pass
            continue

        dmg = int(ft.get('damage', 1))
        
        # 根据文本类型设置不同颜色和大小
        if ft.get('experience'):
            # 经验获取 - 蓝色
            color = (100, 200, 255)
            size = max(14, int(base_tile_size * 0.8))
        elif ft.get('level_up'):
            # 升级 - 金色，较大
            color = (255, 215, 0)
            size = max(18, int(base_tile_size * 1.2))
        elif ft.get('floor_complete'):
            # 楼层完成 - 绿色
            color = (100, 255, 100)
            size = max(16, int(base_tile_size * 1.0))
        else:
            # 伤害 - 红色系，根据伤害值调整
            t = min(1.0, dmg / 6.0)
            r = int(255)
            g = int(120 + (135 * t))
            b = int(120 - (60 * t))
            color = (r, g, max(0, b))
            size = max(12, int(base_tile_size * (1.0 + min(1.0, dmg / 4.0))))
            
        txt_font = get_font(used_font_path, size)
        alpha = max(0, min(255, int(255 * (ft['time'] / FLOAT_TOTAL))))
        txt_surf = txt_font.render(ft['text'], True, color)
        try:
            txt_surf.set_alpha(alpha)
        except Exception:
            pass

        if 'ent_id' in ft:
            px, py = ft.get('last_pos', (0, 0))
            if world_to_screen is not None:
                sx, sy = world_to_screen(px, py)
            else:
                sx, sy = px, py
            tx = sx + (base_tile_size // 2) - (txt_surf.get_width() // 2)
            ty = sy - (base_tile_size // 2)
        else:
            # legacy x/y may be world pixel coords; if caller provided world_to_screen convert them
            if world_to_screen is not None:
                sx, sy = world_to_screen(ft['x'], ft['y'])
            else:
                sx, sy = ft['x'], ft['y']
            tx = sx + (base_tile_size // 2) - (txt_surf.get_width() // 2)
            ty = sy - (base_tile_size // 2)

        surface.blit(txt_surf, (tx, ty))


def compute_shake_offset(screen_shake, shake_time, amplitude):
    if screen_shake <= 0:
        return 0, 0
    factor = max(0.0, min(1.0, screen_shake / shake_time))
    amp = int(amplitude * factor)
    return (pygame.math.Vector2((pygame.time.get_ticks() % 7) - 3, (pygame.time.get_ticks() % 11) - 5) * (amp / 3)).xy


def draw_stamina_bar(surface, x, y, width, height, stamina, max_stamina, font=None):
    # 背景
    try:
        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))
        # 填充比例
        pct = max(0.0, min(1.0, stamina / max_stamina))
        fill_w = int(width * pct)
        color = (80, 200, 120) if pct > 0.4 else (200, 120, 120)
        pygame.draw.rect(surface, color, (x + 1, y + 1, max(0, fill_w - 2), height - 2))
        # 边框
        pygame.draw.rect(surface, (200, 200, 200), (x, y, width, height), 1)
        # 文本
        if font is not None:
            txt = f'{int(stamina)} / {int(max_stamina)}'
            surf = font.render(txt, True, (220, 220, 220))
            sw = surf.get_width()
            sh = surf.get_height()
            # Prefer using font ascent/descent for more accurate vertical centering
            try:
                ascent = font.get_ascent()
                descent = font.get_descent()
                text_height = ascent + abs(descent)
            except Exception:
                text_height = sh
            # compute y so text baseline is centered within bar
            ty = y + (height - text_height) // 2
            surface.blit(surf, (x + (width - sw) // 2, ty))
    except Exception:
        pass


def draw_player_hud(surface, player, ox, oy, view_px_w, font_path=None, tile_size=24):
    """Draw a small HUD showing HP, stamina bar, level and experience at top.
    player: Player instance with hp, stamina, max_stamina, sprint_cooldown, level, experience
    ox, oy: shake offsets
    view_px_w: width of viewport (for positioning)
    tile_size: base tile size for scaling fonts
    """
    try:
        # Scale font sizes based on tile_size
        base_hud_size = max(16, int(tile_size * 0.8))      # 主要文本
        base_small_size = max(14, int(tile_size * 0.7))    # 小文本
        
        hud_font = get_font(font_path, base_hud_size)
        small_font = get_font(font_path, base_small_size)
        
        # HP on left (slightly larger for visibility)
        hp_text = f'HP: {player.hp}'
        if hasattr(player, 'max_hp'):
            hp_text = f'HP: {player.hp}/{player.max_hp}'
        hp_s = hud_font.render(hp_text, True, (255, 180, 180))
        surface.blit(hp_s, (8 + ox, 8 + oy))

        # Level display (below HP) - 调整垂直间距
        level_text = f'Level: {player.level}'
        level_s = small_font.render(level_text, True, (180, 255, 180))
        level_y = 8 + base_hud_size + 4 + oy  # 根据字体大小调整间距
        surface.blit(level_s, (8 + ox, level_y))

        # Experience bar (below level) - 调整尺寸和位置
        if hasattr(player, 'get_experience_info'):
            exp_info = player.get_experience_info()
            exp_bar_w = max(120, int(tile_size * 5))  # 根据tile_size调整宽度
            exp_bar_h = max(8, int(tile_size * 0.35)) # 根据tile_size调整高度
            exp_bar_x = 8 + ox
            exp_bar_y = level_y + base_small_size + 4  # 根据字体大小调整位置
            
            # Background
            pygame.draw.rect(surface, (40, 40, 40), (exp_bar_x, exp_bar_y, exp_bar_w, exp_bar_h))
            
            # Experience fill
            if not exp_info['max_level']:
                fill_w = int(exp_bar_w * exp_info['exp_progress'])
                if fill_w > 0:
                    pygame.draw.rect(surface, (100, 200, 255), (exp_bar_x, exp_bar_y, fill_w, exp_bar_h))
            else:
                # Max level - fill with gold
                pygame.draw.rect(surface, (255, 215, 0), (exp_bar_x, exp_bar_y, exp_bar_w, exp_bar_h))
            
            # Border
            pygame.draw.rect(surface, (100, 100, 100), (exp_bar_x, exp_bar_y, exp_bar_w, exp_bar_h), 1)
            
            # Experience text
            if exp_info['max_level']:
                exp_text = "MAX"
            else:
                exp_text = f"{exp_info['exp_in_level']}/{exp_info['exp_in_level'] + exp_info['exp_to_next']}"
            exp_text_s = small_font.render(exp_text, True, (200, 200, 200))
            surface.blit(exp_text_s, (exp_bar_x + exp_bar_w + 5, exp_bar_y - 2))

        # stamina bar at top-right - 调整尺寸
        bar_w = max(160, int(tile_size * 6.5))  # 根据tile_size调整宽度
        bar_h = max(18, int(tile_size * 0.75))  # 根据tile_size调整高度
        x = view_px_w - bar_w - 8 + ox
        y = 8 + oy
        stamina_font_size = max(14, int(tile_size * 0.6))
        draw_stamina_bar(surface, x, y, bar_w, bar_h, player.stamina, player.max_stamina, font=get_font(font_path, stamina_font_size))

        # cooldown indicator (small) to the left of the bar - 调整尺寸
        cd_pct = max(0.0, min(1.0, player.sprint_cooldown / max(1, player.SPRINT_COOLDOWN_AFTER_EXHAUST)))
        if player.sprint_cooldown > 0:
            try:
                cx = x - 10
                cy = y + bar_h // 2
                base_radius = max(6, int(tile_size * 0.25))
                radius = int(base_radius + base_radius * cd_pct)
                radius = max(4, min(int(tile_size * 0.5), radius))
                alpha = int(140 * cd_pct)
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (200, 80, 80, alpha), (radius, radius), radius)
                surface.blit(s, (cx - radius, cy - radius))
                cooldown_font_size = max(12, int(tile_size * 0.5))
                txt_font = get_font(font_path, cooldown_font_size)
                txt = '疲'
                txt_s = txt_font.render(txt, True, (255, 255, 255))
                try:
                    txt_alpha = int(40 + 60 * cd_pct)
                    txt_s.set_alpha(txt_alpha)
                except Exception:
                    pass
                sw = txt_s.get_width()
                sh = txt_s.get_height()
                surface.blit(txt_s, (cx - sw // 2, cy - sh // 2))
            except Exception:
                pass
        
        # Level up notification - 调整字体大小
        if hasattr(player, 'level_up_notification') and player.level_up_notification:
            try:
                notification = player.level_up_notification
                big_font_size = max(24, int(tile_size * 1.2))
                big_font = get_font(font_path, big_font_size)
                
                # Level up text
                level_up_text = f"LEVEL UP! {notification['level']}"
                level_up_s = big_font.render(level_up_text, True, (255, 255, 100))
                
                # Center horizontally, place in upper middle of screen
                level_up_x = (view_px_w - level_up_s.get_width()) // 2 + ox
                level_up_y = max(80, int(tile_size * 3.5)) + oy
                
                # Background glow effect
                glow_surface = pygame.Surface((level_up_s.get_width() + 20, level_up_s.get_height() + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (255, 255, 100, 60), glow_surface.get_rect(), border_radius=5)
                surface.blit(glow_surface, (level_up_x - 10, level_up_y - 5))
                
                surface.blit(level_up_s, (level_up_x, level_up_y))
                
                # Bonus information
                bonuses = notification.get('bonuses', {})
                bonus_font = get_font(font_path, 12)
                bonus_y = level_up_y + 30
                
                if bonuses.get('hp_bonus', 0) > 0:
                    bonus_text = f"生命值 +{bonuses['hp_bonus']}"
                    bonus_s = bonus_font.render(bonus_text, True, (255, 180, 180))
                    bonus_x = (view_px_w - bonus_s.get_width()) // 2 + ox
                    surface.blit(bonus_s, (bonus_x, bonus_y))
                    bonus_y += 15
                
                if bonuses.get('stamina_bonus', 0) > 0:
                    bonus_text = f"体力 +{bonuses['stamina_bonus']}"
                    bonus_s = bonus_font.render(bonus_text, True, (180, 180, 255))
                    bonus_x = (view_px_w - bonus_s.get_width()) // 2 + ox
                    surface.blit(bonus_s, (bonus_x, bonus_y))
                    bonus_y += 15
                
                if bonuses.get('move_speed_bonus', 0) > 0:
                    bonus_text = f"移动速度 +{bonuses['move_speed_bonus']*100:.0f}%"
                    bonus_s = bonus_font.render(bonus_text, True, (180, 255, 180))
                    bonus_x = (view_px_w - bonus_s.get_width()) // 2 + ox
                    surface.blit(bonus_s, (bonus_x, bonus_y))
                    
            except Exception:
                pass
                
    except Exception:
        pass


def draw_target_indicator(surface, player, target_pos, cam_x, cam_y, ox, oy, view_px_w, view_px_h, font_path=None):
    """Draw an arrow indicator pointing to target_pos (tile coords in pixels).
    If target on-screen, draw a small marker; otherwise clamp to edge and draw arrow.
    target_pos: (wx_px, wy_px)
    """
    try:
        wx_px, wy_px = target_pos
        sx = wx_px - cam_x + ox
        sy = wy_px - cam_y + oy
        # if on-screen, draw small circle at target
        if 0 <= sx < view_px_w and 0 <= sy < view_px_h:
            pygame.draw.circle(surface, (240, 200, 80), (int(sx), int(sy)), 6)
            return

        # otherwise clamp position to viewport edge and compute angle
        cx = max(8, min(view_px_w - 8, int(sx)))
        cy = max(8, min(view_px_h - 8, int(sy)))
        # compute direction vector from center of screen to target
        center_x = view_px_w // 2
        center_y = view_px_h // 2
        dx = sx - center_x
        dy = sy - center_y
        # normalize
        mag = math.hypot(dx, dy)
        if mag == 0:
            return
        ux = dx / mag
        uy = dy / mag
        # arrow base position on edge: move from center towards edge
        edge_x = center_x + ux * (min(center_x, center_y) - 20)
        edge_y = center_y + uy * (min(center_x, center_y) - 20)
        # draw triangle arrow
        angle = math.atan2(uy, ux)

        def rot(px, py, a):
            return (px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a))

        size = 10
        p1 = (edge_x + ux * 6, edge_y + uy * 6)
        left = rot(-size, -size / 2, angle)
        right = rot(-size, size / 2, angle)
        p2 = (edge_x + left[0], edge_y + left[1])
        p3 = (edge_x + right[0], edge_y + right[1])
        pygame.draw.polygon(
            surface, (200, 200, 80), [(int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (int(p3[0]), int(p3[1]))]
        )
    except Exception as e:
        # Log the error instead of silently ignoring it
        print(f"Error in draw_target_indicator: {e}")
        import traceback
        traceback.print_exc()


def draw_sprint_particles(surface, player, world_to_screen: Optional[Callable], font):
    """Render player's sprint_particles list. world_to_screen converts world px -> screen px.
    font: pygame Font used to render particle glyphs."""
    if world_to_screen is None:
        return

    try:
        for p in list(getattr(player, 'sprint_particles', [])):
            sx, sy = world_to_screen(p['x_px'], p['y_px'])
            alpha = int(255 * (p['time'] / 300.0))
            col = (220, 220, 100)
            surf = font.render('.', True, col)
            try:
                surf.set_alpha(alpha)
            except Exception:
                pass
            surface.blit(surf, (sx - 4, sy - 4))
    except Exception:
        pass
