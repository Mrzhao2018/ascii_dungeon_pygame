"""Simulate a floor transition headlessly.

Generates a dungeon for a given floor number and seed, rebuilds EntityManager,
loads entities from data/enemies.json, loads NPCs, and writes two snapshot files:
 - data/last_level_floor_<n>.txt
 - data/last_level_floor_<n>_after_entities.txt

Usage: run with the project's virtualenv Python. Optional args: <floor_number> <seed>
"""
import sys
import os
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from game import utils, entities, dialogs as dialogs_mod

def simulate(floor_number=2, seed=None):
    mw, mh = 100, 40
    level = utils.generate_dungeon(mw, mh, seed=seed)
    # defensive exit/player checks already in generate_dungeon
    # compute exit_pos
    exit_pos = None
    player_pos = None
    for y, row in enumerate(level):
        if player_pos is None:
            p = row.find('@')
            if p != -1:
                player_pos = (p, y)
        if exit_pos is None:
            e = row.find('X')
            if e != -1:
                exit_pos = (e, y)
    # write snapshot immediately after generation
    try:
        dbg_dir = os.path.join(ROOT, 'data', 'debug')
        try:
            os.makedirs(dbg_dir, exist_ok=True)
        except Exception:
            pass
        dbg_path = os.path.join(dbg_dir, f'last_level_floor_{floor_number}.txt')
        with open(dbg_path, 'w', encoding='utf-8') as df:
            df.write('\n'.join(level))
            df.write('\n\n')
            df.write(f'floor={floor_number} exit_pos={exit_pos} player_pos={player_pos}\n')
        print(f'wrote {dbg_path}')
    except Exception as e:
        print('failed writing snapshot', e)

    # rebuild entity manager and load entities
    em = entities.EntityManager()
    enemies_path = os.path.join(ROOT, 'data', 'enemies.json')
    if os.path.exists(enemies_path):
        em.load_from_file(enemies_path, level=level)
    if not any(isinstance(e, entities.Enemy) for e in em.entities_by_id.values()):
        em.load_from_level(level)
        em.place_entity_near(level, len(level[0]), len(level))

    # recompute exit_pos after entity loading
    exit_pos2 = None
    player_pos2 = None
    for y, row in enumerate(level):
        if player_pos2 is None:
            p = row.find('@')
            if p != -1:
                player_pos2 = (p, y)
        if exit_pos2 is None:
            e = row.find('X')
            if e != -1:
                exit_pos2 = (e, y)

    try:
        dbg_path2 = os.path.join(dbg_dir, f'last_level_floor_{floor_number}_after_entities.txt')
        with open(dbg_path2, 'w', encoding='utf-8') as df2:
            df2.write('\n'.join(level))
            df2.write('\n\n')
            df2.write(f'floor={floor_number} exit_pos={exit_pos2} player_pos={player_pos2}\n')
        print(f'wrote {dbg_path2}')
    except Exception as e:
        print('failed writing snapshot 2', e)

if __name__ == '__main__':
    fn = 2
    sd = None
    if len(sys.argv) >= 2:
        try:
            fn = int(sys.argv[1])
        except Exception:
            pass
    if len(sys.argv) >= 3:
        try:
            sd = int(sys.argv[2])
        except Exception:
            sd = None
    simulate(fn, sd)
