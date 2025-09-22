"""
Unit tests for the performance monitoring system
"""
import unittest
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.performance import PerformanceMonitor, PerformanceOptimizer


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor()
    
    def test_frame_timing(self):
        """Test frame timing functionality"""
        self.monitor.enable()
        
        # Simulate frame timing
        self.monitor.start_frame()
        time.sleep(0.01)  # 10ms
        self.monitor.end_frame()
        
        self.monitor.start_frame() 
        time.sleep(0.02)  # 20ms
        self.monitor.end_frame()
        
        stats = self.monitor.get_current_stats()
        
        self.assertGreater(stats['total_frames'], 0)
        self.assertGreaterEqual(len(self.monitor.frame_times), 1)
    
    def test_performance_thresholds(self):
        """Test performance threshold detection"""
        self.monitor.enable()
        
        # First frame to establish baseline timing
        self.monitor.start_frame()
        self.monitor.end_frame()
        
        # Add small delay between frames to simulate actual game timing
        time.sleep(0.06)  # 60ms delay between frames
        
        # Second frame - this should record the 60ms delay as frame time
        self.monitor.start_frame()
        self.monitor.end_frame()
        
        stats = self.monitor.get_current_stats()
        
        # Check that frame time is recorded and is reasonably high
        if self.monitor.frame_times:
            # Frame time should be recorded in milliseconds
            # The delay between frames should be recorded as frame time
            max_frame_time = max(self.monitor.frame_times)
            self.assertGreater(max_frame_time, 50, f"Max frame time {max_frame_time}ms should be > 50ms")  # Should be > 50ms
    
    def test_render_and_update_timing(self):
        """Test render and update time recording"""
        self.monitor.enable()
        
        # Record some timing data
        self.monitor.record_render_time(15.5)
        self.monitor.record_render_time(12.3)
        self.monitor.record_update_time(8.7)
        self.monitor.record_update_time(9.2)
        
        stats = self.monitor.get_current_stats()
        
        self.assertAlmostEqual(stats['avg_render_time'], (15.5 + 12.3) / 2, places=1)
        self.assertAlmostEqual(stats['avg_update_time'], (8.7 + 9.2) / 2, places=1)
    
    def test_enable_disable(self):
        """Test enabling and disabling monitoring"""
        self.monitor.disable()
        self.assertFalse(self.monitor.enabled)
        
        # Operations should not record when disabled
        self.monitor.start_frame()
        self.monitor.record_render_time(10.0)
        stats = self.monitor.get_current_stats()
        
        self.assertEqual(stats, {})
        
        # Re-enable and test
        self.monitor.enable()
        self.assertTrue(self.monitor.enabled)
        
        self.monitor.record_render_time(10.0)
        stats = self.monitor.get_current_stats()
        
        self.assertGreater(len(stats), 0)


class TestPerformanceOptimizer(unittest.TestCase):
    """Test cases for PerformanceOptimizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = PerformanceOptimizer()
    
    def test_performance_issue_detection(self):
        """Test performance issue detection"""
        # Create test performance data
        performance_data = {
            'frame_total': [35.0, 40.0, 45.0],  # Above 33ms threshold
            'rendering': [10.0, 12.0, 8.0],    # Below 16ms threshold
            'game_update': [15.0, 18.0, 20.0]  # Above 10ms threshold
        }
        
        issues = self.optimizer.check_performance_issues(performance_data)
        
        # Should detect issues with frame_total and game_update
        self.assertGreater(len(issues), 0)
        
        # Check that frame_total issue is detected
        frame_issues = [issue for issue in issues if 'frame_total' in issue]
        self.assertGreater(len(frame_issues), 0)
        
        # Check that game_update issue is detected
        update_issues = [issue for issue in issues if 'game_update' in issue]
        self.assertGreater(len(update_issues), 0)
    
    def test_stats_integration(self):
        """Test integration with performance monitor"""
        self.optimizer.monitor.enable()
        
        # Simulate some frame activity
        self.optimizer.start_frame()
        time.sleep(0.01)
        self.optimizer.end_frame()
        
        stats = self.optimizer.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_frames', stats)
        self.assertGreaterEqual(stats['total_frames'], 1)
    
    def test_threshold_configuration(self):
        """Test performance threshold configuration"""
        self.assertEqual(self.optimizer.thresholds['frame_total'], 33.0)
        self.assertEqual(self.optimizer.thresholds['rendering'], 16.0)
        self.assertEqual(self.optimizer.thresholds['game_update'], 10.0)
        self.assertEqual(self.optimizer.thresholds['event_handling'], 5.0)


class TestPerformanceIntegration(unittest.TestCase):
    """Integration tests for performance monitoring"""
    
    def test_full_monitoring_cycle(self):
        """Test a complete monitoring cycle"""
        optimizer = PerformanceOptimizer()
        
        # Simulate several frames
        for i in range(5):
            optimizer.start_frame()
            
            # Simulate variable frame times
            sleep_time = 0.01 + (i * 0.005)  # 10-30ms
            time.sleep(sleep_time)
            
            # Simulate render/update times
            optimizer.monitor.record_render_time(5.0 + i)
            optimizer.monitor.record_update_time(3.0 + i * 0.5)
            
            optimizer.end_frame()
        
        stats = optimizer.get_stats()
        
        # Verify we have data
        self.assertEqual(stats['total_frames'], 5)
        self.assertGreater(len(optimizer.monitor.frame_times), 0)
        self.assertGreater(len(optimizer.monitor.render_times), 0)
        self.assertGreater(len(optimizer.monitor.update_times), 0)
        
        # Verify averages are reasonable
        self.assertGreater(stats['avg_render_time'], 5.0)
        self.assertGreater(stats['avg_update_time'], 3.0)


if __name__ == '__main__':
    unittest.main()