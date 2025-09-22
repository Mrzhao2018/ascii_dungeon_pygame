#!/usr/bin/env python3
"""
直接测试敌人类型加载
"""

import os
import sys
import json

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.entities import EntityManager, Enemy

def test_enemy_loading():
    """测试敌人加载"""
    print("=== 测试敌人类型加载 ===")
    
    # 直接读取配置文件
    with open('data/enemies.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("配置文件内容:")
    for entity in data['entities']:
        print(f"  ID={entity['id']} 类型={entity['kind']} HP={entity['hp']}")
    
    # 创建EntityManager并加载
    mgr = EntityManager()
    mgr.load_from_file('data/enemies.json')
    
    print(f"\n加载的敌人数量: {len(mgr.entities_by_id)}")
    
    for ent_id, ent in mgr.entities_by_id.items():
        if isinstance(ent, Enemy):
            print(f"敌人 {ent_id}:")
            print(f"  类型: {ent.kind}")
            print(f"  HP: {ent.hp}")
            print(f"  位置: ({ent.x}, {ent.y})")
            print(f"  追击范围: {ent.enemy_stats['chase_range']}")
            print(f"  伤害: {ent.enemy_stats['damage']}")
            print(f"  AI间隔: {ent.enemy_stats['ai_update_interval']}")

if __name__ == '__main__':
    test_enemy_loading()