#!/usr/bin/env python3
"""
测试新的敌人AI系统
"""

import os
import sys

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.entities import EntityManager, Enemy
from game import utils

def test_enemy_ai():
    """测试敌人AI功能"""
    print("=== 测试敌人AI系统 ===")
    
    # 创建测试地图
    test_level = [
        "################################",
        "#..............................#",
        "#..............................#",
        "#..............................#", 
        "#......E.......................#",
        "#..............................#",
        "#..............................#",
        "#..........@...................#",
        "#..............................#",
        "#..............................#",
        "#..............................#",
        "################################",
    ]
    
    WIDTH = len(test_level[0])
    HEIGHT = len(test_level)
    
    print(f"测试地图尺寸: {WIDTH}x{HEIGHT}")
    
    # 创建实体管理器
    entity_mgr = EntityManager()
    
    # 手动创建敌人实例测试不同类型
    basic_enemy = Enemy(7, 4, hp=5, kind='basic')
    guard_enemy = Enemy(20, 4, hp=8, kind='guard') 
    scout_enemy = Enemy(25, 6, hp=3, kind='scout')
    
    entity_mgr.add(basic_enemy)
    entity_mgr.add(guard_enemy)
    entity_mgr.add(scout_enemy)
    
    # 在地图上标记敌人位置
    utils.set_tile(test_level, 7, 4, 'E')
    utils.set_tile(test_level, 20, 4, 'E')
    utils.set_tile(test_level, 25, 6, 'E')
    
    print(f"创建了 {len(entity_mgr.entities_by_id)} 个敌人")
    
    # 测试不同类型的敌人属性
    for ent_id, enemy in entity_mgr.entities_by_id.items():
        if isinstance(enemy, Enemy):
            print(f"敌人 {ent_id} ({enemy.kind}):")
            print(f"  位置: ({enemy.x}, {enemy.y})")
            print(f"  HP: {enemy.hp}")
            print(f"  追击范围: {enemy.enemy_stats['chase_range']}")
            print(f"  巡逻范围: {enemy.enemy_stats['patrol_range']}")
            print(f"  伤害: {enemy.enemy_stats['damage']}")
            print(f"  AI更新间隔: {enemy.enemy_stats['ai_update_interval']}")
    
    # 模拟几轮更新
    player_pos = (11, 7)  # 玩家位置
    
    print(f"\n玩家位置: {player_pos}")
    print("模拟5轮AI更新...")
    
    for round_num in range(5):
        print(f"\n--- 第 {round_num + 1} 轮 ---")
        
        events = entity_mgr.update(test_level, player_pos, WIDTH, HEIGHT, move_interval_frames=1)
        
        print(f"产生的事件: {len(events)}")
        for event in events:
            print(f"  {event}")
        
        print("敌人状态:")
        for ent_id, enemy in entity_mgr.entities_by_id.items():
            if isinstance(enemy, Enemy):
                print(f"  敌人 {ent_id}: 位置({enemy.x}, {enemy.y}) 状态={enemy.state} 路径长度={len(enemy.path)}")
    
    print("\n=== 测试完成 ===")

def test_pathfinding():
    """测试寻路算法"""
    print("\n=== 测试寻路算法 ===")
    
    # 创建带障碍的测试地图
    test_level = [
        "############",
        "#..........#",
        "#..####....#",
        "#..#  #....#",
        "#..#  #....#",
        "#..####....#",
        "#..........#",
        "############",
    ]
    
    WIDTH = len(test_level[0])
    HEIGHT = len(test_level)
    
    entity_mgr = EntityManager()
    
    # 测试寻路
    start = (1, 1)
    goal = (10, 6)
    
    path = entity_mgr._find_path(start, goal, test_level, WIDTH, HEIGHT)
    
    print(f"从 {start} 到 {goal} 的路径:")
    print(f"路径长度: {len(path)}")
    print(f"路径: {path}")
    
    # 可视化路径
    print("\n路径可视化:")
    visual_map = [list(row) for row in test_level]
    
    for i, (x, y) in enumerate(path):
        if visual_map[y][x] == '.':
            visual_map[y][x] = str(i % 10)
    
    visual_map[start[1]][start[0]] = 'S'
    visual_map[goal[1]][goal[0]] = 'G'
    
    for row in visual_map:
        print(''.join(row))

if __name__ == '__main__':
    test_enemy_ai()
    test_pathfinding()