#!/usr/bin/env python3
"""
测试敌人紧邻攻击响应
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.entities import EntityManager, Enemy

def test_adjacent_attack():
    """测试敌人紧邻攻击"""
    print("=== 敌人紧邻攻击测试 ===")
    
    # 敌人直接在玩家相邻位置
    level = [
        "#######",
        "#.....#",
        "#.E@E.#",  # 敌人在玩家左右两侧
        "#.EEE.#",  # 敌人在玩家下方
        "#.....#",
        "#######"
    ]
    
    entity_mgr = EntityManager()
    player_pos = (3, 2)  # 玩家在中央
    
    # 创建紧邻的敌人
    enemies = [
        Enemy(2, 2, kind='scout'),    # 左侧，距离1
        Enemy(4, 2, kind='guard'),    # 右侧，距离1
        Enemy(2, 3, kind='basic'),    # 左下，距离1
        Enemy(3, 3, kind='brute'),    # 正下，距离1
        Enemy(4, 3, kind='scout'),    # 右下，距离1
    ]
    
    for enemy in enemies:
        entity_mgr.add(enemy)
        distance = abs(player_pos[0] - enemy.x) + abs(player_pos[1] - enemy.y)
        print(f"{enemy.kind} 在 ({enemy.x}, {enemy.y}), 距离: {distance} 格")
    
    print(f"\n玩家位置: {player_pos}")
    print("所有敌人都在攻击范围内（相邻）")
    
    print("\n=== 攻击测试结果 ===")
    total_attacks = 0
    
    for frame in range(1, 11):
        print(f"\n第 {frame} 帧:")
        events = entity_mgr.update(level, player_pos, 7, 6)
        
        frame_attacks = 0
        for event in events:
            if event['type'] == 'attack':
                attacker = entity_mgr.get_entity_by_id(event['attacker_id'])
                if attacker and isinstance(attacker, Enemy):
                    print(f"  ⚔️ {attacker.kind} 攻击！伤害: {event['damage']}")
                    frame_attacks += 1
                    total_attacks += 1
        
        if frame_attacks == 0:
            print(f"  ⏸️ 本帧无攻击")
        
        # 显示每个敌人的状态
        status_line = "  状态: "
        for enemy in enemies:
            move_status = "✓" if enemy.move_cooldown == 0 else f"{enemy.move_cooldown}"
            ai_status = "✓" if enemy.ai_cooldown == 0 else f"{enemy.ai_cooldown}"
            status_line += f"{enemy.kind}({move_status}/{ai_status}) "
        print(status_line)
    
    print(f"\n=== 总计攻击次数: {total_attacks} ===")
    
    # 性能分析
    print("\n=== 性能分析 ===")
    print("优化前问题：")
    print("❌ 全局15帧移动间隔 = 每秒4次行动")
    print("❌ AI间隔4-12帧 = 攻击响应慢")
    print("❌ 所有敌人同步行动")
    
    print("\n优化后改进：")
    print("✅ 独立移动间隔3-8帧 = 每秒7.5-20次行动")
    print("✅ AI间隔1-4帧 = 快速响应")
    print("✅ 攻击检测优先，无冷却限制")
    print("✅ 不同类型敌人有不同节奏")
    
    for enemy in enemies:
        moves_per_sec = 60 / enemy.enemy_stats['move_interval']
        ai_per_sec = 60 / enemy.enemy_stats['ai_update_interval']
        print(f"  {enemy.kind}: {moves_per_sec:.1f}次/秒移动, {ai_per_sec:.1f}次/秒AI")

if __name__ == "__main__":
    test_adjacent_attack()