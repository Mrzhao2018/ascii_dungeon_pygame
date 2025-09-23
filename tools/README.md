# 工具文档 - Tools Documentation

这个文件夹包含了游戏项目的各种辅助工具，用于维护、监控、测试和优化游戏系统。支持ASCII风格地牢探索游戏的开发、调试和维护全流程。

## 📁 文件组织与维护工具

### 🔧 auto_maintenance.py
**自动文件夹维护系统**

**功能**：
- 自动监控和清理logs和debug文件夹
- 后台运行，定期执行维护任务
- 智能文件归档和压缩
- 集成到游戏日志系统

**使用方法**：
```bash
# 启动自动维护
python tools/auto_maintenance.py --start

# 查看维护状态
python tools/auto_maintenance.py --status

# 停止自动维护
python tools/auto_maintenance.py --stop

# 手动执行一次维护
python tools/auto_maintenance.py --run-once
```

### � auto_cleanup_scheduler.py
**自动清理调度器**

**功能**：
- 定时调度文件清理任务
- 支持灵活的时间配置
- 自动归档旧日志文件

### 🧹 cleanup_debug_files.py
**调试文件清理工具**

**功能**：
- 专门清理调试文件
- 智能识别临时文件
- 保留重要调试信息

### �📂 folder_manager.py
**文件夹管理工具**

**功能**：
- 智能分析logs和debug文件夹状态
- 自动归档旧文件并压缩
- 支持递归扫描子文件夹
- 可配置的清理策略
- 保留最新的重要文件

**使用方法**：
```bash
# 查看文件夹状态
python tools/folder_manager.py --status

# 清理logs文件夹
python tools/folder_manager.py --clean-logs

# 清理debug文件夹
python tools/folder_manager.py --clean-debug

# 自动清理所有
python tools/folder_manager.py --auto-clean

# 自定义配置清理
python tools/folder_manager.py --max-logs 15 --max-debug 25
```

### 📋 folder_fix_report.py
**文件组织修复报告**

**功能**：
- 生成文件组织状态报告
- 检测错位的文件
- 提供修复建议

### 📁 move_debug_files.py
**调试文件移动工具**

**功能**：
- 批量移动调试文件
- 整理文件结构
- 清理临时文件

## 📊 性能监控与优化工具

### ⚡ performance_monitor.py
**性能监控分析工具**

**功能**：
- 实时监控游戏性能指标
- 分析帧率、渲染时间、内存使用
- 生成性能报告和优化建议
- 支持长期性能趋势分析

**使用方法**：
```bash
# 监控30秒性能
python tools/performance_monitor.py --monitor 30

# 分析现有日志
python tools/performance_monitor.py --analyze game.log

# 生成性能报告
python tools/performance_monitor.py --report

# 实时性能显示
python tools/performance_monitor.py --live
```

### 🧠 memory_monitor.py
**内存监控工具**

**功能**：
- 监控内存使用情况
- 检测内存泄漏
- 分析内存使用模式
- 提供内存优化建议

**使用方法**：
```bash
# 开始内存监控
python tools/memory_monitor.py --start

# 查看内存报告
python tools/memory_monitor.py --report

# 检测内存泄漏
python tools/memory_monitor.py --leak-check
```

### 📈 optimization_report.py
**优化报告生成器**

**功能**：
- 生成综合性能优化报告
- 分析系统瓶颈
- 提供具体优化建议

### ⏱️ debug_timing.py
**调试时间分析工具**

**功能**：
- 分析游戏各组件执行时间
- 识别性能瓶颈
- 提供优化建议

### 📊 monitor_game_state.py
**游戏状态监控器**

**功能**：
- 实时监控游戏状态变化
- 记录关键事件时机
- 分析状态转换性能

## 🛠️ 代码质量与类型工具

### 🔧 code_quality_fixer.py
**代码质量修复工具**

**功能**：
- 自动修复常见代码质量问题
- 统一代码风格
- 移除未使用的导入和变量

### 🔤 fix_type_imports.py
**类型导入修复工具**

**功能**：
- 修复类型提示导入问题
- 统一类型注解格式
- 确保类型检查通过

### 📄 completion_report_generator.py
**完成度报告生成器**

**功能**：
- 生成项目完成度报告
- 分析代码覆盖率
- 提供改进建议

### 🔍 logging_config_optimization.py
**日志配置优化工具**

**功能**：
- 优化日志系统配置
- 提高日志性能
- 减少日志文件大小

## 🧪 测试与调试工具

### 🏥 health_check.py
**系统健康检查**

**功能**：
- 检查游戏系统各组件状态
- 验证配置文件完整性
- 检测潜在问题
- 生成健康状态报告

**使用方法**：
```bash
# 完整健康检查
python tools/health_check.py

# 快速检查
python tools/health_check.py --quick

# 检查特定组件
python tools/health_check.py --check-config
python tools/health_check.py --check-files
```

### 🧪 smoke_test.py
**冒烟测试工具**

**功能**：
- 快速验证游戏基本功能
- 自动化基础测试流程
- 检测关键功能是否正常

### ✅ feature_verification.py
**功能验证工具**

**功能**：
- 验证游戏新功能
- 回归测试检查
- 确保功能完整性

### 🎯 final_feature_test.py
**最终功能测试**

**功能**：
- 全面的功能集成测试
- 端到端测试流程
- 发布前质量保证

### 🌱 batch_test_seeds.py
**批量种子测试**

**功能**：
- 批量测试不同随机种子
- 验证游戏稳定性
- 收集测试统计数据

## 🎮 游戏功能专项测试

### 📈 经验系统测试工具
- **test_experience_complete.py**: 完整经验系统测试
- **test_experience_integration.py**: 经验系统集成测试  
- **test_player_experience.py**: 玩家经验功能测试

### 👾 敌人系统测试工具
- **test_enemy_ai.py**: 敌人AI行为测试
- **test_enemy_speed.py**: 敌人移动速度测试
- **test_enhanced_enemies.py**: 增强敌人功能测试
- **test_adjacent_attack.py**: 相邻攻击测试
- **test_attack_speed.py**: 攻击速度测试

### 🏢 楼层系统测试工具
- **test_floor_transition_fix.py**: 楼层切换修复测试
- **test_floor_transition_exit.py**: 楼层出口转换测试
- **test_direct_loading.py**: 直接加载测试

### 🎯 UI界面测试工具
- **test_tab_indicator.py**: Tab指示器测试
- **test_tab_in_game.py**: 游戏内Tab功能测试
- **test_tab_toggle.py**: Tab切换功能测试
- **test_indicator_draw.py**: 指示器绘制测试
- **test_indicator_refresh.py**: 指示器刷新测试
- **test_indicator_rendering.py**: 指示器渲染测试

### 🔄 游戏状态测试工具
- **test_restart_feature.py**: 重启功能测试
- **test_variable_scope_fix.py**: 变量作用域修复测试

## 🔍 调试专用工具

### 🏢 debug_floor_transition.py
**楼层切换调试**

**功能**：
- 调试楼层转换逻辑
- 分析状态切换问题
- 验证数据传递

### 🎮 simulate_floor_transition.py
**模拟楼层切换**

**功能**：
- 模拟楼层转换过程
- 测试边界条件
- 验证转换逻辑

### 🎯 simulate_interact.py
**模拟交互行为**

**功能**：
- 模拟玩家交互
- 测试交互响应
- 验证交互逻辑

### 🚪 diagnose_exit_indicator.py
**出口指示器诊断**

**功能**：
- 诊断出口指示器问题
- 分析渲染状态
- 修复显示问题

### 🔧 fix_exit_indicator.py
**出口指示器修复**

**功能**：
- 修复出口指示器bug
- 优化指示器性能
- 提升用户体验

## 🎮 游戏内容工具

### 👥 check_npcs.py
**NPC检查工具**

**功能**：
- 检查NPC配置
- 验证对话系统
- 检测NPC行为异常

### 💬 edit_dialogs.py
**对话编辑工具**

**功能**：
- 编辑游戏对话内容
- 验证对话逻辑
- 批量更新对话文本

### 🔍 inspect_entities.py
**实体检查工具**

**功能**：
- 检查游戏实体状态
- 分析实体属性
- 调试实体行为

## ⚙️ 配置与文档工具

### ⚙️ config_manager.py
**配置管理工具**

**功能**：
- 管理游戏配置文件
- 验证配置完整性
- 批量更新配置

**使用方法**：
```bash
# 查看当前配置
python tools/config_manager.py --show

# 验证配置
python tools/config_manager.py --validate

# 重置配置
python tools/config_manager.py --reset
```

### 📚 doc_generator.py
**文档生成工具**

**功能**：
- 自动生成代码文档
- 分析代码结构
- 生成API参考文档

**使用方法**：
```bash
# 生成完整文档
python tools/doc_generator.py

# 生成特定模块文档
python tools/doc_generator.py --module game.entities

# 更新现有文档
python tools/doc_generator.py --update
```

## � 快速开始指南

### � 新开发者入门
```bash
# 1. 系统健康检查
python tools/health_check.py

# 2. 运行基础测试
python tools/smoke_test.py

# 3. 启动自动维护
python tools/auto_maintenance.py --start

# 4. 开始开发！
python main.py --debug
```

### 🔧 日常开发流程
```bash
# 开发前检查
python tools/feature_verification.py

# 开发中监控
python tools/performance_monitor.py --live &
python tools/memory_monitor.py --start &

# 开发后测试
python tools/final_feature_test.py

# 清理维护
python tools/folder_manager.py --auto-clean
```

### 🧪 测试工作流程
```bash
# 单元测试
python tools/test_experience_complete.py
python tools/test_enemy_ai.py

# 集成测试  
python tools/test_experience_integration.py
python tools/test_floor_transition_fix.py

# 端到端测试
python tools/final_feature_test.py
python tools/batch_test_seeds.py
```

## 🚀 使用建议

### 日常维护流程
```bash
# 1. 启动自动维护
python tools/auto_maintenance.py --start

# 2. 检查系统健康状态
python tools/health_check.py

# 3. 运行基础测试
python tools/smoke_test.py

# 4. 查看性能状态（如果需要）
python tools/performance_monitor.py --report
```

### 开发调试流程
```bash
# 1. 启动性能监控
python tools/performance_monitor.py --live &

# 2. 启动内存监控
python tools/memory_monitor.py --start &

# 3. 运行游戏进行调试
python main.py --debug --perf

# 4. 分析结果
python tools/optimization_report.py
```

### 特定功能调试
```bash
# 经验系统调试
python tools/test_experience_complete.py
python tools/test_player_experience.py

# 敌人系统调试
python tools/test_enemy_ai.py
python tools/test_enhanced_enemies.py

# 楼层系统调试
python tools/debug_floor_transition.py
python tools/test_floor_transition_fix.py

# UI系统调试
python tools/test_tab_indicator.py
python tools/diagnose_exit_indicator.py
```

### 定期维护建议
- **每日**：运行health_check.py检查系统状态
- **每周**：手动运行folder_manager.py --auto-clean清理文件
- **每月**：运行完整的batch_test_seeds.py进行稳定性测试  
- **开发期间**：持续使用performance_monitor.py监控性能
- **功能开发**：使用对应的test_*工具验证功能

## 🎯 工具分类速查

### 🔧 维护工具
- `auto_maintenance.py` - 自动维护
- `auto_cleanup_scheduler.py` - 定时清理
- `cleanup_debug_files.py` - 调试文件清理
- `folder_manager.py` - 文件夹管理
- `move_debug_files.py` - 文件移动

### � 监控工具
- `performance_monitor.py` - 性能监控
- `memory_monitor.py` - 内存监控
- `monitor_game_state.py` - 游戏状态监控
- `debug_timing.py` - 时间分析

### 🧪 测试工具
- `health_check.py` - 系统健康检查
- `smoke_test.py` - 冒烟测试
- `feature_verification.py` - 功能验证
- `final_feature_test.py` - 最终测试
- `batch_test_seeds.py` - 批量测试

### 🎮 游戏功能测试
- **经验系统**: `test_experience_*.py`
- **敌人系统**: `test_enemy_*.py`, `test_attack_*.py`
- **楼层系统**: `test_floor_*.py`, `test_direct_loading.py`
- **UI系统**: `test_tab_*.py`, `test_indicator_*.py`
- **重启功能**: `test_restart_feature.py`

### 🔍 调试工具
- `debug_floor_transition.py` - 楼层调试
- `simulate_*.py` - 行为模拟
- `diagnose_exit_indicator.py` - 指示器诊断
- `fix_exit_indicator.py` - 指示器修复

### 🛠️ 代码质量
- `code_quality_fixer.py` - 质量修复
- `fix_type_imports.py` - 类型修复
- `logging_config_optimization.py` - 日志优化

### ⚙️ 配置与文档
- `config_manager.py` - 配置管理
- `doc_generator.py` - 文档生成
- `completion_report_generator.py` - 完成度报告

## �📝 注意事项

1. **虚拟环境**：所有工具都需要在激活的Python虚拟环境中运行
2. **权限**：某些工具可能需要文件写入权限
3. **依赖**：确保安装了所有必要的依赖包
4. **配置**：大多数工具支持通过配置文件自定义行为
5. **日志**：工具运行日志保存在logs/文件夹中
6. **测试顺序**：建议按照从基础到复杂的顺序运行测试工具
7. **性能影响**：监控工具可能会影响游戏性能，注意适时关闭

## 🆘 故障排除

如果工具运行出现问题：

1. **检查Python环境**：
   ```bash
   .\.venv\Scripts\Activate.ps1
   python --version  # 确保是3.12+
   ```

2. **检查依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **检查文件权限**：确保对项目文件夹有读写权限

4. **查看日志**：检查logs/error/文件夹中的错误日志

5. **重置配置**：
   ```bash
   python tools/config_manager.py --reset
   ```

6. **运行系统检查**：
   ```bash
   python tools/health_check.py --full
   ```

7. **清理临时文件**：
   ```bash
   python tools/folder_manager.py --clean-all
   ```

### 常见问题解决

- **模块导入错误**：运行 `python tools/fix_type_imports.py`
- **性能问题**：运行 `python tools/optimization_report.py`
- **内存泄漏**：运行 `python tools/memory_monitor.py --leak-check`
- **文件组织混乱**：运行 `python tools/folder_fix_report.py`
- **配置错误**：运行 `python tools/config_manager.py --validate`

---

**最后更新**: 2025年9月23日  
**维护人员**: GitHub Copilot  
**版本**: 2.2.0  
**支持的游戏版本**: v2.2.0+  
**工具总数**: 50+ 个专用工具