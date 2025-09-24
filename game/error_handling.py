import time
import traceback
import threading
from typing import Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import functools
import weakref

#!/usr/bin/env python3
"""
增强的错误处理和恢复系统
"""


class ErrorSeverity(Enum):
    """错误严重级别"""

    CRITICAL = "CRITICAL"  # 导致游戏崩溃的错误
    HIGH = "HIGH"  # 严重影响游戏功能的错误
    MEDIUM = "MEDIUM"  # 中等影响的错误
    LOW = "LOW"  # 轻微影响的错误
    INFO = "INFO"  # 信息性错误


class RecoveryStrategy(Enum):
    """恢复策略"""

    RETRY = "RETRY"  # 重试操作
    SKIP = "SKIP"  # 跳过操作
    FALLBACK = "FALLBACK"  # 使用备用方案
    RESTART = "RESTART"  # 重启组件
    TERMINATE = "TERMINATE"  # 终止程序


class ErrorContext:
    """错误上下文信息"""

    def __init__(self, operation: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.operation = operation
        self.severity = severity
        self.timestamp = datetime.now()
        self.thread_id = threading.get_ident()
        self.stack_trace = traceback.format_stack()
        self.game_state = {}
        self.system_info = {}
        self.retry_count = 0
        self.max_retries = 3

    def add_game_state(self, **state):
        """添加游戏状态信息"""
        self.game_state.update(state)

    def add_system_info(self, **info):
        """添加系统信息"""
        self.system_info.update(info)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'operation': self.operation,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'thread_id': self.thread_id,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'game_state': self.game_state,
            'system_info': self.system_info,
            'stack_trace': self.stack_trace[-5:],  # 只保留最后5层调用栈
        }


class ErrorRecoveryManager:
    """错误恢复管理器"""

    def __init__(self, logger=None):
        self.logger = logger

        # 错误统计和历史
        self.error_history = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.error_patterns = defaultdict(list)

        # 恢复策略映射
        self.recovery_strategies = {
            'rendering': RecoveryStrategy.RETRY,
            'audio': RecoveryStrategy.SKIP,
            'file_io': RecoveryStrategy.FALLBACK,
            'network': RecoveryStrategy.RETRY,
            'memory': RecoveryStrategy.RESTART,
            'physics': RecoveryStrategy.RETRY,
            'ai': RecoveryStrategy.SKIP,
            'ui': RecoveryStrategy.FALLBACK,
        }

        # 严重级别阈值
        self.severity_thresholds = {
            ErrorSeverity.CRITICAL: 1,  # 1次就算严重
            ErrorSeverity.HIGH: 3,  # 3次以上算严重
            ErrorSeverity.MEDIUM: 10,  # 10次以上算严重
            ErrorSeverity.LOW: 50,  # 50次以上算严重
        }

        # 错误抑制（避免日志洪水）
        self.error_suppression = {}
        self.suppression_window = 60  # 60秒内相同错误只记录一次

        # 备用操作注册表
        self.fallback_operations = {}

        # 监控线程
        self.monitoring_enabled = True
        self.monitoring_thread = threading.Thread(target=self._monitor_errors, daemon=True)
        self.monitoring_thread.start()

    def register_fallback(self, operation: str, fallback_func: Callable):
        """注册备用操作"""
        self.fallback_operations[operation] = fallback_func
        if self.logger:
            self.logger.debug(f"Registered fallback for {operation}")

    def handle_error(self, error: Exception, context: ErrorContext) -> RecoveryStrategy:
        """处理错误并返回恢复策略"""
        # 记录错误
        self._record_error(error, context)

        # 检查是否需要抑制
        if self._should_suppress_error(error, context):
            return RecoveryStrategy.SKIP

        # 分析错误严重性
        severity = self._analyze_severity(error, context)
        context.severity = severity

        # 选择恢复策略
        strategy = self._choose_recovery_strategy(error, context)

        # 记录决策
        if self.logger:
            self.logger.warning(
                f"Error in {context.operation}: {error} | " f"Severity: {severity.value} | Strategy: {strategy.value}",
                "ERROR_RECOVERY",
            )

        return strategy

    def _record_error(self, error: Exception, context: ErrorContext):
        """记录错误到历史"""
        error_record = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context.to_dict(),
        }

        self.error_history.append(error_record)
        self.error_counts[context.operation] += 1

        # 记录错误模式
        error_key = f"{type(error).__name__}:{context.operation}"
        self.error_patterns[error_key].append(datetime.now())

    def _should_suppress_error(self, error: Exception, context: ErrorContext) -> bool:
        """检查是否应该抑制错误（避免日志洪水）"""
        error_key = f"{type(error).__name__}:{context.operation}"
        current_time = datetime.now()

        if error_key in self.error_suppression:
            last_reported = self.error_suppression[error_key]
            if (current_time - last_reported).seconds < self.suppression_window:
                return True

        self.error_suppression[error_key] = current_time
        return False

    def _analyze_severity(self, error: Exception, context: ErrorContext) -> ErrorSeverity:
        """分析错误严重性"""
        # 基于错误类型的基础严重性
        if isinstance(error, (MemoryError, SystemExit, KeyboardInterrupt)):
            return ErrorSeverity.CRITICAL
        elif isinstance(error, (ImportError, FileNotFoundError, PermissionError)):
            return ErrorSeverity.HIGH
        elif isinstance(error, (ValueError, TypeError, AttributeError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

    def _choose_recovery_strategy(self, error: Exception, context: ErrorContext) -> RecoveryStrategy:
        """选择恢复策略"""
        # 基于操作类型的策略
        operation_category = self._categorize_operation(context.operation)
        base_strategy = self.recovery_strategies.get(operation_category, RecoveryStrategy.SKIP)

        # 基于错误严重性调整策略
        if context.severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy.TERMINATE
        elif context.severity == ErrorSeverity.HIGH:
            if base_strategy == RecoveryStrategy.RETRY:
                return RecoveryStrategy.FALLBACK

        # 基于重试次数调整策略
        if context.retry_count >= context.max_retries:
            if base_strategy == RecoveryStrategy.RETRY:
                return RecoveryStrategy.FALLBACK
            elif base_strategy == RecoveryStrategy.FALLBACK:
                return RecoveryStrategy.SKIP

        return base_strategy

    def _categorize_operation(self, operation: str) -> str:
        """操作分类 - 优先级从高到低"""
        operation_lower = operation.lower()

        # 最具体的分类优先
        if any(keyword in operation_lower for keyword in ['ui', 'interface', 'menu']):
            return 'ui'
        elif any(keyword in operation_lower for keyword in ['ai', 'npc', 'enemy']):
            return 'ai'
        elif any(keyword in operation_lower for keyword in ['physics', 'collision', 'movement']):
            return 'physics'
        elif any(keyword in operation_lower for keyword in ['memory', 'cache', 'gc']):
            return 'memory'
        elif any(keyword in operation_lower for keyword in ['network', 'http', 'request']):
            return 'network'
        elif any(keyword in operation_lower for keyword in ['file', 'save', 'load', 'write', 'read']):
            return 'file_io'
        elif any(keyword in operation_lower for keyword in ['audio', 'sound', 'music']):
            return 'audio'
        elif any(keyword in operation_lower for keyword in ['render', 'draw', 'display']):
            return 'rendering'
        else:
            return 'general'

    def _monitor_errors(self):
        """监控错误模式"""
        while self.monitoring_enabled:
            try:
                time.sleep(30)  # 每30秒检查一次
                self._analyze_error_patterns()
            except Exception:
                pass  # 监控线程不应该影响主程序

    def _analyze_error_patterns(self):
        """分析错误模式"""
        current_time = datetime.now()

        for error_key, timestamps in self.error_patterns.items():
            # 清理旧的时间戳（只保留最近1小时的）
            recent_timestamps = [ts for ts in timestamps if (current_time - ts).seconds < 3600]
            self.error_patterns[error_key] = recent_timestamps

            # 检查是否有异常频率
            if len(recent_timestamps) > 10:  # 1小时内超过10次
                if self.logger:
                    self.logger.warning(
                        f"High frequency error detected: {error_key} ({len(recent_timestamps)} times in 1 hour)",
                        "ERROR_PATTERN",
                    )

    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        current_time = datetime.now()
        recent_errors = [error for error in self.error_history if (current_time - error['timestamp']).seconds < 3600]

        error_types = defaultdict(int)
        operations = defaultdict(int)

        for error in recent_errors:
            error_types[error['error_type']] += 1
            operations[error['context']['operation']] += 1

        return {
            'total_errors': len(self.error_history),
            'recent_errors': len(recent_errors),
            'error_types': dict(error_types),
            'error_operations': dict(operations),
            'error_patterns': {k: len(v) for k, v in self.error_patterns.items()},
            'suppressed_errors': len(self.error_suppression),
        }

    def generate_error_report(self) -> str:
        """生成错误报告"""
        stats = self.get_error_statistics()

        report = []
        report.append("错误处理报告")
        report.append("=" * 40)
        report.append(f"总错误数: {stats['total_errors']}")
        report.append(f"最近1小时错误数: {stats['recent_errors']}")
        report.append("")

        if stats['error_types']:
            report.append("错误类型分布:")
            for error_type, count in sorted(stats['error_types'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {error_type}: {count}")
            report.append("")

        if stats['error_operations']:
            report.append("操作错误分布:")
            for operation, count in sorted(stats['error_operations'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {operation}: {count}")
            report.append("")

        if stats['error_patterns']:
            report.append("错误模式:")
            for pattern, count in sorted(stats['error_patterns'].items(), key=lambda x: x[1], reverse=True):
                if count > 5:  # 只显示频繁的模式
                    report.append(f"  {pattern}: {count} (高频)")
            report.append("")

        return "\n".join(report)

    def cleanup(self):
        """清理资源"""
        self.monitoring_enabled = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1)


class RobustErrorHandler:
    """健壮的错误处理器"""

    def __init__(self, logger=None):
        self.logger = logger
        self.recovery_manager = ErrorRecoveryManager(logger)

        # 操作装饰器缓存
        self._decorated_operations = weakref.WeakKeyDictionary()

    def safe_operation(self, operation_name: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, max_retries: int = 3):
        """安全操作装饰器"""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                context = ErrorContext(operation_name, severity)
                context.max_retries = max_retries

                # 添加函数参数到上下文
                context.add_system_info(
                    function_name=func.__name__, args_count=len(args), kwargs_keys=list(kwargs.keys())
                )

                while context.retry_count <= context.max_retries:
                    try:
                        result = func(*args, **kwargs)

                        # 如果之前有错误，记录成功恢复
                        if context.retry_count > 0 and self.logger:
                            self.logger.info(
                                f"Operation {operation_name} recovered after {context.retry_count} retries"
                            )

                        return result

                    except Exception as e:
                        strategy = self.recovery_manager.handle_error(e, context)

                        if strategy == RecoveryStrategy.TERMINATE:
                            raise e
                        elif strategy == RecoveryStrategy.SKIP:
                            if self.logger:
                                self.logger.debug(f"Skipping operation {operation_name} due to error: {e}")
                            return None
                        elif strategy == RecoveryStrategy.FALLBACK:
                            fallback = self.recovery_manager.fallback_operations.get(operation_name)
                            if fallback:
                                try:
                                    return fallback(*args, **kwargs)
                                except Exception as fallback_error:
                                    if self.logger:
                                        self.logger.error(f"Fallback failed for {operation_name}: {fallback_error}")
                                    return None
                            else:
                                if self.logger:
                                    self.logger.warning(f"No fallback available for {operation_name}")
                                return None
                        elif strategy == RecoveryStrategy.RETRY:
                            context.retry_count += 1
                            if context.retry_count <= context.max_retries:
                                time.sleep(0.1 * context.retry_count)  # 指数退避
                                continue
                            else:
                                if self.logger:
                                    self.logger.error(f"Max retries exceeded for {operation_name}")
                                return None
                        else:
                            return None

                return None

            return wrapper

        return decorator

    def safe_call(self, func: Callable, operation_name: str, *args, **kwargs):
        """安全调用函数"""
        decorated_func = self.safe_operation(operation_name)(func)
        return decorated_func(*args, **kwargs)

    def register_fallback(self, operation_name: str, fallback_func: Callable):
        """注册备用操作"""
        self.recovery_manager.register_fallback(operation_name, fallback_func)

    def get_error_report(self) -> str:
        """获取错误报告"""
        return self.recovery_manager.generate_error_report()

    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计"""
        return self.recovery_manager.get_error_statistics()

    def cleanup(self):
        """清理资源"""
        self.recovery_manager.cleanup()


# 全局错误处理器实例
_global_error_handler: Optional[RobustErrorHandler] = None


def initialize_global_error_handler(logger=None):
    """初始化全局错误处理器"""
    global _global_error_handler
    _global_error_handler = RobustErrorHandler(logger)


def get_global_error_handler() -> Optional[RobustErrorHandler]:
    """获取全局错误处理器"""
    return _global_error_handler


def safe_operation(operation_name: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, max_retries: int = 3):
    """全局安全操作装饰器"""
    if _global_error_handler:
        return _global_error_handler.safe_operation(operation_name, severity, max_retries)
    else:
        # 如果没有全局处理器，返回简单的装饰器
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    try:
                        # Try to use module logger if available
                        if 'logger' in globals() and globals()['logger']:
                            try:
                                globals()['logger'].error(f"Error in {operation_name}: {e}", "ERROR")
                            except Exception:
                                print(f"Error in {operation_name}: {e}")
                        else:
                            print(f"Error in {operation_name}: {e}")
                    except Exception:
                        pass
                    return None

            return wrapper

        return decorator
