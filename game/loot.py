"""Loot tables and drop logic for enemies.

Provides a deterministic (seedless) drop generation based on enemy position/id
so results are reproducible for the same map, similar to how enemy kinds are assigned.
"""
from typing import Dict, List, Tuple

# Basic per-kind loot configuration.
# Each entry maps to a list of (item_key, min_qty, max_qty, weight)
# Weights are relative within the list; if total weight == 0 -> no drops.
LOOT_TABLE: Dict[str, List[Tuple[str, int, int, int]]] = {
    'basic': [
        ('gold', 1, 3, 70),
        ('nothing', 0, 0, 30),
    ],
    'guard': [
        ('gold', 2, 5, 60),
        ('stamina_shard', 1, 1, 10),
        ('nothing', 0, 0, 30),
    ],
    'scout': [
        ('gold', 1, 2, 50),
        ('speed_fragment', 1, 1, 10),
        ('nothing', 0, 0, 40),
    ],
    'brute': [
        ('gold', 3, 7, 65),
        ('hp_fragment', 1, 1, 15),
        ('nothing', 0, 0, 20),
    ],
}

# Simple mapping for display names (optional future usage)
ITEM_DISPLAY_NAME = {
    'gold': 'Gold',
    'stamina_shard': 'Stamina+',
    'speed_fragment': 'Speed+',
    'hp_fragment': 'HP+',
}


def deterministic_rng(seed_val: int) -> int:
    """Simple LCG-like hash to derive pseudo-random but deterministic values."""
    x = (seed_val ^ 0x9E3779B1) & 0xFFFFFFFF
    x = (x * 1664525 + 1013904223) & 0xFFFFFFFF
    return x


def pick_drop(kind: str, seed_val: int):
    """Pick a single drop entry for given kind using deterministic hashed seed.
    Returns (item_key, quantity) or (None, 0) if no drop."""
    table = LOOT_TABLE.get(kind, LOOT_TABLE.get('basic', []))
    if not table:
        return None, 0
    total_weight = sum(w for _, _, _, w in table)
    if total_weight <= 0:
        return None, 0
    r = deterministic_rng(seed_val) % total_weight
    for item_key, mn, mx, w in table:
        if r < w:
            if item_key == 'nothing':
                return None, 0
            # derive deterministic quantity
            span = max(0, mx - mn)
            if span == 0:
                qty = mn
            else:
                qty = mn + (deterministic_rng(seed_val ^ 0xABCDEF) % (span + 1))
            return item_key, qty
        r -= w
    return None, 0


def generate_loot_for_enemy(enemy, seed_extra: int = 0):
    """Generate loot for an enemy instance. Seed based on id & position and optional extra."""
    if enemy is None:
        return []
    base_seed = (getattr(enemy, 'id', 0) * 1315423911) ^ (enemy.x * 31 + enemy.y * 17) ^ seed_extra
    item_key, qty = pick_drop(getattr(enemy, 'kind', 'basic'), base_seed)
    if item_key and qty > 0:
        return [(item_key, qty)]
    return []
