#!/usr/bin/env python3
"""
测试楼层切换时的出口指示器行为
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_floor_transition_exit():
    """测试楼层切换时的出口指示器"""
    
    print("=== 楼层切换出口指示器测试 ===")
    
    try:
        from game.game import Game
        
        # 创建游戏实例
        print("1. 创建游戏实例...")
        game = Game()
        
        print("2. 初始状态:")
        print(f"   楼层: {game.game_state.floor_number}")
        print(f"   出口位置: {game.game_state.exit_pos}")
        
        if game.game_state.level:
            x_count = sum(row.count('X') for row in game.game_state.level)
            print(f"   地图中'X'数量: {x_count}")
        
        # 模拟楼层切换
        print("\n3. 启动楼层切换...")
        new_floor = 2
        gen_seed = 54321
        
        # 启动楼层切换
        game.game_state.start_floor_transition(new_floor, gen_seed)
        
        print(f"   切换启动后exit_pos: {game.game_state.exit_pos}")
        print(f"   floor_transition: {game.game_state.floor_transition}")
        print(f"   pending_floor: {game.game_state.pending_floor}")
        
        # 等待楼层切换完成
        print("\n4. 处理楼层切换...")
        
        # 直接模拟切换完成
        if game.game_state.floor_transition:
            # 让切换时间倒计时完成
            transition_completed = game.game_state.update_floor_transition(1200)  # 超过1100ms
            print(f"   切换完成状态: {transition_completed}")
            print(f"   剩余floor_transition: {game.game_state.floor_transition}")
            
        # 处理楼层切换
        level, entity_mgr, npcs, new_pos = game.floor_manager.process_floor_transition()
        
        if level is not None:
            print("   楼层切换处理成功")
            print(f"   新楼层: {game.game_state.floor_number}")
            print(f"   新exit_pos: {game.game_state.exit_pos}")
            
            if game.game_state.level:
                x_count = sum(row.count('X') for row in game.game_state.level)
                print(f"   新地图中'X'数量: {x_count}")
                
            # 手动重新计算exit_pos确认
            old_exit = game.game_state.exit_pos
            game.game_state.compute_exit_pos()
            new_exit = game.game_state.exit_pos
            
            print(f"   重新计算后exit_pos: {new_exit}")
            
            if old_exit != new_exit:
                print("   ⚠️  重新计算后exit_pos发生变化!")
                
        else:
            print("   楼层切换处理失败")
            
        print("\n5. 测试Tab键指示器...")
        if game.game_state.exit_pos is not None:
            ex, ey = game.game_state.exit_pos
            tile_size = game.config.tile_size
            expected_target = (ex * tile_size + tile_size // 2, ey * tile_size + tile_size // 2)
            print(f"   预期pending_target: {expected_target}")
            print("   ✅ 出口指示器应该可以工作")
        else:
            print("   ❌ exit_pos为None，指示器不会工作")
            
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_floor_transition_exit()