"""
PyGame 字符地牢探索游戏

一个基于PyGame的2D字符模式地牢探索游戏。
支持多层地牢、实体交互、战斗系统和debug工具。

主要模块:
- config: 游戏配置和命令行参数
- state: 游戏状态管理
- input: 输入处理
- floors: 地牢层级和生成
- renderer: 渲染系统
- game: 主游戏逻辑
- player: 玩家实体
- entities: 游戏实体系统
- logging: 日志和错误处理
- debug: 调试覆盖层
- performance: 性能监控和优化

使用方法:
    python main.py              # 启动游戏
    python main.py --help       # 查看所有选项
    python main.py --debug      # 调试模式
    python main.py --perf       # 性能监控
"""

__version__ = "1.0.0"
__author__ = "Game Developer"
__description__ = "PyGame 字符地牢探索游戏"

# 导入主要类以便于导入
from .config import GameConfig
from .state import GameState
from .game import Game
from .logger import Logger, ErrorHandler, create_performance_timer
from .debug import DebugOverlay
from .performance import PerformanceOptimizer

__all__ = ['GameConfig', 'GameState', 'Game', 'Logger', 'ErrorHandler', 'create_performance_timer', 'DebugOverlay', 'PerformanceOptimizer']
