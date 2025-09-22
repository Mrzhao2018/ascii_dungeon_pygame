#!/usr/bin/env python3
"""
修复 typing 导入问题
"""

import os
import re
from pathlib import Path


def fix_typing_imports(file_path):
    """修复单个文件的 typing 导入"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取已有的导入
    import_lines = []
    other_lines = []
    in_imports = True
    
    for line in content.split('\n'):
        if line.strip() == '' and in_imports:
            continue
        elif line.startswith('import ') or line.startswith('from '):
            import_lines.append(line)
        elif line.strip().startswith('"""') or line.strip().startswith('#'):
            if in_imports:
                other_lines.append(line)
            else:
                other_lines.append(line)
        else:
            in_imports = False
            other_lines.append(line)
    
    # 检查需要的类型
    needed_types = set()
    if 'Dict[' in content or 'Dict ' in content:
        needed_types.add('Dict')
    if 'List[' in content or 'List ' in content:
        needed_types.add('List')
    if 'Optional[' in content or 'Optional ' in content:
        needed_types.add('Optional')
    if 'Tuple[' in content or 'Tuple ' in content:
        needed_types.add('Tuple')
    if 'Any[' in content or 'Any ' in content:
        needed_types.add('Any')
    if 'Set[' in content or 'Set ' in content:
        needed_types.add('Set')
    if 'Callable[' in content or 'Callable ' in content:
        needed_types.add('Callable')
    if 'Union[' in content or 'Union ' in content:
        needed_types.add('Union')
    if 'TYPE_CHECKING' in content:
        needed_types.add('TYPE_CHECKING')
    
    if not needed_types:
        return False
    
    # 检查现有的 typing 导入
    existing_typing_imports = set()
    typing_import_line_idx = -1
    
    for i, line in enumerate(import_lines):
        if line.startswith('from typing import'):
            typing_import_line_idx = i
            # 提取已有的导入
            imports_part = line.replace('from typing import ', '')
            existing_typing_imports.update([imp.strip() for imp in imports_part.split(',')])
    
    # 合并需要的导入
    all_needed = needed_types | existing_typing_imports
    
    if all_needed:
        new_typing_import = f"from typing import {', '.join(sorted(all_needed))}"
        
        if typing_import_line_idx >= 0:
            import_lines[typing_import_line_idx] = new_typing_import
        else:
            # 添加到合适位置
            for i, line in enumerate(import_lines):
                if not line.startswith('import '):
                    import_lines.insert(i, new_typing_import)
                    break
            else:
                import_lines.append(new_typing_import)
    
    # 重新组合文件
    new_content = '\n'.join(import_lines + [''] + other_lines)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    """主函数"""
    game_dir = Path('game')
    
    files_fixed = 0
    
    for py_file in game_dir.glob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        print(f"处理 {py_file}...")
        if fix_typing_imports(py_file):
            files_fixed += 1
            print(f"  ✓ 修复了导入")
        else:
            print(f"  - 无需修复")
    
    print(f"\n修复完成：{files_fixed} 个文件")


if __name__ == '__main__':
    main()