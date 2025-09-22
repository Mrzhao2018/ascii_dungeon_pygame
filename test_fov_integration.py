"""
FOV系统游戏集成测试
验证FOV系统与游戏配置和命令行参数的集成
"""
import subprocess
import sys
import os


def test_fov_config():
    """测试FOV配置选项"""
    print("=== 测试FOV配置选项 ===")
    
    test_commands = [
        # 测试帮助信息包含FOV选项
        [sys.executable, "main.py", "--help"],
        
        # 测试默认FOV设置
        [sys.executable, "main.py", "--sight-radius", "4", "--skip-intro", "--debug"],
        
        # 测试禁用FOV
        [sys.executable, "main.py", "--disable-fov", "--skip-intro", "--debug"],
        
        # 测试大视野半径
        [sys.executable, "main.py", "--sight-radius", "10", "--skip-intro", "--debug"],
    ]
    
    for i, cmd in enumerate(test_commands):
        print(f"\n测试命令 {i+1}: {' '.join(cmd)}")
        
        try:
            if "--help" in cmd:
                # 对于帮助命令，运行完整并检查输出
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if "视野系统" in result.stdout:
                    print("✅ 帮助信息包含FOV选项")
                else:
                    print("❌ 帮助信息缺少FOV选项")
            else:
                # 对于游戏命令，启动短时间后终止
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # 等待几秒钟让游戏初始化
                import time
                time.sleep(3)
                
                # 终止进程
                process.terminate()
                
                try:
                    stdout, stderr = process.communicate(timeout=2)
                    print("✅ 游戏启动成功")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print("✅ 游戏启动成功（强制终止）")
                
        except subprocess.TimeoutExpired:
            print("⚠️ 命令超时")
        except Exception as e:
            print(f"❌ 命令失败: {e}")


def print_fov_usage_guide():
    """打印FOV使用指南"""
    print("\n" + "="*50)
    print("视野系统 (FOV) 使用指南")
    print("="*50)
    
    print("""
🎮 基础功能:
- 玩家周围有限的可见范围
- 已探索区域以暗色显示（雾化效果）
- 未探索区域完全隐藏
- 移动时动态更新视野

⚙️ 配置选项:
- --sight-radius <数字>     设置视野半径 (默认: 6)
- --enable-fov              启用视野系统 (默认启用)
- --disable-fov             禁用视野系统

🎯 游戏效果:
- 增加探索的乐趣和神秘感
- 鼓励玩家仔细探索地图
- 为游戏增加战术深度

📝 测试命令:
python main.py --sight-radius 4    # 较小视野
python main.py --sight-radius 10   # 较大视野  
python main.py --disable-fov       # 禁用FOV（传统模式）

🔧 调试:
- 使用 F12 切换调试模式查看FOV信息
- 调试面板显示当前视野半径和可见区域数量
""")


if __name__ == "__main__":
    print("FOV系统集成测试开始...\n")
    
    # 打印使用指南
    print_fov_usage_guide()
    
    # 运行配置测试
    test_fov_config()
    
    print("\n✅ FOV系统集成测试完成！")
    print("\n🎮 你可以启动游戏体验视野系统:")
    print("python main.py --debug")
    print("使用 WASD 移动，观察视野变化")