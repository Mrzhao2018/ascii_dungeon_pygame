"""
经验升级系统设计文档

## 核心概念

### 1. 等级系统
- 起始等级：1
- 最大等级：50
- 升级公式：需要经验 = 100 * (level^1.5) 

### 2. 经验获取
- 击败敌人：基础经验 10-50（根据敌人类型）
- 探索房间：每个新房间 5 经验
- 到达下一层：25 经验
- 收集道具：部分道具提供经验奖励

### 3. 属性提升
每次升级玩家获得：
- 生命值上限 +2
- 最大体力 +5
- 攻击力 +1（如果有攻击系统）
- 视野半径 +0.2（每5级提升一次）

### 4. 特殊等级奖励
- 5级：移动速度提升 10%
- 10级：体力恢复速度提升 20%
- 15级：冲刺消耗降低 15%
- 20级：无敌时间延长 20%
- 25级：视野半径 +1
- 30级：移动速度再提升 10%

### 5. UI 显示
- 当前等级和经验条
- 升级时的特效和提示
- 属性面板显示当前属性值

### 6. 数据持久化
- 等级和经验在游戏重新开始时重置
- 可选：添加成就系统记录最高等级
"""

# 经验升级系统配置
EXPERIENCE_CONFIG = {
    "max_level": 50,
    "base_exp_requirement": 50,  # 从100减少到50，降低经验需求
    "exp_scaling_factor": 1.3,   # 从1.5减少到1.3，降低升级难度增长
    
    # 经验来源
    "exp_sources": {
        "enemy_kill": {"min": 15, "max": 75},  # 增加敌人经验奖励
        "room_exploration": 8,                 # 从5增加到8
        "floor_completion": 40,                # 从25增加到40
        "item_collection": 5,                  # 从3增加到5
    },
    
    # 每级属性提升
    "level_bonuses": {
        "hp_per_level": 2,
        "stamina_per_level": 5,
        "attack_per_level": 1,
        "sight_radius_every_n_levels": 5,
        "sight_radius_bonus": 0.2,
    },
    
    # 特殊等级奖励
    "special_rewards": {
        5: {"type": "move_speed", "value": 0.1, "description": "移动速度提升 10%"},
        10: {"type": "stamina_regen", "value": 0.2, "description": "体力恢复速度提升 20%"},
        15: {"type": "sprint_cost", "value": -0.15, "description": "冲刺消耗降低 15%"},
        20: {"type": "iframes", "value": 0.2, "description": "无敌时间延长 20%"},
        25: {"type": "sight_radius", "value": 1, "description": "视野半径 +1"},
        30: {"type": "move_speed", "value": 0.1, "description": "移动速度再提升 10%"},
    }
}


def calculate_exp_required(level):
    """计算指定等级需要的总经验"""
    if level <= 1:
        return 0
    config = EXPERIENCE_CONFIG
    return int(config["base_exp_requirement"] * (level ** config["exp_scaling_factor"]))


def calculate_exp_to_next_level(current_level):
    """计算升到下一级需要的经验"""
    if current_level >= EXPERIENCE_CONFIG["max_level"]:
        return 0
    return calculate_exp_required(current_level + 1) - calculate_exp_required(current_level)


def get_enemy_exp_reward(enemy_type="normal"):
    """根据敌人类型计算经验奖励"""
    config = EXPERIENCE_CONFIG["exp_sources"]["enemy_kill"]
    base_exp = config["min"]
    
    # 根据敌人类型调整经验值
    multipliers = {
        "basic": 1.0,      # 15 经验
        "guard": 1.2,      # 18 经验  
        "scout": 0.8,      # 12 经验
        "brute": 1.6,      # 24 经验（更耐打）
        "normal": 1.0,     # 15 经验
        "strong": 1.5,     # 22 经验
        "elite": 2.0,      # 30 经验
        "boss": 3.0,       # 45 经验
    }
    
    multiplier = multipliers.get(enemy_type, 1.0)
    return int(base_exp * multiplier)


def get_level_bonuses(level):
    """获取指定等级的累积属性加成"""
    config = EXPERIENCE_CONFIG["level_bonuses"]
    
    bonuses = {
        "hp_bonus": (level - 1) * config["hp_per_level"],
        "stamina_bonus": (level - 1) * config["stamina_per_level"],
        "attack_bonus": (level - 1) * config["attack_per_level"],
        "sight_radius_bonus": (level - 1) // config["sight_radius_every_n_levels"] * config["sight_radius_bonus"],
        "move_speed_bonus": 0.0,
        "stamina_regen_bonus": 0.0,
        "sprint_cost_reduction": 0.0,
        "iframes_bonus": 0.0,
    }
    
    # 添加特殊等级奖励
    special_rewards = EXPERIENCE_CONFIG["special_rewards"]
    for reward_level, reward in special_rewards.items():
        if level >= reward_level:
            if reward["type"] == "move_speed":
                bonuses["move_speed_bonus"] += reward["value"]
            elif reward["type"] == "stamina_regen":
                bonuses["stamina_regen_bonus"] += reward["value"]
            elif reward["type"] == "sprint_cost":
                bonuses["sprint_cost_reduction"] += abs(reward["value"])
            elif reward["type"] == "iframes":
                bonuses["iframes_bonus"] += reward["value"]
            elif reward["type"] == "sight_radius":
                bonuses["sight_radius_bonus"] += reward["value"]
    
    return bonuses


if __name__ == "__main__":
    # 测试升级系统
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