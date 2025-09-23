# 🎮 ASCII 风格冒险游戏

基于 Pygame 的高性能 ASCII 风格地牢探索游戏，具备完整的性能监控、内存管理、错误处理和自动化维护系统。

## 🚀 快速开始

### 环境准备
```bash
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动游戏
python main.py
```

### 基本游戏操作
- **移动**: 方向键 (↑↓←→) 或 WASD
- **冲刺**: 按住 Shift + 方向键
- **攻击**: 空格键
- **交互**: E 或 回车键
- **显示出口**: 按住 Tab 键
- **重新开始**: R 键（死亡后）
- **退出**: ESC 或关闭窗口

### 调试功能
- **切换调试模式**: F12 键（可随时开启/关闭）
- **调试面板控制**（调试模式下）:
  - **1**: 性能监控面板
  - **2**: 游戏状态面板  
  - **3**: 玩家状态面板
  - **4**: 实体调试面板
  - **5**: 日志面板
- **调试信息**: K 键（临时显示调试信息）

### 🎮 新增功能 (v2.2.0)

#### 📈 经验与升级系统
- **等级进程**: 50级的完整升级系统，每级提升玩家属性
- **经验来源**: 
  - **击杀敌人**: 15-75经验（根据敌人类型调整）
  - **楼层完成**: 40经验奖励
  - **房间探索**: 8经验奖励
  - **道具收集**: 5经验奖励
- **属性提升**: 每级自动提升生命值、体力、移动速度、视野半径
- **特殊奖励**: 
  - **10级**: 额外+50生命值和体力
  - **25级**: 额外+100生命值和体力
  - **50级**: 额外+200生命值和体力
- **UI显示**: 
  - **等级显示**: HUD中显示当前等级
  - **经验条**: 可视化经验进度
  - **升级通知**: 升级时的视觉反馈和浮动文字

#### 🎯 游戏平衡优化
- **快速进程**: 优化的经验值配置，提供更流畅的升级体验
- **敌人分类**: 支持基础、守卫、侦察兵、普通、强力、精英、BOSS等敌人类型
- **递增难度**: 升级所需经验递增，保持挑战性

#### 💀 智能死亡重新开始系统
- **无缝重新开始**: 死亡后不再强制退出，显示死亡屏幕
- **可视化死亡反馈**: 红色背景和骷髅符号的死亡屏幕
- **便捷操作**: 
  - **R 键**: 立即重新开始新游戏
  - **ESC 键**: 退出游戏
- **完整重置**: 自动重置所有游戏状态，包括玩家位置、敌人、道具等

#### 🧭 智能方位指示器系统
- **自动刷新**: 楼层转换时自动更新指示器目标位置
- **精确定位**: 自动计算并指向新楼层的出口位置
- **状态保持**: 尊重用户的指示器开启/关闭设置
- **无需干预**: 无需手动重新开启指示器即可获得正确方向

### 🎯 游戏流程改进
- **经验与升级**: 完整的等级系统提供长期游戏目标和成就感
- **更流畅的游戏体验**: 死亡不再中断游戏流程
- **减少操作负担**: 楼层转换后无需手动刷新方位指示器
- **增强可用性**: 直观的死亡屏幕和重新开始选项
- **属性成长**: 每级提升玩家能力，包括生命值、体力、移动速度、视野范围

## ⚙️ 命令行参数

### 🎯 核心游戏参数
```bash
# 地图生成
--map-width <int>     # 地图宽度 (推荐: 80-160)
--map-height <int>    # 地图高度 (推荐: 30-80)
--rooms <int>         # 房间数量 (推荐: 12-30)
--min-room <int>      # 最小房间尺寸 (推荐: 4-6)
--max-room <int>      # 最大房间尺寸 (推荐: 10-18)
--enemies <int>       # 敌人数量 (推荐: 6-18)
--corridor-radius <int> # 走廊宽度 (推荐: 0-2)

# 视图设置
--view-w <int>        # 视图宽度
--view-h <int>        # 视图高度

# 相机控制
--cam-lerp <float>    # 相机平滑度 (0.05-0.35)
--cam-deadzone <float> # 相机死区 (0.0-2.0)

# 强制重新生成
--regen               # 忽略保存的地图，重新生成
```

### 🏃 移动与体力系统
```bash
--sprint-multiplier <float>  # 冲刺速度倍数 (默认: 0.6)
--sprint-cost <float>        # 冲刺体力消耗 (默认: 35.0)
--stamina-max <float>        # 体力上限 (默认: 100.0)
--stamina-regen <float>      # 体力恢复速度 (默认: 6.0)
--sprint-cooldown-ms <int>   # 冲刺冷却时间 (默认: 2000)
```

### 🔧 调试与性能
```bash
--debug               # 启用调试模式
--perf                # 启用性能监控
--test-mode           # 测试模式
--config <file>       # 指定配置文件
```

## 📁 项目结构

```
E:\pygame\
├── main.py                  # 游戏入口文件
├── requirements.txt         # 依赖包列表
├── game.json               # 游戏配置文件
├── README.md               # 项目说明文档
├── .gitignore              # Git忽略文件
│
├── game/                   # 🎮 核心游戏模块
│   ├── __init__.py         # 模块初始化
│   ├── config.py           # 配置管理系统
│   ├── game.py             # 主游戏逻辑控制器
│   ├── player.py           # 玩家系统 (移动、体力、FOV、等级)
│   ├── experience.py       # 经验与升级系统
│   ├── entities.py         # 实体管理 (敌人、道具)
│   ├── floors.py           # 地图生成算法
│   ├── renderer.py         # 渲染引擎 (ASCII渲染)
│   ├── input.py            # 输入处理系统
│   ├── ui.py               # 用户界面组件 (HUD、经验条、升级通知)
│   ├── fov.py              # 视野系统 (FOV)
│   ├── state.py            # 游戏状态管理
│   ├── performance.py      # 性能监控系统
│   ├── memory.py           # 内存管理工具
│   ├── error_handling.py   # 错误处理机制
│   ├── logging.py          # 日志系统
│   ├── audio.py            # 音效系统
│   ├── dialogs.py          # 对话系统
│   └── utils.py            # 通用工具函数
│
├── tools/                  # 🔧 开发工具集
│   ├── auto_maintenance.py      # 自动维护工具
│   ├── auto_cleanup_scheduler.py # 定时清理调度器
│   ├── cleanup_debug_files.py   # 调试文件清理工具
│   ├── debug_timing.py          # 性能调试工具
│   ├── performance_monitor.py   # 性能监控器
│   ├── memory_monitor.py        # 内存监控器
│   ├── folder_manager.py        # 文件管理工具
│   ├── health_check.py          # 系统健康检查
│   ├── logging_config_optimization.py # 日志配置优化
│   └── README.md                # 工具使用说明
│
├── tests/                  # 🧪 测试套件
│   ├── run_tests.py             # 测试运行器
│   ├── test_config.py           # 配置系统测试
│   ├── test_config_duplicate.py # 配置重复测试
│   ├── test_fov_integration.py  # FOV集成测试
│   ├── test_fov_system.py       # FOV系统测试
│   ├── test_fps_display.py      # FPS显示测试
│   ├── test_error_handling.py   # 错误处理测试
│   ├── test_memory.py           # 内存管理测试
│   ├── test_performance.py      # 性能系统测试
│   ├── test_state.py            # 状态管理测试
│   └── README.md                # 测试说明文档
│
├── data/                   # 📊 游戏数据
│   ├── dialogs.json        # 对话数据文件
│   ├── enemies.json        # 敌人配置数据
│   └── debug/              # 调试数据目录 (自动生成)
│       ├── levels/         # 调试关卡文件
│       └── maps/           # 调试地图文件
│
├── logs/                   # 📝 日志系统
│   ├── session/            # 游戏会话日志
│   ├── error/              # 错误日志
│   └── performance/        # 性能日志 (可选)
│
├── docs/                   # 📚 项目文档
│   ├── cleanup_maintenance_report.md # 清理维护报告
│   ├── fov_implementation_report.md  # FOV实现报告
│   ├── type_fixes_report.md          # 类型修复报告
│   └── *.md                          # 其他文档
│
├── fonts/                  # 🔤 字体资源
│   ├── Uranus_Pixel_11Px.ttf # 游戏字体
│   └── README.txt          # 字体说明
│
├── archive/                # 📦 归档文件
│   ├── main_backup.py      # 主文件备份
│   └── *.zip               # 压缩归档
│
└── .venv/                  # 🐍 Python虚拟环境
    └── ...                 # 虚拟环境文件
```

### 📂 目录说明

- **🎮 game/**: 游戏核心逻辑，包含所有游戏系统模块
- **🔧 tools/**: 开发和维护工具，用于调试、性能监控、文件管理
- **🧪 tests/**: 完整的测试套件，确保代码质量
- **📊 data/**: 游戏数据文件和调试输出
- **📝 logs/**: 结构化日志存储，按类型分目录
- **📚 docs/**: 项目文档和报告
- **🔤 fonts/**: 游戏字体资源
- **📦 archive/**: 备份和归档文件

### 🎮 游戏状态系统

#### 状态管理
游戏现在具备完整的状态管理系统：
- **PLAYING**: 正常游戏状态
- **GAME_OVER**: 死亡状态，显示死亡屏幕
- **RESTART**: 重新开始状态，触发游戏重置

#### 智能UI系统
- **状态感知渲染**: 根据游戏状态显示不同界面
- **响应式输入**: 不同状态下的输入处理
- **流畅过渡**: 状态间的平滑切换

## 🛠️ 开发工具

### 性能监控
```bash
# 实时性能监控
python tools/performance_monitor.py --monitor 30

# 分析现有日志
python tools/performance_monitor.py --analyze game.log

# 生成性能报告
python tools/performance_monitor.py --report
```

### 内存管理
```bash
# 内存监控
python tools/memory_monitor.py --start

# 内存泄漏检测
python tools/memory_monitor.py --leak-check
```

### 系统维护
```bash
# 自动文件夹维护
python tools/auto_maintenance.py --start

# 系统健康检查
python tools/health_check.py

# 文件夹清理
python tools/folder_manager.py --auto-clean
```

## 🧪 测试系统

### 运行测试
```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定测试
python -m unittest tests.test_performance

# 详细测试报告
python -m unittest discover -s tests -v
```

### 测试覆盖
- **配置系统**: ✅ 100%
- **性能监控**: ✅ 95%
- **内存管理**: ✅ 98%
- **错误处理**: ✅ 92%
- **状态管理**: ✅ 95%
- **经验系统**: ✅ 100%
- **死亡重新开始**: ✅ 100%
- **方位指示器**: ✅ 100%

## 📊 系统特性

### 🚀 性能优化
- **智能帧率监控**: 实时FPS跟踪和优化建议
- **内存管理**: 自动内存清理和泄漏检测
- **渲染优化**: 高效的ASCII字符渲染
- **输入响应**: 优化的键盘输入处理

### 🎮 用户体验优化
- **智能死亡处理**: 死亡后无需重新启动游戏
- **自动指示器刷新**: 楼层转换时无需手动操作
- **直观视觉反馈**: 清晰的死亡屏幕和状态显示
- **便捷快捷键**: 一键重新开始和退出

### 🛡️ 错误处理
- **健壮错误恢复**: 多层级错误恢复策略
- **自动重试机制**: 智能故障恢复
- **详细错误日志**: 完整的错误追踪和分析
- **并发安全**: 线程安全的错误处理

### 📁 文件管理
- **自动维护**: 后台自动清理和归档
- **智能归档**: 压缩和TTL管理
- **结构化存储**: 有序的文件组织系统
- **实时监控**: 文件系统状态监控

### 📈 监控系统
- **实时指标**: FPS、内存、性能指标
- **历史分析**: 长期性能趋势分析
- **自动报告**: 定期生成优化建议
- **可视化界面**: 直观的性能数据显示

## 🎯 新功能使用示例

### 💀 死亡重新开始功能
```bash
# 启动游戏
python main.py

# 游戏中死亡后：
# - 查看死亡屏幕（红色背景 + 骷髅符号）
# - 按 R 键立即重新开始
# - 按 ESC 键退出游戏
```

### 🧭 方位指示器自动刷新
```bash
# 启动游戏并开启指示器
python main.py

# 游戏中：
# 1. 按 Tab 键开启方位指示器
# 2. 到达出口进入下一层
# 3. 指示器自动指向新楼层出口（无需手动操作）
```

## 🎯 使用示例

### 标准游戏启动
```bash
python main.py --debug
```

### 高性能模式
```bash
python main.py --debug --perf --map-width 100 --map-height 50
```

### 开发调试模式
```bash
# 启动性能监控
python tools/performance_monitor.py --live &

# 启动游戏
python main.py --debug --test-mode

# 运行测试
python tests/run_tests.py
```

### 自定义配置示例
```bash
python main.py --debug --regen --map-width 80 --map-height 40 --view-w 40 --view-h 24 --rooms 22 --min-room 6 --max-room 16 --enemies 12 --corridor-radius 1 --cam-lerp 0.18 --cam-deadzone 1.0
```

## 🔧 配置管理

### 配置文件支持
- **JSON格式**: `game.json` 主配置文件
- **INI格式**: 传统配置文件格式
- **命令行覆盖**: CLI参数优先级最高

### 配置优先级
1. 命令行参数 (最高)
2. 配置文件设置
3. 系统默认值 (最低)

## 📝 维护建议

### 日常维护
```bash
# 检查系统状态
python tools/health_check.py

# 清理文件
python tools/folder_manager.py --status

# 运行测试
python tests/run_tests.py
```

### 性能优化
```bash
# 性能基准测试
python tools/performance_monitor.py --benchmark

# 内存分析
python tools/memory_monitor.py --report

# 生成优化报告
python tools/optimization_report.py
```

## 🚨 故障排除

### 常见问题
1. **性能问题**: 检查 `logs/performance/` 目录
2. **内存泄漏**: 运行 `python tools/memory_monitor.py --leak-check`
3. **配置错误**: 使用 `python tools/config_manager.py --validate`
4. **文件问题**: 执行 `python tools/health_check.py`

### 系统恢复
```bash
# 重置配置
python tools/config_manager.py --reset

# 清理所有缓存
python tools/folder_manager.py --clean-all

# 运行完整健康检查
python tools/health_check.py --full
```

## 🤝 贡献指南

### 开发流程
1. 激活虚拟环境
2. 运行完整测试套件
3. 进行代码修改
4. 运行相关测试
5. 检查性能影响
6. 提交代码

### 测试要求
- 所有新功能必须有对应测试
- 测试覆盖率不能低于90%
- 性能回归测试必须通过

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 📞 支持

如遇问题请：
1. 查看 `logs/` 目录中的日志
2. 运行 `python tools/health_check.py`
3. 查阅 `docs/` 目录中的文档
4. 检查 `tests/` 目录中的测试用例

## 🎮 游戏说明

这是一个使用网格和等宽字体在 Pygame 窗口中绘制字符的ASCII风格地牢探索游戏。玩家用方向键移动，目标为 `X`，墙体为 `#`。游戏已扩展了敌人、道具、地图生成等功能，并具备完整的优化系统。

### 🎯 游戏特色
- **经验与升级**: 50级完整升级系统，每级提升属性和特殊奖励
- **智能死亡处理**: 死亡后可选择重新开始或退出，无需重启游戏
- **自动化 UI**: 方位指示器在楼层转换时自动刷新目标位置
- **流畅体验**: 无缝的状态切换和响应式界面
- **高级功能**: FOV 视野系统、性能监控、自动维护等

**调优建议**: 从默认参数开始，然后逐步调整地图尺寸、房间大小或走廊宽度来优化游戏体验。如果相机摇摆过于频繁，可以增加 `--cam-deadzone` 到 1.0 或更大。

**新手提示**: 死亡后按 R 键可以立即重新开始游戏，按 Tab 键开启的方位指示器会在进入新楼层时自动指向出口。通过击杀敌人和探索楼层获得经验，每次升级都会提升你的属性！

---

**最后更新**: 2025年9月23日  
**版本**: 2.2.0  
**Python版本**: 3.12+  
**依赖**: pygame 2.6.1+

## 🎮 更新日志

### v2.2.0 (2025-09-23)
**重大新功能:**
- ✨ **经验与升级系统**: 完整的50级升级系统
  - 击杀敌人、楼层完成、探索房间、收集道具获得经验
  - 每级自动提升生命值、体力、移动速度、视野半径
  - 特殊等级奖励 (10级、25级、50级)
  - 升级UI显示：等级、经验条、升级通知
- 🎮 **敌人类型系统**: 支持基础、守卫、侦察兵、普通、强力、精英、BOSS敌人
- 📊 **优化的游戏平衡**: 快速但有挑战性的升级进程

**UI/UX改进:**
- 🎯 **增强的HUD**: 显示玩家等级和经验进度
- ✨ **浮动文字反馈**: 经验获得和升级的视觉反馈
- 🎨 **升级通知**: 优雅的等级提升动画效果

**技术优化:**
- 🛠️ **模块化设计**: 独立的经验系统模块 (`game/experience.py`)
- ⚡ **性能优化**: 高效的经验计算和UI更新
- 🧪 **完整测试**: 经验系统的全面测试覆盖

### v2.1.0 (2025-09-23)
**新增功能:**
- ✨ **死亡重新开始系统**: 死亡后显示死亡屏幕，支持 R 键重新开始
- ✨ **智能方位指示器**: 楼层转换时自动刷新指示器目标位置
- 🎨 **可视化死亡反馈**: 红色背景和骷髅符号的死亡屏幕
- 🔧 **游戏状态管理**: 完整的状态枚举系统 (PLAYING/GAME_OVER/RESTART)

**改进:**
- 🚀 **用户体验**: 死亡不再强制退出游戏
- 🎯 **操作便捷性**: 楼层转换后无需手动刷新指示器
- 📖 **帮助文档**: 更新配置帮助文本包含新功能说明

**技术优化:**
- 🛠️ **状态感知渲染**: 根据游戏状态显示不同界面
- ⚡ **性能优化**: 优化状态切换和渲染逻辑
- 🧪 **测试覆盖**: 新功能的完整测试覆盖

### v2.0.0 (之前版本)
- 完整的性能监控和内存管理系统
- 自动化维护和文件管理
- 视野系统 (FOV) 实现
- 错误处理和恢复机制
