from typing import Dict, Tuple, List, Any, Optional, Callable
import json
import os
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
        self.hp = hp
        self.dir = tuple(dir)
        self.kind = kind

    def to_config(self) -> dict:
        c = super().to_config()
        c.update({'hp': self.hp, 'dir': list(self.dir), 'kind': self.kind})
        return c

    @classmethod
    def from_config(cls, cfg: dict):
        return cls(int(cfg.get('x', 0)), int(cfg.get('y', 0)), int(cfg.get('hp', 5)), tuple(cfg.get('dir', (1, 0))), cfg.get('kind', 'basic'))


class EntityManager:
    def __init__(self):
        # map pos -> entity and id -> entity
        self.entities_by_pos: Dict[Tuple[int, int], Entity] = {}
        self.entities_by_id: Dict[int, Entity] = {}
        self._next_id = 1
        self.move_cooldown = 0

    def add(self, ent: Entity):
        if getattr(ent, 'id', None) is None:
            ent.id = self._next_id
            self._next_id += 1
        self.entities_by_pos[(ent.x, ent.y)] = ent
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
        if getattr(ent, 'id', None) in self.entities_by_id:
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
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
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

    def load_from_file(self, path: str, level: Optional[List[str]] = None):
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
                                for dxn, dyn in ((1,0),(-1,0),(0,1),(0,-1)):
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
                                    for dy in range(-r, r+1):
                                        for dx in range(-r, r+1):
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
                                        for dy in range(-r, r+1):
                                            for dx in range(-r, r+1):
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

    def update(self, level: List[str], player_pos: Tuple[int, int], WIDTH: int, HEIGHT: int, move_interval_frames: int = 15):
        """Update movable entities (currently only Enemy). Returns events list."""
        events: List[dict] = []

        # Ensure map tiles reflect entity positions; fix mismatches where an entity exists but map tile isn't 'E'
        try:
            for (ex, ey), ent in list(self.entities_by_pos.items()):
                if 0 <= ey < len(level) and 0 <= ex < len(level[0]):
                    if level[ey][ex] != 'E':
                        # diagnostic and fix
                        print(f'[entity-debug] fixing map tile for entity at ({ex},{ey}) from "{level[ey][ex]}" to "E"')
                        set_tile(level, ex, ey, 'E')
        except Exception:
            pass

        self.move_cooldown += 1
        if self.move_cooldown < move_interval_frames:
            return events
        self.move_cooldown = 0

        # iterate over a snapshot of positions to allow modifications
        for (ex, ey), ent in list(self.entities_by_pos.items()):
            if not isinstance(ent, Enemy):
                continue
            px, py = player_pos

            # If next step in current direction is player, attack
            dx, dy = ent.dir
            nx, ny = ex + dx, ey + dy
            if (nx, ny) == (px, py):
                events.append({'type': 'attack', 'pos': (px, py), 'damage': 1, 'attacker_id': ent.id})
                continue

            # simple chase behavior
            chase_range = 6
            dist = abs(px - ex) + abs(py - ey)
            moved = False
            if dist <= chase_range:
                # prefer x move then y move
                if px != ex:
                    step_x = 1 if px > ex else -1
                    tx, ty = ex + step_x, ey
                    if 0 <= tx < WIDTH and 0 <= ty < HEIGHT and level[ty][tx] == '.':
                        set_tile(level, ex, ey, '.')
                        set_tile(level, tx, ty, 'E')
                        # update pos map
                        del self.entities_by_pos[(ex, ey)]
                        ent.x, ent.y = tx, ty
                        self.entities_by_pos[(tx, ty)] = ent
                        moved = True
                if not moved and py != ey:
                    step_y = 1 if py > ey else -1
                    tx, ty = ex, ey + step_y
                    if 0 <= tx < WIDTH and 0 <= ty < HEIGHT and level[ty][tx] == '.':
                        set_tile(level, ex, ey, '.')
                        set_tile(level, tx, ty, 'E')
                        del self.entities_by_pos[(ex, ey)]
                        ent.x, ent.y = tx, ty
                        self.entities_by_pos[(tx, ty)] = ent
                        moved = True

            # fallback: patrol move
            if not moved:
                dx, dy = ent.dir
                nx, ny = ex + dx, ey + dy
                can_move = 0 <= nx < WIDTH and 0 <= ny < HEIGHT and level[ny][nx] == '.'
                if (nx, ny) == (px, py):
                    events.append({'type': 'attack', 'pos': (px, py), 'damage': 1, 'attacker_id': ent.id})
                elif can_move:
                    set_tile(level, ex, ey, '.')
                    set_tile(level, nx, ny, 'E')
                    del self.entities_by_pos[(ex, ey)]
                    ent.x, ent.y = nx, ny
                    self.entities_by_pos[(nx, ny)] = ent
                else:
                    # debug: if enemy cannot move and has no free neighbor, print diagnostic
                    neigh = {}
                    for dxn, dyn in ((1,0),(-1,0),(0,1),(0,-1)):
                        txn, tyn = ex + dxn, ey + dyn
                        if 0 <= tyn < HEIGHT and 0 <= txn < WIDTH:
                            neigh[(txn, tyn)] = level[tyn][txn]
                        else:
                            neigh[(txn, tyn)] = None
                    free_neighbors = [p for p, ch in neigh.items() if ch == '.']
                    if not free_neighbors:
                        print(f'[entity-debug] stuck enemy at ({ex},{ey}) tile={level[ey][ex]} neigh={neigh} hp={getattr(ent,"hp",None)} dir={ent.dir}')
                    ent.dir = (-dx, -dy)

        return events
