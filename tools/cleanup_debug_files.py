#!/usr/bin/env python3
"""
Debug Files Cleanup Tool
清理游戏运行过程中产生的调试文件和日志文件
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple
import json

class DebugFilesCleaner:
    """调试文件清理器"""
    
    def __init__(self, game_root: Path):
        self.game_root = Path(game_root).resolve()
        self.logs_dir = self.game_root / "logs"
        self.debug_dir = self.game_root / "data" / "debug"
        
    def get_file_info(self, directory: Path) -> Tuple[int, int, List[Path]]:
        """获取目录文件信息：文件数量、总大小、文件列表"""
        if not directory.exists():
            return 0, 0, []
            
        files = []
        total_size = 0
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                files.append(file_path)
                total_size += file_path.stat().st_size
                
        return len(files), total_size, files
    
    def cleanup_old_logs(self, days_to_keep: int = 3) -> dict:
        """清理超过指定天数的日志文件"""
        if not self.logs_dir.exists():
            return {"cleaned": 0, "size_freed": 0, "kept": 0}
            
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cleaned_count = 0
        size_freed = 0
        kept_count = 0
        
        for log_file in self.logs_dir.rglob("*.log"):
            try:
                # 获取文件修改时间
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    file_size = log_file.stat().st_size
                    log_file.unlink()
                    cleaned_count += 1
                    size_freed += file_size
                    print(f"删除旧日志: {log_file.name} ({file_size} bytes)")
                else:
                    kept_count += 1
                    
            except Exception as e:
                print(f"处理日志文件时出错 {log_file}: {e}")
                
        return {
            "cleaned": cleaned_count,
            "size_freed": size_freed,
            "kept": kept_count
        }
    
    def cleanup_debug_levels(self, max_files: int = 5) -> dict:
        """清理debug目录中的关卡文件，只保留最新的几个"""
        levels_dir = self.debug_dir / "levels"
        if not levels_dir.exists():
            return {"cleaned": 0, "size_freed": 0, "kept": 0}
            
        # 获取所有关卡文件，按修改时间排序
        level_files = []
        for file_path in levels_dir.glob("*.txt"):
            try:
                mtime = file_path.stat().st_mtime
                level_files.append((mtime, file_path))
            except Exception:
                continue
                
        # 按时间排序，最新的在前
        level_files.sort(key=lambda x: x[0], reverse=True)
        
        cleaned_count = 0
        size_freed = 0
        kept_count = 0
        
        # 删除超出数量限制的文件
        for i, (mtime, file_path) in enumerate(level_files):
            if i < max_files:
                kept_count += 1
            else:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    cleaned_count += 1
                    size_freed += file_size
                    print(f"删除旧关卡文件: {file_path.name} ({file_size} bytes)")
                except Exception as e:
                    print(f"删除文件时出错 {file_path}: {e}")
                    
        return {
            "cleaned": cleaned_count,
            "size_freed": size_freed,
            "kept": kept_count
        }
    
    def cleanup_empty_dirs(self) -> int:
        """清理空目录"""
        cleaned_dirs = 0
        
        for directory in [self.debug_dir, self.logs_dir]:
            if not directory.exists():
                continue
                
            # 从最深层开始检查空目录
            for dir_path in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    try:
                        dir_path.rmdir()
                        cleaned_dirs += 1
                        print(f"删除空目录: {dir_path.relative_to(self.game_root)}")
                    except Exception as e:
                        print(f"删除空目录时出错 {dir_path}: {e}")
                        
        return cleaned_dirs
    
    def show_status(self):
        """显示当前调试文件状态"""
        print("=== 调试文件状态 ===")
        
        # 日志文件状态
        log_count, log_size, _ = self.get_file_info(self.logs_dir)
        print(f"日志文件: {log_count} 个文件, {log_size:,} bytes ({log_size/1024:.1f} KB)")
        
        # 调试文件状态
        debug_count, debug_size, _ = self.get_file_info(self.debug_dir)
        print(f"调试文件: {debug_count} 个文件, {debug_size:,} bytes ({debug_size/1024:.1f} KB)")
        
        # 总计
        total_files = log_count + debug_count
        total_size = log_size + debug_size
        print(f"总计: {total_files} 个文件, {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        return {
            "logs": {"count": log_count, "size": log_size},
            "debug": {"count": debug_count, "size": debug_size},
            "total": {"count": total_files, "size": total_size}
        }
    
    def full_cleanup(self, days_to_keep: int = 3, max_level_files: int = 5) -> dict:
        """执行完整清理"""
        print("开始清理调试文件...")
        
        # 显示清理前状态
        before_status = self.show_status()
        print()
        
        # 清理操作
        log_result = self.cleanup_old_logs(days_to_keep)
        level_result = self.cleanup_debug_levels(max_level_files)
        empty_dirs = self.cleanup_empty_dirs()
        
        print()
        print("=== 清理结果 ===")
        print(f"删除日志文件: {log_result['cleaned']} 个 ({log_result['size_freed']:,} bytes)")
        print(f"保留日志文件: {log_result['kept']} 个")
        print(f"删除关卡文件: {level_result['cleaned']} 个 ({level_result['size_freed']:,} bytes)")
        print(f"保留关卡文件: {level_result['kept']} 个")
        print(f"删除空目录: {empty_dirs} 个")
        
        total_freed = log_result['size_freed'] + level_result['size_freed']
        print(f"总计释放空间: {total_freed:,} bytes ({total_freed/1024:.1f} KB)")
        
        # 显示清理后状态
        print()
        after_status = self.show_status()
        
        return {
            "before": before_status,
            "after": after_status,
            "logs_cleaned": log_result,
            "levels_cleaned": level_result,
            "empty_dirs_cleaned": empty_dirs,
            "total_freed": total_freed
        }


def main():
    parser = argparse.ArgumentParser(description="清理游戏调试文件和日志")
    parser.add_argument("--days", type=int, default=3, 
                       help="保留最近N天的日志文件 (默认: 3)")
    parser.add_argument("--max-levels", type=int, default=5,
                       help="保留最新的N个关卡文件 (默认: 5)")
    parser.add_argument("--status-only", action="store_true",
                       help="只显示状态，不执行清理")
    parser.add_argument("--game-root", type=str, default=".",
                       help="游戏根目录路径 (默认: 当前目录)")
    
    args = parser.parse_args()
    
    try:
        cleaner = DebugFilesCleaner(args.game_root)
        
        if args.status_only:
            cleaner.show_status()
        else:
            result = cleaner.full_cleanup(args.days, args.max_levels)
            
            # 保存清理报告
            report_file = Path(args.game_root) / "cleanup_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                result['timestamp'] = datetime.now().isoformat()
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n清理报告已保存到: {report_file}")
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()