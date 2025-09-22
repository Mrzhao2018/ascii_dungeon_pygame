import sys
import os
# Ensure project root is on sys.path so 'game' package is importable when run from tools/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game import utils
from game import dialogs

level = utils.load_level(None)
WIDTH = len(level[0])
HEIGHT = len(level)

print('LEVEL:')
for y,row in enumerate(level):
    print(f'{y:02d}: {row}')

nps = dialogs.load_npcs(level, WIDTH, HEIGHT)
print('\ndialogs.load_npcs returned:')
for k,v in nps.items():
    print(k, v)

print('\nScan for N tiles:')
for y,row in enumerate(level):
    for x,ch in enumerate(row):
        if ch == 'N':
            print(' N at', (x,y))
