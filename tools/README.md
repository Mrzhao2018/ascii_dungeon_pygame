# 工具文档 - Tools Documentation

这个文件夹包含了游戏项目的各种辅助工具，用于维护、监控、测试和优化游戏系统。

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

### 📂 folder_manager.py
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

**配合游戏使用**：
```bash
# 启动游戏并同时监控性能
python main.py --debug --perf &
python tools/performance_monitor.py --monitor 60
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

### 🎯 test_*.py 系列
**专项测试工具**

- **test_floor_transition_fix.py**: 楼层切换功能测试
- **test_tab_indicator.py**: UI界面标签指示器测试
- **test_variable_scope_fix.py**: 变量作用域修复测试

### 🔍 debug_*.py 系列
**调试专用工具**

- **debug_floor_transition.py**: 楼层切换调试
- **simulate_floor_transition.py**: 模拟楼层切换
- **simulate_interact.py**: 模拟交互行为

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

## 🔄 批处理工具

### 🌱 batch_test_seeds.py
**批量种子测试**

**功能**：
- 批量测试不同随机种子
- 验证游戏稳定性
- 收集测试统计数据

### 📁 move_debug_files.py
**调试文件移动工具**

**功能**：
- 批量移动调试文件
- 整理文件结构
- 清理临时文件

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

### 定期维护建议
- **每日**：运行health_check.py检查系统状态
- **每周**：手动运行folder_manager.py --auto-clean清理文件
- **每月**：运行完整的batch_test_seeds.py进行稳定性测试
- **开发期间**：持续使用performance_monitor.py监控性能

## 📝 注意事项

1. **虚拟环境**：所有工具都需要在激活的Python虚拟环境中运行
2. **权限**：某些工具可能需要文件写入权限
3. **依赖**：确保安装了所有必要的依赖包
4. **配置**：大多数工具支持通过配置文件自定义行为
5. **日志**：工具运行日志保存在logs/文件夹中

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

---

**最后更新**: 2025年9月23日  
**维护人员**: GitHub Copilot  
**版本**: 1.0.0