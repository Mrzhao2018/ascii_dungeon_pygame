from typing import Any, Optional

def safe_log(logger: Optional[Any], game_state: Optional[Any], msg: str, *, level: str = 'info', channel: str = 'GAME') -> None:
    try:
        if logger is not None:
            try:
                if level == 'debug' and hasattr(logger, 'debug'):
                    logger.debug(msg, channel)
                    return
                if level == 'warning' and hasattr(logger, 'warning'):
                    logger.warning(msg, channel)
                    return
                if level == 'error' and hasattr(logger, 'error'):
                    logger.error(msg, channel)
                    return
                if hasattr(logger, 'info'):
                    logger.info(msg, channel)
                    return
            except Exception:
                pass
        if game_state is not None and hasattr(game_state, 'game_log'):
            try:
                game_state.game_log(msg)
                return
            except Exception:
                pass
        try:
            print(msg)
        except Exception:
            pass
    except Exception:
        try:
            print(msg)
        except Exception:
            pass

__all__ = ["safe_log"]
