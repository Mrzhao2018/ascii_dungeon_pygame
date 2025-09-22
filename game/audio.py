import pygame
import os


def init_audio():
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
            print(f'[audio] mixer initialized: freq={freq} size={size} chans={chans} buf={buff}')
            return True
        except Exception as e:
            # 尝试下一个配置
            print(f'[audio] mixer init failed for {freq},{size},{chans},{buff}: {e}')
            continue
    # 最后尝试默认初始化一次
    try:
        pygame.mixer.init()
        return True
    except Exception as e:
        print(f'[audio] final mixer init failed: {e}')
        return False


def load_hit_sound(preferred_path=None):
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
            print(f'[audio] sndarray.make_sound failed: {e}')
            return None
    except Exception as e:
        print(f'[audio] numpy synth fallback not available: {e}')
        return None


def load_sprint_sound(preferred_path=None):
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
            print(f'[audio] sprint sndarray.make_sound failed: {e}')
            return None
    except Exception as e:
        print(f'[audio] sprint numpy synth fallback not available: {e}')
        return None


def load_sprint_ready_sound(preferred_path=None):
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
            print(f'[audio] sprint_ready sndarray.make_sound failed: {e}')
            return None
    except Exception as e:
        print(f'[audio] sprint_ready numpy synth fallback not available: {e}')
        return None
