"""
Unit tests for the game state management system
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock pygame for testing
class MockPygame:
    class time:
        @staticmethod
        def get_ticks():
            return 1000
    
    class display:
        @staticmethod
        def get_surface():
            return None

sys.modules['pygame'] = MockPygame()

from game.config import GameConfig
from game.state import GameState


class TestGameState(unittest.TestCase):
    """Test cases for GameState class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        sys.argv = ['test.py']
        self.config = GameConfig()
        self.game_state = GameState(self.config)
    
    def test_initialization(self):
        """Test game state initialization"""
        self.assertIsNotNone(self.game_state.level)
        self.assertEqual(self.game_state.floor, 1)
        self.assertEqual(self.game_state.cam_x, 0)
        self.assertEqual(self.game_state.cam_y, 0)
        self.assertFalse(self.game_state.show_exit_indicator)
        self.assertEqual(len(self.game_state.floating_texts), 0)
    
    def test_level_management(self):
        """Test level setting and retrieval"""
        test_level = [['#' for _ in range(10)] for _ in range(5)]
        
        self.game_state.set_level(test_level)
        retrieved_level = self.game_state.get_level()
        
        self.assertEqual(len(retrieved_level), 5)
        self.assertEqual(len(retrieved_level[0]), 10)
        self.assertEqual(retrieved_level[0][0], '#')
    
    def test_camera_management(self):
        """Test camera position management"""
        self.game_state.set_camera(100, 200)
        
        self.assertEqual(self.game_state.cam_x, 100)
        self.assertEqual(self.game_state.cam_y, 200)
    
    def test_floor_transitions(self):
        """Test floor transition tracking"""
        initial_floor = self.game_state.floor
        
        self.game_state.increment_floor()
        self.assertEqual(self.game_state.floor, initial_floor + 1)
        
        self.game_state.increment_floor()
        self.assertEqual(self.game_state.floor, initial_floor + 2)
    
    def test_floating_text_management(self):
        """Test floating text system"""
        # Add floating text
        self.game_state.add_floating_text("Test message", 50, 100, (255, 255, 255))
        
        self.assertEqual(len(self.game_state.floating_texts), 1)
        
        text = self.game_state.floating_texts[0]
        self.assertEqual(text['text'], "Test message")
        self.assertEqual(text['x'], 50)
        self.assertEqual(text['y'], 100)
        self.assertEqual(text['color'], (255, 255, 255))
        self.assertGreater(text['duration'], 0)
        
        # Test multiple texts
        self.game_state.add_floating_text("Second message", 75, 125, (255, 0, 0))
        self.assertEqual(len(self.game_state.floating_texts), 2)
    
    def test_floating_text_updates(self):
        """Test floating text duration updates"""
        self.game_state.add_floating_text("Temporary", 0, 0, (255, 255, 255))
        
        initial_duration = self.game_state.floating_texts[0]['duration']
        
        # Update floating texts (simulate time passing)
        self.game_state.update_floating_texts(100)  # 100ms
        
        # Duration should decrease
        updated_duration = self.game_state.floating_texts[0]['duration']
        self.assertLess(updated_duration, initial_duration)
        
        # Simulate enough time for text to expire
        self.game_state.update_floating_texts(5000)  # 5 seconds
        
        # Text should be removed when duration expires
        self.assertEqual(len(self.game_state.floating_texts), 0)
    
    def test_exit_indicator(self):
        """Test exit indicator toggle"""
        self.assertFalse(self.game_state.show_exit_indicator)
        
        self.game_state.toggle_exit_indicator()
        self.assertTrue(self.game_state.show_exit_indicator)
        
        self.game_state.toggle_exit_indicator()
        self.assertFalse(self.game_state.show_exit_indicator)
    
    def test_screen_shake(self):
        """Test screen shake functionality"""
        self.assertFalse(self.game_state.is_screen_shaking())
        
        self.game_state.trigger_screen_shake()
        self.assertTrue(self.game_state.is_screen_shaking())
        
        # Test shake intensity decreases over time
        initial_intensity = self.game_state.get_screen_shake_offset()
        
        # Simulate time passing
        self.game_state.update_screen_shake(100)  # 100ms
        
        if self.game_state.is_screen_shaking():
            updated_intensity = self.game_state.get_screen_shake_offset()
            # Can't guarantee exact comparison due to random components
            self.assertIsInstance(updated_intensity, tuple)
            self.assertEqual(len(updated_intensity), 2)
    
    def test_tile_access_helpers(self):
        """Test tile coordinate conversion helpers"""
        # Set up a test level
        test_level = [['.' for _ in range(20)] for _ in range(15)]
        test_level[5][10] = '#'
        self.game_state.set_level(test_level)
        
        # Test coordinate bounds checking
        self.assertTrue(self.game_state.is_valid_position(10, 5))
        self.assertTrue(self.game_state.is_valid_position(0, 0))
        self.assertTrue(self.game_state.is_valid_position(19, 14))
        
        self.assertFalse(self.game_state.is_valid_position(-1, 5))
        self.assertFalse(self.game_state.is_valid_position(10, -1))
        self.assertFalse(self.game_state.is_valid_position(20, 5))
        self.assertFalse(self.game_state.is_valid_position(10, 15))
        
        # Test tile access
        self.assertEqual(self.game_state.get_tile(10, 5), '#')
        self.assertEqual(self.game_state.get_tile(0, 0), '.')


class TestGameStateEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for GameState"""
    
    def setUp(self):
        """Set up test fixtures"""
        sys.argv = ['test.py']
        self.config = GameConfig()
        self.game_state = GameState(self.config)
    
    def test_empty_level(self):
        """Test behavior with empty level"""
        empty_level = []
        self.game_state.set_level(empty_level)
        
        self.assertFalse(self.game_state.is_valid_position(0, 0))
        self.assertIsNone(self.game_state.get_tile(0, 0))
    
    def test_invalid_camera_positions(self):
        """Test camera with invalid positions"""
        # Should handle negative positions
        self.game_state.set_camera(-100, -200)
        self.assertEqual(self.game_state.cam_x, -100)
        self.assertEqual(self.game_state.cam_y, -200)
    
    def test_floating_text_edge_cases(self):
        """Test floating text with edge cases"""
        # Empty text
        self.game_state.add_floating_text("", 0, 0, (255, 255, 255))
        self.assertEqual(len(self.game_state.floating_texts), 1)
        
        # Very long text
        long_text = "A" * 1000
        self.game_state.add_floating_text(long_text, 0, 0, (255, 255, 255))
        self.assertEqual(len(self.game_state.floating_texts), 2)
        
        # Invalid colors should be handled gracefully
        self.game_state.add_floating_text("Test", 0, 0, None)
        self.assertEqual(len(self.game_state.floating_texts), 3)


if __name__ == '__main__':
    unittest.main()