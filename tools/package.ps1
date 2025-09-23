Param(
    [ValidateSet('onedir','onefile')]
    [string]$Mode = 'onefile',
    [switch]$Windowed
)

# Purpose: Package the game with PyInstaller on Windows PowerShell
# Usage examples:
#   powershell -ExecutionPolicy Bypass -File tools/package.ps1
#   powershell -ExecutionPolicy Bypass -File tools/package.ps1 -Mode onedir -Windowed

$ErrorActionPreference = 'Stop'

# Ensure we run from repo root (the script is in tools/)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir '..')

$Name = 'ascii-dungeon'
$Main = 'main.py'

# Build common args
$Args = @('--noconfirm', '--clean', '--name', $Name)

if ($Windowed) { $Args += '--windowed' } else { $Args += '--console' }
if ($Mode -eq 'onefile') { $Args += '--onefile' }

# Add data folders/files (Windows uses ';' as separator in --add-data)
$Datas = @(
    'data;data',
    'fonts;fonts',
    'docs;docs',
    'game.json;.'
)
foreach ($d in $Datas) { $Args += @('--add-data', $d) }

# Entry
$Args += $Main

Write-Host "Running: pyinstaller $($Args -join ' ')" -ForegroundColor Cyan
pyinstaller @Args

Write-Host "\nDone. Output: .\\dist\\$Name (onedir) or .\\dist\\$Name.exe (onefile)" -ForegroundColor Green
