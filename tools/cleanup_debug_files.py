#!/usr/bin/env python3
"""
Debug Files Cleanup Tool
清理游戏运行过程中产生的调试文件和日志文件
"""

import os
import sys
import argparse
import logging
import time
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import json

class DebugFilesCleaner:
    """调试文件清理器"""
    
    def __init__(self, game_root: Path, *, dry_run: bool = False, logger: Optional[logging.Logger] = None,
                 delete_retries: int = 3, retry_delay: float = 0.5):
        """初始化清理器

        Args:
            game_root: 根目录
            dry_run: 如果为 True，则不执行实际删除，只模拟输出
            logger: 可选的 logging.Logger 实例；若为 None 则创建模块级 logger
            delete_retries: 删除文件或目录失败时的重试次数
            retry_delay: 每次重试之间的等待秒数
        """
        self.game_root = Path(game_root).resolve()
        self.logs_dir = self.game_root / "logs"
        self.debug_dir = self.game_root / "data" / "debug"
        self.dry_run = bool(dry_run)
        self.delete_retries = int(delete_retries)
        self.retry_delay = float(retry_delay)

        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        
    def get_file_info(self, directory: Path) -> Tuple[int, int, List[Path]]:
        """获取目录文件信息：文件数量、总大小、文件列表"""
        if not directory.exists():
            return 0, 0, []
            
        files = []
        total_size = 0
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                files.append(file_path)
                try:
                    total_size += file_path.stat().st_size
                except Exception:
                    # 如果 stat 失败，跳过该文件大小统计，但仍保留路径
                    self.logger.debug("无法读取文件大小: %s", file_path, exc_info=True)
                
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
                    try:
                        file_size = log_file.stat().st_size
                    except Exception:
                        file_size = 0
                        self.logger.debug("无法读取日志文件大小: %s", log_file, exc_info=True)

                    if self._remove_with_retries(log_file):
                        cleaned_count += 1
                        size_freed += file_size
                        self.logger.info("删除旧日志: %s (%d bytes)%s", log_file.name, file_size,
                                         " [dry-run]" if self.dry_run else "")
                    else:
                        self.logger.warning("无法删除日志文件: %s", log_file)
                else:
                    kept_count += 1

            except Exception as e:
                self.logger.exception("处理日志文件时出错 %s", log_file)
                
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
                self.logger.debug("无法读取关卡文件属性: %s", file_path, exc_info=True)
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
                    try:
                        file_size = file_path.stat().st_size
                    except Exception:
                        file_size = 0
                        self.logger.debug("无法读取文件大小: %s", file_path, exc_info=True)

                    if self._remove_with_retries(file_path):
                        cleaned_count += 1
                        size_freed += file_size
                        self.logger.info("删除旧关卡文件: %s (%d bytes)%s", file_path.name, file_size,
                                         " [dry-run]" if self.dry_run else "")
                    else:
                        self.logger.warning("无法删除关卡文件: %s", file_path)
                except Exception:
                    self.logger.exception("删除文件时出错 %s", file_path)
                    
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
                        if self.dry_run:
                            self.logger.info("删除空目录: %s [dry-run]", dir_path.relative_to(self.game_root))
                            cleaned_dirs += 1
                        else:
                            # 使用重试逻辑以防止短暂的文件锁
                            removed = False
                            for attempt in range(self.delete_retries):
                                try:
                                    dir_path.rmdir()
                                    removed = True
                                    cleaned_dirs += 1
                                    self.logger.info("删除空目录: %s", dir_path.relative_to(self.game_root))
                                    break
                                except Exception:
                                    self.logger.debug("尝试删除空目录失败: %s (尝试 %d/%d)",
                                                      dir_path, attempt + 1, self.delete_retries, exc_info=True)
                                    time.sleep(self.retry_delay)

                            if not removed:
                                self.logger.warning("删除空目录失败: %s", dir_path)
                    except Exception:
                        self.logger.exception("删除空目录时出错 %s", dir_path)
                        
        return cleaned_dirs
    
    def show_status(self):
        """显示当前调试文件状态"""
        self.logger.info("=== 调试文件状态 ===")

        # 日志文件状态
        log_count, log_size, _ = self.get_file_info(self.logs_dir)
        self.logger.info("日志文件: %d 个文件, %d bytes (%.1f KB)", log_count, log_size, log_size / 1024 if log_size else 0.0)

        # 调试文件状态
        debug_count, debug_size, _ = self.get_file_info(self.debug_dir)
        self.logger.info("调试文件: %d 个文件, %d bytes (%.1f KB)", debug_count, debug_size, debug_size / 1024 if debug_size else 0.0)

        # 总计
        total_files = log_count + debug_count
        total_size = log_size + debug_size
        self.logger.info("总计: %d 个文件, %d bytes (%.1f KB)", total_files, total_size, total_size / 1024 if total_size else 0.0)

        return {
            "logs": {"count": log_count, "size": log_size},
            "debug": {"count": debug_count, "size": debug_size},
            "total": {"count": total_files, "size": total_size}
        }
    
    def full_cleanup(self, days_to_keep: int = 3, max_level_files: int = 5) -> dict:
        """执行完整清理"""
        self.logger.info("开始清理调试文件...%s", " [dry-run]" if self.dry_run else "")

        # 显示清理前状态
        before_status = self.show_status()

        # 清理操作
        log_result = self.cleanup_old_logs(days_to_keep)
        level_result = self.cleanup_debug_levels(max_level_files)
        empty_dirs = self.cleanup_empty_dirs()

        self.logger.info("=== 清理结果 ===")
        self.logger.info("删除日志文件: %d 个 (%d bytes)", log_result["cleaned"], log_result["size_freed"])
        self.logger.info("保留日志文件: %d 个", log_result["kept"])
        self.logger.info("删除关卡文件: %d 个 (%d bytes)", level_result["cleaned"], level_result["size_freed"])
        self.logger.info("保留关卡文件: %d 个", level_result["kept"])
        self.logger.info("删除空目录: %d 个", empty_dirs)

        total_freed = log_result["size_freed"] + level_result["size_freed"]
        self.logger.info("总计释放空间: %d bytes (%.1f KB)", total_freed, total_freed / 1024 if total_freed else 0.0)

        # 显示清理后状态
        after_status = self.show_status()

        return {
            "before": before_status,
            "after": after_status,
            "logs_cleaned": log_result,
            "levels_cleaned": level_result,
            "empty_dirs_cleaned": empty_dirs,
            "total_freed": total_freed
        }

    def _remove_with_retries(self, path: Path) -> bool:
        """尝试删除文件或目录，失败时重试若干次。返回是否删除成功或 dry-run 被计为成功。"""
        if self.dry_run:
            self.logger.debug("dry-run 模式，不实际删除: %s", path)
            return True

        for attempt in range(1, self.delete_retries + 1):
            try:
                # 对文件使用 unlink
                if path.is_dir():
                    path.rmdir()
                else:
                    path.unlink()
                return True
            except Exception:
                self.logger.debug("删除失败: %s (尝试 %d/%d)", path, attempt, self.delete_retries, exc_info=True)
                if attempt < self.delete_retries:
                    time.sleep(self.retry_delay)

        return False


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
    parser.add_argument("--dry-run", action="store_true",
                        help="模拟运行，不实际删除任何文件")
    parser.add_argument("--verbose", action="store_true",
                        help="输出调试日志")

    args = parser.parse_args()

    # 基本日志配置，允许用户通过 --verbose 开启 DEBUG
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s: %(message)s')

    try:
        cleaner = DebugFilesCleaner(args.game_root, dry_run=args.dry_run)

        if args.status_only:
            cleaner.show_status()
        else:
            result = cleaner.full_cleanup(args.days, args.max_levels)

            # 保存清理报告到临时文件然后原子替换，避免半写入
            report_file = Path(args.game_root) / "cleanup_report.json"
            try:
                result['timestamp'] = datetime.now().isoformat()
                # 写入临时文件在同一目录以便保证可重命名原子性
                with tempfile.NamedTemporaryFile('w', delete=False, dir=str(report_file.parent), encoding='utf-8') as tf:
                    json.dump(result, tf, indent=2, ensure_ascii=False)
                    temp_name = tf.name

                # 用重命名操作替换目标文件（在大多数平台下为原子操作）
                os.replace(temp_name, str(report_file))
                cleaner.logger.info("清理报告已保存到: %s", report_file)
            except Exception:
                cleaner.logger.exception("写入清理报告时出错 %s", report_file)

    except Exception:
        logging.exception("运行清理工具时遇到致命错误")
        sys.exit(1)


if __name__ == "__main__":
    main()