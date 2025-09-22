"""Batch test generate_dungeon for a range of seeds and report missing exits.

Usage: run with the project's virtualenv Python.
"""
import sys
import os
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from game import utils

def check_seeds(start=1, end=50):
    missing = []
    for s in range(start, end+1):
        try:
            level = utils.generate_dungeon(80, 30, seed=s)
            has_exit = any('X' in row for row in level)
            if not has_exit:
                missing.append(s)
        except Exception as e:
            print(f'seed {s} raised exception: {e}')
            missing.append(s)
    return missing

if __name__ == '__main__':
    start = 1
    end = 50
    if len(sys.argv) >= 2:
        try:
            start = int(sys.argv[1])
        except Exception:
            pass
    if len(sys.argv) >= 3:
        try:
            end = int(sys.argv[2])
        except Exception:
            pass
    miss = check_seeds(start, end)
    print(f'checked seeds {start}..{end} total={end-start+1} missing_count={len(miss)}')
    if miss:
        print('missing seeds:', miss)
    else:
        print('all seeds produced an exit X')
