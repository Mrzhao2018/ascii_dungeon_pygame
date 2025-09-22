import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game import utils, dialogs

level = utils.load_level(None)
WIDTH = len(level[0])
HEIGHT = len(level)
fontpath = None

player = None
for y,row in enumerate(level):
    x = row.find('@')
    if x!=-1:
        player = (x,y)
        break
print('player at', player)

npcs = dialogs.load_npcs(level, WIDTH, HEIGHT)
print('npcs keys:', list(npcs.keys()))

# find first NPC neighbor of player
if player:
    px,py = player
    neighbors = [(px+1,py),(px-1,py),(px,py+1),(px,py-1)]
    found = None
    for nx, ny in neighbors:
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and level[ny][nx] == 'N':
            found = (nx, ny)
            break
    print('found neighbor:', found)
    if found:
        entry = npcs.get(found)
        print('entry from npcs:', entry)
        dlg = dialogs.get_dialog_for(npcs, found)
        print('get_dialog_for returned:', dlg)
    else:
        print('No adjacent N to player; listing all N tiles:')
        for y,row in enumerate(level):
            for x,ch in enumerate(row):
                if ch=='N':
                    print(' N at', (x,y))
else:
    print('No player on map')
