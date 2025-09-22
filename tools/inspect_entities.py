import sys, os, json

# Ensure project root is on sys.path so 'from game import ...' works when running from tools/
base = os.path.dirname(os.path.dirname(__file__))
if base not in sys.path:
    sys.path.insert(0, base)

from game import utils
from game import entities

enemies_path = os.path.join(base, 'data', 'enemies.json')

# load level via utils (will generate dungeon if no file exists)
level = utils.load_level(None)

print('LEVEL:')
for y, row in enumerate(level):
    print(f'{y:02d}: {row}')

# load enemies.json
with open(enemies_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
print('\nENEMIES JSON:')
for cfg in data.get('entities', []):
    print(cfg)

# instantiate EntityManager and load from file (pass level so tiles get marked/adjusted)
mgr = entities.EntityManager()
mgr.load_from_file(enemies_path, level=level)

print('\nLoaded entities:')
for ent_id, ent in mgr.entities_by_id.items():
    ex, ey = ent.x, ent.y
    ch = level[ey][ex] if 0 <= ey < len(level) and 0 <= ex < len(level[0]) else '?'
    neigh = {}
    for dx, dy, name in [(1,0,'R'),(-1,0,'L'),(0,1,'D'),(0,-1,'U')]:
        tx, ty = ex+dx, ey+dy
        if 0 <= ty < len(level) and 0 <= tx < len(level[0]):
            neigh[name] = level[ty][tx]
        else:
            neigh[name] = None
    print(f'  id={ent_id} pos=({ex},{ey}) hp={getattr(ent, "hp", None)} dir={getattr(ent, "dir", None)} level_char={ch} neigh={neigh}')

# Also check if load_from_level would have created more
print('\nScan level for E tiles:')
for y, row in enumerate(level):
    for x, ch in enumerate(row):
        if ch == 'E':
            print('  E at', (x,y))

print('\nDone')
