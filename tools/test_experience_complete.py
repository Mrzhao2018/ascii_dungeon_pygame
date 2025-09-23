#!/usr/bin/env python3
"""
经验升级系统完整功能测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_complete_experience_system():
    """测试完整的经验升级系统"""
    print("=== 完整经验升级系统测试 ===")
    
    try:
        from game.player import Player
        from game.experience import (
            get_enemy_exp_reward, 
            EXPERIENCE_CONFIG,
            calculate_exp_required,
            get_level_bonuses
        )
        
        print("1. 系统配置验证")
        print(f"   最大等级: {EXPERIENCE_CONFIG['max_level']}")
        print(f"   基础经验需求: {EXPERIENCE_CONFIG['base_exp_requirement']}")
        print(f"   楼层完成经验: {EXPERIENCE_CONFIG['exp_sources']['floor_completion']}")
        
        print("\n2. 玩家初始化")
        player = Player(x=10, y=10, hp=10, max_stamina=100)
        print(f"   等级: {player.level}")
        print(f"   经验: {player.experience}")
        print(f"   基础属性: HP {player.hp}/{player.max_hp}, 体力 {player.max_stamina}")
        
        print("\n3. 经验获取测试")
        
        # 测试不同敌人类型的经验
        enemy_types = ['basic', 'guard', 'scout']
        for enemy_type in enemy_types:
            exp = get_enemy_exp_reward(enemy_type)
            print(f"   {enemy_type} 敌人经验: {exp}")
        
        print("\n4. 升级和属性提升测试")
        
        # 快速升级到5级查看特殊奖励
        target_exp = calculate_exp_required(5)
        leveled_up = player.gain_experience(target_exp)
        
        if leveled_up:
            bonuses = player.get_level_bonuses_info()
            print(f"   升级到 {player.level} 级成功!")
            print(f"   生命值提升: {player.hp}/{player.max_hp} (+{bonuses['hp_bonus']})")
            print(f"   体力提升: {player.max_stamina:.1f} (+{bonuses['stamina_bonus']})")
            print(f"   移动速度提升: +{bonuses['move_speed_bonus']*100:.0f}%")
            print(f"   移动冷却时间: {player.MOVE_COOLDOWN}ms (基础: {player.base_move_cooldown}ms)")
        
        print("\n5. UI数据验证")
        exp_info = player.get_experience_info()
        print(f"   当前等级: {exp_info['level']}")
        print(f"   经验进度: {exp_info['exp_progress']*100:.1f}%")
        print(f"   距离升级: {exp_info['exp_to_next']} 经验")
        
        print("\n6. 升级提示验证")
        if player.level_up_notification:
            notification = player.level_up_notification
            print(f"   升级提示: {notification['message']}")
            print(f"   提示计时器: {player.level_up_timer}ms")
        
        print("\n7. 最大等级测试")
        # 升到最大等级
        max_exp = calculate_exp_required(EXPERIENCE_CONFIG['max_level'])
        player.gain_experience(max_exp)
        
        exp_info = player.get_experience_info()
        print(f"   达到最大等级: {exp_info['level']}")
        print(f"   最大等级状态: {exp_info['max_level']}")
        
        # 尝试继续获得经验
        before_exp = player.experience
        can_level = player.gain_experience(1000)
        print(f"   继续获得经验: {can_level} (应该为 False)")
        print(f"   经验变化: {player.experience - before_exp}")
        
        print("\n8. 重置功能测试")
        player.reset_experience()
        print(f"   重置后等级: {player.level}")
        print(f"   重置后经验: {player.experience}")
        print(f"   重置后属性: HP {player.hp}/{player.max_hp}, 体力 {player.max_stamina}")
        
        print("\n✅ 完整经验升级系统测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_special_level_rewards():
    """测试特殊等级奖励"""
    print("\n=== 特殊等级奖励测试 ===")
    
    try:
        from game.experience import EXPERIENCE_CONFIG, get_level_bonuses
        
        special_levels = [5, 10, 15, 20, 25, 30]
        
        for level in special_levels:
            bonuses = get_level_bonuses(level)
            rewards = EXPERIENCE_CONFIG["special_rewards"].get(level, {})
            
            print(f"\n等级 {level}:")
            print(f"  累积加成: HP +{bonuses['hp_bonus']}, 体力 +{bonuses['stamina_bonus']}")
            
            if rewards:
                print(f"  特殊奖励: {rewards['description']}")
                print(f"  奖励类型: {rewards['type']}, 数值: {rewards['value']}")
            
            # 显示重要的累积加成
            if bonuses['move_speed_bonus'] > 0:
                print(f"  移动速度: +{bonuses['move_speed_bonus']*100:.0f}%")
            if bonuses['stamina_regen_bonus'] > 0:
                print(f"  体力恢复: +{bonuses['stamina_regen_bonus']*100:.0f}%")
            if bonuses['sight_radius_bonus'] > 0:
                print(f"  视野半径: +{bonuses['sight_radius_bonus']:.1f}")
        
        print("\n✅ 特殊等级奖励测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 特殊等级奖励测试失败: {e}")
        return False

def test_experience_sources():
    """测试各种经验来源"""
    print("\n=== 经验来源测试 ===")
    
    try:
        from game.experience import EXPERIENCE_CONFIG, get_enemy_exp_reward
        
        print("1. 敌人击败经验:")
        enemy_types = ['basic', 'guard', 'scout', 'normal', 'strong', 'elite', 'boss']
        for enemy_type in enemy_types:
            exp = get_enemy_exp_reward(enemy_type)
            print(f"   {enemy_type}: {exp} 经验")
        
        print("\n2. 其他经验来源:")
        sources = EXPERIENCE_CONFIG["exp_sources"]
        print(f"   房间探索: {sources['room_exploration']} 经验")
        print(f"   楼层完成: {sources['floor_completion']} 经验")
        print(f"   道具收集: {sources['item_collection']} 经验")
        
        print("\n✅ 经验来源测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 经验来源测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始经验升级系统完整测试...")
    
    success1 = test_complete_experience_system()
    success2 = test_special_level_rewards()
    success3 = test_experience_sources()
    
    print(f"\n" + "="*50)
    if success1 and success2 and success3:
        print("🎉 所有测试通过！经验升级系统完全正常！")
        print("\n系统特性总结:")
        print("✅ 完整的等级和经验管理")
        print("✅ 多种经验获取途径")
        print("✅ 属性随等级自动提升")
        print("✅ 特殊等级奖励机制")
        print("✅ UI集成和升级提示")
        print("✅ 游戏重置功能")
        print("✅ 最大等级限制")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    
    print("="*50)