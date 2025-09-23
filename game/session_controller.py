"""
Session controller: world initialization, level setup, start/restart flows.
"""

from typing import Tuple, Optional, Dict
from game import entities


def _create_player_at(pos, config):
    from game.player import Player

    return Player(
        pos[0],
        pos[1],
        hp=10,
        move_cooldown=config.move_cooldown,
        max_stamina=float(config.stamina_max) if config.stamina_max is not None else 100.0,
        stamina_regen=float(config.stamina_regen) if config.stamina_regen is not None else 12.0,
        sprint_cost=float(config.sprint_cost) if config.sprint_cost is not None else 35.0,
        sprint_cooldown_ms=(int(config.sprint_cooldown_ms) if config.sprint_cooldown_ms is not None else 800),
        sprint_multiplier=(float(config.sprint_multiplier) if config.sprint_multiplier is not None else 0.6),
        sight_radius=int(config.sight_radius) if config.sight_radius is not None else 6,
    )


def initialize_game_world(config, game_state, floor_manager):
    """Generate initial level and create player at '@' position; returns player or None if not found."""
    level = floor_manager.generate_initial_level()
    game_state.set_level(level)

    player_pos = floor_manager.find_player(level)
    if not player_pos:
        return None

    player = _create_player_at(player_pos, config)
    return player


def setup_initial_level(
    config, game_state, renderer, floor_manager, player
) -> Tuple[entities.EntityManager, Dict]:
    """Setup entities/NPCs and initialize camera/FOV; returns (entity_mgr, npcs)."""
    entity_mgr, npcs = floor_manager.setup_level(game_state.level)
    floor_manager.write_initial_snapshot(game_state.level)

    # Initialize camera
    game_state.cam_x = player.x * config.tile_size - renderer.view_px_w // 2
    game_state.cam_y = player.y * config.tile_size - renderer.view_px_h // 2
    game_state.cam_x = max(0, min(game_state.cam_x, max(0, game_state.width * config.tile_size - renderer.view_px_w)))
    game_state.cam_y = max(0, min(game_state.cam_y, max(0, game_state.height * config.tile_size - renderer.view_px_h)))

    # Initialize FOV if enabled
    if getattr(config, 'enable_fov', False):
        player.update_fov(game_state.level)

    return entity_mgr, npcs


def restart_game(config, logger, floor_manager, renderer, game_state):
    """Reinitialize game state, world, and player; returns (game_state, player, entity_mgr, npcs)."""
    # Reset state in place to keep references
    game_state.__init__(config)
    game_state.logger = logger

    level = floor_manager.generate_initial_level()
    player_pos = floor_manager.find_player(level)
    if not player_pos:
        logger.error("重新开始时未找到玩家位置", "GAME")
        return game_state, None, None, {}

    game_state.set_level(level)
    player = _create_player_at(player_pos, config)

    entity_mgr, npcs = setup_initial_level(config, game_state, renderer, floor_manager, player)

    # Re-init FOV
    if getattr(config, 'enable_fov', False) and player:
        player.update_fov(game_state.level)

    return game_state, player, entity_mgr, npcs


def start_game_if_needed(config, logger, game_state, floor_manager, renderer):
    """Ensure the world is initialized and switch to PLAYING state; returns (player, entity_mgr, npcs)."""
    player = None
    entity_mgr: Optional[entities.EntityManager] = None
    npcs: Dict = {}

    if game_state.level is None or len(game_state.level) == 0:
        player = initialize_game_world(config, game_state, floor_manager)
        if not player:
            logger.error("未找到玩家 '@'，请在地图中放置玩家", "GAME")
            return None, None, {}
        entity_mgr, npcs = setup_initial_level(config, game_state, renderer, floor_manager, player)

    # Switch to PLAYING
    from game.state import GameStateEnum
    game_state.set_game_state(GameStateEnum.PLAYING)

    return player, entity_mgr, npcs
