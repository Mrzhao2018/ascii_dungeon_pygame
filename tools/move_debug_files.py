"""Move debug snapshot files from data/ into data/debug/.

This script moves files matching patterns:
 - last_generated_level_*.txt
 - last_level_floor_*.txt
 - exit_log.txt

It preserves dialogs.json and enemies.json in data/.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(ROOT, 'data')
debug_dir = os.path.join(data_dir, 'debug')
os.makedirs(debug_dir, exist_ok=True)

patterns = [
    'last_generated_level_'
    , 'last_level_floor_'
]

moved = []
for name in os.listdir(data_dir):
    src = os.path.join(data_dir, name)
    if not os.path.isfile(src):
        continue
    # skip core data files
    if name in ('dialogs.json', 'enemies.json'):
        continue
    if any(name.startswith(p) and name.endswith('.txt') for p in patterns) or name == 'exit_log.txt':
        dst = os.path.join(debug_dir, name)
        try:
            shutil.move(src, dst)
            moved.append(name)
        except Exception:
            pass

print('moved files count=', len(moved))
for n in moved[:200]:
    print('  ', n)
