#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.experience import *

print("=== 经验升级系统测试 ===")

for level in [1, 5, 10, 15, 20, 25, 30, 50]:
    total_exp = calculate_exp_required(level)
    next_exp = calculate_exp_to_next_level(level)
    bonuses = get_level_bonuses(level)
    
    print(f"\n等级 {level}:")
    print(f"  总经验需求: {total_exp}")
    print(f"  升级经验: {next_exp}")
    print(f"  生命值加成: +{bonuses['hp_bonus']}")
    print(f"  体力加成: +{bonuses['stamina_bonus']}")
    print(f"  视野加成: +{bonuses['sight_radius_bonus']:.1f}")
    print(f"  移动速度加成: +{bonuses['move_speed_bonus']*100:.0f}%")