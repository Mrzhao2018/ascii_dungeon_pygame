#!/usr/bin/env python3
"""
Debug script to trace floor transition and exit_pos computation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from game import utils, entities, dialogs as dialogs_mod

def test_floor_transition_detailed():
    """Simulate the exact floor transition logic from main.py"""
    
    print("=== DEBUGGING FLOOR TRANSITION LOGIC ===")
    
    # Simulate floor 2 generation with same parameters as main.py
    floor_number = 2
    mw, mh = 100, 40  # typical map size
    rooms = 18
    enemies = 8
    min_room = 5
    max_room = 16
    corridor_radius = 1
    
    # Use a fixed seed to reproduce the issue
    import time
    gen_seed = int(time.time() * 1000)
    print(f"Using seed: {gen_seed}")
    
    # Step 1: Generate dungeon (same as main.py)
    print("\n--- Step 1: Generate dungeon ---")
    level = utils.generate_dungeon(mw, mh, room_attempts=rooms, num_enemies=enemies, 
                                 seed=gen_seed, min_room=min_room, max_room=max_room, 
                                 corridor_radius=corridor_radius)
    
    WIDTH = len(level[0]) if level else 0
    HEIGHT = len(level)
    print(f"Generated level: {WIDTH}x{HEIGHT}")
    
    # Check for 'X' immediately after generation
    exit_count = sum(row.count('X') for row in level)
    print(f"Exit 'X' count after generation: {exit_count}")
    
    if exit_count > 0:
        for y, row in enumerate(level):
            x = row.find('X')
            if x != -1:
                print(f"Found 'X' at ({x}, {y})")
                break
    
    # Step 2: Entity management (same as main.py)
    print("\n--- Step 2: Entity management ---")
    entity_mgr = entities.EntityManager()
    enemies_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'enemies.json')
    
    # Clear existing 'E' marks (same as main.py)
    if os.path.exists(enemies_path):
        e_count_before = sum(row.count('E') for row in level)
        print(f"'E' count before clearing: {e_count_before}")
        
        for y, row in enumerate(level):
            for x, ch in enumerate(row):
                if ch == 'E':
                    # Use main.py's set_tile logic
                    old_ch = level[y][x]
                    utils.set_tile(level, x, y, '.')
                    new_ch = level[y][x]
                    print(f"Cleared 'E' at ({x},{y}): '{old_ch}' -> '{new_ch}'")
        
        e_count_after = sum(row.count('E') for row in level)
        print(f"'E' count after clearing: {e_count_after}")
    
    # Check 'X' count after entity clearing
    exit_count_after_clear = sum(row.count('X') for row in level)
    print(f"Exit 'X' count after entity clearing: {exit_count_after_clear}")
    
    # Load entities
    entity_mgr.load_from_file(enemies_path, level=level)
    if not any(isinstance(e, entities.Enemy) for e in entity_mgr.entities_by_id.values()):
        entity_mgr.load_from_level(level)
        entity_mgr.place_entity_near(level, WIDTH, HEIGHT)
    
    # Check 'X' count after entity loading
    exit_count_after_entities = sum(row.count('X') for row in level)
    print(f"Exit 'X' count after entity loading: {exit_count_after_entities}")
    
    # Step 3: NPC loading (same as main.py)
    print("\n--- Step 3: NPC loading ---")
    npcs = dialogs_mod.load_npcs(level, WIDTH, HEIGHT)
    
    # Check 'X' count after NPC loading
    exit_count_after_npcs = sum(row.count('X') for row in level)
    print(f"Exit 'X' count after NPC loading: {exit_count_after_npcs}")
    
    # Step 4: Compute exit_pos (same as main.py)
    print("\n--- Step 4: Compute exit_pos ---")
    try:
        found = None
        for yrow, row in enumerate(level):
            xcol = row.find('X')
            if xcol != -1:
                found = (xcol, yrow)
                print(f"Found 'X' for exit_pos at ({xcol}, {yrow})")
                break
        exit_pos = found
    except Exception as e:
        print(f"Exception computing exit_pos: {e}")
        exit_pos = None
    
    print(f"Final exit_pos: {exit_pos}")
    
    # Step 5: Write debug snapshots with detailed info
    print("\n--- Step 5: Write debug snapshots ---")
    try:
        # Find player position
        new_pos = None
        for y, row in enumerate(level):
            x = row.find('@')
            if x != -1:
                new_pos = (x, y)
                break
        
        dbg_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'debug')
        os.makedirs(dbg_dir, exist_ok=True)
        
        # Pre-NPC snapshot
        dbg_path = os.path.join(dbg_dir, f'debug_floor_{floor_number}_detailed.txt')
        with open(dbg_path, 'w', encoding='utf-8') as df:
            df.write('\n'.join(level))
            df.write('\n\n')
            df.write(f'floor={floor_number} exit_pos={exit_pos} player_pos={new_pos}\n')
            df.write(f'exit_count_generation={exit_count}\n')
            df.write(f'exit_count_after_entity_clear={exit_count_after_clear}\n')
            df.write(f'exit_count_after_entities={exit_count_after_entities}\n')
            df.write(f'exit_count_after_npcs={exit_count_after_npcs}\n')
            df.write(f'seed={gen_seed}\n')
        
        print(f"Wrote detailed debug snapshot: {dbg_path}")
        
    except Exception as e:
        print(f"Exception writing debug snapshot: {e}")
    
    # Step 6: Manual scan for any 'X' in final level
    print("\n--- Step 6: Final level scan ---")
    final_x_positions = []
    for y, row in enumerate(level):
        for x, ch in enumerate(row):
            if ch == 'X':
                final_x_positions.append((x, y))
    
    print(f"All 'X' positions in final level: {final_x_positions}")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Seed: {gen_seed}")
    print(f"Level size: {WIDTH}x{HEIGHT}")
    print(f"Exit count after generation: {exit_count}")
    print(f"Exit count after entity clearing: {exit_count_after_clear}")
    print(f"Exit count after entity loading: {exit_count_after_entities}")
    print(f"Exit count after NPC loading: {exit_count_after_npcs}")
    print(f"Computed exit_pos: {exit_pos}")
    print(f"All final 'X' positions: {final_x_positions}")
    
    if exit_count > 0 and len(final_x_positions) == 0:
        print("❌ BUG DETECTED: 'X' was generated but disappeared during processing!")
    elif exit_count > 0 and exit_pos is None:
        print("❌ BUG DETECTED: 'X' exists but exit_pos computation failed!")
    elif exit_count == 0:
        print("❌ BUG DETECTED: Generator failed to create 'X'!")
    else:
        print("✅ No obvious bug detected in this run")

if __name__ == '__main__':
    test_floor_transition_detailed()