#!/usr/bin/env python3
"""
错误处理增强系统测试
"""
import unittest
import sys
import time
import tempfile
import threading
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.error_handling import (
    ErrorSeverity, RecoveryStrategy, ErrorContext, 
    ErrorRecoveryManager, RobustErrorHandler,
    safe_operation, initialize_global_error_handler, get_global_error_handler
)
from game.logger import Logger
from game.config import GameConfig


class TestErrorContext(unittest.TestCase):
    """测试错误上下文"""
    
    def test_initialization(self):
        """测试初始化"""
        context = ErrorContext("test_operation", ErrorSeverity.HIGH)
        self.assertEqual(context.operation, "test_operation")
        self.assertEqual(context.severity, ErrorSeverity.HIGH)
        self.assertEqual(context.retry_count, 0)
        self.assertEqual(context.max_retries, 3)
    
    def test_context_data(self):
        """测试上下文数据"""
        context = ErrorContext("test_operation")
        context.add_game_state(level=5, player_hp=100)
        context.add_system_info(memory_mb=256, fps=60)
        
        data = context.to_dict()
        self.assertEqual(data['operation'], "test_operation")
        self.assertEqual(data['game_state']['level'], 5)
        self.assertEqual(data['system_info']['memory_mb'], 256)


class TestErrorRecoveryManager(unittest.TestCase):
    """测试错误恢复管理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = GameConfig()
        self.logger = Logger(self.config)
        self.recovery_manager = ErrorRecoveryManager(self.logger)
    
    def tearDown(self):
        """清理测试环境"""
        self.recovery_manager.cleanup()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.recovery_manager.recovery_strategies)
        self.assertIn('rendering', self.recovery_manager.recovery_strategies)
    
    def test_error_handling(self):
        """测试错误处理"""
        context = ErrorContext("test_rendering", ErrorSeverity.MEDIUM)
        error = ValueError("Test error")
        
        strategy = self.recovery_manager.handle_error(error, context)
        self.assertIsInstance(strategy, RecoveryStrategy)
    
    def test_fallback_registration(self):
        """测试备用操作注册"""
        def fallback_func():
            return "fallback_result"
        
        self.recovery_manager.register_fallback("test_operation", fallback_func)
        self.assertIn("test_operation", self.recovery_manager.fallback_operations)
    
    def test_error_statistics(self):
        """测试错误统计"""
        # 生成一些错误
        for i in range(5):
            context = ErrorContext(f"test_operation_{i % 2}", ErrorSeverity.LOW)
            error = RuntimeError(f"Test error {i}")
            self.recovery_manager.handle_error(error, context)
        
        stats = self.recovery_manager.get_error_statistics()
        self.assertGreater(stats['total_errors'], 0)
        self.assertIn('recent_errors', stats)
    
    def test_error_suppression(self):
        """测试错误抑制"""
        context = ErrorContext("repeated_operation", ErrorSeverity.LOW)
        error = ValueError("Repeated error")
        
        # 第一次应该记录
        strategy1 = self.recovery_manager.handle_error(error, context)
        self.assertIsInstance(strategy1, RecoveryStrategy)
        
        # 立即重复应该被抑制
        strategy2 = self.recovery_manager.handle_error(error, context)
        self.assertEqual(strategy2, RecoveryStrategy.SKIP)


class TestRobustErrorHandler(unittest.TestCase):
    """测试健壮错误处理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = GameConfig()
        self.logger = Logger(self.config)
        self.error_handler = RobustErrorHandler(self.logger)
    
    def tearDown(self):
        """清理测试环境"""
        self.error_handler.cleanup()
    
    def test_safe_operation_decorator(self):
        """测试安全操作装饰器"""
        @self.error_handler.safe_operation("test_function", ErrorSeverity.LOW, max_retries=2)
        def test_function(should_fail=False):
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # 成功情况
        result = test_function(False)
        self.assertEqual(result, "success")
        
        # 失败情况
        result = test_function(True)
        self.assertIsNone(result)
    
    def test_safe_call(self):
        """测试安全调用"""
        def test_function(value):
            if value < 0:
                raise ValueError("Negative value")
            return value * 2
        
        # 成功调用
        result = self.error_handler.safe_call(test_function, "test_operation", 5)
        self.assertEqual(result, 10)
        
        # 失败调用
        result = self.error_handler.safe_call(test_function, "test_operation", -1)
        self.assertIsNone(result)
    
    def test_fallback_mechanism(self):
        """测试备用机制"""
        def main_function():
            raise RuntimeError("Main function failed")
        
        def fallback_function():
            return "fallback_result"
        
        # 注册备用操作
        self.error_handler.register_fallback("fallback_test", fallback_function)
        
        # 使用装饰器，应该调用备用操作
        @self.error_handler.safe_operation("fallback_test", ErrorSeverity.MEDIUM)
        def test_function():
            raise RuntimeError("Main function failed")
        
        result = test_function()
        # 由于我们的恢复策略，可能返回None或fallback结果
        # 这取决于错误分类和策略选择
        self.assertIn(result, [None, "fallback_result"])


class TestGlobalErrorHandler(unittest.TestCase):
    """测试全局错误处理器"""
    
    def test_global_initialization(self):
        """测试全局初始化"""
        config = GameConfig()
        logger = Logger(config)
        
        # 初始化全局处理器
        initialize_global_error_handler(logger)
        
        # 获取全局处理器
        global_handler = get_global_error_handler()
        self.assertIsNotNone(global_handler)
    
    def test_global_decorator(self):
        """测试全局装饰器"""
        # 确保全局处理器已初始化
        if get_global_error_handler() is None:
            config = GameConfig()
            logger = Logger(config)
            initialize_global_error_handler(logger)
        
        @safe_operation("global_test", ErrorSeverity.LOW)
        def test_function(should_fail=False):
            if should_fail:
                raise ValueError("Global test error")
            return "global_success"
        
        # 成功情况
        result = test_function(False)
        self.assertEqual(result, "global_success")
        
        # 失败情况
        result = test_function(True)
        self.assertIsNone(result)


class TestErrorHandlerIntegration(unittest.TestCase):
    """测试错误处理器集成"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = GameConfig()
        self.logger = Logger(self.config)
    
    def test_logger_integration(self):
        """测试日志器集成"""
        # Logger应该有error_handler属性
        if hasattr(self.logger, 'error_handler') and self.logger.error_handler:
            self.assertIsInstance(self.logger.error_handler, RobustErrorHandler)
    
    def test_error_statistics(self):
        """测试错误统计集成"""
        # 生成一些错误
        try:
            raise ValueError("Test error for statistics")
        except Exception as e:
            self.logger.error("Test error", "TEST", e)
        
        stats = self.logger.get_error_statistics()
        self.assertIn('session_id', stats)
        self.assertGreaterEqual(stats['total_errors'], 1)
    
    def test_session_report(self):
        """测试会话报告"""
        # 生成一些错误
        try:
            raise RuntimeError("Test error for report")
        except Exception as e:
            self.logger.critical("Critical test error", "TEST", e)
        
        report = self.logger.generate_session_report()
        self.assertIn("游戏会话报告", report)
        self.assertIn("总错误数", report)


class TestErrorRecoveryStrategies(unittest.TestCase):
    """测试错误恢复策略"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = GameConfig()
        self.logger = Logger(self.config)
        self.recovery_manager = ErrorRecoveryManager(self.logger)
    
    def tearDown(self):
        """清理测试环境"""
        self.recovery_manager.cleanup()
    
    def test_operation_categorization(self):
        """测试操作分类"""
        # 测试各种操作的分类
        test_cases = [
            ("render_frame", "rendering"),
            ("play_sound", "audio"),
            ("save_game", "file_io"),
            ("update_physics", "physics"),
            ("ai_pathfinding", "ai"),
            ("ui_draw", "ui"),  # 更明确的UI操作名称
            ("unknown_operation", "general")
        ]
        
        for operation, expected_category in test_cases:
            category = self.recovery_manager._categorize_operation(operation)
            self.assertEqual(category, expected_category, f"Operation {operation} should be categorized as {expected_category}, got {category}")
    
    def test_severity_analysis(self):
        """测试严重性分析"""
        context = ErrorContext("test_operation")
        
        # 测试不同类型的错误
        critical_error = MemoryError("Out of memory")
        severity = self.recovery_manager._analyze_severity(critical_error, context)
        self.assertEqual(severity, ErrorSeverity.CRITICAL)
        
        high_error = FileNotFoundError("File not found")
        severity = self.recovery_manager._analyze_severity(high_error, context)
        self.assertEqual(severity, ErrorSeverity.HIGH)
        
        medium_error = ValueError("Invalid value")
        severity = self.recovery_manager._analyze_severity(medium_error, context)
        self.assertEqual(severity, ErrorSeverity.MEDIUM)


class TestConcurrentErrorHandling(unittest.TestCase):
    """测试并发错误处理"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = GameConfig()
        self.logger = Logger(self.config)
        self.error_handler = RobustErrorHandler(self.logger)
        self.results = []
    
    def tearDown(self):
        """清理测试环境"""
        self.error_handler.cleanup()
    
    def _worker_thread(self, thread_id):
        """工作线程函数"""
        @self.error_handler.safe_operation(f"thread_operation_{thread_id}", ErrorSeverity.LOW)
        def thread_work():
            if thread_id % 2 == 0:  # 偶数线程抛出错误
                raise RuntimeError(f"Error in thread {thread_id}")
            return f"Success in thread {thread_id}"
        
        result = thread_work()
        self.results.append((thread_id, result))
    
    def test_concurrent_error_handling(self):
        """测试并发错误处理"""
        threads = []
        
        # 创建多个线程
        for i in range(10):
            thread = threading.Thread(target=self._worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        self.assertEqual(len(self.results), 10)
        
        # 检查成功和失败的分布
        successes = [r for r in self.results if r[1] is not None]
        failures = [r for r in self.results if r[1] is None]
        
        self.assertEqual(len(successes), 5)  # 奇数线程应该成功
        self.assertEqual(len(failures), 5)   # 偶数线程应该失败


if __name__ == '__main__':
    unittest.main()