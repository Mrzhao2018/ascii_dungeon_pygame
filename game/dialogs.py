import json
import os


def load_npcs(level, WIDTH, HEIGHT):
    dialogs_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dialogs.json')
    npcs = {}
    try:
        with open(dialogs_path, 'r', encoding='utf-8') as f:
            doc = json.load(f)
            for entry in doc.get('npcs', []):
                nx = int(entry.get('x', 0))
                ny = int(entry.get('y', 0))
                ch = entry.get('char', 'N')
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and level[ny][nx] == '.':
                    from game.utils import set_tile

                    set_tile(level, nx, ny, ch)
                    npcs[(nx, ny)] = entry
    except FileNotFoundError:
        # 如果没有文件，返回空 npcs（main 会回退）
        pass
    return npcs


def get_dialog_for(npcs, pos):
    entry = npcs.get(pos)
    if entry and 'dialog' in entry:
        return entry['dialog'][:]
    return None
