"""
Transition controller: helpers for applying floor transitions, including camera reset,
FOV recalculation, exit indicator refresh, and centralized transition logging/statistics.
"""

from typing import Tuple, Dict, Optional, List
from game import entities


def reset_camera_to_player(config, game_state, renderer, player) -> None:
    ts = config.tile_size
    game_state.cam_x = player.x * ts - renderer.view_px_w // 2
    game_state.cam_y = player.y * ts - renderer.view_px_h // 2

    max_x = max(0, game_state.width * ts - renderer.view_px_w)
    max_y = max(0, game_state.height * ts - renderer.view_px_h)

    game_state.cam_x = max(0, min(game_state.cam_x, max_x))
    game_state.cam_y = max(0, min(game_state.cam_y, max_y))


def apply_floor_transition(
    config,
    game_state,
    renderer,
    player,
    level: List[str],
    entity_mgr: entities.EntityManager,
    npcs: Optional[Dict],
    new_pos: Optional[Tuple[int, int]],
) -> Tuple[entities.EntityManager, Dict]:
    """Apply a new floor state to the game: set level, update entities/NPCs, reset camera,
    recalc FOV (if enabled), and refresh exit indicator. Returns (entity_mgr, npcs_dict).
    """
    # Update game state level first (width/height will reflect the new level)
    game_state.set_level(level)

    # Update entity manager and NPCs dictionary
    npcs_dict: Dict = npcs or {}

    # Clear exploration/FOV data for the new floor
    if getattr(config, 'enable_fov', False):
        player.clear_exploration()

    # Update player position if provided
    if new_pos:
        player.x, player.y = new_pos

    # Update renderer view size for the new level dimensions
    renderer.update_view_size(game_state.width, game_state.height)

    # Reset camera to center on player within bounds
    reset_camera_to_player(config, game_state, renderer, player)

    # Recalculate FOV for new position if enabled
    if getattr(config, 'enable_fov', False):
        player.update_fov(game_state.level)

    # Refresh exit indicator to point to the new floor's exit
    game_state.refresh_exit_indicator(config.tile_size)

    return entity_mgr, npcs_dict


def log_transition_triggered(logger, next_floor: int, seed: int) -> None:
    """Log that a floor transition has been triggered."""
    try:
        logger.info(f"Floor transition triggered: floor {next_floor}, seed {seed}", "FLOOR")
    except Exception:
        pass


def log_transition_summary(logger, game_state, entity_mgr: Optional[entities.EntityManager]) -> None:
    """Log a concise summary after a floor transition is applied."""
    try:
        width, height = game_state.width, game_state.height
        enemy_count = 0
        total_entities = 0
        if entity_mgr:
            total_entities = len(getattr(entity_mgr, 'entities_by_id', {}))
            enemy_count = len(
                [e for e in getattr(entity_mgr, 'entities_by_id', {}).values() if hasattr(e, 'hp')]
            )
        logger.info(
            f"楼层转换完成：第 {game_state.floor_number} 层 | 地图 {width}x{height} | 敌人 {enemy_count} | 实体 {total_entities}",
            "FLOOR",
        )
    except Exception:
        pass
