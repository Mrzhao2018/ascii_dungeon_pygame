#!/usr/bin/env python3
"""
代码优化自动修复工具
修复flake8和mypy发现的代码质量问题
"""

import os
import subprocess
import sys
from pathlib import Path


def fix_whitespace_issues():
    """修复空白字符问题"""
    print("正在修复空白字符问题...")
    
    game_dir = Path("game")
    for py_file in game_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除行尾空白
            lines = content.split('\n')
            lines = [line.rstrip() for line in lines]
            
            # 移除空行中的空白字符
            for i, line in enumerate(lines):
                if not line.strip():
                    lines[i] = ""
            
            # 确保文件以换行符结尾
            if lines and lines[-1]:
                lines.append("")
            
            # 写回文件
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
            print(f"已修复: {py_file}")
            
        except Exception as e:
            print(f"修复 {py_file} 时出错: {e}")


def fix_import_issues():
    """修复导入问题"""
    print("正在检查并修复导入问题...")
    
    # 需要移除的未使用导入
    unused_imports = {
        "game/config.py": ["argparse", "os"],
        "game/config_file.py": ["os"],
        "game/debug.py": ["List", "Dict", "Any", "Optional"],
        "game/dialogs.py": ["Dict", "Tuple"],
        "game/entities.py": ["Callable"],
        "game/error_handling.py": ["os", "sys", "json", "Path", "List", "Union", "timedelta"],
        "game/game.py": ["os", "Optional", "create_performance_timer", "dialogs_mod"],
        "game/input.py": ["Tuple", "Optional", "Callable"],
    "game/logger.py": ["sys"],
        "game/memory.py": ["Tuple", "threading"],
        "game/performance.py": ["threading", "os", "Optional"],
        "game/player.py": ["pygame"],
        "game/renderer.py": ["random", "List", "Optional", "Logger"],
        "game/state.py": ["Dict", "Tuple", "Any"],
        "game/ui.py": ["math", "List", "Any"],
    }
    
    for file_path, imports_to_remove in unused_imports.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                should_keep = True
                for import_name in imports_to_remove:
                    if f"import {import_name}" in line or f"from typing import" in line and import_name in line:
                        # 检查是否是完整的导入语句
                        if line.strip().startswith(('import ', 'from ')):
                            should_keep = False
                            break
                
                if should_keep:
                    new_lines.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            print(f"已清理导入: {file_path}")
            
        except Exception as e:
            print(f"清理 {file_path} 导入时出错: {e}")


def fix_spacing_issues():
    """修复间距问题"""
    print("正在修复间距问题...")
    
    spacing_fixes = [
        # 算术运算符周围的空格
        (r'(\w+)([+\-*/])(\w+)', r'\1 \2 \3'),
        # 逗号后面的空格
        (r',(\w)', r', \1'),
        # 等号周围的空格
        (r'(\w+)=(\w+)', r'\1 = \2'),
    ]
    
    game_dir = Path("game")
    for py_file in game_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 应用正则表达式修复
            import re
            for pattern, replacement in spacing_fixes:
                content = re.sub(pattern, replacement, content)
            
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"修复 {py_file} 间距时出错: {e}")


def run_black_formatter():
    """运行black代码格式化"""
    print("正在运行black代码格式化...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "black", 
            "game/", 
            "--line-length", "120",
            "--skip-string-normalization"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Black格式化完成")
        else:
            print(f"Black格式化出错: {result.stderr}")
            
    except Exception as e:
        print(f"运行black时出错: {e}")


def check_progress():
    """检查修复进度"""
    print("\n=== 检查修复进度 ===")
    
    try:
        # 运行flake8检查
        result = subprocess.run([
            sys.executable, "-m", "flake8", 
            "game/", 
            "--max-line-length=120", 
            "--ignore=E203,W503",
            "--count"
        ], capture_output=True, text=True)
        
        if result.stdout:
            error_count = result.stdout.strip().split('\n')[-1]
            print(f"Flake8错误数量: {error_count}")
        
        # 运行mypy检查
        result = subprocess.run([
            sys.executable, "-m", "mypy", 
            "game/", 
            "--ignore-missing-imports", 
            "--no-strict-optional"
        ], capture_output=True, text=True)
        
        if "Found" in result.stdout:
            error_line = [line for line in result.stdout.split('\n') if "Found" in line]
            if error_line:
                print(f"Mypy错误: {error_line[0]}")
        else:
            print("Mypy检查通过!")
            
    except Exception as e:
        print(f"检查进度时出错: {e}")


def main():
    """主函数"""
    print("开始代码优化修复...")
    
    # 切换到项目根目录
    os.chdir(Path(__file__).parent.parent)
    
    # 执行修复步骤
    fix_whitespace_issues()
    fix_import_issues()
    run_black_formatter()
    
    # 检查修复结果
    check_progress()
    
    print("\n代码优化修复完成!")


if __name__ == "__main__":
    main()