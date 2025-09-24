import json
import os
from functools import lru_cache
from typing import Dict, Any

# 单一来源的默认配置，避免散落硬编码
DEFAULT_CONFIG: Dict[str, Any] = {
    "distribution": [
        {"kind": "basic", "weight": 60},
        {"kind": "guard", "weight": 20},
        {"kind": "scout", "weight": 15},
        {"kind": "brute", "weight": 5},
    ],
    "types": {
        "basic": {
            "hp": 5,
            "chase_range": 6,
            "patrol_range": 3,
            "speed": 1,
            "damage": 1,
            "ai_update_interval": 3,
            "move_interval": 6,
        },
        "guard": {
            "hp": 8,
            "chase_range": 8,
            "patrol_range": 2,
            "speed": 1,
            "damage": 2,
            "ai_update_interval": 2,
            "move_interval": 5,
        },
        "scout": {
            "hp": 3,
            "chase_range": 10,
            "patrol_range": 5,
            "speed": 2,
            "damage": 1,
            "ai_update_interval": 1,
            "move_interval": 3,
        },
        "brute": {
            "hp": 12,
            "chase_range": 4,
            "patrol_range": 1,
            "speed": 1,
            "damage": 3,
            "ai_update_interval": 4,
            "move_interval": 8,
        },
    },
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'enemy_types.json')


@lru_cache(maxsize=1)
def load_enemy_config() -> Dict[str, Any]:
    """尝试从 data/enemy_types.json 读取；否则返回内置 DEFAULT_CONFIG。
    读不到文件也不会抛异常，保证游戏可启动。
    """
    path = CONFIG_PATH
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 轻量验证
            if 'distribution' in data and 'types' in data:
                return data
    except Exception:
        pass
    return DEFAULT_CONFIG


def get_enemy_stats(kind: str) -> Dict[str, Any]:
    cfg = load_enemy_config()
    return dict(cfg['types'].get(kind, cfg['types']['basic']))


def get_enemy_hp(kind: str) -> int:
    return int(get_enemy_stats(kind).get('hp', 5))


def pick_enemy_kind_for_coord(x: int, y: int) -> str:
    """根据坐标哈希 + 配置中的权重分布确定敌人种类。
    保持确定性：同一 (x,y) 在相同配置下始终返回同一结果。
    """
    cfg = load_enemy_config()
    dist = cfg['distribution']
    total = sum(item.get('weight', 0) for item in dist) or 1
    h = (x * 31 + y * 17) % total
    cumulative = 0
    for item in dist:
        w = int(item.get('weight', 0))
        cumulative += w
        if h < cumulative:
            return item.get('kind', 'basic')
    return 'basic'


def reassign_enemy_kind(ent) -> None:
    """用于旧存档中的 basic 敌人升级为多样化：保持其它字段不变。"""
    k = pick_enemy_kind_for_coord(ent.x, ent.y)
    ent.kind = k
    # 不直接覆盖 ent.hp，避免破坏运行时已受伤血量；只在初始 HP 形态可加逻辑（可选）

__all__ = [
    'load_enemy_config',
    'get_enemy_stats',
    'get_enemy_hp',
    'pick_enemy_kind_for_coord',
    'reassign_enemy_kind',
]
