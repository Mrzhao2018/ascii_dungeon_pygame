import pygame
import os
from typing import Any, Optional


def init_audio(logger: Optional[Any] = None, game_state: Optional[Any] = None):
    # 如果已经初始化，直接返回 True
    try:
        if pygame.mixer.get_init():
            return True
    except Exception:
        pass

    # 尝试使用常见参数预初始化并初始化 mixer
    presets = [
        (22050, -16, 2, 512),
        (44100, -16, 2, 512),
        (22050, -16, 2, 1024),
    ]
    for freq, size, chans, buff in presets:
        try:
            pygame.mixer.pre_init(freq, size, chans, buff)
            pygame.mixer.init()
            _safe_log(f'[audio] mixer initialized: freq={freq} size={size} chans={chans} buf={buff}', logger=logger, game_state=game_state)
            return True
        except Exception as e:
            # 尝试下一个配置
            _safe_log(f'[audio] mixer init failed for {freq},{size},{chans},{buff}: {e}', level='warning', logger=logger, game_state=game_state)
            continue
    # 最后尝试默认初始化一次
    try:
        pygame.mixer.init()
        return True
    except Exception as e:
        _safe_log(f'[audio] final mixer init failed: {e}', level='error', logger=logger, game_state=game_state)
        return False


def load_hit_sound(preferred_path=None, logger: Optional[Any] = None, game_state: Optional[Any] = None):
    # 优先加载项目内 wav 文件（如果存在），否则返回 None（上层可尝试合成音）
    if preferred_path:
        try:
            return pygame.mixer.Sound(preferred_path)
        except Exception:
            pass
    # 搜索 assets/sfx/hit.*
    base = os.path.join(os.path.dirname(__file__), '..')
    candidates = [
        os.path.join(base, 'assets', 'sfx', 'hit.wav'),
        os.path.join(base, 'assets', 'sfx', 'hit.ogg'),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return pygame.mixer.Sound(c)
            except Exception:
                pass
    # 回退：确保 mixer 已初始化（尝试再次初始化），然后使用 numpy 合成短音
    try:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass
    except Exception:
        pass

    try:
        import numpy as _np

        # 生成短正弦波
        freq = 600
        duration = 0.06
        sample_rate = 22050
        t = _np.linspace(0, duration, int(sample_rate * duration), False)
        tone = (_np.sin(2 * _np.pi * freq * t) * 32767).astype(_np.int16)
        stereo = _np.column_stack((tone, tone))
        try:
            return pygame.sndarray.make_sound(stereo.copy())
        except Exception as e:
            _safe_log(f'[audio] sndarray.make_sound failed: {e}', level='warning', logger=logger, game_state=game_state)
            return None
    except Exception as e:
        _safe_log(f'[audio] numpy synth fallback not available: {e}', level='info', logger=logger, game_state=game_state)
        return None


def load_sprint_sound(preferred_path=None, logger: Optional[Any] = None, game_state: Optional[Any] = None):
    # Similar to load_hit_sound but looks for sprint.* candidates and uses a higher-pitch synth fallback
    if preferred_path:
        try:
            return pygame.mixer.Sound(preferred_path)
        except Exception:
            pass
    base = os.path.join(os.path.dirname(__file__), '..')
    candidates = [
        os.path.join(base, 'assets', 'sfx', 'sprint.wav'),
        os.path.join(base, 'assets', 'sfx', 'sprint.ogg'),
        # fallback to generic hit if sprint not provided
        os.path.join(base, 'assets', 'sfx', 'hit.wav'),
        os.path.join(base, 'assets', 'sfx', 'hit.ogg'),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return pygame.mixer.Sound(c)
            except Exception:
                pass

    # synth fallback
    try:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass
    except Exception:
        pass

    try:
        import numpy as _np

        freq = 900
        duration = 0.05
        sample_rate = 22050
        t = _np.linspace(0, duration, int(sample_rate * duration), False)
        tone = (_np.sin(2 * _np.pi * freq * t) * 32767).astype(_np.int16)
        stereo = _np.column_stack((tone, tone))
        try:
            return pygame.sndarray.make_sound(stereo.copy())
        except Exception as e:
            _safe_log(f'[audio] sprint sndarray.make_sound failed: {e}', level='warning', logger=logger, game_state=game_state)
            return None
    except Exception as e:
        _safe_log(f'[audio] sprint numpy synth fallback not available: {e}', level='info', logger=logger, game_state=game_state)
        return None


def load_sprint_ready_sound(preferred_path=None, logger: Optional[Any] = None, game_state: Optional[Any] = None):
    # Sound to play when sprint cooldown completes
    if preferred_path:
        try:
            return pygame.mixer.Sound(preferred_path)
        except Exception:
            pass
    base = os.path.join(os.path.dirname(__file__), '..')
    candidates = [
        os.path.join(base, 'assets', 'sfx', 'sprint_ready.wav'),
        os.path.join(base, 'assets', 'sfx', 'sprint_ready.ogg'),
        # fallback to sprint or hit
        os.path.join(base, 'assets', 'sfx', 'sprint.wav'),
        os.path.join(base, 'assets', 'sfx', 'hit.wav'),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return pygame.mixer.Sound(c)
            except Exception:
                pass

    # synth polite chime fallback
    try:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass
    except Exception:
        pass
    try:
        import numpy as _np

        freq = 1100
        duration = 0.08
        sample_rate = 22050
        t = _np.linspace(0, duration, int(sample_rate * duration), False)
        tone = (_np.sin(2 * _np.pi * freq * t) * 32767 * _np.exp(-3 * t)).astype(_np.int16)
        stereo = _np.column_stack((tone, tone))
        try:
            return pygame.sndarray.make_sound(stereo.copy())
        except Exception as e:
            _safe_log(f'[audio] sprint_ready sndarray.make_sound failed: {e}', level='warning', logger=logger, game_state=game_state)
            return None
    except Exception as e:
        _safe_log(f'[audio] sprint_ready numpy synth fallback not available: {e}', level='info', logger=logger, game_state=game_state)
        return None


def _safe_log(msg: str, level: str = 'info', logger: Optional[Any] = None, game_state: Optional[Any] = None):
    """Small helper to prefer in-game logger, then game_state.game_log, else print"""
    try:
        if logger is not None:
            # Prefer logger methods if available
            try:
                if level == 'debug' and hasattr(logger, 'debug'):
                    logger.debug(msg, 'AUDIO')
                    return
                if level == 'info' and hasattr(logger, 'info'):
                    logger.info(msg, 'AUDIO')
                    return
                if level == 'warning' and hasattr(logger, 'warning'):
                    logger.warning(msg, 'AUDIO')
                    return
                if level == 'error' and hasattr(logger, 'error'):
                    logger.error(msg, 'AUDIO')
                    return
                if level == 'critical' and hasattr(logger, 'critical'):
                    logger.critical(msg, 'AUDIO')
                    return
            except Exception:
                pass

        if game_state is not None and hasattr(game_state, 'game_log'):
            try:
                game_state.game_log(msg)
                return
            except Exception:
                pass

        # Fallback to console
        print(msg)
    except Exception:
        try:
            print(msg)
        except Exception:
            pass
