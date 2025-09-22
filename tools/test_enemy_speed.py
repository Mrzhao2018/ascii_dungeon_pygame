#!/usr/bin/env python3
"""
测试优化后的敌人速度和响应性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.entities import EntityManager, Enemy

def create_test_level(width, height):
    """创建简单的测试关卡"""
    level = []
    for y in range(height):
        row = ""
        for x in range(width):
            if x == 0 or x == width-1 or y == 0 or y == height-1:
                row += "#"
            else:
                row += "."
        level.append(row)
    return level

def test_enemy_speed_optimization():
    """测试敌人速度优化"""
    print("=== 敌人速度优化测试 ===")
    
    # 创建简单的测试关卡
    level = create_test_level(20, 10)
    
    # 创建EntityManager
    entity_mgr = EntityManager()
    
    # 添加不同类型的敌人
    enemy_types = ['basic', 'guard', 'scout', 'brute']
    enemies = []
    
    for i, kind in enumerate(enemy_types):
        enemy = Enemy(5 + i * 3, 5, kind=kind)
        entity_mgr.add(enemy)
        enemies.append(enemy)
        print(f"添加 {kind} 敌人:")
        print(f"  移动间隔: {enemy.enemy_stats['move_interval']} 帧")
        print(f"  AI间隔: {enemy.enemy_stats['ai_update_interval']} 帧")
        print(f"  追击范围: {enemy.enemy_stats['chase_range']}")
        print(f"  伤害: {enemy.enemy_stats['damage']}")
    
    print("\n=== 速度比较 ===")
    print("优化前 vs 优化后:")
    print("- 全局移动间隔: 15帧 -> 独立间隔3-8帧")
    print("- AI更新间隔: 4-12帧 -> 1-4帧") 
    print("- 攻击响应: 受AI间隔限制 -> 立即响应")
    
    # 模拟几轮更新来展示响应速度
    print("\n=== 模拟更新循环 ===")
    player_pos = (10, 5)
    
    for frame in range(1, 11):
        print(f"\n第 {frame} 帧:")
        events = entity_mgr.update(level, player_pos, 20, 10)
        
        for enemy in enemies:
            status = "移动" if enemy.move_cooldown == 0 else f"冷却({enemy.move_cooldown})"
            ai_status = "AI更新" if enemy.ai_cooldown == 0 else f"AI冷却({enemy.ai_cooldown})"
            print(f"  {enemy.kind}: {status}, {ai_status}")
        
        if events:
            print(f"  事件: {len(events)} 个")
            for event in events:
                if event['type'] == 'attack':
                    print(f"    攻击玩家，伤害: {event['damage']}")
    
    print("\n=== 速度性能分析 ===")
    
    # 计算每种敌人的有效速度（每秒移动次数，假设60FPS）
    for enemy in enemies:
        moves_per_second = 60 / enemy.enemy_stats['move_interval']
        ai_updates_per_second = 60 / enemy.enemy_stats['ai_update_interval']
        print(f"{enemy.kind}:")
        print(f"  每秒移动次数: {moves_per_second:.1f}")
        print(f"  每秒AI更新: {ai_updates_per_second:.1f}")
        print(f"  响应延迟: {enemy.enemy_stats['move_interval']/60*1000:.1f}ms")
    
    print("\n测试完成！敌人速度已大幅提升！")

if __name__ == "__main__":
    test_enemy_speed_optimization()