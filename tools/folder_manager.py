#!/usr/bin/env python3
"""
文件夹管理工具 - 用于维护debug和logs文件夹
"""
import os
import sys
import shutil
import datetime
import argparse
import zipfile
from pathlib import Path
from typing import List, Dict, Tuple
import re
import glob

class FolderManager:
    """智能文件夹管理器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.logs_dir = self.project_root / "logs"
        self.debug_dir = self.project_root / "data" / "debug"
        self.archive_dir = self.project_root / "archive"
        
        # 默认配置
        self.config = {
            'logs': {
                'max_files': 20,
                'max_size_mb': 100,
                'archive_after_days': 7,
                'compress_archive': True,
                'scan_subdirs': True  # 新增：扫描子文件夹
            },
            'debug': {
                'max_files': 30,  # 减少限制，因为现在分散在子文件夹中
                'max_size_mb': 200,
                'archive_after_days': 3,
                'compress_archive': True,
                'keep_latest_level': True,
                'scan_subdirs': True  # 新增：扫描子文件夹
            }
        }
    
    def analyze_folder(self, folder_path: Path) -> Dict:
        """分析文件夹状态（递归扫描所有子文件夹）"""
        if not folder_path.exists():
            return {'exists': False}
        
        # 递归收集所有文件
        files = []
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                files.append(file_path)
        
        total_size = sum(f.stat().st_size for f in files)
        
        # 按修改时间排序
        files_with_time = [(f, f.stat().st_mtime) for f in files]
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        
        # 分析文件类型
        file_types = {}
        for f, _ in files_with_time:
            ext = f.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            'exists': True,
            'total_files': len(files_with_time),
            'total_size_mb': total_size / (1024 * 1024),
            'file_types': file_types,
            'files_by_age': files_with_time,
            'oldest_file': files_with_time[-1][0] if files_with_time else None,
            'newest_file': files_with_time[0][0] if files_with_time else None
        }
    
    def cleanup_logs(self, dry_run: bool = False) -> Dict:
        """清理日志文件夹"""
        print(f"🔍 分析logs文件夹: {self.logs_dir}")
        
        analysis = self.analyze_folder(self.logs_dir)
        if not analysis['exists']:
            return {'status': 'folder_not_found', 'message': 'logs文件夹不存在'}
        
        config = self.config['logs']
        actions = []
        
        # 按类型分组文件
        game_logs = []
        error_logs = []
        other_logs = []
        
        for file_path, mtime in analysis['files_by_age']:
            filename = file_path.name
            if filename.startswith('game_'):
                game_logs.append((file_path, mtime))
            elif filename.startswith('error_'):
                error_logs.append((file_path, mtime))
            else:
                other_logs.append((file_path, mtime))
        
        # 处理游戏日志
        if len(game_logs) > config['max_files'] // 2:
            files_to_archive = game_logs[config['max_files'] // 2:]
            for file_path, mtime in files_to_archive:
                actions.append(('archive', file_path, 'too_many_game_logs'))
        
        # 处理错误日志
        if len(error_logs) > config['max_files'] // 2:
            files_to_archive = error_logs[config['max_files'] // 2:]
            for file_path, mtime in files_to_archive:
                actions.append(('archive', file_path, 'too_many_error_logs'))
        
        # 处理旧文件
        cutoff_time = datetime.datetime.now().timestamp() - (config['archive_after_days'] * 24 * 3600)
        for file_path, mtime in analysis['files_by_age']:
            if mtime < cutoff_time:
                actions.append(('archive', file_path, 'old_file'))
        
        # 执行操作
        results = {'archived': [], 'errors': []}
        if not dry_run:
            results = self._execute_actions(actions, 'logs')
        
        return {
            'status': 'success',
            'analysis': analysis,
            'actions': actions,
            'results': results,
            'dry_run': dry_run
        }
    
    def cleanup_debug(self, dry_run: bool = False) -> Dict:
        """清理debug文件夹"""
        print(f"🔍 分析debug文件夹: {self.debug_dir}")
        
        analysis = self.analyze_folder(self.debug_dir)
        if not analysis['exists']:
            return {'status': 'folder_not_found', 'message': 'debug文件夹不存在'}
        
        config = self.config['debug']
        actions = []
        
        # 分析生成的关卡文件
        level_files = {}
        other_files = []
        
        for file_path, mtime in analysis['files_by_age']:
            filename = file_path.name
            # 匹配 last_generated_level_xxx.txt 格式
            level_match = re.match(r'last_generated_level_(\d+|[\d]+)\.txt', filename)
            if level_match:
                level_id = level_match.group(1)
                if level_id not in level_files:
                    level_files[level_id] = []
                level_files[level_id].append((file_path, mtime))
            else:
                other_files.append((file_path, mtime))
        
        # 保留每个level的最新文件，归档其他的
        for level_id, files in level_files.items():
            if len(files) > 1:
                # 按时间排序，保留最新的
                files.sort(key=lambda x: x[1], reverse=True)
                if config['keep_latest_level']:
                    files_to_archive = files[1:]  # 保留最新的
                else:
                    files_to_archive = files
                
                for file_path, mtime in files_to_archive:
                    actions.append(('archive', file_path, f'duplicate_level_{level_id}'))
        
        # 处理文件数量过多的情况
        all_debug_files = analysis['files_by_age']
        if len(all_debug_files) > config['max_files']:
            # 保留最新的N个文件
            files_to_archive = all_debug_files[config['max_files']:]
            for file_path, mtime in files_to_archive:
                if ('archive', file_path, f'duplicate_level_{level_id}') not in actions:
                    actions.append(('archive', file_path, 'too_many_files'))
        
        # 处理旧文件
        cutoff_time = datetime.datetime.now().timestamp() - (config['archive_after_days'] * 24 * 3600)
        for file_path, mtime in analysis['files_by_age']:
            if mtime < cutoff_time:
                # 避免重复添加
                action_exists = any(action[1] == file_path for action in actions)
                if not action_exists:
                    actions.append(('archive', file_path, 'old_file'))
        
        # 执行操作
        results = {'archived': [], 'errors': []}
        if not dry_run:
            results = self._execute_actions(actions, 'debug')
        
        return {
            'status': 'success',
            'analysis': analysis,
            'actions': actions,
            'results': results,
            'dry_run': dry_run
        }
    
    def _execute_actions(self, actions: List[Tuple], folder_type: str) -> Dict:
        """执行文件操作"""
        results = {'archived': [], 'errors': []}
        
        if not actions:
            return results
        
        # 创建归档目录
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_folder = self.archive_dir / f"{folder_type}_{timestamp}"
        archive_folder.mkdir(parents=True, exist_ok=True)
        
        for action, file_path, reason in actions:
            try:
                if action == 'archive':
                    # 移动文件到归档文件夹
                    archive_path = archive_folder / file_path.name
                    shutil.move(str(file_path), str(archive_path))
                    results['archived'].append({
                        'file': file_path.name,
                        'reason': reason,
                        'archive_path': str(archive_path)
                    })
                    print(f"📦 归档: {file_path.name} -> {archive_path}")
                
            except Exception as e:
                results['errors'].append({
                    'file': file_path.name,
                    'error': str(e)
                })
                print(f"❌ 错误: {file_path.name} - {e}")
        
        # 压缩归档文件夹
        if results['archived'] and self.config[folder_type]['compress_archive']:
            try:
                self._compress_archive(archive_folder)
                print(f"🗜️ 已压缩归档: {archive_folder.name}.zip")
            except Exception as e:
                print(f"❌ 压缩失败: {e}")
        
        return results
    
    def _compress_archive(self, archive_folder: Path):
        """压缩归档文件夹"""
        zip_path = archive_folder.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in archive_folder.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(archive_folder)
                    zipf.write(file_path, arcname)
        
        # 删除原文件夹
        shutil.rmtree(archive_folder)
    
    def create_folder_structure(self):
        """创建优化的文件夹结构"""
        folders_to_create = [
            self.logs_dir,
            self.debug_dir,
            self.archive_dir,
            self.logs_dir / "session",
            self.logs_dir / "error", 
            self.logs_dir / "performance",
            self.debug_dir / "levels",
            self.debug_dir / "maps",
            self.debug_dir / "entities"
        ]
        
        for folder in folders_to_create:
            folder.mkdir(parents=True, exist_ok=True)
            print(f"📁 创建文件夹: {folder}")
    
    def get_status_report(self) -> Dict:
        """获取文件夹状态报告"""
        logs_analysis = self.analyze_folder(self.logs_dir)
        debug_analysis = self.analyze_folder(self.debug_dir)
        
        return {
            'logs': logs_analysis,
            'debug': debug_analysis,
            'recommendations': self._get_recommendations(logs_analysis, debug_analysis)
        }
    
    def _get_recommendations(self, logs_analysis: Dict, debug_analysis: Dict) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        if logs_analysis.get('total_files', 0) > self.config['logs']['max_files']:
            recommendations.append(f"日志文件过多 ({logs_analysis['total_files']}个)，建议清理")
        
        if debug_analysis.get('total_files', 0) > self.config['debug']['max_files']:
            recommendations.append(f"Debug文件过多 ({debug_analysis['total_files']}个)，建议清理")
        
        if logs_analysis.get('total_size_mb', 0) > self.config['logs']['max_size_mb']:
            recommendations.append(f"日志文件夹过大 ({logs_analysis['total_size_mb']:.1f}MB)")
        
        if debug_analysis.get('total_size_mb', 0) > self.config['debug']['max_size_mb']:
            recommendations.append(f"Debug文件夹过大 ({debug_analysis['total_size_mb']:.1f}MB)")
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description='文件夹管理工具')
    parser.add_argument('--cleanup-logs', action='store_true', help='清理日志文件夹')
    parser.add_argument('--cleanup-debug', action='store_true', help='清理debug文件夹')
    parser.add_argument('--cleanup-all', action='store_true', help='清理所有文件夹')
    parser.add_argument('--status', action='store_true', help='显示文件夹状态')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，不实际执行操作')
    parser.add_argument('--create-structure', action='store_true', help='创建优化的文件夹结构')
    
    args = parser.parse_args()
    
    manager = FolderManager()
    
    if args.create_structure:
        manager.create_folder_structure()
        return
    
    if args.status:
        print("📊 文件夹状态报告")
        print("=" * 50)
        report = manager.get_status_report()
        
        # 日志文件夹状态
        logs = report['logs']
        if logs['exists']:
            print(f"📁 Logs文件夹:")
            print(f"   文件数量: {logs['total_files']}")
            print(f"   总大小: {logs['total_size_mb']:.1f} MB")
            print(f"   文件类型: {logs['file_types']}")
        else:
            print("📁 Logs文件夹: 不存在")
        
        print()
        
        # Debug文件夹状态
        debug = report['debug']
        if debug['exists']:
            print(f"🐛 Debug文件夹:")
            print(f"   文件数量: {debug['total_files']}")
            print(f"   总大小: {debug['total_size_mb']:.1f} MB")
            print(f"   文件类型: {debug['file_types']}")
        else:
            print("🐛 Debug文件夹: 不存在")
        
        print()
        
        # 建议
        if report['recommendations']:
            print("💡 优化建议:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        else:
            print("✅ 文件夹状态良好")
        
        return
    
    if args.cleanup_logs or args.cleanup_all:
        print("🧹 清理日志文件夹...")
        result = manager.cleanup_logs(dry_run=args.dry_run)
        print(f"结果: {result['status']}")
        if result.get('actions'):
            print(f"计划操作: {len(result['actions'])}个文件")
        print()
    
    if args.cleanup_debug or args.cleanup_all:
        print("🧹 清理debug文件夹...")
        result = manager.cleanup_debug(dry_run=args.dry_run)
        print(f"结果: {result['status']}")
        if result.get('actions'):
            print(f"计划操作: {len(result['actions'])}个文件")
        print()
    
    if not any([args.cleanup_logs, args.cleanup_debug, args.cleanup_all, args.status, args.create_structure]):
        parser.print_help()


if __name__ == "__main__":
    main()