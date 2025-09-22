#!/usr/bin/env python3
"""
游戏状态诊断脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def diagnose_exit_indicator():
    """诊断出口指示器问题"""
    
    print("=== 出口指示器诊断 ===")
    
    try:
        from game.game import Game
        
        # 创建游戏实例
        print("1. 创建游戏实例...")
        game = Game()
        
        print(f"2. 初始状态:")
        print(f"   楼层: {game.game_state.floor_number}")
        print(f"   出口位置: {game.game_state.exit_pos}")
        print(f"   地图尺寸: {game.game_state.width}x{game.game_state.height}")
        
        # 检查初始地图
        if game.game_state.level:
            x_count = sum(row.count('X') for row in game.game_state.level)
            print(f"   地图中'X'数量: {x_count}")
            
            if x_count > 0:
                print("   找到的'X'位置:")
                for y, row in enumerate(game.game_state.level):
                    for x, ch in enumerate(row):
                        if ch == 'X':
                            print(f"     ({x}, {y})")
        
        # 重新计算exit_pos
        print("\n3. 重新计算exit_pos...")
        old_exit_pos = game.game_state.exit_pos
        game.game_state.compute_exit_pos()
        new_exit_pos = game.game_state.exit_pos
        
        print(f"   原exit_pos: {old_exit_pos}")
        print(f"   新exit_pos: {new_exit_pos}")
        
        if old_exit_pos != new_exit_pos:
            print("   ⚠️  exit_pos发生了变化!")
        
        # 模拟Tab键按下
        print("\n4. 模拟Tab键测试...")
        if game.game_state.exit_pos is not None:
            ex, ey = game.game_state.exit_pos
            tile_size = game.config.tile_size
            expected_pending_target = (ex * tile_size + tile_size // 2, ey * tile_size + tile_size // 2)
            print(f"   Tab按下时应该的pending_target: {expected_pending_target}")
            
            # 测试输入处理器 - 现在Tab键在handle_keydown中处理
            import pygame
            pygame.init()
            
            # 模拟Tab键keydown事件
            tab_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
            game.input_handler.handle_keydown(tab_event)
            print(f"   输入处理后的pending_target: {game.game_state.pending_target}")
            
        else:
            print("   exit_pos为None，无法计算pending_target")
            
        # 检查是否有楼层切换状态
        print("\n5. 楼层切换状态:")
        print(f"   floor_transition: {game.game_state.floor_transition}")
        print(f"   pending_floor: {game.game_state.pending_floor}")
        
        print("\n=== 诊断完成 ===")
        
    except Exception as e:
        print(f"诊断过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    diagnose_exit_indicator()