"""Non-graphical smoke test for core subsystems: generator, dialogs, EntityManager.

This script runs without opening a Pygame window and verifies:
- generate_dungeon returns a non-empty level and consistent dimensions
- dialogs.load_npcs returns a dict mapping positions to dialog entries
- entities.EntityManager can load enemies.json (if present) or load from generated level

Exit code 0 on success, 1 on failure.
"""
import sys
import os
import traceback

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from game import utils, dialogs, entities

FAIL = False

def fail(msg):
    global FAIL
    FAIL = True
    print('FAIL:', msg)


def main():
    try:
        print('Running smoke-test...')
        # 1) generator
        level = utils.generate_dungeon(40, 20, room_attempts=12, num_enemies=6, seed=42, min_room=5, max_room=12, corridor_radius=1)
        if not level or not isinstance(level, list) or not level[0]:
            fail('generate_dungeon returned empty or invalid level')
        else:
            h = len(level)
            w = len(level[0])
            print(f'  generator: level size {w}x{h}')

        # 2) dialogs
        npcs = dialogs.load_npcs(level, w, h)
        if not isinstance(npcs, dict):
            fail('dialogs.load_npcs did not return dict')
        else:
            print(f'  dialogs: loaded {len(npcs)} NPC entries')

        # 3) EntityManager load
        em = entities.EntityManager()
        enemies_path = os.path.join(ROOT, 'data', 'enemies.json')
        if os.path.exists(enemies_path):
            try:
                em.load_from_file(enemies_path, level=level)
                print(f'  entity_mgr: loaded {len(em.entities_by_id)} entities from enemies.json')
            except Exception as e:
                fail(f'EntityManager.load_from_file raised: {e}')
        else:
            try:
                em.load_from_level(level)
                print(f'  entity_mgr: loaded {len(em.entities_by_id)} entities from level (fallback)')
            except Exception as e:
                fail(f'EntityManager.load_from_level raised: {e}')

    except Exception:
        traceback.print_exc()
        fail('Unhandled exception during smoke-test')

    if FAIL:
        print('\nSMOKE TEST: FAILED')
        sys.exit(1)
    else:
        print('\nSMOKE TEST: PASSED')
        sys.exit(0)

if __name__ == '__main__':
    main()
