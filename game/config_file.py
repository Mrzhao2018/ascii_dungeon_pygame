import json
import configparser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

"""
Game configuration file management
Supports JSON and INI configuration files for persistent settings
"""



class ConfigFile:
    """Configuration file manager"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration file manager

        Args:
            config_path: Path to configuration file (defaults to game.conf)
        """
        if config_path is None:
            self.config_path = Path("game.conf")
        else:
            self.config_path = Path(config_path)

        self.data: Dict[str, Any] = {}
        self.format = "json"  # json or ini

        # Determine format from extension
        if self.config_path.suffix.lower() in ['.ini', '.cfg']:
            self.format = "ini"
        elif self.config_path.suffix.lower() in ['.json']:
            self.format = "json"

        self.load()

    def load(self) -> bool:
        """Load configuration from file

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.config_path.exists():
            return False

        try:
            if self.format == "json":
                return self._load_json()
            elif self.format == "ini":
                return self._load_ini()
        except Exception as e:
            print(f"Error loading config file: {e}")
            return False

        return False

    def save(self) -> bool:
        """Save configuration to file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            if self.format == "json":
                return self._save_json()
            elif self.format == "ini":
                return self._save_ini()
        except Exception as e:
            print(f"Error saving config file: {e}")
            return False

        return False

    def _load_json(self) -> bool:
        """Load JSON configuration"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return True

    def _save_json(self) -> bool:
        """Save JSON configuration"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        return True

    def _load_ini(self) -> bool:
        """Load INI configuration"""
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding='utf-8')

        # Convert to nested dict
        self.data = {}
        for section_name in config.sections():
            self.data[section_name] = {}
            for key, value in config[section_name].items():
                # Try to convert to appropriate type
                self.data[section_name][key] = self._convert_value(value)

        return True

    def _save_ini(self) -> bool:
        """Save INI configuration"""
        config = configparser.ConfigParser()

        for section_name, section_data in self.data.items():
            config.add_section(section_name)
            for key, value in section_data.items():
                config.set(section_name, key, str(value))

        with open(self.config_path, 'w', encoding='utf-8') as f:
            config.write(f)

        return True

    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type"""
        # Try boolean
        if value.lower() in ['true', 'yes', '1']:
            return True
        elif value.lower() in ['false', 'no', '0']:
            return False

        # Try int
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def get(self, key: str, default: Any = None, section: Optional[str] = None) -> Any:
        """Get configuration value

        Args:
            key: Configuration key
            default: Default value if not found
            section: Section name for INI format

        Returns:
            Configuration value or default
        """
        if self.format == "ini" and section:
            return self.data.get(section, {}).get(key, default)
        elif '.' in key:
            # Support dot notation like "display.width"
            parts = key.split('.')
            current = self.data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
        else:
            return self.data.get(key, default)

    def set(self, key: str, value: Any, section: Optional[str] = None) -> None:
        """Set configuration value

        Args:
            key: Configuration key
            value: Value to set
            section: Section name for INI format
        """
        if self.format == "ini" and section:
            if section not in self.data:
                self.data[section] = {}
            self.data[section][key] = value
        elif '.' in key:
            # Support dot notation
            parts = key.split('.')
            current = self.data
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self.data[key] = value

    def has(self, key: str, section: Optional[str] = None) -> bool:
        """Check if configuration key exists

        Args:
            key: Configuration key
            section: Section name for INI format

        Returns:
            True if key exists, False otherwise
        """
        if self.format == "ini" and section:
            return section in self.data and key in self.data[section]
        elif '.' in key:
            parts = key.split('.')
            current = self.data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return True
        else:
            return key in self.data

    def delete(self, key: str, section: Optional[str] = None) -> bool:
        """Delete configuration key

        Args:
            key: Configuration key
            section: Section name for INI format

        Returns:
            True if deleted, False if not found
        """
        if self.format == "ini" and section:
            if section in self.data and key in self.data[section]:
                del self.data[section][key]
                return True
        elif '.' in key:
            parts = key.split('.')
            current = self.data
            for part in parts[:-1]:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            if isinstance(current, dict) and parts[-1] in current:
                del current[parts[-1]]
                return True
        else:
            if key in self.data:
                del self.data[key]
                return True

        return False

    def get_all_keys(self, section: Optional[str] = None) -> list:
        """Get all configuration keys

        Args:
            section: Section name for INI format

        Returns:
            List of all keys
        """
        if self.format == "ini" and section:
            return list(self.data.get(section, {}).keys())
        elif self.format == "ini":
            # Return all keys from all sections
            keys = []
            for section_data in self.data.values():
                keys.extend(section_data.keys())
            return keys
        else:
            return self._get_nested_keys(self.data)

    def _get_nested_keys(self, data: dict, prefix: str = "") -> list:
        """Get all nested keys from dictionary"""
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.extend(self._get_nested_keys(value, full_key))
            else:
                keys.append(full_key)
        return keys

    def export_to_args(self, prefix: str = "--") -> list:
        """Export configuration as command line arguments

        Args:
            prefix: Argument prefix (e.g., "--")

        Returns:
            List of command line arguments
        """
        args = []

        if self.format == "ini":
            for section_name, section_data in self.data.items():
                for key, value in section_data.items():
                    if isinstance(value, bool):
                        if value:
                            args.append(f"{prefix}{key}")
                    else:
                        args.extend([f"{prefix}{key}", str(value)])
        else:
            for key in self.get_all_keys():
                value = self.get(key)
                if isinstance(value, bool):
                    if value:
                        # Convert dot notation to dashes
                        arg_key = key.replace('.', '-')
                        args.append(f"{prefix}{arg_key}")
                else:
                    arg_key = key.replace('.', '-')
                    args.extend([f"{prefix}{arg_key}", str(value)])

        return args

    def merge_from_args(self, args_dict: Dict[str, Any]) -> None:
        """Merge configuration from arguments dictionary

        Args:
            args_dict: Dictionary of arguments to merge
        """
        for key, value in args_dict.items():
            if value is not None:
                # Convert dashes back to dots for nested keys
                config_key = key.replace('-', '.')
                self.set(config_key, value)

    def create_default_config(self) -> None:
        """Create default configuration file"""
        default_config = {
            "display": {"width": 1024, "height": 768, "fullscreen": False, "vsync": True},
            "game": {"map_width": 100, "map_height": 40, "rooms": 18, "enemies": 8, "debug": False, "seed": None},
            "player": {
                "sprint_multiplier": 0.6,
                "sprint_cost": 35.0,
                "stamina_max": 100.0,
                "stamina_regen": 12.0,
                "sprint_cooldown_ms": 800,
            },
            "camera": {"lerp": 0.2, "deadzone": 0.0},
            "debug": {"show_fps": False, "show_coords": False, "performance_monitoring": False, "log_level": "INFO"},
        }

        self.data = default_config
        self.save()


def create_sample_configs():
    """Create sample configuration files"""

    # Create JSON config
    json_config = ConfigFile("config/game.json")
    json_config.create_default_config()

    # Create INI config
    ini_config = ConfigFile("config/game.ini")
    ini_config.format = "ini"
    ini_config.data = {
        "display": {"width": 1024, "height": 768, "fullscreen": False},
        "game": {"debug": False, "map_width": 100, "map_height": 40},
        "player": {"sprint_multiplier": 0.6, "stamina_max": 100.0},
    }
    ini_config.save()

    print("Sample configuration files created:")
    print("- config/game.json")
    print("- config/game.ini")


if __name__ == "__main__":
    # Demo configuration file usage
    create_sample_configs()

    # Test JSON config
    config = ConfigFile("config/game.json")
    print(f"Display width: {config.get('display.width')}")
    print(f"Debug mode: {config.get('game.debug')}")

    # Test INI config
    ini_config = ConfigFile("config/game.ini")
    print(f"Map width: {ini_config.get('map_width', section='game')}")

    # Export as command line args
    args = config.export_to_args()
    print(f"Command line args: {args[:6]}...")  # Show first few
