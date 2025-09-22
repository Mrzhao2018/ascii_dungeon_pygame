"""
Floor management and generation
"""
import os
import time
from typing import List, Tuple, Optional
from game import utils, entities, dialogs as dialogs_mod


class FloorManager:
    """Manages floor generation, transitions, and state"""
    
    def __init__(self, config, game_state):
        self.config = config
        self.game_state = game_state
    
    def generate_initial_level(self) -> List[str]:
        """Generate the initial level based on configuration"""
        if self.config.regen:
            print('[FloorManager] --regen flag detected: forcing dungeon regeneration')
            return utils.generate_dungeon(
                self.config.map_width, 
                self.config.map_height, 
                seed=int(time.time() * 1000)
            )
        else:
            # If user specified map dimensions, generate new map
            if hasattr(self.config, 'map_w') or hasattr(self.config, 'map_h'):
                return utils.generate_dungeon(self.config.map_width, self.config.map_height)
            else:
                # Try to load from external file, fallback to generation
                return utils.load_level(None)
    
    def setup_level(self, level: List[str]):
        """Setup a level with entities and NPCs"""
        self.game_state.set_level(level)
        
        # Setup entity manager
        entity_mgr = entities.EntityManager()
        enemies_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'enemies.json')
        
        # Clear existing 'E' marks if enemies file exists
        if os.path.exists(enemies_path):
            for y, row in enumerate(level):
                for x, ch in enumerate(row):
                    if ch == 'E':
                        utils.set_tile(level, x, y, '.')
        
        # Load entities
        entity_mgr.load_from_file(enemies_path, level=level)
        if not any(isinstance(e, entities.Enemy) for e in entity_mgr.entities_by_id.values()):
            entity_mgr.load_from_level(level)
            entity_mgr.place_entity_near(level, self.game_state.width, self.game_state.height)
        
        # Load NPCs
        npcs = dialogs_mod.load_npcs(level, self.game_state.width, self.game_state.height)
        
        # Add fallback NPC if none exist
        if all('N' not in row for row in level):
            # Find player position to place NPC nearby
            player_pos = self.find_player(level)
            if player_pos:
                px, py = player_pos
                nx = min(px + 2, self.game_state.width - 2)
                ny = py
                if level[ny][nx] == '.':
                    utils.set_tile(level, nx, ny, 'N')
        
        # Compute exit position
        self.game_state.compute_exit_pos()
        
        return entity_mgr, npcs
    
    def find_player(self, level: List[str]) -> Optional[Tuple[int, int]]:
        """Find player position in level"""
        for y, row in enumerate(level):
            x = row.find("@")
            if x != -1:
                return x, y
        return None
    
    def process_floor_transition(self) -> Tuple[Optional[List[str]], Optional[entities.EntityManager], Optional[dict], Optional[Tuple[int, int]]]:
        """Process a floor transition if ready. Returns (level, entity_mgr, npcs, new_pos) or (None, None, None, None)"""
        if not self.game_state.floor_transition:
            return None, None, None, None
        
        if not self.game_state.update_floor_transition(0):  # Check if ready
            return None, None, None, None
        
        # Execute floor generation
        try:
            params = self.game_state.pending_floor or {}
            gen_seed = params.get('seed')
            floor_number = params.get('floor', 2)
            gen_width = params.get('width', self.config.map_width)
            gen_height = params.get('height', self.config.map_height)
            gen_rooms = params.get('rooms', self.config.rooms)
            gen_enemies = params.get('enemies', self.config.enemies)
            gen_min_room = params.get('min_room', self.config.min_room)
            gen_max_room = params.get('max_room', self.config.max_room)
            gen_corridor_radius = params.get('corridor_radius', self.config.corridor_radius)
            
            self.game_state.write_exit_log(f'Generating floor {floor_number} with seed {gen_seed}, size {gen_width}x{gen_height}')
            
            # Generate new level
            level = utils.generate_dungeon(
                gen_width, gen_height, 
                room_attempts=gen_rooms, 
                num_enemies=gen_enemies, 
                seed=gen_seed, 
                min_room=gen_min_room, 
                max_room=gen_max_room, 
                corridor_radius=gen_corridor_radius
            )
            
            # Setup the level
            entity_mgr, npcs = self.setup_level(level)
            
            # Write debug snapshots
            self._write_floor_snapshots(level, floor_number)
            
            # Update player position
            new_pos = self.find_player(level)
            
            # Complete transition
            self.game_state.complete_floor_transition()
            
            return level, entity_mgr, npcs, new_pos
            
        except Exception as e:
            self.game_state.game_log(f'floor transition generation failed: {e}')
            self.game_state.complete_floor_transition()
            return None, None, None, None
    
    def _write_floor_snapshots(self, level: List[str], floor_number: int):
        """Write debug snapshots for the floor"""
        # Find player position
        new_pos = self.find_player(level)
        
        try:
            dbg_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'debug', 'maps')
            os.makedirs(dbg_dir, exist_ok=True)
            
            # Pre-entities snapshot
            dbg_path = os.path.join(dbg_dir, f'last_level_floor_{floor_number}.txt')
            with open(dbg_path, 'w', encoding='utf-8') as df:
                df.write('\n'.join(level))
                df.write('\n\n')
                df.write(f'floor={floor_number} exit_pos={self.game_state.exit_pos} player_pos={new_pos}\n')
            self.game_state.write_exit_log(f'Wrote floor snapshot: {dbg_path}')
            
        except Exception as e:
            self.game_state.write_exit_log(f'Failed to write floor snapshot: {e}')
        
        try:
            # Post-entities snapshot
            dbg_path2 = os.path.join(dbg_dir, f'last_level_floor_{floor_number}_after_entities.txt')
            with open(dbg_path2, 'w', encoding='utf-8') as df2:
                df2.write('\n'.join(level))
                df2.write('\n\n')
                df2.write(f'floor={floor_number} exit_pos={self.game_state.exit_pos} player_pos={new_pos}\n')
            self.game_state.write_exit_log(f'Wrote post-entity floor snapshot: {dbg_path2}')
            
        except Exception as e:
            self.game_state.write_exit_log(f'Failed to write post-entity floor snapshot: {e}')
    
    def write_initial_snapshot(self, level: List[str]):
        """Write snapshot for the initial floor"""
        try:
            player_pos = self.find_player(level)
            dbg_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'debug', 'maps')
            os.makedirs(dbg_dir, exist_ok=True)
            dbg_path = os.path.join(dbg_dir, f'last_level_floor_1.txt')
            with open(dbg_path, 'w', encoding='utf-8') as df:
                df.write('\n'.join(level))
                df.write('\n\n')
                df.write(f'exit_pos={self.game_state.exit_pos} player_pos={player_pos}\n')
        except Exception:
            pass