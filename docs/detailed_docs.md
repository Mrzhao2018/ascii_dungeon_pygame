# 游戏代码文档

自动生成的代码文档

## 目录

- [__init__](#--init--)
- [audio](#audio)
- [config](#config)
- [config_file](#config-file)
- [debug](#debug)
- [dialogs](#dialogs)
- [entities](#entities)
- [floors](#floors)
- [game](#game)
- [input](#input)
- [logging](#logging)
- [performance](#performance)
- [player](#player)
- [renderer](#renderer)
- [state](#state)
- [ui](#ui)
- [utils](#utils)

## __init__

**文件:** `__init__.py`

**描述:**

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

### 导入

- `from config import GameConfig`
- `from state import GameState`
- `from game import Game`
- `from logging import Logger, ErrorHandler`
- `from debug import DebugOverlay`
- `from performance import PerformanceOptimizer`

---

## audio

**文件:** `audio.py`

### 导入

- `import pygame`
- `import os`
- `import numpy`
- `import numpy`
- `import numpy`

### 函数

#### init_audio()

*无文档*

#### load_hit_sound(preferred_path)

*无文档*

#### load_sprint_sound(preferred_path)

*无文档*

#### load_sprint_ready_sound(preferred_path)

*无文档*

---

## config

**文件:** `config.py`

**描述:**

Game configuration and command line argument parsing

### 导入

- `import argparse`
- `import sys`
- `import os`
- `from pathlib import Path`
- `from config_file import ConfigFile`

### 类

#### GameConfig

Handles game configuration and command line argument parsing

**方法:**

- `__init__(self)`
  Initialize game configuration

- `parse_int_arg(self, name, default)`
  Parse integer command line argument

- `parse_float_arg(self, name, default)`
  Parse float command line argument

- `_load_config_file(self)`
  Load configuration from file

- `_save_config_if_requested(self)`
  Save current configuration to file if requested

- `_update_config_from_current_settings(self)`
  Update config file with current game settings

- `_get_config_value(self, key, default, section)`
  Get value from config file with fallback to default

- `parse_arguments(self)`
  Parse all command line arguments

- `show_help(self)`
  Display help information

---

## config_file

**文件:** `config_file.py`

**描述:**

Game configuration file management
Supports JSON and INI configuration files for persistent settings

### 导入

- `import json`
- `import configparser`
- `import os`
- `from pathlib import Path`
- `from typing import Dict, Any, Optional`

### 类

#### ConfigFile

Configuration file manager

**方法:**

- `__init__(self, config_path)`
  Initialize configuration file manager
  
  Args:
  config_path: Path to configuration file (defaults to game.conf)

- `load(self)`
  Load configuration from file
  
  Returns:
  True if loaded successfully, False otherwise

- `save(self)`
  Save configuration to file
  
  Returns:
  True if saved successfully, False otherwise

- `_load_json(self)`
  Load JSON configuration

- `_save_json(self)`
  Save JSON configuration

- `_load_ini(self)`
  Load INI configuration

- `_save_ini(self)`
  Save INI configuration

- `_convert_value(self, value)`
  Convert string value to appropriate type

- `get(self, key, default, section)`
  Get configuration value
  
  Args:
  key: Configuration key
  default: Default value if not found
  section: Section name for INI format
  
  Returns:
  Configuration value or default

- `set(self, key, value, section)`
  Set configuration value
  
  Args:
  key: Configuration key
  value: Value to set
  section: Section name for INI format

- `has(self, key, section)`
  Check if configuration key exists
  
  Args:
  key: Configuration key
  section: Section name for INI format
  
  Returns:
  True if key exists, False otherwise

- `delete(self, key, section)`
  Delete configuration key
  
  Args:
  key: Configuration key
  section: Section name for INI format
  
  Returns:
  True if deleted, False if not found

- `get_all_keys(self, section)`
  Get all configuration keys
  
  Args:
  section: Section name for INI format
  
  Returns:
  List of all keys

- `_get_nested_keys(self, data, prefix)`
  Get all nested keys from dictionary

- `export_to_args(self, prefix)`
  Export configuration as command line arguments
  
  Args:
  prefix: Argument prefix (e.g., "--")
  
  Returns:
  List of command line arguments

- `merge_from_args(self, args_dict)`
  Merge configuration from arguments dictionary
  
  Args:
  args_dict: Dictionary of arguments to merge

- `create_default_config(self)`
  Create default configuration file

### 函数

#### create_sample_configs()

Create sample configuration files

---

## debug

**文件:** `debug.py`

**描述:**

Enhanced debug overlay and developer tools

### 导入

- `import pygame`
- `from typing import List, Dict, Any, Optional`
- `from game import utils`

### 类

#### DebugOverlay

Enhanced debug overlay showing game state and performance

**方法:**

- `__init__(self, config, logger)`

- `_initialize_fonts(self)`
  Initialize debug fonts

- `toggle_panel(self, panel_name)`
  Toggle visibility of a debug panel

- `render(self, screen, game_state, player, entity_mgr, npcs)`
  Render all enabled debug panels

- `_render_performance_panel(self, screen)`
  Render performance statistics panel

- `_render_game_state_panel(self, screen, game_state)`
  Render game state information panel

- `_render_player_state_panel(self, screen, player)`
  Render player state information panel

- `_render_entity_debug_panel(self, screen, entity_mgr, npcs)`
  Render entity debug information panel

- `_render_logs_panel(self, screen, game_state)`
  Render game logs panel

- `_render_fps_counter(self, screen)`
  Render FPS counter in top-right corner

- `_render_coordinates(self, screen, player, game_state)`
  Render player coordinates

- `handle_debug_input(self, key)`
  Handle debug-specific input

---

## dialogs

**文件:** `dialogs.py`

### 导入

- `import json`
- `import os`
- `from typing import Dict, Tuple`
- `from game.utils import set_tile`

### 函数

#### load_npcs(level, WIDTH, HEIGHT)

*无文档*

#### get_dialog_for(npcs, pos)

*无文档*

---

## entities

**文件:** `entities.py`

### 导入

- `from typing import Dict, Tuple, List, Any, Optional, Callable`
- `import json`
- `import os`
- `from game.utils import set_tile`

### 类

#### Entity

**方法:**

- `__init__(self, x, y)`

- `to_config(self)`

- `from_config(cls, cfg)` (类方法)

#### Enemy

**继承:** `Entity`

**方法:**

- `__init__(self, x, y, hp, dir, kind)`

- `to_config(self)`

- `from_config(cls, cfg)` (类方法)

#### EntityManager

**方法:**

- `__init__(self)`

- `add(self, ent)`

- `get_entity_at(self, x, y)`

- `get_entity_by_id(self, ent_id)`

- `remove(self, ent_or_id)`

- `load_from_level(self, level)`

- `place_entity_near(self, level, WIDTH, HEIGHT, preferred)`

- `to_config_list(self)`

- `save_to_file(self, path)`

- `load_from_file(self, path)`

- `load_from_file(self, path, level)`
  Load entities from a JSON file. If level is provided, ensure entities are placed on the map:
  - If the target tile is '.', place the entity there (set map char to 'E').
  - Otherwise try to find the nearest '.' and place entity there; if none found, skip the entity.

- `update(self, level, player_pos, WIDTH, HEIGHT, move_interval_frames)`
  Update movable entities (currently only Enemy). Returns events list.

### 函数

#### is_empty(x, y)

*无文档*

#### has_free_neighbor(x, y)

*无文档*

---

## floors

**文件:** `floors.py`

**描述:**

Floor management and generation

### 导入

- `import os`
- `import time`
- `from typing import List, Tuple, Optional`
- `from game import utils, entities, dialogs`

### 类

#### FloorManager

Manages floor generation, transitions, and state

**方法:**

- `__init__(self, config, game_state)`

- `generate_initial_level(self)`
  Generate the initial level based on configuration

- `setup_level(self, level)`
  Setup a level with entities and NPCs

- `find_player(self, level)`
  Find player position in level

- `process_floor_transition(self)`
  Process a floor transition if ready. Returns (level, entity_mgr, npcs) or (None, None, None)

- `_write_floor_snapshots(self, level, floor_number)`
  Write debug snapshots for the floor

- `write_initial_snapshot(self, level)`
  Write snapshot for the initial floor

---

## game

**文件:** `game.py`

**描述:**

Main game class that orchestrates all game systems

### 导入

- `import sys`
- `import pygame`
- `import time`
- `import os`
- `from typing import Optional`
- `from game.config import GameConfig`
- `from game.state import GameState`
- `from game.input import InputHandler`
- `from game.floors import FloorManager`
- `from game.renderer import Renderer`
- `from game.player import Player`
- `from game.logger import Logger, ErrorHandler, create_performance_timer`
- `from game import entities, dialogs, audio`
- `from game.utils import set_tile`

### 类

#### Game

Main game class that manages the game loop and systems

**方法:**

- `__init__(self)`

- `_initialize_game_world(self)`
  Initialize the game world (level, player, etc.)

- `_setup_initial_level(self)`
  Setup the initial level with entities and NPCs

- `_initialize_audio(self)`
  Initialize audio system

- `run(self)`
  Main game loop with enhanced monitoring and error handling

- `_process_input_results(self, input_results, dt)`
  Process discrete input events

- `_process_continuous_input(self, continuous_input, dt)`
  Process continuous input (movement, etc.)

- `_handle_movement_result(self, moved_result, dt)`
  Handle the result of player movement

- `_trigger_floor_transition(self)`
  Trigger a floor transition

- `_handle_interaction(self)`
  Handle interaction with NPCs

- `_handle_attack(self)`
  Handle player attack

- `_handle_debug(self)`
  Handle debug key press

- `_update_game_systems(self, dt)`
  Update all game systems

- `_process_entity_events(self, events)`
  Process events from entity updates

- `_process_floor_transitions(self)`
  Process floor transitions

- `_log_performance_stats(self)`
  Log performance statistics

---

## input

**文件:** `input.py`

**描述:**

Input handling for the game

### 导入

- `import pygame`
- `from typing import Dict, Tuple, Optional, Callable, Any`

### 类

#### InputHandler

Handles keyboard input and events

**方法:**

- `__init__(self, config, game_state)`

- `setup_default_handlers(self)`
  Setup default event handlers

- `handle_events(self, events)`
  Handle pygame events and return action results

- `handle_quit(self, event)`
  Handle quit event

- `handle_keydown(self, event)`
  Handle keydown events

- `handle_dialog_input(self, event)`
  Handle input during dialog

- `handle_continuous_input(self)`
  Handle continuous key states (movement, sprint, tab)

---

## logging

**文件:** `logging.py`

**描述:**

Enhanced logging and error handling utilities

### 导入

- `import os`
- `import sys`
- `import traceback`
- `import pygame`
- `from typing import Optional, Any, Dict, List`
- `from datetime import datetime`
- `import time`

### 类

#### Logger

Enhanced logging system for the game

**方法:**

- `__init__(self, config)`

- `debug(self, msg, category)`
  Log debug message

- `info(self, msg, category)`
  Log info message

- `warning(self, msg, category)`
  Log warning message

- `error(self, msg, category, exception)`
  Log error message with optional exception

- `_log(self, msg, level, category)`
  Internal logging method

- `log_performance(self, operation, duration_ms)`
  Log performance data

- `get_performance_stats(self, operation)`
  Get performance statistics for an operation

- `write_debug_snapshot(self, filename, content, metadata)`
  Write a debug snapshot file

- `clear_old_logs(self, max_age_days)`
  Clear old log files

#### ErrorHandler

Enhanced error handling and recovery

**方法:**

- `__init__(self, logger)`

- `handle_exception(self, operation, exception, context)`
  Handle an exception with logging and recovery logic
  Returns True if the operation should be retried, False if it should be skipped

- `safe_call(self, func, operation)`
  Safely call a function with error handling

#### PerformanceTimer

**方法:**

- `__init__(self)`

- `__enter__(self)`

- `__exit__(self, exc_type, exc_val, exc_tb)`

### 函数

#### create_performance_timer(logger: Logger, operation: str)

Context manager for timing operations

---

## performance

**文件:** `performance.py`

**描述:**

Performance optimization utilities

### 导入

- `import pygame`
- `import time`
- `import threading`
- `import os`
- `from typing import Dict, List, Any, Optional`
- `from collections import defaultdict, deque`
- `from game import utils`

### 类

#### PerformanceMonitor

Real-time performance monitoring and data collection

**方法:**

- `__init__(self, logger)`

- `enable(self)`
  Enable performance monitoring

- `disable(self)`
  Disable performance monitoring

- `start_frame(self)`
  Mark the start of a frame

- `end_frame(self)`
  Mark the end of a frame

- `record_render_time(self, render_time_ms)`
  Record rendering time

- `record_update_time(self, update_time_ms)`
  Record game update time

- `get_current_stats(self)`
  Get current performance statistics

- `log_performance_summary(self)`
  Log a summary of performance statistics

#### PerformanceOptimizer

Analyzes and optimizes game performance

**方法:**

- `__init__(self, logger)`

- `start_frame(self)`
  Start frame performance monitoring

- `end_frame(self)`
  End frame performance monitoring

- `get_stats(self)`
  Get current performance statistics

- `check_performance_issues(self, performance_data)`
  Analyze performance data and return list of issues

- `optimize_rendering(self, config, game_state, screen)`
  Apply rendering optimizations

- `get_optimized_font(self, font_size, text)`
  Get cached font rendering

- `_cleanup_font_cache(self)`
  Remove oldest items from font cache

- `suggest_optimizations(self, config, performance_data)`
  Suggest specific optimizations based on performance data

- `auto_optimize(self, config, game_state, performance_data)`
  Automatically apply safe optimizations

- `get_performance_report(self, performance_data)`
  Generate a comprehensive performance report

#### CacheManager

Manages various game caches for performance

**方法:**

- `__init__(self, max_size)`

- `get_cached_surface(self, cache_type, key, generator_func)`
  Get cached surface or generate and cache it

- `_cleanup_cache(self, cache_type)`
  Remove least recently used items from cache

- `clear_all_caches(self)`
  Clear all caches

- `get_cache_stats(self)`
  Get statistics about cache usage

---

## player

**文件:** `player.py`

### 导入

- `import pygame`
- `import random`

### 类

#### Player

**方法:**

- `__init__(self, x, y, hp, move_cooldown, max_stamina, stamina_regen, sprint_cost, sprint_cooldown_ms, sprint_multiplier)`

- `spawn_sprint_particle(self, tile_x, tile_y, dx, dy)`

- `update_particles(self, dt, TILE_SIZE)`

- `from_level(cls, level)` (类方法)

- `position(self)`

- `apply_damage(self, dmg)`

- `update_timers(self, dt)`

- `_compute_sprint_consumption(self, delta_ms)`

- `_compute_stamina_regen(self, delta_ms)`

- `attempt_move(self, level, dx, dy, is_sprinting, dt, WIDTH, HEIGHT)`

- `passive_stamina_update(self, dt)`

---

## renderer

**文件:** `renderer.py`

**描述:**

Rendering management for the game

### 导入

- `import pygame`
- `import random`
- `from typing import List, Optional, Tuple`
- `from game import ui, utils`
- `from game.debug import DebugOverlay`
- `from game.logger import Logger`

### 类

#### Renderer

Manages all rendering operations

**方法:**

- `__init__(self, config, game_state)`

- `update_view_size(self, width, height)`
  Update view size when level changes

- `render_frame(self, player, entity_mgr, floating_texts, npcs)`
  Render a complete frame

- `_render_level_tiles(self, x0, y0, x1, y1, entity_mgr, player, ox, oy)`
  Render the level tiles

- `_get_tile_color(self, ch, x, y, entity_mgr, player)`
  Get the color for a tile character

- `_render_ui(self, player, floating_texts, entity_mgr, ox, oy)`
  Render UI elements

- `_render_dialog(self, ox, oy)`
  Render dialog box

- `_render_floor_transition(self)`
  Render floor transition overlay

- `_render_debug_logs(self)`
  Render debug logs in the corner

### 函数

#### position_lookup(ent_id)

*无文档*

#### world_to_screen(wx_px, wy_px)

*无文档*

---

## state

**文件:** `state.py`

**描述:**

Game state management

### 导入

- `import pygame`
- `import os`
- `from typing import Optional, Dict, List, Tuple, Any`
- `import random`

### 类

#### GameState

Manages the overall game state

**方法:**

- `__init__(self, config)`

- `set_level(self, level)`
  Set the current level and update dimensions

- `compute_exit_pos(self)`
  Find the exit position in the current level

- `start_floor_transition(self, floor_number, gen_seed)`
  Start a floor transition with given parameters

- `update_floor_transition(self, dt)`
  Update floor transition timer. Returns True if transition completed.

- `complete_floor_transition(self)`
  Complete the floor transition and clean up state

- `update_screen_shake(self, dt)`
  Update screen shake effect

- `add_screen_shake(self)`
  Add screen shake effect

- `update_enemy_flash(self, dt)`
  Update enemy flash effects

- `add_enemy_flash(self, entity_id)`
  Add enemy flash effect

- `game_log(self, msg)`
  Add a debug log message

- `write_exit_log(self, msg)`
  Write to the persistent exit log

- `update_camera(self, player_x, player_y, view_px_w, view_px_h)`
  Update camera position with smooth following

- `get_screen_shake_offset(self)`
  Get current screen shake offset

---

## ui

**文件:** `ui.py`

### 导入

- `import pygame`
- `import math`
- `import math`

### 常量

- **FLOAT_TOTAL** = `700`

### 函数

#### get_font(path_or_none, size)

*无文档*

#### draw_floating_texts(surface, texts, base_tile_size, dt, used_font_path, position_lookup: callable, world_to_screen: callable)

*无文档*

#### compute_shake_offset(screen_shake, shake_time, amplitude)

*无文档*

#### draw_stamina_bar(surface, x, y, width, height, stamina, max_stamina, font)

*无文档*

#### draw_player_hud(surface, player, ox, oy, view_px_w, font_path)

Draw a small HUD showing HP and stamina bar at top-right.
player: Player instance with hp, stamina, max_stamina, sprint_cooldown
ox, oy: shake offsets
view_px_w: width of viewport (for positioning)

#### draw_target_indicator(surface, player, target_pos, cam_x, cam_y, ox, oy, view_px_w, view_px_h, font_path)

Draw an arrow indicator pointing to target_pos (tile coords in pixels).
If target on-screen, draw a small marker; otherwise clamp to edge and draw arrow.
target_pos: (wx_px, wy_px)

#### draw_sprint_particles(surface, player, world_to_screen: callable, font)

Render player's sprint_particles list. world_to_screen converts world px -> screen px.
font: pygame Font used to render particle glyphs.

#### rot(px, py, a)

*无文档*

---

## utils

**文件:** `utils.py`

### 导入

- `import os`
- `import json`
- `import pygame`
- `import random`
- `import random`
- `import time`

### 函数

#### find_player(level)

*无文档*

#### set_tile(level, x, y, ch)

*无文档*

#### load_preferred_font(tile_size)

Scan fonts/ and system fonts and return a pygame Font instance plus the path used (or None).

#### load_level(fallback_level)

尝试从 data/level.txt 加载地图；若不存在则返回 fallback_level（list of str）。

#### generate_dungeon(width: int, height: int, room_attempts: int, num_enemies: int, seed: int, min_room, max_room, corridor_radius)

生成一个简单的房间+走廊地牢，返回 list[str] 格式的地图。

算法：随机放置若干矩形房间（不重叠），然后用直线走廊连接房间中心。
地图用 '#' 表示墙，'.' 表示地面，'@' 表示玩家起始位置，'X' 表示目标。

#### center(r)

*无文档*

#### carve_stepwise(x1, y1, x2, y2)

*无文档*

---
