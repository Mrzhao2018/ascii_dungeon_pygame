#!/usr/bin/env python3
"""
Configuration management tool for the game
"""
import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.config_file import ConfigFile, create_sample_configs


def list_configs():
    """List available configuration files"""
    print("Available configuration files:")
    
    config_files = []
    
    # Check common locations
    common_paths = [
        'game.json',
        'game.ini', 
        'config/game.json',
        'config/game.ini',
        '.game.json',
        '.game.ini'
    ]
    
    for path in common_paths:
        if Path(path).exists():
            config_files.append(path)
            size = Path(path).stat().st_size
            print(f"  {path} ({size} bytes)")
    
    if not config_files:
        print("  No configuration files found")
    
    return config_files


def show_config(config_path):
    """Show configuration file contents"""
    config = ConfigFile(config_path)
    
    if not config.data:
        print(f"Configuration file '{config_path}' is empty or doesn't exist")
        return
    
    print(f"Configuration from '{config_path}':")
    print("=" * 50)
    
    if config.format == "json":
        print(json.dumps(config.data, indent=2, ensure_ascii=False))
    else:
        # INI format - show by sections
        for section, section_data in config.data.items():
            print(f"[{section}]")
            for key, value in section_data.items():
                print(f"{key} = {value}")
            print()


def edit_config(config_path):
    """Interactive configuration editor"""
    config = ConfigFile(config_path)
    
    if not config.data:
        print(f"Configuration file '{config_path}' doesn't exist. Creating new one...")
        config.create_default_config()
    
    print(f"Editing configuration: {config_path}")
    print("Commands: set <key> <value>, get <key>, delete <key>, list, save, quit")
    print("Use dot notation for nested keys (e.g., 'display.width')")
    print()
    
    while True:
        try:
            command = input("config> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd in ['quit', 'exit', 'q']:
                break
            
            elif cmd == 'list':
                keys = config.get_all_keys()
                print("Available keys:")
                for key in sorted(keys):
                    value = config.get(key)
                    print(f"  {key} = {value}")
            
            elif cmd == 'get' and len(command) > 1:
                key = command[1]
                value = config.get(key)
                print(f"{key} = {value}")
            
            elif cmd == 'set' and len(command) > 2:
                key = command[1]
                value = ' '.join(command[2:])
                
                # Try to convert to appropriate type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif '.' in value:
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # Keep as string
                
                config.set(key, value)
                print(f"Set {key} = {value}")
            
            elif cmd == 'delete' and len(command) > 1:
                key = command[1]
                if config.delete(key):
                    print(f"Deleted {key}")
                else:
                    print(f"Key {key} not found")
            
            elif cmd == 'save':
                if config.save():
                    print(f"Configuration saved to {config_path}")
                else:
                    print("Failed to save configuration")
            
            else:
                print("Unknown command. Available: set, get, delete, list, save, quit")
        
        except KeyboardInterrupt:
            print("\nQuitting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def validate_config(config_path):
    """Validate configuration file"""
    config = ConfigFile(config_path)
    
    if not config.data:
        print(f"ERROR: Configuration file '{config_path}' doesn't exist or is empty")
        return False
    
    print(f"Validating configuration: {config_path}")
    
    issues = []
    
    # Check required sections for JSON
    if config.format == "json":
        required_sections = ['display', 'game', 'player', 'camera', 'debug']
        for section in required_sections:
            if not config.has(section):
                issues.append(f"Missing section: {section}")
    
    # Validate numeric ranges
    checks = [
        ('game.map_width', 20, 500),
        ('game.map_height', 20, 200),
        ('game.rooms', 5, 50),
        ('game.enemies', 0, 100),
        ('player.sprint_multiplier', 0.1, 2.0),
        ('player.stamina_max', 10.0, 1000.0),
        ('camera.lerp', 0.0, 1.0)
    ]
    
    for key, min_val, max_val in checks:
        value = config.get(key)
        if value is not None:
            try:
                value = float(value)
                if value < min_val or value > max_val:
                    issues.append(f"{key} = {value} (should be between {min_val} and {max_val})")
            except (ValueError, TypeError):
                issues.append(f"{key} = {value} (should be a number)")
    
    # Report results
    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
        return False
    else:
        print("✅ Configuration is valid")
        return True


def export_config_as_args(config_path):
    """Export configuration as command line arguments"""
    config = ConfigFile(config_path)
    
    if not config.data:
        print(f"Configuration file '{config_path}' doesn't exist")
        return
    
    args = config.export_to_args()
    
    print(f"Command line arguments from '{config_path}':")
    print(' '.join(args))
    
    # Also show as a script
    print("\nAs a startup script:")
    print(f"python main.py {' '.join(args)}")


def main():
    """Main configuration management interface"""
    if len(sys.argv) < 2:
        print("Configuration Management Tool")
        print("Usage:")
        print("  python tools/config_manager.py list")
        print("  python tools/config_manager.py show <config_file>")
        print("  python tools/config_manager.py edit <config_file>")
        print("  python tools/config_manager.py validate <config_file>")
        print("  python tools/config_manager.py export <config_file>")
        print("  python tools/config_manager.py create [config_file]")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_configs()
    
    elif command == 'show' and len(sys.argv) > 2:
        show_config(sys.argv[2])
    
    elif command == 'edit' and len(sys.argv) > 2:
        edit_config(sys.argv[2])
    
    elif command == 'validate' and len(sys.argv) > 2:
        validate_config(sys.argv[2])
    
    elif command == 'export' and len(sys.argv) > 2:
        export_config_as_args(sys.argv[2])
    
    elif command == 'create':
        config_file = sys.argv[2] if len(sys.argv) > 2 else 'game.json'
        config = ConfigFile(config_file)
        config.create_default_config()
        print(f"Created default configuration: {config_file}")
    
    elif command == 'samples':
        create_sample_configs()
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, show, edit, validate, export, create, samples")


if __name__ == '__main__':
    main()