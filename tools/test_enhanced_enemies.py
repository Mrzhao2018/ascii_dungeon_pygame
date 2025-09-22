#!/usr/bin/env python3
"""
在真实游戏环境中测试敌人AI
"""

import os
import sys

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import Game

def test_enhanced_enemies_in_game():
    """测试增强敌人在游戏中的表现"""
    print("=== 测试增强敌人在游戏中的表现 ===")
    
    # 备份原始敌人文件
    import shutil
    backup_path = "data/enemies_backup.json"
    if os.path.exists("data/enemies.json"):
        shutil.copy("data/enemies.json", backup_path)
        print("已备份原始enemies.json")
    
    # 复制增强敌人文件
    if os.path.exists("data/enemies_enhanced.json"):
        shutil.copy("data/enemies_enhanced.json", "data/enemies.json")
        print("已应用增强敌人配置")
    
    try:
        # 创建游戏实例
        game = Game()
        
        print(f"游戏创建成功")
        print(f"地图尺寸: {game.game_state.width} x {game.game_state.height}")
        print(f"敌人数量: {len(game.entity_mgr.entities_by_id) if game.entity_mgr else 0}")
        
        # 检查敌人类型分布
        if game.entity_mgr:
            enemy_types = {}
            for ent_id, ent in game.entity_mgr.entities_by_id.items():
                if hasattr(ent, 'kind'):
                    enemy_types[ent.kind] = enemy_types.get(ent.kind, 0) + 1
            
            print(f"敌人类型分布: {enemy_types}")
            
            # 显示每个敌人的详细信息
            for ent_id, ent in game.entity_mgr.entities_by_id.items():
                if hasattr(ent, 'kind'):
                    print(f"敌人 {ent_id}: {ent.kind} HP={ent.hp} 位置=({ent.x}, {ent.y}) 追击范围={ent.enemy_stats['chase_range']}")
        
        # 模拟几轮游戏循环
        print("\n模拟游戏更新...")
        for i in range(10):
            if game.entity_mgr:
                player_pos = (game.player.x, game.player.y)
                events = game.entity_mgr.update(
                    game.game_state.level, 
                    player_pos, 
                    game.game_state.width, 
                    game.game_state.height,
                    move_interval_frames=1  # 加速更新
                )
                
                if events:
                    print(f"轮次 {i+1}: 产生 {len(events)} 个事件")
                    for event in events:
                        print(f"  {event}")
        
        print("✅ 增强敌人在游戏中运行正常")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 恢复原始敌人文件
        if os.path.exists(backup_path):
            shutil.copy(backup_path, "data/enemies.json")
            os.remove(backup_path)
            print("已恢复原始enemies.json")

if __name__ == '__main__':
    test_enhanced_enemies_in_game()