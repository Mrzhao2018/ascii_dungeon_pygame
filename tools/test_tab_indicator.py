#!/usr/bin/env python3
"""
Test the Tab indicator logic to ensure it can find the exit
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_tab_indicator_logic():
    """Test the Tab key indicator logic"""
    
    print("=== TESTING TAB INDICATOR LOGIC ===")
    
    from game import utils
    
    # Generate a test level
    level = utils.generate_dungeon(50, 20, seed=12345)
    
    print(f"Generated test level: {len(level[0])}x{len(level)}")
    
    # Find the exit using the same logic as main.py
    print("\n--- Testing exit_pos computation (same as main.py) ---")
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
    
    print(f"exit_pos result: {exit_pos}")
    
    # Test Tab indicator logic (same as main.py)
    print("\n--- Testing Tab indicator logic (same as main.py) ---")
    TILE_SIZE = 24
    
    try:
        # Simulate keys_state[pygame.K_TAB] being True
        keys_tab_pressed = True
        
        if keys_tab_pressed:
            # Compass: 指向当前楼层记录的 exit_pos（若存在）
            if exit_pos is not None:
                ex, ey = exit_pos
                pending_target = (ex * TILE_SIZE + TILE_SIZE//2, ey * TILE_SIZE + TILE_SIZE//2)
                print(f"Tab pressed: exit_pos={exit_pos} -> pending_target={pending_target}")
            else:
                pending_target = None
                print("Tab pressed: exit_pos is None -> pending_target=None")
        else:
            pending_target = None
            print("Tab not pressed -> pending_target=None")
    except Exception as e:
        pending_target = None
        print(f"Exception in Tab logic: {e}")
    
    print(f"Final pending_target: {pending_target}")
    
    # Verify the level actually contains 'X'
    print("\n--- Manual verification ---")
    x_count = sum(row.count('X') for row in level)
    print(f"Total 'X' count in level: {x_count}")
    
    if x_count > 0:
        print("Level contents around exit:")
        ex, ey = exit_pos
        for dy in range(-2, 3):
            y = ey + dy
            if 0 <= y < len(level):
                row = level[y]
                start = max(0, ex - 5)
                end = min(len(row), ex + 6)
                segment = row[start:end]
                print(f"  Row {y:2d}: ...{segment}...")
    
    print("\n=== TEST SUMMARY ===")
    if exit_pos is not None and pending_target is not None:
        print("✅ Tab indicator logic works correctly")
        print("✅ exit_pos is computed successfully")
        print("✅ pending_target is set when Tab is pressed")
    elif exit_pos is None:
        print("❌ exit_pos computation failed - no 'X' found")
    elif pending_target is None:
        print("❌ pending_target not set despite exit_pos being valid")
    else:
        print("❌ Unknown issue with Tab indicator logic")

if __name__ == '__main__':
    test_tab_indicator_logic()