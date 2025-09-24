import os
import traceback
import pygame
import json
import threading
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

"""
Enhanced logging and error handling utilities
"""


# Import enhanced error handling
try:
    from .error_handling import RobustErrorHandler, initialize_global_error_handler

    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False


class Logger:
    """Enhanced logging system for the game"""

    def __init__(self, config):
        self.config = config
        self.debug_enabled = getattr(config, 'debug_mode', False)

        # Enhanced logging features with size and retention controls
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_directory = Path("logs")
        self.log_directory.mkdir(exist_ok=True)

        # Logging configuration
        self.max_log_size = getattr(config, 'max_log_size', 512 * 1024)  # 512KB default
        self.max_log_files = getattr(config, 'max_log_files', 3)  # Keep only 3 files
        self.enable_performance_logging = getattr(config, 'enable_performance_logging', False)
        self.log_only_important = getattr(config, 'log_only_important', True)  # Reduce verbosity

        # Create organized subdirectories
        (self.log_directory / "session").mkdir(exist_ok=True)
        (self.log_directory / "error").mkdir(exist_ok=True)
        if self.enable_performance_logging:
            (self.log_directory / "performance").mkdir(exist_ok=True)

        # Multiple log files for different purposes - now organized in subdirectories
        self.log_file = self.log_directory / "session" / f"game_{self.session_id}.log"
        self.error_log = self.log_directory / "error" / f"error_{self.session_id}.log"
        if self.enable_performance_logging:
            self.performance_log = self.log_directory / "performance" / f"performance_{self.session_id}.log"
        else:
            self.performance_log = None

        # Clean up old logs on startup
        self._cleanup_old_logs()

        # Legacy debug directory for compatibility
        self.debug_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'debug')

        # In-game log buffer for display
        self.game_logs: List[str] = []
        self.max_game_logs = 8

        # Performance tracking
        self.performance_data = {}

        # Thread safety
        self.log_lock = threading.Lock()

        # Error statistics
        self.error_stats = {'total_errors': 0, 'critical_errors': 0, 'session_start': datetime.now()}

        # Initialize directories
        try:
            os.makedirs(self.debug_dir, exist_ok=True)
        except Exception as e:
            # Use internal warning method; if that fails fall back to a minimal print
            try:
                self.warning(f"Could not create debug directory: {e}", "LOGGER")
            except Exception:
                # keep only a minimal console message to aid debugging in very early init
                print(f"Warning: Could not create debug directory: {e}")

        # Initialize enhanced error handling
        if ERROR_HANDLING_AVAILABLE:
            initialize_global_error_handler(self)
            self.error_handler = RobustErrorHandler(self)
        else:
            self.error_handler = None

        # Initialize auto folder maintenance
        self.auto_maintenance = None
        try:
            from tools.auto_maintenance import get_auto_maintenance

            self.auto_maintenance = get_auto_maintenance(self)
            self.auto_maintenance.start_maintenance()
            self.debug("Auto folder maintenance started", "LOGGER")
        except ImportError:
            self.debug("Auto maintenance not available", "LOGGER")
        except Exception as e:
            self.debug(f"Failed to start auto maintenance: {e}", "LOGGER")

        self.info(f"Logger initialized with session ID: {self.session_id}")

    def _cleanup_old_logs(self):
        """Clean up old log files based on retention policy"""
        try:
            from datetime import timedelta

            cutoff_time = datetime.now() - timedelta(days=3)  # Keep 3 days

            for subdir in ["session", "error", "performance"]:
                subdir_path = self.log_directory / subdir
                if not subdir_path.exists():
                    continue

                # Get all log files in subdirectory
                log_files = list(subdir_path.glob("*.log"))

                # Remove old files
                for log_file in log_files:
                    try:
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < cutoff_time:
                            log_file.unlink()
                            try:
                                self.info(f"Removed old log: {log_file}", "LOGGER")
                            except Exception:
                                # minimal fallback
                                print(f"Removed old log: {log_file}")
                    except Exception:
                        continue

                # If still too many files, keep only the newest ones
                remaining_files = list(subdir_path.glob("*.log"))
                if len(remaining_files) > self.max_log_files:
                    # Sort by modification time, newest first
                    remaining_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    # Remove excess files
                    for old_file in remaining_files[self.max_log_files :]:
                        try:
                            old_file.unlink()
                            try:
                                self.info(f"Removed excess log: {old_file}", "LOGGER")
                            except Exception:
                                print(f"Removed excess log: {old_file}")
                        except Exception:
                            continue

        except Exception as e:
            try:
                self.warning(f"Failed to cleanup old logs: {e}", "LOGGER")
            except Exception:
                print(f"Warning: Failed to cleanup old logs: {e}")

    def _should_log(self, level: str, category: str) -> bool:
        """Determine if a message should be logged based on filters"""
        if not self.log_only_important:
            return True

        # Always log errors and warnings
        if level in ["ERROR", "CRITICAL", "WARN"]:
            return True

        # Filter out verbose categories in normal mode
        if self.log_only_important and category in ["MOVEMENT", "RENDER", "INPUT", "FRAME"]:
            return False

        return True

    def debug(self, msg: str, category: str = "DEBUG"):
        """Log debug message"""
        if not self.debug_enabled:
            return

        self._log(msg, "DEBUG", category)

    def info(self, msg: str, category: str = "INFO"):
        """Log info message"""
        self._log(msg, "INFO", category)

    def warning(self, msg: str, category: str = "WARN"):
        """Log warning message"""
        self._log(msg, "WARN", category)
        # Also print minimally to console for visibility in early stages
        try:
            print(f"WARNING: {msg}")
        except Exception:
            pass

    def error(self, msg: str, category: str = "ERROR", exception: Optional[Exception] = None):
        """Log error message with optional exception"""
        self.error_stats['total_errors'] += 1
        self._log(msg, "ERROR", category)
        self._log_to_error_file(msg, "ERROR", category, exception)
        # Also print minimally to console for visibility in early stages
        try:
            print(f"ERROR: {msg}")
        except Exception:
            pass

        if exception:
            tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
            tb_str = ''.join(tb)
            self._log(f"Exception details:\n{tb_str}", "ERROR", category)
            self._log_to_error_file(f"Exception details:\n{tb_str}", "ERROR", category)
            # Print stacktrace minimally to console to help debugging
            try:
                print(tb_str)
            except Exception:
                pass

    def critical(self, msg: str, category: str = "CRITICAL", exception: Optional[Exception] = None):
        """Log critical error message"""
        self.error_stats['total_errors'] += 1
        self.error_stats['critical_errors'] += 1
        self._log(msg, "CRITICAL", category)
        self._log_to_error_file(msg, "CRITICAL", category, exception)
        # Print critical messages minimally to console
        try:
            print(f"CRITICAL: {msg}")
        except Exception:
            pass

        if exception:
            tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
            tb_str = ''.join(tb)
            self._log(f"Critical exception details:\n{tb_str}", "CRITICAL", category)
            self._log_to_error_file(f"Critical exception details:\n{tb_str}", "CRITICAL", category)
            try:
                print(tb_str)
            except Exception:
                pass

    def _log(self, msg: str, level: str, category: str):
        """Internal logging method with filtering and size control"""
        try:
            # Check if this message should be logged
            if not self._should_log(level, category):
                return

            # Check log file size and rotate if necessary
            if self.log_file.exists() and self.log_file.stat().st_size > self.max_log_size:
                self._rotate_log_file()

            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            pygame_time = pygame.time.get_ticks() if pygame.get_init() else 0

            # Format log entry
            entry = f"[{timestamp}][{pygame_time:06d}][{level}][{category}] {msg}"

            # Add to in-game log buffer
            if self.debug_enabled:
                self.game_logs.append(entry)
                if len(self.game_logs) > self.max_game_logs:
                    self.game_logs.pop(0)

            # Write to file
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(entry + "\n")
            except Exception:
                pass  # Silently fail file logging to avoid recursion

        except Exception:
            pass  # Silently fail logging to avoid recursion

    def _rotate_log_file(self):
        """Rotate log file when it gets too large"""
        try:
            # Create backup filename with timestamp
            backup_name = f"game_{self.session_id}_old_{datetime.now().strftime('%H%M%S')}.log"
            backup_path = self.log_file.parent / backup_name

            # Move current log to backup
            self.log_file.rename(backup_path)

            # Clean up old backups
            backups = list(self.log_file.parent.glob("*_old_*.log"))
            if len(backups) > 2:  # Keep only 2 old backups
                backups.sort(key=lambda f: f.stat().st_mtime)
                for old_backup in backups[:-2]:
                    old_backup.unlink()

        except Exception:
            pass  # Silently fail rotation

    def log_performance(self, operation: str, duration_ms: float):
        """Log performance data"""
        if not self.debug_enabled:
            return

        if operation not in self.performance_data:
            self.performance_data[operation] = []

        self.performance_data[operation].append(duration_ms)

        # Keep only last 100 samples
        if len(self.performance_data[operation]) > 100:
            self.performance_data[operation].pop(0)

    def get_performance_stats(self, operation: str) -> Dict[str, float]:
        """Get performance statistics for an operation"""
        if operation not in self.performance_data:
            return {}

        data = self.performance_data[operation]
        if not data:
            return {}

        return {'avg': sum(data) / len(data), 'min': min(data), 'max': max(data), 'count': len(data)}

    def write_debug_snapshot(self, filename: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Write a debug snapshot file"""
        try:
            filepath = os.path.join(self.debug_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

                if metadata:
                    f.write("\n\n--- Metadata ---\n")
                    for key, value in metadata.items():
                        f.write(f"{key}={value}\n")

            self.debug(f"Wrote debug snapshot: {filename}", "SNAPSHOT")
            return filepath

        except Exception as e:
            self.error(f"Failed to write debug snapshot {filename}: {e}", "SNAPSHOT")
            return None

    def clear_old_logs(self, max_age_days: int = 7):
        """Clear old log files"""
        try:
            import time

            current_time = time.time()

            for filename in os.listdir(self.debug_dir):
                filepath = os.path.join(self.debug_dir, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > (max_age_days * 24 * 3600):  # Convert days to seconds
                        os.remove(filepath)
                        self.debug(f"Removed old debug file: {filename}", "CLEANUP")
        except Exception as e:
            self.warning(f"Failed to clean old logs: {e}", "CLEANUP")

    def _log_to_error_file(self, msg: str, level: str, category: str, exception: Optional[Exception] = None):
        """Log to dedicated error file"""
        with self.log_lock:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                pygame_time = pygame.time.get_ticks() if pygame.get_init() else 0

                entry = f"[{timestamp}][{pygame_time:06d}][{level}][{category}] {msg}"

                with open(self.error_log, 'a', encoding='utf-8') as f:
                    f.write(entry + "\n")

                    if exception:
                        f.write(f"Exception type: {type(exception).__name__}\n")
                        f.write(f"Exception args: {exception.args}\n")
                        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
                        f.write("".join(tb) + "\n")
                        f.write("-" * 50 + "\n")

            except Exception:
                pass  # Silently fail to avoid recursion

    def log_performance_detailed(self, operation: str, duration_ms: float, context: Optional[Dict[str, Any]] = None):
        """Log detailed performance data"""
        if not self.enable_performance_logging or self.performance_log is None:
            return

        with self.log_lock:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                perf_data = {
                    'timestamp': timestamp,
                    'operation': operation,
                    'duration_ms': duration_ms,
                    'context': context or {},
                }

                with open(self.performance_log, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(perf_data) + "\n")

            except Exception:
                pass

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for this session"""
        session_duration = (datetime.now() - self.error_stats['session_start']).total_seconds()

        return {
            'session_id': self.session_id,
            'session_duration_seconds': session_duration,
            'total_errors': self.error_stats['total_errors'],
            'critical_errors': self.error_stats['critical_errors'],
            'error_rate': self.error_stats['total_errors'] / max(session_duration / 60, 1),  # errors per minute
            'has_enhanced_handler': self.error_handler is not None,
        }

    def generate_session_report(self) -> str:
        """Generate a session report"""
        stats = self.get_error_statistics()

        report = []
        report.append(f"游戏会话报告 - {self.session_id}")
        report.append("=" * 50)
        report.append(f"会话时长: {stats['session_duration_seconds']:.1f} 秒")
        report.append(f"总错误数: {stats['total_errors']}")
        report.append(f"严重错误数: {stats['critical_errors']}")
        report.append(f"错误率: {stats['error_rate']:.2f} 错误/分钟")
        report.append(f"增强错误处理: {'启用' if stats['has_enhanced_handler'] else '禁用'}")
        report.append("")

        # 添加错误处理器统计
        if self.error_handler:
            error_handler_stats = self.error_handler.get_error_statistics()
            report.append("错误处理统计:")
            report.append(f"  错误模式数: {len(error_handler_stats.get('error_patterns', {}))}")
            report.append(f"  被抑制的错误: {error_handler_stats.get('suppressed_errors', 0)}")
            report.append("")

        return "\n".join(report)


class ErrorHandler:
    """Enhanced error handling and recovery"""

    def __init__(self, logger: Logger):
        self.logger = logger
        self.error_counts = {}
        self.max_error_count = 10

    def handle_exception(self, operation: str, exception: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle an exception with logging and recovery logic
        Returns True if the operation should be retried, False if it should be skipped
        """
        # Log the exception
        self.logger.error(f"Exception in {operation}: {exception}", operation, exception)

        # Track error frequency
        if operation not in self.error_counts:
            self.error_counts[operation] = 0
        self.error_counts[operation] += 1

        # Too many errors in this operation, give up
        if self.error_counts[operation] > self.max_error_count:
            self.logger.error(f"Too many errors in {operation}, disabling", operation)
            return False

        # Log context if provided
        if context:
            self.logger.debug(f"Error context for {operation}: {context}", operation)

        # Some operations can be safely retried
        if operation in ['audio_playback', 'sprite_particles', 'floating_text']:
            return False  # Skip non-critical operations

        return True  # Retry by default

    def safe_call(self, func, operation: str, *args, **kwargs):
        """Safely call a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if self.handle_exception(operation, e):
                self.logger.debug(f"Retrying {operation} after error", operation)
                try:
                    return func(*args, **kwargs)
                except Exception as e2:
                    self.logger.error(f"Retry failed for {operation}: {e2}", operation)
            return None


def create_performance_timer(logger: Logger, operation: str):
    """Context manager for timing operations"""

    class PerformanceTimer:
        def __init__(self):
            self.start_time = None

        def __enter__(self):
            self.start_time = pygame.time.get_ticks()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time is not None:
                duration = pygame.time.get_ticks() - self.start_time
                logger.log_performance(operation, duration)

    return PerformanceTimer()
