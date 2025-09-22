#!/usr/bin/env python3
"""
Game health check and diagnostic tool
"""
import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_python_environment():
    """Check Python and package versions"""
    print("=== Python Environment ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check required packages
    required_packages = ['pygame']
    for package in required_packages:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"{package}: {version} ✓")
        except ImportError:
            print(f"{package}: NOT INSTALLED ✗")
    
    print()


def check_game_files():
    """Check if all game files are present"""
    print("=== Game Files ===")
    
    project_root = Path(__file__).parent.parent
    
    # Required files and directories
    required_items = [
        'main.py',
        'game/__init__.py',
        'game/config.py',
        'game/state.py',
        'game/input.py',
        'game/floors.py',
        'game/renderer.py',
        'game/game.py',
        'game/player.py',
        'game/entities.py',
        'game/logging.py',
        'game/debug.py',
        'game/performance.py',
        'data/',
        'data/enemies.json',
        'fonts/',
    ]
    
    missing_files = []
    for item in required_items:
        path = project_root / item
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f"{item}: {size} bytes ✓")
            else:
                print(f"{item}: directory ✓")
        else:
            print(f"{item}: MISSING ✗")
            missing_files.append(item)
    
    if missing_files:
        print(f"\nWARNING: {len(missing_files)} files/directories are missing!")
        return False
    
    print()
    return True


def check_game_configuration():
    """Check game configuration and data files"""
    print("=== Game Configuration ===")
    
    project_root = Path(__file__).parent.parent
    
    # Check enemies.json
    enemies_file = project_root / 'data' / 'enemies.json'
    if enemies_file.exists():
        try:
            with open(enemies_file, 'r', encoding='utf-8') as f:
                enemies_data = json.load(f)
            
            entity_count = len(enemies_data.get('entities', []))
            print(f"enemies.json: {entity_count} entities ✓")
            
            # Validate entity structure
            for i, entity in enumerate(enemies_data.get('entities', [])):
                required_fields = ['id', 'type', 'x', 'y', 'hp']
                missing_fields = [field for field in required_fields if field not in entity]
                if missing_fields:
                    print(f"  Entity {i}: missing fields {missing_fields} ✗")
                else:
                    print(f"  Entity {entity['id']}: valid ✓")
        
        except json.JSONDecodeError as e:
            print(f"enemies.json: INVALID JSON - {e} ✗")
        except Exception as e:
            print(f"enemies.json: ERROR - {e} ✗")
    else:
        print("enemies.json: MISSING ✗")
    
    # Check dialogs.json
    dialogs_file = project_root / 'data' / 'dialogs.json'
    if dialogs_file.exists():
        try:
            with open(dialogs_file, 'r', encoding='utf-8') as f:
                dialogs_data = json.load(f)
            
            npc_count = len(dialogs_data.get('npcs', []))
            print(f"dialogs.json: {npc_count} NPCs ✓")
        except json.JSONDecodeError as e:
            print(f"dialogs.json: INVALID JSON - {e} ✗")
        except Exception as e:
            print(f"dialogs.json: ERROR - {e} ✗")
    else:
        print("dialogs.json: not found (optional)")
    
    print()


def check_debug_files():
    """Check debug and log files"""
    print("=== Debug Files ===")
    
    project_root = Path(__file__).parent.parent
    
    # Check main log file
    log_file = project_root / 'game.log'
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"game.log: {size} bytes ✓")
    else:
        print("game.log: not found (will be created)")
    
    # Check debug directory
    debug_dir = project_root / 'data' / 'debug'
    if debug_dir.exists():
        debug_files = list(debug_dir.glob('*'))
        print(f"debug directory: {len(debug_files)} files ✓")
        
        # Show recent debug files
        recent_files = sorted(debug_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        for file in recent_files:
            mtime = file.stat().st_mtime
            size = file.stat().st_size
            print(f"  {file.name}: {size} bytes")
    else:
        print("debug directory: not found (will be created)")
    
    print()


def run_basic_import_test():
    """Test basic game imports"""
    print("=== Import Test ===")
    
    modules_to_test = [
        'game.config',
        'game.state', 
        'game.input',
        'game.floors',
        'game.renderer',
        'game.game',
        'game.logging',
        'game.debug',
        'game.performance'
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"{module}: ✓")
        except ImportError as e:
            print(f"{module}: FAILED - {e} ✗")
            failed_imports.append(module)
        except Exception as e:
            print(f"{module}: ERROR - {e} ✗")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nWARNING: {len(failed_imports)} modules failed to import!")
        return False
    
    print()
    return True


def test_game_instantiation():
    """Test basic game instantiation"""
    print("=== Game Instantiation Test ===")
    
    try:
        # Mock sys.argv to avoid argument parsing issues
        original_argv = sys.argv[:]
        sys.argv = ['main.py', '--help']  # This should exit gracefully
        
        from game.config import GameConfig
        config = GameConfig()
        print("GameConfig: ✓")
        
        # Reset argv
        sys.argv = ['main.py']
        config = GameConfig()
        print("GameConfig (no args): ✓")
        
        from game.state import GameState
        game_state = GameState(config)
        print("GameState: ✓")
        
        from game.logging import Logger
        logger = Logger(config)
        print("Logger: ✓")
        
        # Don't try to create full Game instance as it requires pygame init
        print("Basic instantiation: ✓")
        
    except SystemExit:
        print("Config help system: ✓")
    except Exception as e:
        print(f"Game instantiation: FAILED - {e} ✗")
        return False
    finally:
        sys.argv = original_argv
    
    print()
    return True


def check_disk_space():
    """Check available disk space"""
    print("=== Disk Space ===")
    
    project_root = Path(__file__).parent.parent
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(project_root)
        
        print(f"Total space: {total // (1024**3)} GB")
        print(f"Used space: {used // (1024**3)} GB")
        print(f"Free space: {free // (1024**3)} GB")
        
        if free < 1024**3:  # Less than 1 GB
            print("WARNING: Low disk space! ⚠️")
        else:
            print("Disk space: ✓")
    
    except Exception as e:
        print(f"Could not check disk space: {e}")
    
    print()


def main():
    """Run comprehensive health check"""
    print("Game Health Check and Diagnostic Tool")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Run all checks
    check_python_environment()
    
    if not check_game_files():
        all_checks_passed = False
    
    check_game_configuration()
    check_debug_files()
    
    if not run_basic_import_test():
        all_checks_passed = False
    
    if not test_game_instantiation():
        all_checks_passed = False
    
    check_disk_space()
    
    # Final summary
    print("=" * 50)
    if all_checks_passed:
        print("✓ All critical checks passed! Game should run correctly.")
        print("\nTo start the game:")
        print("  python main.py")
        print("  python main.py --help    # for all options")
        print("  python main.py --debug   # for debug mode")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  - Install missing packages: pip install pygame")
        print("  - Check file permissions")
        print("  - Verify Python version compatibility")
    
    print("\nFor performance monitoring:")
    print("  python tools/performance_monitor.py --monitor 30")


if __name__ == '__main__':
    main()