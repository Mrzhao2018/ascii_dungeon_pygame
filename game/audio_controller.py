"""
Audio controller: init mixer and load commonly used sounds.
"""

from typing import Tuple, Optional
import pygame
from game import audio as audio_mod


def initialize_audio(
    logger=None,
) -> Tuple[bool, Optional[pygame.mixer.Sound], Optional[pygame.mixer.Sound], Optional[pygame.mixer.Sound]]:
    """Initialize audio system and load sounds.

    Returns: (sound_enabled, hit_sound, sprint_sound, sprint_ready_sound)
    """
    sound_enabled = audio_mod.init_audio()
    hit_sound: Optional[pygame.mixer.Sound] = audio_mod.load_hit_sound() if sound_enabled else None
    sprint_sound: Optional[pygame.mixer.Sound] = audio_mod.load_sprint_sound() if sound_enabled else None
    sprint_ready_sound: Optional[pygame.mixer.Sound] = (
        audio_mod.load_sprint_ready_sound() if sound_enabled else None
    )

    if logger:
        logger.debug(
            f"Audio initialized: sound_enabled={sound_enabled} hit={hit_sound is not None} sprint={sprint_sound is not None}",
            "AUDIO",
        )

    return sound_enabled, hit_sound, sprint_sound, sprint_ready_sound


def play_safe(sound: Optional[pygame.mixer.Sound]):
    """Safely play a pygame sound if available; ignore failures."""
    if not sound:
        return
    try:
        sound.play()
    except Exception:
        pass
