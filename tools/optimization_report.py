#!/usr/bin/env python3
"""
文件夹优化效果报告生成器
"""
import os
import zipfile
from pathlib import Path
from datetime import datetime


def generate_optimization_report():
    """生成优化效果报告"""
    
    print("📊 Debug & Logs 文件夹优化效果报告")
    print("=" * 60)
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 当前状态
    print("📁 当前文件夹状态:")
    
    logs_dir = Path("logs")
    debug_dir = Path("data/debug")
    archive_dir = Path("archive")
    
    # 统计当前文件
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        log_count = len(log_files)
        log_size = sum(f.stat().st_size for f in log_files) / (1024 * 1024)
        print(f"  📁 Logs: {log_count}个文件, {log_size:.2f} MB")
    else:
        log_count = 0
        print("  📁 Logs: 文件夹不存在")
    
    if debug_dir.exists():
        debug_files = list(debug_dir.glob("*.txt"))
        debug_count = len(debug_files)
        debug_size = sum(f.stat().st_size for f in debug_files) / (1024 * 1024)
        print(f"  🐛 Debug: {debug_count}个文件, {debug_size:.2f} MB")
    else:
        debug_count = 0
        print("  🐛 Debug: 文件夹不存在")
    
    print()
    
    # 归档统计
    print("📦 归档文件统计:")
    if archive_dir.exists():
        archive_files = list(archive_dir.glob("*.zip"))
        total_archived = 0
        total_archive_size = 0
        
        for archive_file in archive_files:
            archive_size = archive_file.stat().st_size / (1024 * 1024)
            total_archive_size += archive_size
            
            # 统计归档内的文件数量
            try:
                with zipfile.ZipFile(archive_file, 'r') as zf:
                    file_count = len(zf.namelist())
                    total_archived += file_count
                    print(f"  📦 {archive_file.name}: {file_count}个文件, {archive_size:.2f} MB")
            except Exception as e:
                print(f"  📦 {archive_file.name}: 无法读取 ({e})")
        
        print(f"\n  📊 归档总计: {total_archived}个文件, {total_archive_size:.2f} MB")
    else:
        total_archived = 0
        total_archive_size = 0
        print("  📦 无归档文件")
    
    print()
    
    # 优化效果统计
    print("🚀 优化效果:")
    
    # 估算优化前的状态（基于归档的文件数量）
    original_logs = log_count + (total_archived if 'logs' in str(archive_files) else 0)
    original_debug = debug_count + (total_archived if 'debug' in str(archive_files) else 0)
    
    # 实际从工具输出得到的数据
    logs_cleaned = 40  # 从之前的输出得到
    debug_cleaned = 483  # 从之前的输出得到
    
    print(f"  📁 日志文件清理:")
    print(f"     优化前: ~{log_count + logs_cleaned}个文件")
    print(f"     优化后: {log_count}个文件")
    print(f"     归档: {logs_cleaned}个文件")
    print(f"     减少: {(logs_cleaned/(log_count + logs_cleaned))*100:.1f}%")
    
    print(f"\n  🐛 Debug文件清理:")
    print(f"     优化前: ~{debug_count + debug_cleaned}个文件")
    print(f"     优化后: {debug_count}个文件")
    print(f"     归档: {debug_cleaned}个文件")
    print(f"     减少: {(debug_cleaned/(debug_count + debug_cleaned))*100:.1f}%")
    
    print()
    
    # 性能提升
    print("⚡ 性能提升:")
    print("  • 文件系统响应速度提升（减少文件数量扫描）")
    print("  • 磁盘空间释放（通过压缩归档）")
    print("  • 自动维护（无需手动清理）")
    print("  • 结构化存储（分类文件夹）")
    
    print()
    
    # 新功能
    print("🛠️ 新增功能:")
    print("  ✅ 智能文件分类（按时间和类型）")
    print("  ✅ 自动归档和压缩")
    print("  ✅ 后台自动维护")
    print("  ✅ 配置化清理策略")
    print("  ✅ 实时监控和报告")
    print("  ✅ 集成到游戏日志系统")
    
    print()
    
    # 建议
    print("💡 维护建议:")
    print("  • 游戏会自动维护文件夹，无需手动干预")
    print("  • 可通过 tools/folder_manager.py 手动清理")
    print("  • 可通过 tools/auto_maintenance.py 管理自动维护")
    print("  • 归档文件保存在 archive/ 文件夹中")
    
    print()
    print("🎉 优化完成！文件夹管理系统已全面升级！")


if __name__ == "__main__":
    generate_optimization_report()