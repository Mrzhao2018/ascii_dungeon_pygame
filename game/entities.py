import json
import os
from typing import Dict, List, Optional, Tuple, Any
from game.utils import set_tile

class Entity:
    def __init__(self, x: int, y: int):
        # id will be assigned by EntityManager when added
        self.id: Optional[int] = None
        self.x = x
        self.y = y

    def to_config(self) -> dict:
        d = {'type': self.__class__.__name__, 'x': self.x, 'y': self.y}
        if getattr(self, 'id', None) is not None:
            d['id'] = self.id
        return d

    @classmethod
    def from_config(cls, cfg: dict):
        return cls(int(cfg.get('x', 0)), int(cfg.get('y', 0)))


class Enemy(Entity):
    def __init__(self, x: int, y: int, hp: int = 5, dir=(1, 0), kind: str = 'basic'):
        super().__init__(x, y)
        self.kind = kind
        
        # 敌人类型属性
        self.enemy_stats = self._get_enemy_stats(kind)
        
        # 根据类型设置默认HP
        if hp == 5:  # 如果是默认HP，则根据类型调整
            default_hp = {
                'basic': 5,
                'guard': 8,
                'scout': 3,
                'brute': 12
            }
            self.hp = default_hp.get(kind, 5)
        else:
            self.hp = hp
            
        self.dir = tuple(dir)
        
        # AI状态和寻路
        self.path: List[Tuple[int, int]] = []  # 当前路径
        self.target_pos: Optional[Tuple[int, int]] = None  # 目标位置
        self.patrol_points: List[Tuple[int, int]] = []  # 巡逻点
        self.state: str = 'patrol'  # 状态: patrol, chase, attack
        self.last_player_pos: Optional[Tuple[int, int]] = None  # 上次看到玩家的位置
        self.stuck_counter: int = 0  # 卡住计数器
        self.ai_cooldown: int = 0  # AI决策冷却
        self.move_cooldown: int = 0  # 独立的移动冷却
        
    def _get_enemy_stats(self, kind: str) -> dict:
        """获取敌人类型的属性"""
        stats = {
            'basic': {
                'chase_range': 6,
                'patrol_range': 3,
                'speed': 1,
                'damage': 1,
                'ai_update_interval': 3,  # 大幅提升反应速度
                'move_interval': 6        # 移动间隔：快速
            },
            'guard': {
                'chase_range': 8,
                'patrol_range': 2,
                'speed': 1,
                'damage': 2,
                'ai_update_interval': 2,  # 守卫反应最快
                'move_interval': 5        # 移动间隔：很快
            },
            'scout': {
                'chase_range': 10,
                'patrol_range': 5,
                'speed': 2,
                'damage': 1,
                'ai_update_interval': 1,  # 侦察兵瞬间反应
                'move_interval': 3        # 移动间隔：极快
            },
            'brute': {
                'chase_range': 4,
                'patrol_range': 1,
                'speed': 1,
                'damage': 3,
                'ai_update_interval': 4,  # 重装兵稍慢，但仍然比之前快很多
                'move_interval': 8        # 移动间隔：较慢但仍然可以接受
            }
        }
        return stats.get(kind, stats['basic'])

    def to_config(self) -> dict:
        c = super().to_config()
        c.update({'hp': self.hp, 'dir': list(self.dir), 'kind': self.kind})
        return c

    @classmethod
    def from_config(cls, cfg: dict):
        kind = cfg.get('kind', 'basic')
        
        # 根据类型设置默认HP
        default_hp = {
            'basic': 5,
            'guard': 8,
            'scout': 3,
            'brute': 12
        }
        
        # 如果配置中没有HP或者HP是默认值，使用类型对应的HP
        hp = cfg.get('hp', default_hp.get(kind, 5))
        
        return cls(
            int(cfg.get('x', 0)),
            int(cfg.get('y', 0)),
            hp,
            tuple(cfg.get('dir', (1, 0))),
            kind,
        )


class EntityManager:
    def __init__(self):
        # map pos -> entity and id -> entity
        self.entities_by_pos: Dict[Tuple[int, int], Entity] = {}
        self.entities_by_id: Dict[int, Entity] = {}
        self._next_id = 1
        self.move_cooldown = 0
        # Optional runtime-injected references (set by Game or controllers)
        self.logger = None
        self.game_state = None

    def _prefer_log(self, msg: str, level: str = 'debug'):
        try:
            if getattr(self, 'logger', None):
                try:
                    if level == 'debug' and hasattr(self.logger, 'debug'):
                        self.logger.debug(msg, 'ENTITY')
                        return
                    if level == 'info' and hasattr(self.logger, 'info'):
                        self.logger.info(msg, 'ENTITY')
                        return
                    if level == 'warning' and hasattr(self.logger, 'warning'):
                        self.logger.warning(msg, 'ENTITY')
                        return
                    if level == 'error' and hasattr(self.logger, 'error'):
                        self.logger.error(msg, 'ENTITY')
                        return
                except Exception:
                    pass

            if getattr(self, 'game_state', None) and hasattr(self.game_state, 'game_log'):
                try:
                    self.game_state.game_log(msg)
                    return
                except Exception:
                    pass

            try:
                print(msg)
            except Exception:
                pass
        except Exception:
            try:
                print(msg)
            except Exception:
                pass

    def add(self, ent: Entity):
        if getattr(ent, 'id', None) is None:
            ent.id = self._next_id
            self._next_id += 1
        self.entities_by_pos[(ent.x, ent.y)] = ent
        if ent.id is not None:
            self.entities_by_id[ent.id] = ent

    def get_entity_at(self, x: int, y: int) -> Optional[Entity]:
        return self.entities_by_pos.get((x, y))

    def get_entity_by_id(self, ent_id: int) -> Optional[Entity]:
        return self.entities_by_id.get(ent_id)

    def remove(self, ent_or_id: Any):
        # accept either entity or id
        ent = ent_or_id if isinstance(ent_or_id, Entity) else self.entities_by_id.get(ent_or_id)
        if ent is None:
            return
        key = (ent.x, ent.y)
        if key in self.entities_by_pos:
            del self.entities_by_pos[key]
        if getattr(ent, 'id', None) is not None and ent.id in self.entities_by_id:
            del self.entities_by_id[ent.id]

    def load_from_level(self, level: List[str]):
        # scan for 'E' tiles and create Enemy instances
        for y, row in enumerate(level):
            for x, ch in enumerate(row):
                if ch == 'E':
                    self.add(Enemy(x, y))

    def place_entity_near(self, level: List[str], WIDTH: int, HEIGHT: int, preferred=(8, 4)):
        # if no enemies, place one near preferred or first '.'
        if any(isinstance(e, Enemy) for e in self.entities_by_id.values()):
            return
        px0, py0 = preferred
        found = None
        for r in range(0, max(WIDTH, HEIGHT)):
            stop = False
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx = px0 + dx
                    ny = py0 + dy
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and level[ny][nx] == '.':
                        found = (nx, ny)
                        stop = True
                        break
                if stop:
                    break
            if found:
                break
        if not found:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if level[y][x] == '.':
                        found = (x, y)
                        break
                if found:
                    break
        if found:
            ex, ey = found
            set_tile(level, ex, ey, 'E')
            self.add(Enemy(ex, ey))

    def to_config_list(self) -> List[dict]:
        return [e.to_config() for e in self.entities_by_id.values()]

    def save_to_file(self, path: str):
        data = {'entities': self.to_config_list()}
        try:
            from game.utils import write_json_atomic
            write_json_atomic(path, data, ensure_ascii=False, indent=2)
        except Exception:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, path: str):
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for cfg in data.get('entities', []):
                    t = cfg.get('type', 'Enemy')
                    if t == 'Enemy':
                        e = Enemy.from_config(cfg)
                        # respect id in cfg if present
                        if 'id' in cfg:
                            try:
                                e.id = int(cfg.get('id'))
                                if e.id >= self._next_id:
                                    self._next_id = e.id + 1
                            except Exception:
                                pass
                        self.add(e)
        except Exception:
            pass

    def load_from_file_with_level(self, path: str, level: Optional[List[str]] = None):
        """Load entities from a JSON file. If level is provided, ensure entities are placed on the map:
        - If the target tile is '.', place the entity there (set map char to 'E').
        - Otherwise try to find the nearest '.' and place entity there; if none found, skip the entity.
        """
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # if level provided, clear existing 'E' marks to avoid leftover static enemies
                if level is not None and len(level) > 0:
                    w = len(level[0])
                    h = len(level)
                    for y in range(h):
                        for x in range(w):
                            if level[y][x] == 'E':
                                set_tile(level, x, y, '.')
                for cfg in data.get('entities', []):
                    t = cfg.get('type', 'Enemy')
                    if t == 'Enemy':
                        e = Enemy.from_config(cfg)
                        # respect id in cfg if present
                        if 'id' in cfg:
                            try:
                                e.id = int(cfg.get('id'))
                                if e.id >= self._next_id:
                                    self._next_id = e.id + 1
                            except Exception:
                                pass
                        # If level provided, try to place on a valid '.' tile
                        if level is not None and len(level) > 0:
                            w = len(level[0])
                            h = len(level)
                            ex, ey = int(e.x), int(e.y)

                            def is_empty(x, y):
                                return 0 <= x < w and 0 <= y < h and level[y][x] == '.'

                            def has_free_neighbor(x, y):
                                for dxn, dyn in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                                    nxn, nyn = x + dxn, y + dyn
                                    if 0 <= nxn < w and 0 <= nyn < h and level[nyn][nxn] == '.':
                                        return True
                                return False

                            if not is_empty(ex, ey):
                                # search for nearest '.' using increasing radius, prefer tiles with a free neighbor
                                found = None
                                found_any = None
                                for r in range(1, max(w, h)):
                                    stop = False
                                    for dy in range(-r, r + 1):
                                        for dx in range(-r, r + 1):
                                            nx = ex + dx
                                            ny = ey + dy
                                            if is_empty(nx, ny):
                                                # prefer tiles that have at least one free neighbor
                                                if has_free_neighbor(nx, ny):
                                                    found = (nx, ny)
                                                    stop = True
                                                    break
                                                if found_any is None:
                                                    found_any = (nx, ny)
                                        if stop:
                                            break
                                    if found:
                                        break
                                if not found and found_any:
                                    found = found_any
                                if found:
                                    ex, ey = found
                                    e.x, e.y = ex, ey
                                    set_tile(level, ex, ey, 'E')
                                else:
                                    # can't place entity, skip
                                    continue
                            else:
                                # tile is empty; if it has no free neighbor, try to find a better spot
                                if not has_free_neighbor(ex, ey):
                                    # look for a nearby empty tile that has a free neighbor
                                    found = None
                                    for r in range(1, max(w, h)):
                                        stop = False
                                        for dy in range(-r, r + 1):
                                            for dx in range(-r, r + 1):
                                                nx = ex + dx
                                                ny = ey + dy
                                                if is_empty(nx, ny) and has_free_neighbor(nx, ny):
                                                    found = (nx, ny)
                                                    stop = True
                                                    break
                                            if stop:
                                                break
                                        if found:
                                            break
                                    if found:
                                        ex, ey = found
                                        e.x, e.y = ex, ey
                                        set_tile(level, ex, ey, 'E')
                                    else:
                                        # accept original empty tile
                                        set_tile(level, ex, ey, 'E')
                                else:
                                    # tile is empty and has free neighbor, mark it as entity
                                    set_tile(level, ex, ey, 'E')
                        # finally add entity to manager
                        self.add(e)
        except Exception:
            pass

    def update(
        self, level: List[str], player_pos: Tuple[int, int], WIDTH: int, HEIGHT: int, move_interval_frames: int = 15
    ):
        """Update movable entities (currently only Enemy). Returns events list."""
        events: List[dict] = []

        # Ensure map tiles reflect entity positions; fix mismatches where an entity exists but map tile isn't 'E'
        try:
            for (ex, ey), ent in list(self.entities_by_pos.items()):
                if 0 <= ey < len(level) and 0 <= ex < len(level[0]):
                    if level[ey][ex] != 'E':
                        # diagnostic and fix (use logger if available)
                        try:
                            log_msg = f'[entity-debug] fixing map tile for entity at ({ex},{ey}) from "{level[ey][ex]}" to "E"'
                            self._prefer_log(log_msg, level='debug')
                        except Exception:
                            pass
                        set_tile(level, ex, ey, 'E')
        except Exception:
            pass

        # Update enemies with improved AI - 不再使用全局冷却
        for (ex, ey), ent in list(self.entities_by_pos.items()):
            if not isinstance(ent, Enemy):
                continue
            
            # 每个敌人独立的移动冷却
            ent.move_cooldown += 1
            move_threshold = ent.enemy_stats.get('move_interval', 6)
            
            if ent.move_cooldown < move_threshold:
                continue  # 还没到这个敌人的移动时间
            
            ent.move_cooldown = 0  # 重置冷却
            
            # Update AI state and get next action
            action = self._update_enemy_ai(ent, level, player_pos, WIDTH, HEIGHT)
            
            # Process the action
            if action['type'] == 'attack':
                events.append({
                    'type': 'attack', 
                    'pos': action['target'], 
                    'damage': ent.enemy_stats['damage'], 
                    'attacker_id': ent.id
                })
            elif action['type'] == 'move':
                success = self._move_entity(ent, action['target'], level, WIDTH, HEIGHT)
                if not success:
                    ent.stuck_counter += 1
                    if ent.stuck_counter > 3:
                        # 如果连续卡住，重新规划路径或改变状态
                        ent.path = []
                        ent.stuck_counter = 0
                        if ent.state == 'chase':
                            ent.state = 'patrol'
                else:
                    ent.stuck_counter = 0

        return events

    def _update_enemy_ai(self, enemy: Enemy, level: List[str], player_pos: Tuple[int, int], WIDTH: int, HEIGHT: int) -> dict:
        """更新敌人AI逻辑，返回行动决策"""
        px, py = player_pos
        ex, ey = enemy.x, enemy.y
        
        # 计算与玩家的距离
        distance = abs(px - ex) + abs(py - ey)
        chase_range = enemy.enemy_stats['chase_range']
        
        # 检查是否能立即攻击玩家（攻击判断优先，无冷却）
        attack_positions = [(ex + dx, ey + dy) for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]]
        if (px, py) in attack_positions:
            return {'type': 'attack', 'target': (px, py)}
        
        # AI更新间隔控制（仅对移动和规划行为）
        enemy.ai_cooldown += 1
        ai_threshold = enemy.enemy_stats.get('ai_update_interval', 3)
        
        if enemy.ai_cooldown < ai_threshold:
            # 没到AI更新时间，执行当前路径
            if enemy.path:
                next_pos = enemy.path[0]
                return {'type': 'move', 'target': next_pos}
            else:
                return {'type': 'idle'}
        
        enemy.ai_cooldown = 0
        
        # 状态机逻辑
        if distance <= chase_range and self._has_line_of_sight(enemy, player_pos, level, WIDTH, HEIGHT):
            # 进入追击状态
            enemy.state = 'chase'
            enemy.last_player_pos = (px, py)
            # 使用寻路算法计算到玩家的路径
            enemy.path = self._find_path((ex, ey), (px, py), level, WIDTH, HEIGHT)
        elif enemy.state == 'chase' and enemy.last_player_pos:
            # 继续追击上次看到玩家的位置
            if (ex, ey) == enemy.last_player_pos:
                # 到达目标位置但没找到玩家，切换到巡逻
                enemy.state = 'patrol'
                enemy.last_player_pos = None
                enemy.path = []
            elif not enemy.path:
                # 重新计算到上次位置的路径
                enemy.path = self._find_path((ex, ey), enemy.last_player_pos, level, WIDTH, HEIGHT)
        else:
            # 巡逻状态
            enemy.state = 'patrol'
            if not enemy.path:
                # 生成巡逻路径
                enemy.path = self._generate_patrol_path(enemy, level, WIDTH, HEIGHT)
        
        # 执行路径中的下一步
        if enemy.path:
            next_pos = enemy.path.pop(0)
            return {'type': 'move', 'target': next_pos}
        else:
            # 没有路径，随机移动
            return self._get_random_move(enemy, level, WIDTH, HEIGHT)

    def _has_line_of_sight(self, enemy: Enemy, target_pos: Tuple[int, int], level: List[str], WIDTH: int, HEIGHT: int) -> bool:
        """检查敌人到目标是否有视线"""
        ex, ey = enemy.x, enemy.y
        tx, ty = target_pos
        
        # 简单的直线视线检查
        dx = abs(tx - ex)
        dy = abs(ty - ey)
        steps = max(dx, dy)
        
        if steps == 0:
            return True
        
        x_step = (tx - ex) / steps
        y_step = (ty - ey) / steps
        
        for i in range(1, steps):
            check_x = int(ex + x_step * i)
            check_y = int(ey + y_step * i)
            
            if 0 <= check_x < WIDTH and 0 <= check_y < HEIGHT:
                if level[check_y][check_x] in ['#', 'E']:  # 墙壁或其他敌人阻挡视线
                    return False
            else:
                return False
        
        return True

    def _find_path(self, start: Tuple[int, int], goal: Tuple[int, int], level: List[str], WIDTH: int, HEIGHT: int) -> List[Tuple[int, int]]:
        """使用简单BFS寻路算法"""
        if start == goal:
            return []
        
        from collections import deque
        queue = deque([(start, [])])
        visited = {start}
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        max_path_length = 20  # 限制路径长度避免过长计算
        
        while queue:
            (x, y), path = queue.popleft()
            
            if len(path) >= max_path_length:
                continue
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                if (nx, ny) == goal:
                    return path + [(nx, ny)]
                
                if (nx, ny) not in visited and 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                    tile = level[ny][nx]
                    if tile in ['.', '@']:  # 可以移动的格子
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))
        
        return []  # 没找到路径

    def _generate_patrol_path(self, enemy: Enemy, level: List[str], WIDTH: int, HEIGHT: int) -> List[Tuple[int, int]]:
        """生成巡逻路径"""
        ex, ey = enemy.x, enemy.y
        patrol_range = enemy.enemy_stats['patrol_range']
        
        # 随机选择一个巡逻目标点
        import random
        attempts = 10
        for _ in range(attempts):
            target_x = ex + random.randint(-patrol_range, patrol_range)
            target_y = ey + random.randint(-patrol_range, patrol_range)
            
            if (0 <= target_x < WIDTH and 0 <= target_y < HEIGHT and 
                level[target_y][target_x] == '.' and (target_x, target_y) != (ex, ey)):
                
                path = self._find_path((ex, ey), (target_x, target_y), level, WIDTH, HEIGHT)
                if path:
                    return path
        
        return []

    def _get_random_move(self, enemy: Enemy, level: List[str], WIDTH: int, HEIGHT: int) -> dict:
        """获取随机移动方向"""
        ex, ey = enemy.x, enemy.y
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        import random
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and level[ny][nx] == '.':
                return {'type': 'move', 'target': (nx, ny)}
        
        return {'type': 'idle'}

    def _move_entity(self, entity: Entity, target_pos: Tuple[int, int], level: List[str], WIDTH: int, HEIGHT: int) -> bool:
        """移动实体到目标位置"""
        old_x, old_y = entity.x, entity.y
        new_x, new_y = target_pos
        
        # 检查目标位置是否有效
        if not (0 <= new_x < WIDTH and 0 <= new_y < HEIGHT):
            return False
        
        if level[new_y][new_x] != '.':
            return False
        
        # 更新地图
        set_tile(level, old_x, old_y, '.')
        set_tile(level, new_x, new_y, 'E')
        
        # 更新实体位置
        del self.entities_by_pos[(old_x, old_y)]
        entity.x, entity.y = new_x, new_y
        self.entities_by_pos[(new_x, new_y)] = entity
        
        return True
