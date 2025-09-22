#!/usr/bin/env python3
"""
自动日志清理任务
定期清理过期的日志和调试文件
"""

import os
import sys
import time
import schedule
from pathlib import Path
from datetime import datetime
from tools.cleanup_debug_files import DebugFilesCleaner


def setup_auto_cleanup():
    """设置自动清理任务"""
    game_root = Path(__file__).parent.parent
    cleaner = DebugFilesCleaner(game_root)
    
    def daily_cleanup():
        """每日清理任务"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动清理...")
        try:
            result = cleaner.full_cleanup(days_to_keep=2, max_level_files=3)
            total_freed = result['total_freed']
            print(f"自动清理完成，释放空间: {total_freed:,} bytes ({total_freed/1024:.1f} KB)")
        except Exception as e:
            print(f"自动清理失败: {e}")
    
    def weekly_deep_clean():
        """每周深度清理"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始深度清理...")
        try:
            result = cleaner.full_cleanup(days_to_keep=1, max_level_files=1)
            total_freed = result['total_freed']
            print(f"深度清理完成，释放空间: {total_freed:,} bytes ({total_freed/1024:.1f} KB)")
        except Exception as e:
            print(f"深度清理失败: {e}")
    
    # 计划任务
    schedule.every().day.at("02:00").do(daily_cleanup)  # 每天凌晨2点
    schedule.every().sunday.at("03:00").do(weekly_deep_clean)  # 每周日凌晨3点
    
    print("自动清理任务已设置:")
    print("- 每日清理: 每天凌晨2点")
    print("- 深度清理: 每周日凌晨3点")
    
    return schedule


def run_cleanup_daemon():
    """运行清理守护进程"""
    schedule = setup_auto_cleanup()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n清理守护进程已停止")


if __name__ == "__main__":
    if "--daemon" in sys.argv:
        run_cleanup_daemon()
    else:
        print("使用 --daemon 参数启动自动清理守护进程")
        print("或者直接运行 tools/cleanup_debug_files.py 进行手动清理")