#!/usr/bin/env python3
"""
实时监控游戏状态的调试工具
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def monitor_game_state():
    """监控游戏中的exit_pos和Tab指示器状态"""
    
    print("=== 游戏状态实时监控 ===")
    print("按 Ctrl+C 退出监控")
    print("")
    
    try:
        from game.game import Game
        
        # 创建游戏实例
        game = Game()
        
        # 监控循环
        frame_count = 0
        while True:
            time.sleep(0.1)  # 100ms间隔
            frame_count += 1
            
            if frame_count % 10 == 0:  # 每秒输出一次
                print(f"\n--- 帧 {frame_count} ---")
                print(f"楼层: {game.game_state.floor_number}")
                print(f"出口位置 (exit_pos): {game.game_state.exit_pos}")
                print(f"目标指示器 (pending_target): {game.game_state.pending_target}")
                print(f"地图尺寸: {game.game_state.width}x{game.game_state.height}")
                
                # 检查地图中是否确实有'X'
                if game.game_state.level:
                    x_count = sum(row.count('X') for row in game.game_state.level)
                    print(f"地图中'X'的数量: {x_count}")
                    
                    if x_count > 0 and game.game_state.exit_pos is None:
                        print("⚠️  警告: 地图有'X'但exit_pos为None!")
                    elif x_count == 0 and game.game_state.exit_pos is not None:
                        print("⚠️  警告: 地图无'X'但exit_pos不为None!")
                        
                # 检查是否在楼层切换中
                if game.game_state.floor_transition:
                    print(f"楼层切换中: {game.game_state.floor_transition}")
                    
                if game.game_state.pending_floor:
                    print(f"待处理楼层: {game.game_state.pending_floor}")
                    
    except KeyboardInterrupt:
        print("\n监控已停止")
    except Exception as e:
        print(f"监控出错: {e}")

if __name__ == '__main__':
    monitor_game_state()