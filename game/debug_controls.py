"""
Debug controls: toggle debug mode and panels, decoupled from Game class.
"""

from typing import Optional


def toggle_debug_mode(config, renderer, logger, game_state) -> Optional[bool]:
    """Toggle debug mode (F12) and update related systems.

    Returns the new debug mode state (True/False) or None on failure.
    """
    try:
        new_state = config.toggle_debug_mode()

        # Update debug overlay
        if hasattr(renderer, 'debug_overlay') and renderer.debug_overlay:
            renderer.debug_overlay.update_debug_mode()

        # Update logger debug mode if available
        if hasattr(logger, 'debug_enabled'):
            logger.debug_enabled = new_state

        # Log the state change and add to in-game log if available
        status_message = f"Debug mode {'enabled' if new_state else 'disabled'}"
        if new_state:
            logger.info(f"{status_message} - Press 1-5 to toggle panels, F12 to disable", "DEBUG")
            if hasattr(game_state, 'game_log'):
                game_state.game_log("Debug mode enabled (F12 to disable)")
        else:
            logger.info(f"{status_message}", "DEBUG")
            if hasattr(game_state, 'game_log'):
                game_state.game_log("Debug mode disabled")

        return new_state

    except Exception as e:
        # Use logger if possible
        try:
            logger.error("Failed to toggle debug mode", "DEBUG", e)
        except Exception:
            pass
        return None


def toggle_panel(renderer, panel_name: str, logger, game_state, config) -> bool:
    """Toggle a debug panel by name when debug mode is active.

    Returns True if toggled, False otherwise.
    """
    try:
        if hasattr(renderer, 'debug_overlay') and renderer.debug_overlay and getattr(config, 'debug_mode', False):
            renderer.debug_overlay.toggle_panel(panel_name)
            panel_status = (
                "visible" if panel_name in renderer.debug_overlay.visible_panels else "hidden"
            )
            logger.debug(f"Debug panel '{panel_name}' is now {panel_status}", "DEBUG")
            if hasattr(game_state, 'game_log'):
                game_state.game_log(f"Debug panel '{panel_name}': {panel_status}")
            return True
    except Exception as e:
        try:
            logger.error(f"Failed to toggle debug panel '{panel_name}'", "DEBUG", e)
        except Exception:
            pass
    return False
