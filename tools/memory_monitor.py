#!/usr/bin/env python3
"""
内存管理监控工具
"""
import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.memory import MemoryMonitor, SmartCacheManager, MemoryOptimizer
from game.performance import PerformanceOptimizer


def monitor_memory_usage(duration=30):
    """监控内存使用情况"""
    print("内存使用监控演示")
    print("=" * 50)
    
    # 创建内存监控器
    monitor = MemoryMonitor()
    monitor.set_baseline()
    
    print(f"基线内存: {monitor.baseline_memory:.2f}MB")
    print(f"监控时长: {duration}秒")
    print("开始监控...")
    
    start_time = time.time()
    while time.time() - start_time < duration:
        monitor.update()
        
        # 每5秒输出一次统计
        if int(time.time() - start_time) % 5 == 0:
            stats = monitor.get_memory_stats()
            current_memory = stats.get('current_memory_mb', 0)
            peak_memory = stats.get('peak_memory_mb', 0)
            growth = stats.get('memory_growth_mb', 0)
            
            print(f"当前内存: {current_memory:.2f}MB | "
                  f"峰值: {peak_memory:.2f}MB | "
                  f"增长: {growth:+.2f}MB")
        
        time.sleep(1)
    
    # 最终统计
    final_stats = monitor.get_memory_stats()
    print("\n监控完成!")
    print(f"最终内存使用: {final_stats.get('current_memory_mb', 0):.2f}MB")
    print(f"峰值内存使用: {final_stats.get('peak_memory_mb', 0):.2f}MB")
    print(f"总内存增长: {final_stats.get('memory_growth_mb', 0):+.2f}MB")


def demo_cache_management():
    """演示缓存管理功能"""
    print("\n缓存管理演示")
    print("=" * 50)
    
    cache_manager = SmartCacheManager(max_size=50, max_memory_mb=10)
    
    print("添加测试项目到缓存...")
    
    # 添加字体渲染缓存
    for size in [12, 16, 20, 24, 32]:
        for text in ["Hello", "World", "游戏", "测试", "缓存"]:
            key = f"{size}_{text}"
            cache_manager.get_cached_item(
                'font_renders', key,
                lambda s=size, t=text: f"Font({s}): {t}"
            )
    
    # 添加Surface缓存
    for i in range(20):
        cache_manager.get_cached_item(
            'surfaces', f'tile_{i}',
            lambda i=i: f"Surface_{i}x{i}"
        )
    
    # 显示缓存统计
    stats = cache_manager.get_cache_stats()
    print("\n缓存统计:")
    for cache_type, cache_stats in stats.items():
        if cache_type != 'total':
            print(f"  {cache_type}: {cache_stats['items']} 项目, "
                  f"{cache_stats['size_mb']:.2f}MB")
    
    print(f"\n总计: {stats['total']['items']} 项目, "
          f"{stats['total']['size_mb']:.2f}MB "
          f"({stats['total']['memory_efficiency']:.1f}% 内存效率)")
    
    # 演示缓存清理
    print("\n触发缓存清理...")
    cache_manager.force_cleanup()
    
    # 清理后的统计
    stats_after = cache_manager.get_cache_stats()
    print(f"清理后: {stats_after['total']['items']} 项目, "
          f"{stats_after['total']['size_mb']:.2f}MB")


def demo_memory_optimization():
    """演示内存优化功能"""
    print("\n内存优化演示")
    print("=" * 50)
    
    # 创建完整的内存管理系统
    memory_monitor = MemoryMonitor()
    cache_manager = SmartCacheManager(max_size=100, max_memory_mb=20)
    memory_optimizer = MemoryOptimizer(memory_monitor, cache_manager)
    
    # 设置基线
    memory_monitor.set_baseline()
    initial_memory = memory_monitor.process.memory_info().rss / 1024 / 1024
    print(f"初始内存: {initial_memory:.2f}MB")
    
    # 模拟内存使用
    print("模拟内存使用...")
    large_objects = []
    for i in range(100):
        # 创建一些大对象
        large_objects.append("x" * 10000)  # 10KB字符串
        
        # 添加到缓存
        cache_manager.get_cached_item(
            'test_cache', f'large_obj_{i}',
            lambda i=i: "x" * 5000
        )
    
    # 更新内存监控
    memory_monitor.update()
    current_memory = memory_monitor.process.memory_info().rss / 1024 / 1024
    print(f"使用后内存: {current_memory:.2f}MB (+{current_memory - initial_memory:.2f}MB)")
    
    # 执行优化
    print("\n执行内存优化...")
    optimizations = memory_optimizer.optimize_memory()
    for opt in optimizations:
        print(f"  - {opt}")
    
    # 检查优化后的内存
    time.sleep(1)  # 给GC一些时间
    memory_monitor.update()
    final_memory = memory_monitor.process.memory_info().rss / 1024 / 1024
    print(f"优化后内存: {final_memory:.2f}MB ({final_memory - current_memory:+.2f}MB)")
    
    # 获取优化建议
    suggestions = memory_optimizer.suggest_optimizations()
    if suggestions:
        print("\n优化建议:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    else:
        print("\n暂无优化建议")


def demo_performance_integration():
    """演示性能系统集成"""
    print("\n性能系统集成演示")
    print("=" * 50)
    
    # 创建性能优化器（包含内存管理）
    optimizer = PerformanceOptimizer()
    
    if optimizer.memory_monitor:
        print("内存管理系统已集成到性能系统中")
        
        # 模拟一些帧循环
        print("模拟游戏循环...")
        for frame in range(10):
            optimizer.start_frame()
            
            # 模拟一些工作
            time.sleep(0.01)
            
            # 使用优化的字体渲染
            for i in range(5):
                surface = optimizer.get_optimized_font(16, f"Frame {frame} Text {i}")
            
            optimizer.end_frame()
        
        # 获取统计信息
        stats = optimizer.get_stats()
        print(f"\n性能统计:")
        print(f"  总帧数: {stats.get('total_frames', 0)}")
        print(f"  当前FPS: {stats.get('current_fps', 0)}")
        if 'current_memory_mb' in stats:
            print(f"  当前内存: {stats['current_memory_mb']:.2f}MB")
        
        # 获取内存报告
        memory_report = optimizer.get_memory_report()
        if 'current_memory' in memory_report:
            print(f"  内存增长: {memory_report['memory_stats'].get('memory_growth_mb', 0):+.2f}MB")
    else:
        print("内存管理系统不可用（缺少psutil）")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='内存管理监控工具')
    parser.add_argument('--monitor-duration', type=int, default=10,
                       help='内存监控持续时间（秒）')
    parser.add_argument('--demo', choices=['memory', 'cache', 'optimization', 'integration', 'all'],
                       default='all', help='运行特定演示')
    
    args = parser.parse_args()
    
    try:
        if args.demo in ['memory', 'all']:
            monitor_memory_usage(args.monitor_duration)
        
        if args.demo in ['cache', 'all']:
            demo_cache_management()
        
        if args.demo in ['optimization', 'all']:
            demo_memory_optimization()
        
        if args.demo in ['integration', 'all']:
            demo_performance_integration()
    
    except KeyboardInterrupt:
        print("\n\n演示已中断")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")


if __name__ == '__main__':
    main()