#!/usr/bin/env python3
"""
Automatic code documentation generator
Generates comprehensive documentation for the game codebase
"""
import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json


class CodeAnalyzer:
    """Analyzes Python source code to extract documentation information"""
    
    def __init__(self):
        self.modules = {}
        self.classes = {}
        self.functions = {}
        self.constants = {}
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            module_info = {
                'file_path': str(file_path),
                'docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': [],
                'constants': [],
                'imports': []
            }
            
            for node in ast.walk(tree):
                try:
                    if isinstance(node, ast.ClassDef):
                        class_info = self._analyze_class(node)
                        module_info['classes'].append(class_info)
                    
                    elif isinstance(node, ast.FunctionDef):
                        # Check if this is a top-level function (not in a class)
                        if not self._is_method(node, tree):
                            func_info = self._analyze_function(node)
                            module_info['functions'].append(func_info)
                    
                    elif isinstance(node, ast.Assign):
                        # Look for module-level constants (ALL_CAPS variables)
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id.isupper():
                                try:
                                    const_info = {
                                        'name': target.id,
                                        'line': node.lineno,
                                        'value': self._get_node_value(node.value)
                                    }
                                    module_info['constants'].append(const_info)
                                except Exception:
                                    const_info = {
                                        'name': target.id,
                                        'line': node.lineno,
                                        'value': '<unknown>'
                                    }
                                    module_info['constants'].append(const_info)
                    
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        import_info = self._analyze_import(node)
                        if import_info:
                            module_info['imports'].append(import_info)
                except Exception:
                    # Skip problematic nodes
                    continue
            
            return module_info
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method (inside a class)"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return True
        return False
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class definition"""
        class_info = {
            'name': node.name,
            'line': node.lineno,
            'docstring': ast.get_docstring(node),
            'methods': [],
            'attributes': [],
            'bases': [self._get_node_name(base) for base in node.bases]
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function(item)
                method_info['is_method'] = True
                
                # Check for static/class methods with error handling
                try:
                    method_info['is_static'] = any(isinstance(d, ast.Name) and d.id == 'staticmethod' for d in item.decorator_list)
                    method_info['is_class'] = any(isinstance(d, ast.Name) and d.id == 'classmethod' for d in item.decorator_list)
                except Exception:
                    method_info['is_static'] = False
                    method_info['is_class'] = False
                
                class_info['methods'].append(method_info)
            
            elif isinstance(item, ast.Assign):
                # Class attributes
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        try:
                            attr_info = {
                                'name': target.id,
                                'line': item.lineno,
                                'value': self._get_node_value(item.value)
                            }
                            class_info['attributes'].append(attr_info)
                        except Exception:
                            attr_info = {
                                'name': target.id,
                                'line': item.lineno,
                                'value': '<unknown>'
                            }
                            class_info['attributes'].append(attr_info)
        
        return class_info
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze a function definition"""
        func_info = {
            'name': node.name,
            'line': node.lineno,
            'docstring': ast.get_docstring(node),
            'args': [],
            'returns': None,
            'decorators': []
        }
        
        # Analyze decorators with error handling
        for decorator in node.decorator_list:
            try:
                decorator_name = self._get_node_name(decorator)
                if decorator_name:
                    func_info['decorators'].append(decorator_name)
            except Exception:
                func_info['decorators'].append('<decorator>')
        
        # Analyze arguments
        for arg in node.args.args:
            try:
                arg_info = {
                    'name': arg.arg,
                    'annotation': self._get_node_name(arg.annotation) if arg.annotation else None
                }
                func_info['args'].append(arg_info)
            except Exception:
                arg_info = {
                    'name': arg.arg,
                    'annotation': None
                }
                func_info['args'].append(arg_info)
        
        # Return type annotation
        if node.returns:
            func_info['returns'] = self._get_node_name(node.returns)
        
        return func_info
    
    def _analyze_import(self, node) -> Dict[str, Any]:
        """Analyze import statements"""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names],
                'line': node.lineno
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [alias.name for alias in node.names],
                'line': node.lineno
            }
    
    def _get_node_name(self, node) -> str:
        """Get string representation of a node"""
        if node is None:
            return None
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_node_name(node.value)
            return f"{value_name}.{node.attr}" if value_name else node.attr
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Subscript):
            value_name = self._get_node_name(node.value)
            return f"{value_name}[...]" if value_name else "Subscript"
        elif isinstance(node, ast.List):
            return "List"
        elif isinstance(node, ast.Dict):
            return "Dict"
        elif isinstance(node, ast.Call):
            func_name = self._get_node_name(node.func)
            return f"{func_name}(...)" if func_name else "Call"
        elif isinstance(node, ast.JoinedStr):
            return "f-string"
        elif isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare)):
            return f"<{type(node).__name__}>"
        else:
            return str(type(node).__name__)
    
    def _get_node_value(self, node) -> str:
        """Get value representation of a node"""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_node_name(node.value)
            return f"{value_name}.{node.attr}" if value_name else node.attr
        elif isinstance(node, ast.List):
            if len(node.elts) <= 3:
                elements = [self._get_node_value(elt) for elt in node.elts]
                return f"[{', '.join(elements)}]"
            else:
                return f"[{len(node.elts)} items]"
        elif isinstance(node, ast.Dict):
            if len(node.keys) <= 3:
                pairs = []
                for k, v in zip(node.keys, node.values):
                    key_str = self._get_node_value(k) if k else "None"
                    val_str = self._get_node_value(v)
                    pairs.append(f"{key_str}: {val_str}")
                return f"{{{', '.join(pairs)}}}"
            else:
                return f"{{{len(node.keys)} items}}"
        elif isinstance(node, ast.Call):
            func_name = self._get_node_name(node.func)
            return f"{func_name}(...)" if func_name else "function_call(...)"
        elif isinstance(node, ast.JoinedStr):
            return "f'...'"
        elif isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare)):
            return f"<{type(node).__name__.lower()}_expression>"
        else:
            return f"<{type(node).__name__}>"


class DocumentationGenerator:
    """Generates documentation from analyzed code"""
    
    def __init__(self):
        self.analyzer = CodeAnalyzer()
    
    def generate_docs(self, source_dir: Path, output_file: Path):
        """Generate documentation for all Python files in source directory"""
        
        # Find all Python files
        python_files = list(source_dir.rglob("*.py"))
        
        # Analyze each file
        modules = {}
        for file_path in python_files:
            relative_path = file_path.relative_to(source_dir)
            module_info = self.analyzer.analyze_file(file_path)
            if module_info:
                modules[str(relative_path)] = module_info
        
        # Generate documentation
        doc_content = self._generate_markdown(modules)
        
        # Write to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"Documentation generated: {output_file}")
        return doc_content
    
    def _generate_markdown(self, modules: Dict[str, Any]) -> str:
        """Generate Markdown documentation"""
        lines = []
        
        # Title
        lines.append("# 游戏代码文档")
        lines.append("")
        lines.append("自动生成的代码文档")
        lines.append("")
        
        # Table of contents
        lines.append("## 目录")
        lines.append("")
        for module_path in sorted(modules.keys()):
            module_name = Path(module_path).stem
            lines.append(f"- [{module_name}](#{module_name.replace('_', '-')})")
        lines.append("")
        
        # Module documentation
        for module_path in sorted(modules.keys()):
            module = modules[module_path]
            self._generate_module_docs(lines, module_path, module)
        
        return "\n".join(lines)
    
    def _generate_module_docs(self, lines: List[str], module_path: str, module: Dict[str, Any]):
        """Generate documentation for a single module"""
        module_name = Path(module_path).stem
        
        lines.append(f"## {module_name}")
        lines.append("")
        lines.append(f"**文件:** `{module_path}`")
        lines.append("")
        
        if module['docstring']:
            lines.append("**描述:**")
            lines.append("")
            lines.append(module['docstring'])
            lines.append("")
        
        # Imports
        if module['imports']:
            lines.append("### 导入")
            lines.append("")
            for imp in module['imports']:
                if imp['type'] == 'import':
                    lines.append(f"- `import {', '.join(imp['modules'])}`")
                else:
                    names = ', '.join(imp['names'])
                    lines.append(f"- `from {imp['module']} import {names}`")
            lines.append("")
        
        # Constants
        if module['constants']:
            lines.append("### 常量")
            lines.append("")
            for const in module['constants']:
                lines.append(f"- **{const['name']}** = `{const['value']}`")
            lines.append("")
        
        # Classes
        if module['classes']:
            lines.append("### 类")
            lines.append("")
            for cls in module['classes']:
                self._generate_class_docs(lines, cls)
        
        # Functions
        if module['functions']:
            lines.append("### 函数")
            lines.append("")
            for func in module['functions']:
                self._generate_function_docs(lines, func)
        
        lines.append("---")
        lines.append("")
    
    def _generate_class_docs(self, lines: List[str], cls: Dict[str, Any]):
        """Generate documentation for a class"""
        lines.append(f"#### {cls['name']}")
        lines.append("")
        
        if cls['bases']:
            base_names = ', '.join(cls['bases'])
            lines.append(f"**继承:** `{base_names}`")
            lines.append("")
        
        if cls['docstring']:
            lines.append(cls['docstring'])
            lines.append("")
        
        # Attributes
        if cls['attributes']:
            lines.append("**属性:**")
            lines.append("")
            for attr in cls['attributes']:
                lines.append(f"- `{attr['name']}` = `{attr['value']}`")
            lines.append("")
        
        # Methods
        if cls['methods']:
            lines.append("**方法:**")
            lines.append("")
            for method in cls['methods']:
                method_type = ""
                if method.get('is_static'):
                    method_type = " (静态)"
                elif method.get('is_class'):
                    method_type = " (类方法)"
                
                args = ', '.join(arg['name'] for arg in method['args'])
                lines.append(f"- `{method['name']}({args})`{method_type}")
                
                if method['docstring']:
                    # Indent the docstring
                    doc_lines = method['docstring'].split('\n')
                    for doc_line in doc_lines:
                        lines.append(f"  {doc_line.strip()}")
                lines.append("")
    
    def _generate_function_docs(self, lines: List[str], func: Dict[str, Any]):
        """Generate documentation for a function"""
        args = []
        for arg in func['args']:
            arg_str = arg['name']
            if arg['annotation']:
                arg_str += f": {arg['annotation']}"
            args.append(arg_str)
        
        signature = f"{func['name']}({', '.join(args)})"
        if func['returns']:
            signature += f" -> {func['returns']}"
        
        lines.append(f"#### {signature}")
        lines.append("")
        
        if func['docstring']:
            lines.append(func['docstring'])
        else:
            lines.append("*无文档*")
        
        lines.append("")


def main():
    """Main documentation generation script"""
    if len(sys.argv) > 1:
        source_dir = Path(sys.argv[1])
    else:
        source_dir = Path("game")
    
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        output_file = Path("docs/code_documentation.md")
    
    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return
    
    generator = DocumentationGenerator()
    generator.generate_docs(source_dir, output_file)
    
    print(f"\nDocumentation generated successfully!")
    print(f"Source: {source_dir}")
    print(f"Output: {output_file}")
    
    # Also generate JSON for programmatic use
    json_output = output_file.with_suffix('.json')
    
    # Re-analyze for JSON export
    python_files = list(source_dir.rglob("*.py"))
    modules = {}
    analyzer = CodeAnalyzer()
    
    for file_path in python_files:
        relative_path = file_path.relative_to(source_dir)
        module_info = analyzer.analyze_file(file_path)
        if module_info:
            modules[str(relative_path)] = module_info
    
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(modules, f, indent=2, ensure_ascii=False)
    
    print(f"JSON export: {json_output}")


if __name__ == '__main__':
    main()