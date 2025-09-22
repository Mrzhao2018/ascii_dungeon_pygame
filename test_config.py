#!/usr/bin/env python3
"""
Test configuration file loading
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.config import GameConfig

def test_config_loading():
    """Test if configuration values are loaded correctly"""
    print("Testing configuration file loading...")
    
    # Test without config file
    print("\n1. Default configuration:")
    sys.argv = ['test.py']
    config1 = GameConfig()
    print(f"  Map size: {config1.map_width}x{config1.map_height}")
    print(f"  Rooms: {config1.rooms}")
    print(f"  Enemies: {config1.enemies}")
    print(f"  Debug: {config1.debug_mode}")
    
    # Test with config file
    print("\n2. Configuration from game.json:")
    sys.argv = ['test.py', '--config', 'game.json']
    config2 = GameConfig()
    print(f"  Map size: {config2.map_width}x{config2.map_height}")
    print(f"  Rooms: {config2.rooms}")
    print(f"  Enemies: {config2.enemies}")
    print(f"  Debug: {config2.debug_mode}")
    
    # Test command line override
    print("\n3. Command line override:")
    sys.argv = ['test.py', '--config', 'game.json', '--map-width', '150', '--debug']
    config3 = GameConfig()
    print(f"  Map size: {config3.map_width}x{config3.map_height}")
    print(f"  Rooms: {config3.rooms}")
    print(f"  Enemies: {config3.enemies}")
    print(f"  Debug: {config3.debug_mode}")
    
    # Check if values changed as expected
    print("\n4. Validation:")
    if config2.map_width == 80 and config2.map_height == 30:
        print("  ✓ Config file values loaded correctly")
    else:
        print("  ✗ Config file values not loaded")
    
    if config3.map_width == 150 and config3.debug_mode:
        print("  ✓ Command line override working")
    else:
        print("  ✗ Command line override failed")
    
    if config2.rooms == 12 and config2.enemies == 5:
        print("  ✓ Game parameters loaded from config")
    else:
        print("  ✗ Game parameters not loaded correctly")

if __name__ == '__main__':
    test_config_loading()