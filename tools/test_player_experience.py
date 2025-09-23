#!/usr/bin/env python3
"""
测试玩家经验和升级系统
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.player import Player
from game.experience import get_enemy_exp_reward, EXPERIENCE_CONFIG

def test_player_experience_system():
    """测试玩家经验系统"""
    print("=== 玩家经验系统测试 ===")
    
    # 创建玩家
    player = Player(x=10, y=10, hp=10, max_stamina=100)
    
    print(f"初始状态:")
    print(f"  等级: {player.level}")
    print(f"  经验: {player.experience}")
    print(f"  生命值: {player.hp}/{player.max_hp}")
    print(f"  体力: {player.stamina:.1f}/{player.max_stamina:.1f}")
    print(f"  移动冷却: {player.MOVE_COOLDOWN}ms")
    
    # 测试经验获取和升级
    print("\n=== 模拟战斗获得经验 ===")
    
    # 击败更多敌人来触发升级
    for i in range(30):
        exp_reward = get_enemy_exp_reward("normal")
        leveled_up = player.gain_experience(exp_reward)
        
        if leveled_up:
            exp_info = player.get_experience_info()
            bonuses = player.get_level_bonuses_info()
            print(f"\n🎉 升级到 {player.level} 级!")
            print(f"  当前经验: {player.experience}")
            print(f"  生命值: {player.hp}/{player.max_hp} (+{bonuses['hp_bonus']})")
            print(f"  体力上限: {player.max_stamina:.1f} (+{bonuses['stamina_bonus']})")
            print(f"  移动速度加成: +{bonuses['move_speed_bonus']*100:.0f}%")
            if bonuses['sight_radius_bonus'] > 0:
                print(f"  视野半径: +{bonuses['sight_radius_bonus']:.1f}")
        elif i < 5 or i % 5 == 0:  # 只显示前几次和每5次的详情
            exp_info = player.get_experience_info()
            print(f"击败敌人 {i+1}: +{exp_reward} 经验 (总计: {player.experience}, 距离升级: {exp_info['exp_to_next']})")
        
        # 模拟一些时间流逝来测试升级提示
        if player.level_up_notification:
            print(f"  升级提示: {player.level_up_notification['message']}")
            
        # 如果达到5级就停止，这样可以看到特殊奖励
        if player.level >= 5:
            break
    
    print(f"\n=== 最终状态 ===")
    exp_info = player.get_experience_info()
    bonuses = player.get_level_bonuses_info()
    
    print(f"等级: {player.level}")
    print(f"总经验: {player.experience}")
    print(f"本级经验: {exp_info['exp_in_level']}")
    print(f"升级进度: {exp_info['exp_progress']*100:.1f}%")
    print(f"生命值: {player.hp}/{player.max_hp}")
    print(f"体力: {player.stamina:.1f}/{player.max_stamina:.1f}")
    print(f"体力恢复速度: {player.stamina_regen_per_sec:.1f}/秒")
    print(f"冲刺消耗: {player.sprint_cost_per_sec:.1f}/秒")
    print(f"移动冷却: {player.MOVE_COOLDOWN}ms")
    print(f"无敌时间: {player.PLAYER_IFRAMES}ms")
    
    print(f"\n累积属性加成:")
    print(f"  生命值: +{bonuses['hp_bonus']}")
    print(f"  体力: +{bonuses['stamina_bonus']}")
    print(f"  移动速度: +{bonuses['move_speed_bonus']*100:.0f}%")
    print(f"  体力恢复: +{bonuses['stamina_regen_bonus']*100:.0f}%")
    print(f"  冲刺效率: +{bonuses['sprint_cost_reduction']*100:.0f}%")
    print(f"  无敌时间: +{bonuses['iframes_bonus']*100:.0f}%")
    print(f"  视野半径: +{bonuses['sight_radius_bonus']:.1f}")

def test_reset_experience():
    """测试经验重置功能"""
    print("\n=== 经验重置测试 ===")
    
    player = Player(x=10, y=10)
    
    # 获得一些经验
    player.gain_experience(500)
    print(f"升级后: 等级 {player.level}, 经验 {player.experience}")
    
    # 重置经验
    player.reset_experience()
    print(f"重置后: 等级 {player.level}, 经验 {player.experience}")
    print(f"属性已重置: HP {player.hp}/{player.max_hp}, 体力 {player.max_stamina}")

def test_max_level():
    """测试最大等级限制"""
    print("\n=== 最大等级测试 ===")
    
    player = Player(x=10, y=10)
    
    # 给予大量经验达到最大等级
    max_exp = EXPERIENCE_CONFIG["base_exp_requirement"] * (EXPERIENCE_CONFIG["max_level"] ** EXPERIENCE_CONFIG["exp_scaling_factor"])
    player.gain_experience(int(max_exp))
    
    exp_info = player.get_experience_info()
    print(f"达到最大等级: {player.level}")
    print(f"最大等级状态: {exp_info['max_level']}")
    
    # 尝试继续获得经验
    before_exp = player.experience
    leveled_up = player.gain_experience(1000)
    print(f"继续获得经验: {leveled_up} (应该为 False)")
    print(f"经验增长: {player.experience - before_exp}")

if __name__ == "__main__":
    test_player_experience_system()
    test_reset_experience()
    test_max_level()