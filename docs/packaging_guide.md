# 打包指南（Windows）

本文档介绍如何在 Windows 上将本项目打包为可执行文件（.exe）。

## 前置条件

- 已安装 Python 3.10+（建议与开发时一致）
- 已安装 pip 并可正常访问 PyPI
- 在仓库根目录创建并激活虚拟环境（可选但推荐）

```powershell
# 可选：创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 安装 PyInstaller
pip install pyinstaller
```

## 一键打包脚本（推荐）

提供了 PowerShell 脚本 `tools/package.ps1` 用于简化打包：

```powershell
# 缺省模式：单文件（onefile），控制台窗口模式
powershell -ExecutionPolicy Bypass -File tools/package.ps1

# 单目录（onedir）模式：
powershell -ExecutionPolicy Bypass -File tools/package.ps1 -Mode onedir

# 隐藏控制台窗口（窗口化模式）：
powershell -ExecutionPolicy Bypass -File tools/package.ps1 -Windowed
```

打包完成后输出位于 `dist/`：

- onefile: `dist/ascii-dungeon.exe`
- onedir: `dist/ascii-dungeon/`

脚本默认把以下资源一并打包：

- `data/`（地图、敌人、对话等数据）
- `fonts/`（字体）
- `docs/`（文档，可选）
- `game.json`（配置）

## 手动命令

不使用脚本时，可直接运行：

```powershell
pyinstaller --noconfirm --clean --name ascii-dungeon --onefile --console \
  --add-data "data;data" \
  --add-data "fonts;fonts" \
  --add-data "docs;docs" \
  --add-data "game.json;." \
  main.py
```

注意：在 Windows 上 `--add-data` 的分隔符是 `;`；在 macOS/Linux 上是 `:`。

## 冻结环境路径注意事项（_MEIPASS）

项目当前对资源路径使用了相对 `__file__` 的定位，例如：

- `game/utils.py` 使用 `os.path.join(os.path.dirname(__file__), '..', 'data', ...)`

PyInstaller 打包后，这些路径仍然可行，因为我们通过 `--add-data` 保持了相对目录结构（`data/`, `fonts/`, `docs/`）。如果未来需要在运行时检测 `_MEIPASS`，可以在一个集中工具处做类似：

```python
import sys, os

def resource_path(*parts: str) -> str:
    base = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    return os.path.join(base, *parts)
```

然后将原先 `os.path.join(os.path.dirname(__file__), '..', 'data', 'xxx')` 替换为 `resource_path('data', 'xxx')`。

## 常见问题

- 字体/数据没被带上：确认 `--add-data` 是否包含；或检查脚本 `tools/package.ps1` 是否被修改。
- 双击运行没有窗口：如果使用了 `--windowed`，请检查是否有异常日志；控制台输出被隐藏，建议先用 `--console` 调试。
- 防病毒误报：尝试改用 onedir 模式；或对生成的 exe 做签名（超出本文档范围）。
