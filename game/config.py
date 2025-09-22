"""
Game configuration and command line argument parsing
"""
import argparse
import sys
import os
from pathlib import Path
from .config_file import ConfigFile


class GameConfig:
    """Handles game configuration and command line argument parsing"""
    
    def __init__(self):
        """Initialize game configuration"""
        self.config_file = None
        self._load_config_file()
        self.parse_arguments()
        self._save_config_if_requested()
    
    def parse_int_arg(self, name, default=None):
        """Parse integer command line argument"""
        if name in sys.argv:
            try:
                idx = sys.argv.index(name)
                return int(sys.argv[idx + 1])
            except Exception:
                return default
        return default
    
    def parse_float_arg(self, name, default):
        """Parse float command line argument"""
        if name in sys.argv:
            try:
                idx = sys.argv.index(name)
                return float(sys.argv[idx + 1])
            except Exception:
                return default
        return default
    
    def _load_config_file(self):
        """Load configuration from file"""
        # Check for config file argument
        config_path = None
        if '--config' in sys.argv:
            try:
                idx = sys.argv.index('--config')
                config_path = sys.argv[idx + 1]
            except (IndexError, ValueError):
                pass
        
        # Default config files to try
        default_configs = ['game.json', 'config/game.json', 'game.ini', 'config/game.ini']
        
        if config_path:
            self.config_file = ConfigFile(config_path)
        else:
            # Try to find existing config file
            for config_name in default_configs:
                if Path(config_name).exists():
                    self.config_file = ConfigFile(config_name)
                    break
        
        # Create default config if none found and --create-config specified
        if '--create-config' in sys.argv:
            config_path = 'game.json'
            if '--config' in sys.argv:
                try:
                    idx = sys.argv.index('--config')
                    config_path = sys.argv[idx + 1]
                except (IndexError, ValueError):
                    pass
            
            self.config_file = ConfigFile(config_path)
            self.config_file.create_default_config()
            print(f"Created default configuration file: {config_path}")
    
    def toggle_debug_mode(self):
        """Toggle debug mode at runtime"""
        self.debug_mode = not self.debug_mode
        
        # Update related settings when debug mode changes
        if self.debug_mode:
            self.performance_monitoring = True
            self.show_fps = True
        
        # Save the new debug mode setting
        if self.config_file:
            try:
                self.config_file.set('game.debug', self.debug_mode)
                self.config_file.save()
            except Exception as e:
                # Silently fail if unable to save
                pass
        
        return self.debug_mode
    
    def get_debug_status(self) -> str:
        """Get current debug mode status as a formatted string"""
        return f"Debug Mode: {'ON' if self.debug_mode else 'OFF'}"
    
    def _save_config_if_requested(self):
        """Save current configuration to file if requested"""
        if '--save-config' in sys.argv and self.config_file:
            # Update config file with current settings
            self._update_config_from_current_settings()
            if self.config_file.save():
                print(f"Configuration saved to: {self.config_file.config_path}")
            else:
                print("Failed to save configuration file")
    
    def _update_config_from_current_settings(self):
        """Update config file with current game settings"""
        if not self.config_file:
            return
        
        # Update display settings
        self.config_file.set('display.width', getattr(self, 'screen_width', 1024))
        self.config_file.set('display.height', getattr(self, 'screen_height', 768))
        
        # Update game settings
        self.config_file.set('game.map_width', self.map_width)
        self.config_file.set('game.map_height', self.map_height)
        self.config_file.set('game.rooms', self.rooms)
        self.config_file.set('game.enemies', self.enemies)
        self.config_file.set('game.debug', self.debug_mode)
        self.config_file.set('game.seed', getattr(self, 'seed', None))
        
        # Update player settings
        self.config_file.set('player.sprint_multiplier', self.sprint_multiplier)
        self.config_file.set('player.sprint_cost', self.sprint_cost)
        self.config_file.set('player.stamina_max', self.stamina_max)
        self.config_file.set('player.stamina_regen', self.stamina_regen)
        self.config_file.set('player.sprint_cooldown_ms', self.sprint_cooldown_ms)
        
        # Update FOV settings
        self.config_file.set('fov.sight_radius', getattr(self, 'sight_radius', 6))
        self.config_file.set('fov.enabled', getattr(self, 'enable_fov', True))
        
        # Update camera settings
        self.config_file.set('camera.lerp', self.cam_lerp)
        self.config_file.set('camera.deadzone', self.cam_deadzone)
        
        # Update debug settings
        self.config_file.set('debug.show_fps', self.show_fps)
        self.config_file.set('debug.show_coords', self.show_coordinates)
        self.config_file.set('debug.performance_monitoring', getattr(self, 'perf_mode', False))
    
    def _get_config_value(self, key, default=None, section=None):
        """Get value from config file with fallback to default"""
        if self.config_file:
            return self.config_file.get(key, default)
        return default
    
    def parse_arguments(self):
        """Parse all command line arguments"""
        # Handle help request
        if '--help' in sys.argv or '-h' in sys.argv:
            self.show_help()
            sys.exit(0)
        
        # Basic flags
        self.regen = '--regen' in sys.argv
        self.debug_mode = '--debug' in sys.argv or self._get_config_value('game.debug', False)
        
        # Map generation parameters
        map_w = self.parse_int_arg('--map-width', None)
        map_h = self.parse_int_arg('--map-height', None)
        self.map_width = map_w or self._get_config_value('game.map_width', 100)
        self.map_height = map_h or self._get_config_value('game.map_height', 40)
        
        # View parameters
        self.view_width = self.parse_int_arg('--view-w', 24)
        self.view_height = self.parse_int_arg('--view-h', 16)
        
        # Generator parameters
        self.rooms = self.parse_int_arg('--rooms', None) or self._get_config_value('game.rooms', 18)
        self.min_room = self.parse_int_arg('--min-room', None) or self._get_config_value('game.min_room', 5)
        self.max_room = self.parse_int_arg('--max-room', None) or self._get_config_value('game.max_room', 16)
        self.enemies = self.parse_int_arg('--enemies', None) or self._get_config_value('game.enemies', 8)
        self.seed = self.parse_int_arg('--seed', None) or self._get_config_value('game.seed', None)
        self.corridor_radius = self.parse_int_arg('--corridor-radius', None) or self._get_config_value('game.corridor_radius', 1)
        
        # Camera parameters
        self.cam_lerp = self.parse_float_arg('--cam-lerp', None) or self._get_config_value('camera.lerp', 0.2)
        self.cam_deadzone = self.parse_float_arg('--cam-deadzone', None) or self._get_config_value('camera.deadzone', 0.0)
        
        # Player parameters
        self.sprint_multiplier = self.parse_float_arg('--sprint-multiplier', None) or self._get_config_value('player.sprint_multiplier', 0.6)
        self.sprint_cost = self.parse_float_arg('--sprint-cost', None) or self._get_config_value('player.sprint_cost', 35.0)
        self.stamina_max = self.parse_float_arg('--stamina-max', None) or self._get_config_value('player.stamina_max', 100.0)
        self.stamina_regen = self.parse_float_arg('--stamina-regen', None) or self._get_config_value('player.stamina_regen', 12.0)
        self.sprint_cooldown_ms = self.parse_int_arg('--sprint-cooldown-ms', None) or self._get_config_value('player.sprint_cooldown_ms', 800)
        
        # FOV parameters
        self.sight_radius = self.parse_int_arg('--sight-radius', None) or self._get_config_value('fov.sight_radius', 6)
        self.enable_fov = '--enable-fov' in sys.argv if '--enable-fov' in sys.argv or '--disable-fov' in sys.argv else self._get_config_value('fov.enabled', True)
        if '--disable-fov' in sys.argv:
            self.enable_fov = False
        
        # Logging configuration
        self.max_log_size = self.parse_int_arg('--max-log-size', None) or self._get_config_value('logging.max_log_size', 512 * 1024)  # 512KB
        self.max_log_files = self.parse_int_arg('--max-log-files', None) or self._get_config_value('logging.max_log_files', 3)
        self.enable_performance_logging = '--enable-perf-logging' in sys.argv if '--enable-perf-logging' in sys.argv or '--disable-perf-logging' in sys.argv else self._get_config_value('logging.enable_performance_logging', False)
        if '--disable-perf-logging' in sys.argv:
            self.enable_performance_logging = False
        self.log_only_important = '--verbose-logging' not in sys.argv and self._get_config_value('logging.log_only_important', True)
        
        # Debug file configuration
        self.save_debug_levels = '--save-debug-levels' in sys.argv or self._get_config_value('debug.save_debug_levels', False)
        self.max_debug_levels = self.parse_int_arg('--max-debug-levels', None) or self._get_config_value('debug.max_debug_levels', 3)
        
        # Display parameters
        self.tile_size = 24
        self.fps = 30
        
        # Logging and debug configuration
        self.verbose_logging = '--verbose' in sys.argv
        self.performance_monitoring = '--perf' in sys.argv or self.debug_mode
        self.game_log_max = self.parse_int_arg('--log-max', 8)
        
        # Developer tools
        self.show_fps = '--show-fps' in sys.argv or self.debug_mode
        self.show_coordinates = '--show-coords' in sys.argv
        self.infinite_health = '--god-mode' in sys.argv
        self.infinite_stamina = '--infinite-stamina' in sys.argv
        self.skip_intro = '--skip-intro' in sys.argv
        
        # Game constants
        self.move_cooldown = 150  # ms per tile when walking
        self.screen_shake_time = 250
        self.screen_shake_amplitude = 6
    
    def show_help(self):
        """Display help information"""
        help_text = """
PyGame 字符地牢探索游戏 - 命令行参数

基本选项:
  --help, -h              显示此帮助信息
  --debug                 启用调试模式
  --verbose               详细日志输出
  --perf                  性能监控
  --regen                 强制重新生成地牢

配置文件:
  --config <文件>         指定配置文件
  --create-config         创建默认配置文件
  --save-config           保存当前设置到配置文件

日志和调试:
  --max-log-size <字节>   最大日志文件大小 (默认: 512KB)
  --max-log-files <数量>  保留的日志文件数量 (默认: 3)
  --enable-perf-logging   启用性能日志
  --disable-perf-logging  禁用性能日志
  --verbose-logging       详细日志输出
  --save-debug-levels     保存调试关卡文件
  --max-debug-levels <数量> 保留的调试关卡数量 (默认: 3)

地图生成:
  --map-width <数字>      地图宽度 (默认: 100)
  --map-height <数字>     地图高度 (默认: 40)
  --rooms <数字>          房间数量 (默认: 18)
  --enemies <数字>        敌人数量 (默认: 8)
  --min-room <数字>       最小房间大小 (默认: 5)
  --max-room <数字>       最大房间大小 (默认: 16)
  --corridor-radius <数字> 走廊半径 (默认: 1)
  --seed <数字>           随机种子

显示设置:
  --view-w <数字>         视窗宽度(瓦片) (默认: 24)
  --view-h <数字>         视窗高度(瓦片) (默认: 16)
  --show-fps              显示FPS
  --show-coords           显示坐标

相机设置:
  --cam-lerp <浮点数>     相机跟随平滑度 (默认: 0.2)
  --cam-deadzone <浮点数> 相机死区 (默认: 0.0)

玩家设置:
  --sprint-multiplier <浮点数>    冲刺速度倍数 (默认: 0.6)
  --sprint-cost <浮点数>          冲刺体力消耗 (默认: 35.0)
  --stamina-max <浮点数>          最大体力 (默认: 100.0)
  --stamina-regen <浮点数>        体力恢复速度 (默认: 12.0)
  --sprint-cooldown-ms <数字>     冲刺冷却时间(毫秒) (默认: 800)

视野系统:
  --sight-radius <数字>           视野半径 (默认: 6)
  --enable-fov                    启用视野系统 (默认: 启用)
  --disable-fov                   禁用视野系统

开发者选项:
  --god-mode              无敌模式
  --infinite-stamina      无限体力
  --skip-intro            跳过介绍
  --log-max <数字>        最大日志条数 (默认: 8)

控制说明:
  WASD/方向键             移动
  Shift                   冲刺
  空格                    攻击
  E/回车                  交互
  Tab                     显示出口指示器
  K                       调试信息
  F12                     切换调试模式
  1-5                     切换调试面板 (调试模式下)
  Esc                     退出
"""
        print(help_text)