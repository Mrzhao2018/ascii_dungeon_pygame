#!/usr/bin/env python3
"""
Unit tests for game state management
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.state import GameState
from game.config import GameConfig


class TestGameState(unittest.TestCase):
    """Test cases for GameState class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = GameConfig()
        self.game_state = GameState(self.config)
    
    def test_initialization(self):
        """Test game state initialization"""
        self.assertIsNotNone(self.game_state.config)
        self.assertEqual(self.game_state.floor_number, 1)
        self.assertEqual(self.game_state.width, 0)
        self.assertEqual(self.game_state.height, 0)
        self.assertEqual(len(self.game_state.level), 0)
        self.assertEqual(self.game_state.cam_x, 0)
        self.assertEqual(self.game_state.cam_y, 0)
        
    def test_level_management(self):
        """Test level setting and retrieval"""
        test_level = [
            "######",
            "#....#",
            "#....#", 
            "######"
        ]
        
        self.game_state.set_level(test_level)
        self.assertEqual(self.game_state.level, test_level)
        self.assertEqual(self.game_state.width, 6)
        self.assertEqual(self.game_state.height, 4)
        
    def test_camera_management(self):
        """Test camera position management"""
        # Camera starts at (0, 0)
        self.assertEqual(self.game_state.cam_x, 0)
        self.assertEqual(self.game_state.cam_y, 0)
        
        # Update camera position
        self.game_state.cam_x = 100
        self.game_state.cam_y = 200
        self.assertEqual(self.game_state.cam_x, 100)
        self.assertEqual(self.game_state.cam_y, 200)
        
    def test_floor_transitions(self):
        """Test floor transition tracking"""
        initial_floor = self.game_state.floor_number
        self.assertEqual(initial_floor, 1)
        
        # Test floor transition state
        self.assertIsNone(self.game_state.floor_transition)
        self.assertIsNone(self.game_state.pending_floor)
        
        # Simulate floor transition
        self.game_state.floor_number = 2
        self.assertEqual(self.game_state.floor_number, 2)
        
    def test_floating_text_management(self):
        """Test floating text system"""
        # Initially empty
        self.assertEqual(len(self.game_state.floating_texts), 0)
        
        # Add floating text manually (since add_floating_text doesn't exist)
        floating_text = {
            "text": "Test message",
            "x": 50,
            "y": 100,
            "color": (255, 255, 255),
            "duration": 1000
        }
        self.game_state.floating_texts.append(floating_text)
        
        self.assertEqual(len(self.game_state.floating_texts), 1)
        self.assertEqual(self.game_state.floating_texts[0]["text"], "Test message")
        
    def test_dialog_management(self):
        """Test dialog state management"""
        self.assertFalse(self.game_state.dialog_active)
        self.assertEqual(len(self.game_state.dialog_lines), 0)
        self.assertEqual(self.game_state.dialog_index, 0)
        
        # Activate dialog
        self.game_state.dialog_active = True
        self.game_state.dialog_lines = ["Hello", "World"]
        self.assertTrue(self.game_state.dialog_active)
        self.assertEqual(len(self.game_state.dialog_lines), 2)
        
    def test_screen_shake(self):
        """Test screen shake functionality"""
        # Initially no shake
        self.assertEqual(self.game_state.screen_shake, 0)
        
        # Add screen shake
        self.game_state.screen_shake = 10
        self.assertEqual(self.game_state.screen_shake, 10)
        
        # Simulate shake decay
        self.game_state.screen_shake = max(0, self.game_state.screen_shake - 1)
        self.assertEqual(self.game_state.screen_shake, 9)
        
    def test_visual_effects(self):
        """Test visual effects state management"""
        # Enemy flash effects
        self.assertEqual(len(self.game_state.enemy_flash), 0)
        
        # Add enemy flash
        self.game_state.enemy_flash["enemy_1"] = 500
        self.assertEqual(self.game_state.enemy_flash["enemy_1"], 500)
        
        # Test pending target
        self.assertIsNone(self.game_state.pending_target)
        self.game_state.pending_target = (10, 20)
        self.assertEqual(self.game_state.pending_target, (10, 20))
        
    def test_exit_position_computation(self):
        """Test exit position computation"""
        # Set up a level with an exit (X character)
        test_level = [
            "######",
            "#....#",
            "#..X.#",  # X is exit
            "######"
        ]
        
        self.game_state.set_level(test_level)
        self.game_state.compute_exit_pos()
        
        # Should find the exit at position (3, 2)
        self.assertEqual(self.game_state.exit_pos, (3, 2))


class TestGameStateEdgeCases(unittest.TestCase):
    """Test edge cases for GameState"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = GameConfig()
        self.game_state = GameState(self.config)
    
    def test_empty_level(self):
        """Test behavior with empty level"""
        # Set empty level
        self.game_state.set_level([])
        self.assertEqual(self.game_state.width, 0)
        self.assertEqual(self.game_state.height, 0)
        
        # Exit computation should handle empty level gracefully
        self.game_state.compute_exit_pos()
        self.assertIsNone(self.game_state.exit_pos)
        
    def test_game_logs(self):
        """Test game log storage and access"""
        # Initially empty
        self.assertEqual(len(self.game_state.game_logs), 0)
        
        # Add some logs
        self.game_state.game_logs.append("Game started")
        self.game_state.game_logs.append("Player moved")
        
        self.assertEqual(len(self.game_state.game_logs), 2)
        self.assertEqual(self.game_state.game_logs[0], "Game started")
        
    def test_floor_transition_data(self):
        """Test floor transition data structure"""
        # Test transition state
        transition_data = {
            "time": 1000,
            "text": "Moving to floor 2..."
        }
        self.game_state.floor_transition = transition_data
        
        self.assertEqual(self.game_state.floor_transition["time"], 1000)
        self.assertEqual(self.game_state.floor_transition["text"], "Moving to floor 2...")
        
        # Test pending floor data
        pending_data = {
            "floor_number": 2,
            "seed": 12345
        }
        self.game_state.pending_floor = pending_data
        
        self.assertEqual(self.game_state.pending_floor["floor_number"], 2)
        self.assertEqual(self.game_state.pending_floor["seed"], 12345)


if __name__ == '__main__':
    unittest.main()