#!/usr/bin/env python3
"""
测试Tab键切换功能
"""

import os
import sys
import pygame

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import GameConfig
from game.state import GameState
from game.input import InputHandler

def test_tab_toggle():
    """Test Tab key toggle functionality"""
    print("=== TESTING TAB TOGGLE FUNCTIONALITY ===")
    
    # Initialize pygame
    pygame.init()
    
    # Create test level with exit
    test_level = [
        "#" * 30,
        "#" + "." * 28 + "#",
        "#" + "." * 28 + "#",
        "#" + "." * 13 + "X" + "." * 14 + "#",
        "#" + "." * 28 + "#",
        "#" * 30,
    ]
    
    print(f"Generated test level: {len(test_level[0])}x{len(test_level)}")
    
    # Create game components
    config = GameConfig()
    game_state = GameState(config)
    input_handler = InputHandler(config, game_state)
    
    # Set up level
    game_state.level = test_level
    game_state.width = len(test_level[0])
    game_state.height = len(test_level)
    
    # Compute initial exit position
    game_state.compute_exit_pos()
    print(f"Initial exit_pos: {game_state.exit_pos}")
    print(f"Initial pending_target: {game_state.pending_target}")
    
    # Test 1: First Tab press (should show indicator)
    print("\n--- Test 1: First Tab press (show indicator) ---")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
    result = input_handler.handle_keydown(event)
    print(f"After first Tab press:")
    print(f"  pending_target: {game_state.pending_target}")
    print(f"  Expected: should show exit indicator")
    
    # Test 2: Second Tab press (should hide indicator)
    print("\n--- Test 2: Second Tab press (hide indicator) ---")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
    result = input_handler.handle_keydown(event)
    print(f"After second Tab press:")
    print(f"  pending_target: {game_state.pending_target}")
    print(f"  Expected: None (hidden)")
    
    # Test 3: Third Tab press (should show indicator again)
    print("\n--- Test 3: Third Tab press (show indicator again) ---")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
    result = input_handler.handle_keydown(event)
    print(f"After third Tab press:")
    print(f"  pending_target: {game_state.pending_target}")
    print(f"  Expected: should show exit indicator again")
    
    # Test 4: Test with no exit_pos
    print("\n--- Test 4: Tab with no exit_pos ---")
    game_state.exit_pos = None
    game_state.pending_target = None
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
    result = input_handler.handle_keydown(event)
    print(f"After Tab with no exit_pos:")
    print(f"  exit_pos: {game_state.exit_pos} (should be recomputed)")
    print(f"  pending_target: {game_state.pending_target}")
    
    print("\n=== TEST SUMMARY ===")
    print("✅ Tab key toggle functionality tested")
    print("✅ Should show/hide indicator on alternating presses")
    print("✅ Should auto-recompute exit_pos when needed")

if __name__ == "__main__":
    test_tab_toggle()