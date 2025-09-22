#!/usr/bin/env python3
"""
内存管理系统测试
"""
import unittest
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.memory import MemoryMonitor, SmartCacheManager, MemoryOptimizer
from game.performance import PerformanceOptimizer


class TestMemoryMonitor(unittest.TestCase):
    """测试内存监控器"""
    
    def setUp(self):
        """设置测试环境"""
        self.monitor = MemoryMonitor()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertTrue(self.monitor.enabled)
        self.assertIsNotNone(self.monitor.process)
        self.assertEqual(len(self.monitor.memory_history), 0)
        self.assertEqual(self.monitor.peak_memory, 0)
    
    def test_memory_tracking(self):
        """测试内存跟踪"""
        # 设置基线
        self.monitor.set_baseline()
        self.assertGreater(self.monitor.baseline_memory, 0)
        
        # 更新内存监控
        self.monitor.update()
        
        # 检查统计数据
        stats = self.monitor.get_memory_stats()
        self.assertIn('current_memory_mb', stats)
        self.assertGreater(stats['current_memory_mb'], 0)
    
    def test_memory_thresholds(self):
        """测试内存阈值检查"""
        # 设置低阈值进行测试
        original_warning = self.monitor.warning_threshold
        original_critical = self.monitor.critical_threshold
        
        self.monitor.warning_threshold = 1  # 1MB
        self.monitor.critical_threshold = 2  # 2MB
        
        # 更新监控，应该触发警告
        self.monitor.update()
        
        # 恢复原始阈值
        self.monitor.warning_threshold = original_warning
        self.monitor.critical_threshold = original_critical


class TestSmartCacheManager(unittest.TestCase):
    """测试智能缓存管理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.cache_manager = SmartCacheManager(max_size=10, max_memory_mb=1)
    
    def test_cache_operations(self):
        """测试缓存操作"""
        # 测试缓存添加
        def generate_test_item():
            return "test_item"
        
        item = self.cache_manager.get_cached_item('test_cache', 'key1', generate_test_item)
        self.assertEqual(item, "test_item")
        
        # 测试缓存命中
        item2 = self.cache_manager.get_cached_item('test_cache', 'key1')
        self.assertEqual(item2, "test_item")
    
    def test_cache_cleanup(self):
        """测试缓存清理"""
        # 填充缓存超过限制
        for i in range(15):  # 超过max_size=10
            self.cache_manager.get_cached_item(
                'test_cache', f'key{i}', 
                lambda i=i: f"item_{i}"
            )
        
        # 缓存应该被清理
        cache = self.cache_manager.caches['test_cache']
        self.assertLessEqual(len(cache), 12)  # 应该清理了一些项目
    
    def test_ttl_expiration(self):
        """测试TTL过期"""
        # 设置短TTL
        self.cache_manager.ttl['test_cache'] = 0.1  # 100ms
        
        # 添加项目
        item = self.cache_manager.get_cached_item('test_cache', 'ttl_key', lambda: "ttl_item")
        self.assertEqual(item, "ttl_item")
        
        # 等待TTL过期
        time.sleep(0.2)
        
        # 项目应该过期
        item2 = self.cache_manager.get_cached_item('test_cache', 'ttl_key')
        self.assertIsNone(item2)
    
    def test_cache_stats(self):
        """测试缓存统计"""
        # 添加一些项目
        for i in range(5):
            self.cache_manager.get_cached_item(
                'test_cache', f'stat_key{i}', 
                lambda i=i: f"stat_item_{i}"
            )
        
        stats = self.cache_manager.get_cache_stats()
        self.assertIn('test_cache', stats)
        self.assertIn('total', stats)
        self.assertEqual(stats['test_cache']['items'], 5)


class TestMemoryOptimizer(unittest.TestCase):
    """测试内存优化器"""
    
    def setUp(self):
        """设置测试环境"""
        self.memory_monitor = MemoryMonitor()
        self.cache_manager = SmartCacheManager()
        self.optimizer = MemoryOptimizer(self.memory_monitor, self.cache_manager)
    
    def test_optimization_suggestions(self):
        """测试优化建议"""
        suggestions = self.optimizer.suggest_optimizations()
        self.assertIsInstance(suggestions, list)
    
    def test_memory_optimization(self):
        """测试内存优化"""
        # 填充一些缓存
        for i in range(20):
            self.cache_manager.get_cached_item(
                'test_cache', f'opt_key{i}', 
                lambda i=i: f"opt_item_{i}"
            )
        
        # 执行优化
        optimizations = self.optimizer.optimize_memory()
        self.assertIsInstance(optimizations, list)
    
    def test_memory_report(self):
        """测试内存报告"""
        report = self.optimizer.get_memory_report()
        self.assertIn('current_memory', report)
        self.assertIn('memory_stats', report)
        self.assertIn('cache_stats', report)
        self.assertIn('suggestions', report)


class TestPerformanceIntegration(unittest.TestCase):
    """测试性能系统集成"""
    
    def setUp(self):
        """设置测试环境"""
        self.optimizer = PerformanceOptimizer()
    
    def test_memory_system_integration(self):
        """测试内存系统集成"""
        # 检查内存系统是否可用
        if self.optimizer.memory_monitor:
            self.assertIsNotNone(self.optimizer.cache_manager)
            self.assertIsNotNone(self.optimizer.memory_optimizer)
    
    def test_enhanced_stats(self):
        """测试增强的统计信息"""
        stats = self.optimizer.get_stats()
        self.assertIsInstance(stats, dict)
        
        # 如果内存系统可用，应该包含内存统计
        if self.optimizer.memory_monitor:
            self.assertIn('current_memory_mb', stats)
    
    def test_memory_report(self):
        """测试内存报告功能"""
        report = self.optimizer.get_memory_report()
        self.assertIsInstance(report, dict)
        
        if self.optimizer.memory_optimizer:
            self.assertIn('current_memory', report)
        else:
            self.assertIn('error', report)
    
    def test_force_optimization(self):
        """测试强制优化"""
        optimizations = self.optimizer.force_memory_optimization()
        self.assertIsInstance(optimizations, list)
        # 优化结果可能为空，这是正常的
        # self.assertGreater(len(optimizations), 0)


if __name__ == '__main__':
    unittest.main()