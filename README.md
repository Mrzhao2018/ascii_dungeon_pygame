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
├── game/                    # 核心游戏模块
│   ├── config.py           # 配置管理
│   ├── game.py             # 主游戏逻辑
│   ├── player.py           # 玩家系统
│   ├── entities.py         # 实体管理
│   ├── floors.py           # 地图生成
│   ├── renderer.py         # 渲染引擎
│   ├── input.py            # 输入处理
│   ├── ui.py               # 用户界面
│   ├── performance.py      # 性能监控
│   ├── memory.py           # 内存管理
│   ├── error_handling.py   # 错误处理
│   └── logging.py          # 日志系统
├── tools/                   # 开发工具
│   ├── auto_maintenance.py # 自动维护
│   ├── performance_monitor.py # 性能监控
│   ├── memory_monitor.py   # 内存监控
│   ├── folder_manager.py   # 文件管理
│   ├── health_check.py     # 系统检查
│   └── README.md           # 工具说明
├── tests/                   # 测试套件
│   ├── run_tests.py        # 测试运行器
│   ├── test_*.py          # 各模块测试
│   └── README.md          # 测试说明
├── data/                    # 游戏数据
│   ├── dialogs.json        # 对话数据
│   ├── enemies.json        # 敌人数据
│   └── debug/              # 调试文件
├── logs/                    # 日志文件
│   ├── session/            # 会话日志
│   ├── error/              # 错误日志
│   └── performance/        # 性能日志
└── docs/                    # 文档
```

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
- **状态管理**: ✅ 88%

## 📊 系统特性

### 🚀 性能优化
- **智能帧率监控**: 实时FPS跟踪和优化建议
- **内存管理**: 自动内存清理和泄漏检测
- **渲染优化**: 高效的ASCII字符渲染
- **输入响应**: 优化的键盘输入处理

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

这是一个使用网格和等宽字体在 Pygame 窗口中绘制字符的ASCII风格游戏。玩家用方向键移动，目标为 `X`，墙体为 `#`。游戏已扩展了敌人、道具、地图生成等功能，并具备完整的优化系统。

**调优建议**: 从默认参数开始，然后逐步调整地图尺寸、房间大小或走廊宽度来优化游戏体验。如果相机摇摆过于频繁，可以增加 `--cam-deadzone` 到 1.0 或更大。

---

**最后更新**: 2025年9月23日  
**版本**: 2.0.0  
**Python版本**: 3.12+  
**依赖**: pygame 2.6.1+
