#!/usr/bin/env python3
"""
自动文件夹管理和维护脚本
集成到游戏的日志系统中
"""
import os
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.folder_manager import FolderManager
    from game.logging import Logger
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保从项目根目录运行此脚本")
    sys.exit(1)


class AutoFolderMaintenance:
    """自动文件夹维护系统"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.folder_manager = FolderManager()
        self.logger = logger
        self.maintenance_thread = None
        self.running = False
        
        # 维护配置
        self.config = {
            'check_interval_minutes': 30,  # 每30分钟检查一次
            'auto_cleanup_enabled': True,
            'log_maintenance_events': True,
            'max_logs_before_cleanup': 25,
            'max_debug_before_cleanup': 60
        }
    
    def start_maintenance(self):
        """启动自动维护"""
        if self.running:
            return
        
        self.running = True
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True
        )
        self.maintenance_thread.start()
        
        if self.logger:
            self.logger.info("Auto folder maintenance started", "MAINTENANCE")
        else:
            print("🔧 自动文件夹维护已启动")
    
    def stop_maintenance(self):
        """停止自动维护"""
        self.running = False
        if self.maintenance_thread and self.maintenance_thread.is_alive():
            self.maintenance_thread.join(timeout=5)
        
        if self.logger:
            self.logger.info("Auto folder maintenance stopped", "MAINTENANCE")
        else:
            print("🛑 自动文件夹维护已停止")
    
    def _maintenance_loop(self):
        """维护循环"""
        while self.running:
            try:
                self._check_and_cleanup()
                # 休眠指定时间
                time.sleep(self.config['check_interval_minutes'] * 60)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Maintenance error: {e}", "MAINTENANCE")
                else:
                    print(f"❌ 维护错误: {e}")
    
    def _check_and_cleanup(self):
        """检查并清理文件夹"""
        if not self.config['auto_cleanup_enabled']:
            return
        
        # 获取状态报告
        report = self.folder_manager.get_status_report()
        
        cleanup_needed = False
        reasons = []
        
        # 检查日志文件夹
        logs_analysis = report['logs']
        if logs_analysis.get('total_files', 0) > self.config['max_logs_before_cleanup']:
            cleanup_needed = True
            reasons.append(f"logs过多({logs_analysis['total_files']}个)")
        
        # 检查debug文件夹
        debug_analysis = report['debug']
        if debug_analysis.get('total_files', 0) > self.config['max_debug_before_cleanup']:
            cleanup_needed = True
            reasons.append(f"debug文件过多({debug_analysis['total_files']}个)")
        
        if cleanup_needed:
            self._perform_cleanup(reasons)
    
    def _perform_cleanup(self, reasons: list):
        """执行清理"""
        try:
            if self.logger:
                self.logger.info(f"Starting auto cleanup: {', '.join(reasons)}", "MAINTENANCE")
            
            # 清理日志文件夹
            logs_result = self.folder_manager.cleanup_logs(dry_run=False)
            logs_archived = len(logs_result.get('results', {}).get('archived', []))
            
            # 清理debug文件夹
            debug_result = self.folder_manager.cleanup_debug(dry_run=False)
            debug_archived = len(debug_result.get('results', {}).get('archived', []))
            
            # 记录结果
            if self.logger:
                self.logger.info(
                    f"Auto cleanup completed: {logs_archived} logs, {debug_archived} debug files archived",
                    "MAINTENANCE"
                )
            else:
                print(f"🧹 自动清理完成: 归档了{logs_archived}个日志文件, {debug_archived}个debug文件")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Auto cleanup failed: {e}", "MAINTENANCE")
            else:
                print(f"❌ 自动清理失败: {e}")
    
    def force_cleanup(self):
        """强制清理"""
        self._perform_cleanup(["手动触发"])
    
    def get_status(self) -> Dict:
        """获取维护状态"""
        report = self.folder_manager.get_status_report()
        
        return {
            'maintenance_active': self.running,
            'config': self.config,
            'folder_status': report,
            'next_check_minutes': self.config['check_interval_minutes'] if self.running else None
        }


# 全局实例
_auto_maintenance = None

def get_auto_maintenance(logger: Optional[Logger] = None) -> AutoFolderMaintenance:
    """获取全局自动维护实例"""
    global _auto_maintenance
    if _auto_maintenance is None:
        _auto_maintenance = AutoFolderMaintenance(logger)
    return _auto_maintenance

def start_auto_maintenance(logger: Optional[Logger] = None):
    """启动自动维护"""
    maintenance = get_auto_maintenance(logger)
    maintenance.start_maintenance()

def stop_auto_maintenance():
    """停止自动维护"""
    global _auto_maintenance
    if _auto_maintenance:
        _auto_maintenance.stop_maintenance()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自动文件夹维护系统')
    parser.add_argument('--start', action='store_true', help='启动自动维护')
    parser.add_argument('--stop', action='store_true', help='停止自动维护')
    parser.add_argument('--status', action='store_true', help='显示维护状态')
    parser.add_argument('--force-cleanup', action='store_true', help='强制清理')
    parser.add_argument('--daemon', action='store_true', help='后台运行')
    
    args = parser.parse_args()
    
    maintenance = get_auto_maintenance()
    
    if args.start:
        maintenance.start_maintenance()
        if args.daemon:
            print("🔧 自动维护已启动（后台模式）")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n🛑 收到停止信号")
                maintenance.stop_maintenance()
        else:
            print("🔧 自动维护已启动")
    
    elif args.stop:
        maintenance.stop_maintenance()
    
    elif args.status:
        status = maintenance.get_status()
        print("📊 自动维护状态")
        print("=" * 40)
        print(f"维护状态: {'运行中' if status['maintenance_active'] else '已停止'}")
        print(f"检查间隔: {status['config']['check_interval_minutes']}分钟")
        print(f"自动清理: {'启用' if status['config']['auto_cleanup_enabled'] else '禁用'}")
        
        folder_status = status['folder_status']
        print(f"\n📁 文件夹状态:")
        if folder_status['logs']['exists']:
            print(f"  日志文件: {folder_status['logs']['total_files']}个")
        if folder_status['debug']['exists']:
            print(f"  Debug文件: {folder_status['debug']['total_files']}个")
        
        if folder_status['recommendations']:
            print(f"\n💡 建议:")
            for rec in folder_status['recommendations']:
                print(f"  • {rec}")
    
    elif args.force_cleanup:
        print("🧹 强制执行清理...")
        maintenance.force_cleanup()
        print("✅ 清理完成")
    
    else:
        parser.print_help()