"""
Unit tests for the game configuration system
"""
import unittest
import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.config import GameConfig
from game.config_file import ConfigFile


class TestGameConfig(unittest.TestCase):
    """Test cases for GameConfig class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.original_argv = sys.argv[:]
    
    def tearDown(self):
        """Clean up after tests"""
        sys.argv = self.original_argv
    
    def test_default_config(self):
        """Test default configuration values"""
        sys.argv = ['test.py']
        config = GameConfig()
        
        # Note: These values may come from existing config file
        # Check that they are reasonable defaults
        self.assertGreater(config.map_width, 0)
        self.assertGreater(config.map_height, 0)
        self.assertGreater(config.rooms, 0)
        self.assertGreater(config.enemies, 0)
        self.assertFalse(config.regen)
        self.assertGreater(config.sprint_multiplier, 0)
    
    def test_command_line_args(self):
        """Test command line argument parsing"""
        sys.argv = ['test.py', '--map-width', '150', '--debug', '--rooms', '25']
        config = GameConfig()
        
        self.assertEqual(config.map_width, 150)
        self.assertEqual(config.rooms, 25)
        self.assertTrue(config.debug_mode)
    
    def test_config_file_integration(self):
        """Test configuration file loading"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                "game": {
                    "map_width": 80,
                    "map_height": 25,
                    "rooms": 15,
                    "enemies": 6
                },
                "player": {
                    "sprint_multiplier": 0.8,
                    "stamina_max": 150.0
                }
            }
            json.dump(test_config, f)
            config_path = f.name
        
        try:
            sys.argv = ['test.py', '--config', config_path]
            config = GameConfig()
            
            self.assertEqual(config.map_width, 80)
            self.assertEqual(config.map_height, 25)
            self.assertEqual(config.rooms, 15)
            self.assertEqual(config.enemies, 6)
            self.assertEqual(config.sprint_multiplier, 0.8)
            self.assertEqual(config.stamina_max, 150.0)
        finally:
            Path(config_path).unlink()
    
    def test_command_line_override(self):
        """Test command line arguments override config file"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                "game": {
                    "map_width": 80,
                    "rooms": 15
                }
            }
            json.dump(test_config, f)
            config_path = f.name
        
        try:
            sys.argv = ['test.py', '--config', config_path, '--map-width', '200', '--rooms', '30']
            config = GameConfig()
            
            # Command line should override config file
            self.assertEqual(config.map_width, 200)
            self.assertEqual(config.rooms, 30)
        finally:
            Path(config_path).unlink()


class TestConfigFile(unittest.TestCase):
    """Test cases for ConfigFile class"""
    
    def test_json_config(self):
        """Test JSON configuration file operations"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        
        try:
            # Test creation and saving
            config = ConfigFile(config_path)
            config.set('test.value', 42)
            config.set('nested.setting', 'hello')
            config.save()
            
            # Test loading
            config2 = ConfigFile(config_path)
            self.assertEqual(config2.get('test.value'), 42)
            self.assertEqual(config2.get('nested.setting'), 'hello')
            
            # Test default values
            self.assertEqual(config2.get('nonexistent', 'default'), 'default')
            
            # Test deletion
            self.assertTrue(config2.delete('test.value'))
            self.assertFalse(config2.has('test.value'))
            
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    def test_ini_config(self):
        """Test INI configuration file operations"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            config_path = f.name
        
        try:
            # Test creation and saving
            config = ConfigFile(config_path)
            config.set('value', 42, section='test')
            config.set('setting', 'hello', section='nested')
            config.save()
            
            # Test loading
            config2 = ConfigFile(config_path)
            self.assertEqual(config2.get('value', section='test'), 42)
            self.assertEqual(config2.get('setting', section='nested'), 'hello')
            
            # Test deletion
            self.assertTrue(config2.delete('value', section='test'))
            self.assertFalse(config2.has('value', section='test'))
            
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    def test_export_to_args(self):
        """Test exporting configuration as command line arguments"""
        config = ConfigFile()
        config.data = {
            'display': {'width': 1024, 'fullscreen': True},
            'game': {'debug': False, 'map_width': 100}
        }
        
        args = config.export_to_args()
        
        # Check that arguments are generated correctly
        self.assertIn('--display-width', args)
        self.assertIn('1024', args)
        self.assertIn('--display-fullscreen', args)
        self.assertIn('--game-map_width', args)
        self.assertIn('100', args)
        # Boolean false should not appear
        self.assertNotIn('--game-debug', args)


if __name__ == '__main__':
    unittest.main()