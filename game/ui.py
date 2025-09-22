import pygame
import pygame
import math
from typing import Dict, Optional, Tuple, Callable, Any

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


def draw_player_hud(surface, player, ox, oy, view_px_w, font_path=None):
    """Draw a small HUD showing HP and stamina bar at top-right.
    player: Player instance with hp, stamina, max_stamina, sprint_cooldown
    ox, oy: shake offsets
    view_px_w: width of viewport (for positioning)
    """
    try:
        hud_font = get_font(font_path, 16)
        # HP on left (slightly larger for visibility)
        hp_s = hud_font.render(f'HP: {player.hp}', True, (255, 180, 180))
        surface.blit(hp_s, (8 + ox, 8 + oy))

        # stamina bar at top-right
        bar_w = 160
        bar_h = 18
        x = view_px_w - bar_w - 8 + ox
        y = 8 + oy
        draw_stamina_bar(surface, x, y, bar_w, bar_h, player.stamina, player.max_stamina, font=get_font(font_path, 14))

        # cooldown indicator (small) to the left of the bar
        cd_pct = max(0.0, min(1.0, player.sprint_cooldown / max(1, player.SPRINT_COOLDOWN_AFTER_EXHAUST)))
        if player.sprint_cooldown > 0:
            try:
                cx = x - 10
                cy = y + bar_h // 2
                radius = int(6 + 6 * cd_pct)
                radius = max(4, min(12, radius))
                alpha = int(140 * cd_pct)
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (200, 80, 80, alpha), (radius, radius), radius)
                surface.blit(s, (cx - radius, cy - radius))
                txt_font = get_font(font_path, 12)
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
