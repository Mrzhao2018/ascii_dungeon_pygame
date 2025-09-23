#!/usr/bin/env python3
"""
测试经验升级系统在游戏中的集成效果
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_experience_integration():
    """测试经验系统在游戏中的集成"""
    print("=== 经验升级系统集成测试 ===")
    
    try:
        from game.player import Player
        from game.experience import get_enemy_exp_reward, EXPERIENCE_CONFIG
        
        # 创建玩家
        player = Player(x=10, y=10, hp=10, max_stamina=100)
        
        print(f"初始状态:")
        print(f"  等级: {player.level}")
        print(f"  经验: {player.experience}")
        print(f"  生命值: {player.hp}/{player.max_hp}")
        print(f"  体力: {player.stamina:.1f}/{player.max_stamina:.1f}")
        
        # 测试经验获取信息
        exp_info = player.get_experience_info()
        print(f"  经验进度: {exp_info['exp_progress']*100:.1f}%")
        print(f"  距离升级: {exp_info['exp_to_next']} 经验")
        
        # 模拟击败多个敌人
        total_enemies = 0
        print(f"\n=== 模拟战斗 ===")
        
        while player.level < 5:  # 升到5级看特殊奖励
            # 击败不同类型的敌人
            enemy_types = ['basic', 'guard', 'scout', 'basic']
            enemy_type = enemy_types[total_enemies % len(enemy_types)]
            
            exp_reward = get_enemy_exp_reward(enemy_type)
            old_level = player.level
            leveled_up = player.gain_experience(exp_reward)
            total_enemies += 1
            
            if leveled_up:
                exp_info = player.get_experience_info()
                bonuses = player.get_level_bonuses_info()
                print(f"\n🎉 击败 {enemy_type} 敌人，升级到 {player.level} 级!")
                print(f"  总经验: {player.experience}")
                print(f"  生命值: {player.hp}/{player.max_hp}")
                print(f"  体力上限: {player.max_stamina:.1f}")
                print(f"  移动速度提升: {bonuses['move_speed_bonus']*100:.0f}%")
                print(f"  体力恢复提升: {bonuses['stamina_regen_bonus']*100:.0f}%")
                
                # 检查升级提示
                if player.level_up_notification:
                    print(f"  升级提示: {player.level_up_notification['message']}")
                    
            elif total_enemies % 5 == 0:
                exp_info = player.get_experience_info()
                print(f"击败第 {total_enemies} 个敌人({enemy_type}): +{exp_reward} 经验 (等级 {player.level}, 进度 {exp_info['exp_progress']*100:.1f}%)")
        
        # 模拟楼层完成
        print(f"\n=== 模拟楼层完成 ===")
        floor_exp = EXPERIENCE_CONFIG["exp_sources"]["floor_completion"]
        old_level = player.level
        leveled_up = player.gain_experience(floor_exp)
        
        print(f"完成楼层: +{floor_exp} 经验")
        if leveled_up:
            print(f"🎉 楼层完成时升级到 {player.level} 级!")
        
        # 最终状态
        print(f"\n=== 最终状态 ===")
        exp_info = player.get_experience_info()
        bonuses = player.get_level_bonuses_info()
        
        print(f"等级: {player.level}")
        print(f"总经验: {player.experience}")
        print(f"击败敌人: {total_enemies} 个")
        print(f"生命值: {player.hp}/{player.max_hp} (+{bonuses['hp_bonus']})")
        print(f"体力: {player.stamina:.1f}/{player.max_stamina:.1f} (+{bonuses['stamina_bonus']})")
        print(f"移动冷却: {player.MOVE_COOLDOWN}ms (基础: {player.base_move_cooldown}ms)")
        print(f"体力恢复: {player.stamina_regen_per_sec:.1f}/秒 (基础: {player.base_stamina_regen:.1f}/秒)")
        
        print(f"\n累积属性加成:")
        for key, value in bonuses.items():
            if value > 0:
                unit = "%" if "bonus" in key else ""
                display_value = value * 100 if "bonus" in key else value
                print(f"  {key}: +{display_value:.1f}{unit}")
        
        print(f"\n✅ 经验系统集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_info_methods():
    """测试UI相关的信息方法"""
    print(f"\n=== UI信息方法测试 ===")
    
    try:
        from game.player import Player
        
        player = Player(x=10, y=10)
        player.gain_experience(500)  # 升到2级
        
        # 测试经验信息
        exp_info = player.get_experience_info()
        print(f"经验信息: {exp_info}")
        
        # 测试等级加成信息
        bonuses = player.get_level_bonuses_info()
        print(f"等级加成: {bonuses}")
        
        # 测试升级提示
        if player.level_up_notification:
            print(f"升级提示: {player.level_up_notification}")
        
        print(f"✅ UI信息方法测试完成")
        return True
        
    except Exception as e:
        print(f"❌ UI信息方法测试失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_experience_integration()
    success2 = test_ui_info_methods()
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！经验升级系统集成成功。")
    else:
        print(f"\n❌ 部分测试失败，请检查错误信息。")