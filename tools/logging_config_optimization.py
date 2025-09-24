"""
游戏配置 - 日志和调试设置优化
减少日志文件的生成和大小
"""

# 在 game/config.py 中添加日志控制选项
# 在 game/logger.py 中实现日志轮转和大小限制

# 日志配置优化
LOGGING_CONFIG = {
    # 日志级别 - 减少详细日志输出
    "default_level": "INFO",  # 从 DEBUG 改为 INFO
    "error_level": "ERROR",
    
    # 日志文件大小限制
    "max_file_size": 1024 * 1024,  # 1MB per file
    "max_files": 5,  # 最多保留5个日志文件
    
    # 日志轮转设置
    "rotate_on_startup": True,
    "compress_old_logs": True,
    
    # 性能日志控制
    "enable_performance_logging": False,  # 默认关闭性能日志
    "performance_log_interval": 60,  # 60秒记录一次
    
    # 调试文件控制
    "save_debug_levels": False,  # 默认不保存调试关卡文件
    "max_debug_levels": 3,  # 最多保留3个调试关卡
}

# 运行时日志控制
RUNTIME_LOG_FILTERS = {
    # 过滤频繁的消息
    "filter_movement_logs": True,
    "filter_render_logs": True,
    "filter_input_logs": True,
    
    # 只记录重要事件
    "log_only_errors": False,
    "log_game_events": True,  # 游戏状态变化
    "log_system_events": True,  # 系统事件
}