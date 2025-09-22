"""简单对话编辑器：列出 NPC、查看/追加/替换对话行并保存到 data/dialogs.json

用法示例：
  python tools/edit_dialogs.py list
  python tools/edit_dialogs.py show old_man
  python tools/edit_dialogs.py add-line old_man "这是新的一行"
  python tools/edit_dialogs.py set-lines old_man "行1" "行2"

这是一个非常轻量的编辑器，适合快速修改示例对话。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT, 'data', 'dialogs.json')


def load():
    if not os.path.exists(DATA_PATH):
        return {'npcs': []}
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save(doc):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)


def find_npc(doc, npc_id):
    for entry in doc.get('npcs', []):
        if entry.get('id') == npc_id:
            return entry
    return None


def cmd_list(args):
    doc = load()
    for e in doc.get('npcs', []):
        print(f"{e.get('id')} @ ({e.get('x')},{e.get('y')}) char={e.get('char')}")


def cmd_show(args):
    if len(args) < 1:
        print('需要 NPC id')
        return
    doc = load()
    e = find_npc(doc, args[0])
    if not e:
        print('未找到 NPC')
        return
    print(json.dumps(e, ensure_ascii=False, indent=2))


def cmd_add_line(args):
    if len(args) < 2:
        print('用法: add-line <npc_id> <text>')
        return
    npc_id = args[0]
    text = args[1]
    doc = load()
    e = find_npc(doc, npc_id)
    if not e:
        print('未找到 NPC')
        return
    e.setdefault('dialog', []).append(text)
    save(doc)
    print('已追加')


def cmd_set_lines(args):
    if len(args) < 2:
        print('用法: set-lines <npc_id> <line1> [line2 ...]')
        return
    npc_id = args[0]
    lines = args[1:]
    doc = load()
    e = find_npc(doc, npc_id)
    if not e:
        print('未找到 NPC')
        return
    e['dialog'] = lines
    save(doc)
    print('已设置对话行')


COMMANDS = {
    'list': cmd_list,
    'show': cmd_show,
    'add-line': cmd_add_line,
    'set-lines': cmd_set_lines,
}


def main():
    if len(sys.argv) < 2:
        print('用法: edit_dialogs.py <command> [args]')
        print('commands:', ', '.join(COMMANDS.keys()))
        return
    cmd = sys.argv[1]
    func = COMMANDS.get(cmd)
    if not func:
        print('未知命令')
        return
    func(sys.argv[2:])


if __name__ == '__main__':
    main()
