import os
import json
import pygame
from typing import Optional

def find_player(level):
    for y, row in enumerate(level):
        x = row.find("@")
        if x != -1:
            return x, y
    return None


def set_tile(level, x, y, ch):
    # defensive: avoid accidentally overwriting an exit 'X' unless caller explicitly forces it
    try:
        row = level[y]
    except Exception:
        return
    try:
        cur = row[x]
    except Exception:
        return
    # if there's an exit here, don't overwrite it by default
    if cur == 'X' and ch != 'X':
        return
    level[y] = row[:x] + ch + row[x + 1 :]


def load_preferred_font(tile_size):
    """Scan fonts/ and system fonts and return a pygame Font instance plus the path used (or None)."""
    fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')
    candidates = []
    try:
        if os.path.isdir(fonts_dir):
            for name in os.listdir(fonts_dir):
                if name.lower().endswith(('.ttf', '.otf')):
                    candidates.append(os.path.join(fonts_dir, name))
    except Exception:
        candidates = []

    patterns = ['mplus', 'mplu', 'unifont', 'noto', 'sourcehan', 'wenquan', 'uranus', 'pixel']
    used_path = None
    font = None
    for pat in patterns:
        for fpath in candidates:
            if pat in os.path.basename(fpath).lower():
                try:
                    font = pygame.font.Font(fpath, tile_size)
                    used_path = fpath
                    break
                except Exception:
                    font = None
        if font:
            break

    if font is None and candidates:
        for fpath in candidates:
            try:
                font = pygame.font.Font(fpath, tile_size)
                used_path = fpath
                break
            except Exception:
                font = None

    if font is None:
        system_font_names = [
            'Microsoft YaHei',
            'Microsoft YaHei UI',
            'SimHei',
            'SimSun',
            'Noto Sans CJK SC',
            'WenQuanYi Micro Hei',
            'Arial Unicode MS',
        ]
        for name in system_font_names:
            try:
                match = pygame.font.match_font(name)
            except Exception:
                match = None
            if match:
                try:
                    font = pygame.font.Font(match, tile_size)
                    used_path = match
                    break
                except Exception:
                    font = None

    if font is None:
        try:
            font = pygame.font.Font(pygame.font.get_default_font(), tile_size)
        except Exception:
            font = pygame.font.SysFont(None, tile_size)

    return font, used_path


def load_chinese_font(tile_size):
    """专门加载支持中文的字体"""
    # 系统中文字体列表
    chinese_font_names = [
        'Microsoft YaHei',
        'Microsoft YaHei UI', 
        'SimHei',
        'SimSun',
        'Noto Sans CJK SC',
        'WenQuanYi Micro Hei',
        'Source Han Sans SC',
        'PingFang SC',
        'Hiragino Sans GB',
        'STHeiti',
        'DengXian',
        'KaiTi',
        'FangSong',
    ]
    
    font = None
    used_path = None
    
    # 首先尝试系统字体
    for font_name in chinese_font_names:
        try:
            match = pygame.font.match_font(font_name)
        except Exception:
            match = None
        if match:
            try:
                font = pygame.font.Font(match, tile_size)
                # 测试是否能渲染中文
                test_surface = font.render("中", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    used_path = match
                    break
                else:
                    font = None
            except Exception:
                font = None
    
    # 如果系统字体都不行，尝试本地字体目录
    if font is None:
        fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')
        chinese_patterns = ['noto', 'sourcehan', 'wenquan', 'simhei', 'simsun', 'yahei']
        candidates = []
        try:
            if os.path.isdir(fonts_dir):
                for name in os.listdir(fonts_dir):
                    if name.lower().endswith(('.ttf', '.otf')):
                        candidates.append(os.path.join(fonts_dir, name))
        except Exception:
            candidates = []
        
        for pattern in chinese_patterns:
            for fpath in candidates:
                if pattern in os.path.basename(fpath).lower():
                    try:
                        font = pygame.font.Font(fpath, tile_size)
                        # 测试是否能渲染中文
                        test_surface = font.render("中", True, (255, 255, 255))
                        if test_surface.get_width() > 0:
                            used_path = fpath
                            break
                        else:
                            font = None
                    except Exception:
                        font = None
            if font:
                break
    
    return font, used_path


def load_level(fallback_level):
    """尝试从 data/level.txt 加载地图；若不存在则返回 fallback_level（list of str）。"""
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'level.txt')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]
                if lines:
                    return lines
        except Exception:
            pass
    # 如果没有地图文件，则生成一个简单的地牢作为回退
    try:
        w = len(fallback_level[0]) if fallback_level and len(fallback_level) > 0 else 24
        h = len(fallback_level) if fallback_level and len(fallback_level) > 0 else 9
        return generate_dungeon(w, h)
    except Exception:
        return fallback_level


def generate_dungeon(
    width: Optional[int] = None,
    height: Optional[int] = None,
    room_attempts: int = 18,
    num_enemies: int = 8,
    seed: Optional[int] = None,
    min_room=4,
    max_room=12,
    corridor_radius=1,
):
    """生成一个简单的房间+走廊地牢，返回 list[str] 格式的地图。

    算法：随机放置若干矩形房间（不重叠），然后用直线走廊连接房间中心。
    地图用 '#' 表示墙，'.' 表示地面，'@' 表示玩家起始位置，'X' 表示目标。
    """
    import random

    import random as _r

    # 随机化尺寸（如果未提供），并保证最小尺寸
    # 默认生成更大的地图以便房间优先策略能发挥效果
    if width is None or width < 32:
        width = _r.randint(80, 160)
    if height is None or height < 16:
        height = _r.randint(30, 80)

    width = max(16, width)
    height = max(9, height)

    # 初始化全墙
    grid = [['#' for _ in range(width)] for _ in range(height)]

    # If caller didn't tune room_attempts, bias toward more rooms for room-first strategy
    if room_attempts is None:
        room_attempts = 28
    else:
        # allow caller to request more rooms; but if they passed default, slightly increase it
        if room_attempts == 18:
            room_attempts = 26

    rooms = []
    for _ in range(room_attempts):
        # 随机房间尺寸，允许偶尔更大的房间
        # 偏向生成更小的房间（房间更多、更紧凑）
        rw_upper1 = max(6, (min_room + max_room) // 3)
        rw_upper1 = max(rw_upper1, min_room)
        rw_upper2 = min(max_room, width - 6)
        rw_upper2 = max(rw_upper2, min_room)
        rw = _r.choice([_r.randint(min_room, rw_upper1), _r.randint(min_room, rw_upper2)])

        rh_upper1 = max(4, (min_room + max_room) // 4)
        rh_upper1 = max(rh_upper1, min_room)
        rh_upper2 = min(max_room // 2, height - 6)
        rh_upper2 = max(rh_upper2, min_room)
        rh = _r.choice([_r.randint(min_room, rh_upper1), _r.randint(min_room, rh_upper2)])
        # 偶尔扩大房间尺寸，增加多样性
        if _r.random() < 0.18:
            rw = min(width - 6, rw + _r.randint(1, 4))
            rh = min(height - 6, rh + _r.randint(1, 3))
        rx = _r.randint(1, max(1, width - rw - 2))
        ry = _r.randint(1, max(1, height - rh - 2))
        new_room = (rx, ry, rw, rh)
        # 检查重叠（允许更紧密靠近以形成更自然的连通空间）
        ok = True
        for ox, oy, ow, oh in rooms:
            if rx < ox + ow + 2 and rx + rw + 2 > ox and ry < oy + oh + 2 and ry + rh + 2 > oy:
                ok = False
                break
        if ok:
            rooms.append(new_room)
            # carve room interior
            for yy in range(ry, ry + rh):
                for xx in range(rx, rx + rw):
                    grid[yy][xx] = '.'
            # optionally carve a small cleared area around the room to soften walls
            if _r.random() < 0.25:
                for yy in range(max(0, ry - 1), min(height, ry + rh + 1)):
                    for xx in range(max(0, rx - 1), min(width, rx + rw + 1)):
                        if grid[yy][xx] == '#':
                            if _r.random() < 0.5:
                                grid[yy][xx] = '.'

    # 连接房间中心（改为 MST + 若干额外连边以生成回路），并用步进式随机走廊使路径更自然
    def center(r):
        rx, ry, rw, rh = r
        return (rx + rw // 2, ry + rh // 2)

    centers = [center(r) for r in rooms]
    if centers:
        # Build MST (Prim-like)
        remaining = set(range(len(centers)))
        visited = {remaining.pop()}
        edges = []
        while remaining:
            best = None
            best_pair = None
            for a in visited:
                (ax, ay) = centers[a]
                for b in remaining:
                    (bx, by) = centers[b]
                    dist = abs(ax - bx) + abs(ay - by)
                    if best is None or dist < best:
                        best = dist
                        best_pair = (a, b)
            if best_pair is None:
                break
            a, b = best_pair
            edges.append((a, b))
            visited.add(b)
            remaining.remove(b)

        # add a larger number of extra random connections to create more loops (room-first -> many cycles)
        extra = max(1, len(centers) // 2)
        tries = 0
        while extra > 0 and tries < len(centers) * 4:
            tries += 1
            a = _r.randrange(len(centers))
            b = _r.randrange(len(centers))
            if a == b:
                continue
            pair = (min(a, b), max(a, b))
            # avoid duplicate edges
            if pair in [(min(x, y), max(x, y)) for x, y in edges]:
                continue
            edges.append((a, b))
            extra -= 1

        # stepwise corridor drawer with jitter
        def carve_stepwise(x1, y1, x2, y2):
            x, y = x1, y1
            max_steps = abs(x2 - x1) + abs(y2 - y1) + 20
            steps = 0
            while (x, y) != (x2, y2) and steps < max_steps:
                steps += 1
                # carve radius at current
                for dy in range(-corridor_radius, corridor_radius + 1):
                    for dx in range(-corridor_radius, corridor_radius + 1):
                        xx = max(0, min(width - 1, x + dx))
                        yy = max(0, min(height - 1, y + dy))
                        grid[yy][xx] = '.'
                # randomly choose axis to step towards target (gives more organic corridors)
                if x != x2 and y != y2:
                    if _r.random() < 0.5:
                        x += 1 if x2 > x else -1
                    else:
                        y += 1 if y2 > y else -1
                elif x != x2:
                    x += 1 if x2 > x else -1
                elif y != y2:
                    y += 1 if y2 > y else -1
                # small random jitter occasionally
                if _r.random() < 0.08:
                    if _r.random() < 0.5 and x + 1 < width - 1:
                        x += 1
                    elif y + 1 < height - 1:
                        y += 1

        for a, b in edges:
            (x1, y1) = centers[a]
            (x2, y2) = centers[b]
            carve_stepwise(x1, y1, x2, y2)

    # place player @ in first room center, place X in last room center (if rooms found)
    # Place player @ in first room center. Ensure the exit X is placed reliably.
    if rooms:
        px, py = center(rooms[0])
        grid[py][px] = '@'
        # Force exit in the last room center (single source-of-truth)
        tx, ty = center(rooms[-1])
        # if last room equals first room, place exit at a different nearby floor tile
        if (tx, ty) == (px, py):
            # find any floor tile near the room center that's not the player
            found_tile = None
            for ddy in range(-2, 3):
                for ddx in range(-2, 3):
                    nx, ny = tx + ddx, ty + ddy
                    if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == '.' and (nx, ny) != (px, py):
                        found_tile = (nx, ny)
                        break
                if found_tile:
                    break
            if found_tile:
                tx, ty = found_tile
        grid[ty][tx] = 'X'
    else:
        # no rooms: pick sensible defaults for player and exit
        floor_tiles = [(x, y) for y in range(height) for x in range(width) if grid[y][x] == '.']
        if floor_tiles:
            cx, cy = width // 2, height // 2
            # player near center
            best_p = min(floor_tiles, key=lambda t: abs(t[0] - cx) + abs(t[1] - cy))
            grid[best_p[1]][best_p[0]] = '@'
            # exit farthest from player
            best_e = max(floor_tiles, key=lambda t: abs(t[0] - best_p[0]) + abs(t[1] - best_p[1]))
            grid[best_e[1]][best_e[0]] = 'X'
    # place enemies on random floor tiles (not on player or target)
    if seed is not None:
        _r.seed(seed)

    floor_positions = [(x, y) for y in range(height) for x in range(width) if grid[y][x] == '.']
    placed = []
    if floor_positions:
        n = min(num_enemies, len(floor_positions))
        picks = _r.sample(floor_positions, n)
        next_id = 1
        for ex, ey in picks:
            # avoid player/target tile
            if grid[ey][ex] in ('@', 'X'):
                continue
            grid[ey][ex] = 'E'
            placed.append({'id': next_id, 'type': 'Enemy', 'x': ex, 'y': ey, 'hp': 5, 'dir': [1, 0], 'kind': 'basic'})
            next_id += 1

    # persist enemy placements to data/enemies.json so subsequent runs can load them
    try:
        out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'enemies.json')
        data = {'entities': placed}
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # non-fatal if we can't write
        pass

    # Debug: write a snapshot of the generated level for offline inspection (includes E markers)
    try:
        import time as _time

        level_lines = [''.join(row) for row in grid]
        # find exit and player positions
        exit_pos = None
        player_pos = None
        for y, row in enumerate(level_lines):
            if player_pos is None:
                p = row.find('@')
                if p != -1:
                    player_pos = (p, y)
            if exit_pos is None:
                e = row.find('X')
                if e != -1:
                    exit_pos = (e, y)
            if player_pos is not None and exit_pos is not None:
                break
        stamp = seed if seed is not None else int(_time.time() * 1000)
        dbg_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'debug', 'levels')
        try:
            os.makedirs(dbg_dir, exist_ok=True)
        except Exception:
            pass
        dbg_path = os.path.join(dbg_dir, f'last_generated_level_{stamp}.txt')
        with open(dbg_path, 'w', encoding='utf-8') as dbgf:
            dbgf.write('\n'.join(level_lines))
            dbgf.write('\n\n')
            dbgf.write(f'seed={seed} stamp={stamp} exit_pos={exit_pos} player_pos={player_pos}\n')
    except Exception:
        pass

    return [''.join(row) for row in grid]
