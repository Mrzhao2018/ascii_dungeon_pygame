#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

PyGame 字符地牢探索游戏""""""

重构版本 - 使用模块化架构

"""PyGame 字符地牢探索游戏PyGame 字符地牢探索游戏



import sys重构版本 - 使用模块化架构重构版本 - 使用模块化架构

from game.game import Game

""""""



def main():

    """主函数 - 现在只是简单地创建和运行游戏"""

    try:import sysimport sys

        game = Game()

        game.run()from game.game import Gamefrom game.game import Game

    except KeyboardInterrupt:

        print("\n游戏被用户中断")

    except Exception as e:

        print(f"游戏运行时发生错误: {e}")

        import traceback

        traceback.print_exc()def main():def main():

        return 1

        """主函数 - 现在只是简单地创建和运行游戏"""    """主函数 - 现在只是简单地创建和运行游戏"""

    return 0

    try:    try:



if __name__ == '__main__':        game = Game()        game = Game()

    sys.exit(main())
        game.run()        game.run()

    except KeyboardInterrupt:    except KeyboardInterrupt:

        print("\n游戏被用户中断")        print("\n游戏被用户中断")

    except Exception as e:    except Exception as e:

        print(f"游戏运行时发生错误: {e}")        print(f"游戏运行时发生错误: {e}")

        import traceback        import traceback

        traceback.print_exc()        traceback.print_exc()

        return 1        return 1

        

    return 0    return 0





if __name__ == '__main__':if __name__ == '__main__':

    sys.exit(main())    sys.exit(main())


    font, used_path = utils.load_preferred_font(TILE_SIZE)
    # locate player position on the level (we'll instantiate Player later once we have config)
    player_pos = find_player(level)
    if not player_pos:
        print("未找到玩家 '@'，请在地图中放置玩家")
        pygame.quit()
        sys.exit(1)

    # 对话系统状态
    dialog_active = False
    dialog_lines = []
    dialog_index = 0
    # 楼层切换过场状态（用于显示 "第 N 层" 并短暂停留）
    floor_transition = None  # dict {time: ms_remaining, text: str}
    pending_floor = None  # dict with generation params when transition finishes
    # 临时目标指示器（当玩家按住 Tab 时显示鼠标世界坐标）
    pending_target = None
    # 记录当前楼层的出口位置（世界瓦片坐标）以便罗盘使用
    exit_pos = None

    # 玩家状态（创建 Player 对象以封装移动/体力/受击逻辑）
    MOVE_COOLDOWN = 150  # ms per tile when walking
    SPRINT_MULTIPLIER = sprint_multiplier
    max_stamina = float(stamina_max_cli)
    stamina_regen_per_sec = float(stamina_regen_cli or 6.0)
    sprint_cost_per_sec = float(sprint_cost)

    # instantiate Player object at located position (default HP 10)
    player = Player(player_pos[0], player_pos[1], hp=10, move_cooldown=MOVE_COOLDOWN, max_stamina=max_stamina, stamina_regen=stamina_regen_per_sec, sprint_cost=sprint_cost_per_sec, sprint_cooldown_ms=sprint_cooldown_after_exhaust_cli or 2000, sprint_multiplier=SPRINT_MULTIPLIER)
    # track previous sprint cooldown for transition sound
    prev_sprint_cd = player.sprint_cooldown

    # 敌人管理：使用 EntityManager（对象化）
    entity_mgr = entities.EntityManager()
    # 敌人受击闪烁记录 id -> ms 剩余闪烁时间
    enemy_flash = {}
    # 浮动伤害文本列表，元素: {'ent_id': int, 'text': str, 'time': ms 剩余, 'alpha': 255, 'damage': int, 'last_pos': (x,y)}
    floating_texts = []
    # 屏幕抖动计时（ms）与强度（像素）
    screen_shake = 0
    SCREEN_SHAKE_TIME = 250
    SCREEN_SHAKE_AMPLITUDE = 6
    # 冲刺冷却与动画状态由 Player 管理（player.sprint_cooldown / player.SPRINT_COOLDOWN_AFTER_EXHAUST）
    # cooldown animation state
    sprint_cd_anim = 0.0  # progress 0.0-1.0 for visual pulse (visual only)
    # 粒子系统由 Player 管理（player.sprint_particles）
    # 恢复/消耗曲线和短暂恢复延迟由 Player 管理
    # in-game debug log (visible in window when console not available)
    game_logs = []  # list of (ts_ms, text)
    GAME_LOG_MAX = 8
    def game_log(msg: str):
        if not debug_mode:
            return
        try:
            ts = pygame.time.get_ticks()
        except Exception:
            ts = 0
        entry = f"[{ts}] {msg}"
        game_logs.append(entry)
        if len(game_logs) > GAME_LOG_MAX:
            del game_logs[0]
        # also append to disk log for post-mortem
        try:
            log_path = os.path.join(os.path.dirname(__file__), 'game.log')
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(entry + "\n")
        except Exception:
            pass
    # persistent exit/transition log for debugging across runs
    def write_exit_log(msg: str):
        try:
            dbg_dir = os.path.join(os.path.dirname(__file__), 'data', 'debug')
            try:
                os.makedirs(dbg_dir, exist_ok=True)
            except Exception:
                pass
            p = os.path.join(dbg_dir, 'exit_log.txt')
            with open(p, 'a', encoding='utf-8') as lf:
                ts = pygame.time.get_ticks() if 'pygame' in globals() else 0
                lf.write(f'[{ts}] {msg}\n')
        except Exception:
            pass
    # 尝试从 data/enemies.json 加载实体配置；否则扫描地图或放置示例敌人
    enemies_path = os.path.join(os.path.dirname(__file__), 'data', 'enemies.json')
    # 如果存在实体配置文件，先清理地图上可能残留的 'E' 标记，避免留下没有对应对象的静态敌人
    if os.path.exists(enemies_path):
        for y, row in enumerate(level):
            for x, ch in enumerate(row):
                if ch == 'E':
                    set_tile(level, x, y, '.')
    entity_mgr.load_from_file(enemies_path, level=level)
    # 如果文件里没实体，从地图字符生成或放置一个示例敌人
    if not any(isinstance(e, entities.Enemy) for e in entity_mgr.entities_by_id.values()):
        entity_mgr.load_from_level(level)
        entity_mgr.place_entity_near(level, WIDTH, HEIGHT)

    # compute exit_pos from level
    try:
        found = None
        for y, row in enumerate(level):
            x = row.find('X')
            if x != -1:
                found = (x, y)
                break
        exit_pos = found
    except Exception:
        exit_pos = None
    # dump a debug snapshot of the generated level to data/ for inspection
    try:
        dbg_path = os.path.join(os.path.dirname(__file__), 'data', f'last_level_floor_1.txt')
        with open(dbg_path, 'w', encoding='utf-8') as df:
            df.write('\n'.join(level))
            df.write('\n\n')
            df.write(f'exit_pos={exit_pos} player_pos={player_pos}\n')
    except Exception:
        pass

    # 初始化音频（audio 模块会尝试初始化 mixer 并优先加载本地音效）
    sound_enabled = audio_mod.init_audio()
    hit_sound = None
    if sound_enabled:
        hit_sound = audio_mod.load_hit_sound()
    sprint_sound = None
    if sound_enabled:
        sprint_sound = audio_mod.load_sprint_sound()
    sprint_ready_sound = None
    if sound_enabled:
        sprint_ready_sound = audio_mod.load_sprint_ready_sound()
    print(f'[main] sound_enabled={sound_enabled} hit_sound_present={hit_sound is not None}')

    # 加载 NPC / 对话（dialogs 模块）
    npcs = dialogs_mod.load_npcs(level, WIDTH, HEIGHT)
    # 回退：如果没有 NPC，放一个简单的默认 NPC 在玩家右边（保持兼容以前行为）
    if all('N' not in row for row in level):
        px, py = player.x, player.y
        nx = min(px + 2, WIDTH - 2)
        ny = py
        if level[ny][nx] == '.':
            set_tile(level, nx, ny, 'N')

    running = True
    game_log('game initialized')
    while running:
        dt = clock.tick(FPS)
        # display a persistent header so overlay is obvious
        if debug_mode:
            if not game_logs or 'DEBUG:' not in game_logs[0]:
                game_logs.insert(0, 'DEBUG: in-window log (press E near N to interact)')
                if len(game_logs) > GAME_LOG_MAX:
                    game_logs = game_logs[-GAME_LOG_MAX:]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # 在楼层切换过场时忽略除退出以外的按键
                if floor_transition:
                    game_log('input ignored during floor transition')
                    continue
                game_log(f'KEYDOWN {event.key}')
                # 如果处于对话状态，优先处理对话翻页/关闭
                if dialog_active:
                    if event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                        dialog_index += 1
                        if dialog_index >= len(dialog_lines):
                            dialog_active = False
                    elif event.key == pygame.K_ESCAPE:
                        dialog_active = False
                    # 对话期间忽略移动键
                    continue

                dx = dy = 0
                if event.key in (pygame.K_UP, pygame.K_w):
                    dy = -1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    dy = 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    dx = -1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    dx = 1

                # 交互键 E 或 回车
                if event.key in (pygame.K_e, pygame.K_RETURN) and dx == 0 and dy == 0:
                    game_log('E pressed (interact)')
                    # 检查四邻是否有 NPC
                    px, py = player.x, player.y
                    neighbors = [(px+1,py),(px-1,py),(px,py+1),(px,py-1)]
                    found = None
                    for nx, ny in neighbors:
                        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and level[ny][nx] == 'N':
                            found = (nx, ny)
                            break
                    game_log(f'neighbor scan result: {found}')
                    # 交互不应触发地图重生；只读取 NPC 对话并显示
                    if found is not None:
                        dialog_active = True
                        # 从 npcs 字典中读取对话内容
                        entry = npcs.get(found)
                        game_log(f'interact found at {found} entry={entry}')
                        if entry and 'dialog' in entry:
                            # 复制一份对话列表以防止共享引用
                            dialog_lines = entry['dialog'][:]
                        else:
                            # 回退对话（防止空列表导致死循环）
                            dialog_lines = [
                                "你好，旅行者。欢迎来到字符世界！",
                                "按 E 或 空格 翻页，Esc 关闭对话。",
                            ]
                        dialog_index = 0
                    continue

                # 攻击键 空格：对相邻敌人造成伤害
                if event.key == pygame.K_SPACE:
                    px, py = player.x, player.y
                    neighbors = [(px+1,py),(px-1,py),(px,py+1),(px,py-1)]
                    for nx, ny in neighbors:
                        ent = entity_mgr.get_entity_at(nx, ny)
                        if isinstance(ent, entities.Enemy):
                            # 造成伤害并触发敌人闪烁（使用 id）
                            ent.hp -= 3
                            enemy_flash[ent.id] = 200
                            print(f'你攻击了敌人 ({nx},{ny})，剩余HP={ent.hp} id={ent.id}')
                            # 添加浮动文本（基于实体 id，并记录最后已知位置）并触发抖动/音效
                            floating_texts.append({'ent_id': ent.id, 'text': f'-3', 'time': 700, 'alpha': 255, 'damage': 3, 'last_pos': (nx * TILE_SIZE, ny * TILE_SIZE)})
                            screen_shake = SCREEN_SHAKE_TIME
                            if hit_sound:
                                try:
                                    hit_sound.play()
                                except Exception:
                                    pass
                            if ent.hp <= 0:
                                # 移除实体并清理地图与闪烁记录（使用 id）
                                entity_mgr.remove(ent)
                                if ent.id in enemy_flash:
                                    del enemy_flash[ent.id]
                                set_tile(level, nx, ny, '.')
                            break

                # 每次按键（瞬态）中按下冲刺键时可以播放小提示音（非循环）
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    if sprint_sound:
                        try:
                            sprint_sound.play()
                        except Exception:
                            pass

                # 调试按键：按 K 输出当前实体列表与周边格子（用于排查不动的敌人）
                if event.key == pygame.K_k:
                    print('[debug] Entities:')
                    for ent in entity_mgr.entities_by_id.values():
                        ex, ey = ent.x, ent.y
                        ch = level[ey][ex] if 0 <= ey < HEIGHT and 0 <= ex < WIDTH else '?'
                        neigh = {}
                        for dxn, dyn, name in ((1,0,'R'),(-1,0,'L'),(0,1,'D'),(0,-1,'U')):
                            tx, ty = ex + dxn, ey + dyn
                            if 0 <= ty < HEIGHT and 0 <= tx < WIDTH:
                                neigh[name] = level[ty][tx]
                            else:
                                neigh[name] = None
                        print(f'  id={ent.id} pos=({ex},{ey}) hp={getattr(ent,"hp",None)} dir={getattr(ent,"dir",None)} tile={ch} neigh={neigh}')

                # NOTE: 实际的持续按键移动在事件循环之后的按键状态处理中处理

        # 敌人行为更新：委托给 entity_mgr（返回事件列表，例如攻击事件）
            evts = entity_mgr.update(level, (player.x, player.y), WIDTH, HEIGHT)
        for ev in evts:
            if ev.get('type') == 'attack':
                px_ev, py_ev = ev.get('pos')
                dmg = int(ev.get('damage', 1))
                attacker_id = ev.get('attacker_id')
                # delegate damage handling to player object (it enforces i-frames)
                if player.i_frames <= 0:
                    damaged = player.apply_damage(dmg)
                    if damaged:
                        print(f'敌人攻击了你！ 你的HP={player.hp}')
                        # Prefer ent_id-based floating text so it follows the entity; fallback to static x/y
                        if attacker_id is not None:
                            floating_texts.append({'ent_id': attacker_id, 'text': f'-{dmg}', 'time': 700, 'alpha': 255, 'damage': dmg, 'last_pos': (px_ev * TILE_SIZE, py_ev * TILE_SIZE)})
                        else:
                            px_scr = px_ev * TILE_SIZE
                            py_scr = py_ev * TILE_SIZE
                            floating_texts.append({'x': px_scr, 'y': py_scr, 'text': f'-{dmg}', 'time': 700, 'alpha': 255, 'damage': dmg})
                        screen_shake = SCREEN_SHAKE_TIME
                        if hit_sound:
                            try:
                                hit_sound.play()
                            except Exception:
                                pass
                        if player.hp <= 0:
                            print('你死了。游戏结束。')
                            running = False

        # 按摄像机视图逐瓦片绘制（提高性能）
        # 目标摄像机中心（像素坐标）
        target_px = (player.x * TILE_SIZE + TILE_SIZE // 2, player.y * TILE_SIZE + TILE_SIZE // 2)
        world_px_w = WIDTH * TILE_SIZE
        world_px_h = HEIGHT * TILE_SIZE
        target_cam_x = target_px[0] - view_px_w // 2
        target_cam_y = target_px[1] - view_px_h // 2
        # clamp target
        target_cam_x = max(0, min(target_cam_x, max(0, world_px_w - view_px_w)))
        target_cam_y = max(0, min(target_cam_y, max(0, world_px_h - view_px_h)))

        # 平滑相机：带死区（deadzone）和可配置 lerp
        deadzone_px = cam_deadzone * TILE_SIZE
        if 'cam_x' not in locals():
            cam_x = target_cam_x
            cam_y = target_cam_y
        else:
            dx_cam = target_cam_x - cam_x
            if abs(dx_cam) > deadzone_px:
                cam_x = cam_x + dx_cam * cam_lerp
            dy_cam = target_cam_y - cam_y
            if abs(dy_cam) > deadzone_px:
                cam_y = cam_y + dy_cam * cam_lerp
            # clamp again to world bounds
            cam_x = max(0, min(cam_x, max(0, world_px_w - view_px_w)))
            cam_y = max(0, min(cam_y, max(0, world_px_h - view_px_h)))

        # clamp again to world bounds for the initial branch as well
        if 'cam_x' not in locals():
            # ensure cam_x/cam_y are clamped even when first initialized
            cam_x = max(0, min(target_cam_x, max(0, world_px_w - view_px_w)))
            cam_y = max(0, min(target_cam_y, max(0, world_px_h - view_px_h)))

        # 计算屏幕抖动偏移（用于世界绘制与浮动文字） —— 必须在绘制瓦片之前定义
        if screen_shake > 0:
            amp = int(SCREEN_SHAKE_AMPLITUDE * (screen_shake / SCREEN_SHAKE_TIME))
            try:
                ox = random.randint(-amp, amp)
                oy = random.randint(-amp, amp)
            except Exception:
                ox = oy = 0
        else:
            ox = oy = 0

        # 计算可见 tile 范围
        x0 = max(0, int(cam_x // TILE_SIZE))
        y0 = max(0, int(cam_y // TILE_SIZE))
        x1 = min(WIDTH, int((cam_x + view_px_w) // TILE_SIZE) + 1)
        y1 = min(HEIGHT, int((cam_y + view_px_h) // TILE_SIZE) + 1)

        # 绘制可见瓦片
        screen.fill((0, 0, 0))
        for y in range(y0, y1):
            row = level[y]
            for x in range(x0, x1):
                ch = row[x]
                color = (200, 200, 200)
                if ch == '#':
                    color = (100, 100, 100)
                elif ch == '@':
                    color = (255, 215, 0)
                    if player.flash_time > 0:
                        color = (255, 255, 255)
                elif ch == 'X':
                    color = (150, 255, 150)
                elif ch == 'N':
                    color = (180, 150, 255)
                elif ch == 'E':
                    color = (220, 100, 100)
                    ent_here = entity_mgr.get_entity_at(x, y)
                    if ent_here and enemy_flash.get(getattr(ent_here, 'id', None), 0) > 0:
                        color = (255, 180, 180)

                surf = font.render(ch, True, color)
                px = x * TILE_SIZE - cam_x + ox
                py = y * TILE_SIZE - cam_y + oy
                screen.blit(surf, (int(px), int(py)))

        # 对话框与玩家 HP 改为屏幕空间绘制（稍后在屏幕上绘制），
        # 浮动文字仍在 world_surf 上（世界坐标），随后裁切到视窗

        # 使用 ui 模块渲染浮动文本（并自动更新它们的 time/y）
        def position_lookup(ent_id):
            ent = entity_mgr.get_entity_by_id(ent_id)
            if ent:
                return (ent.x * TILE_SIZE, ent.y * TILE_SIZE)
            return None

        # world_to_screen：把世界像素坐标映射到屏幕像素坐标，包含相机偏移与屏幕抖动
        def world_to_screen(wx_px, wy_px):
            sx = wx_px - cam_x + ox
            sy = wy_px - cam_y + oy
            return sx, sy

        # 屏幕空间：绘制玩家 HUD（HP + stamina + 冷却指示器）
        ui.draw_player_hud(screen, player, ox, oy, view_px_w, font_path=used_path)

        # 屏幕空间：对话框（底部）
        if dialog_active:
            # Safety checks to avoid a stuck dialog state where dialog_lines is empty
            game_log(f'rendering dialog? dialog_index={dialog_index} len={len(dialog_lines)}')
            if not dialog_lines:
                game_log('[warn] dialog_active True but dialog_lines is empty -> populating fallback dialog')
                dialog_lines = [
                    "你好，旅行者。欢迎来到字符世界！",
                    "按 E 或 空格 翻页，Esc 关闭对话。",
                ]
                dialog_index = 0
            elif dialog_index < 0 or dialog_index >= len(dialog_lines):
                game_log(f'[warn] dialog_index out of range ({dialog_index}) for dialog_lines length {len(dialog_lines)} -> closing dialog')
                dialog_active = False
            else:
                pad = 8
                box_h = TILE_SIZE * 3
                box_w = view_px_w - pad * 2
                game_log(f'dialog box size box_w={box_w} box_h={box_h} view_px_w={view_px_w} view_px_h={view_px_h}')
                box_x = pad + ox
                box_y = view_px_h - box_h - pad + oy
                # 防御性：确保 box_w/box_h 为正
                if box_w > 0 and box_h > 0:
                    s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                    s.fill((0, 0, 0, 200))
                    screen.blit(s, (box_x, box_y))
                    line_y = box_y + 8
                    # dialog_lines 的每一项通常是一个字符串；分行显示
                    for i, line in enumerate(dialog_lines[dialog_index].split('\n')):
                        surf = font.render(line, True, (240, 240, 240))
                        screen.blit(surf, (box_x + 8, line_y + i * TILE_SIZE))
                else:
                    game_log(f'[warn] dialog box dimensions invalid: box_w={box_w} box_h={box_h}')

        # 更新玩家内部计时（闪烁 / i-frames / move timer / sprint cooldown / regen pause）
        prev_sprint_cd = getattr(player, 'sprint_cooldown', 0)
        player.update_timers(dt)

        # 更新敌人闪烁计时并清理已结束的（键为 ent_id）
        for ent_id in list(enemy_flash.keys()):
            enemy_flash[ent_id] -= dt
            if enemy_flash[ent_id] <= 0:
                del enemy_flash[ent_id]

        # 减少屏幕抖动计时
        if screen_shake > 0:
            screen_shake -= dt
            if screen_shake < 0:
                screen_shake = 0

        # 在屏幕上渲染浮动文字（传入 world_to_screen 以便浮动文字随相机/抖动移动）
        try:
            ui.draw_floating_texts(screen, floating_texts, TILE_SIZE, dt, used_font_path=used_path, position_lookup=position_lookup, world_to_screen=world_to_screen)
        except Exception:
            # 防御性：若 UI 渲染出错，继续运行不崩溃
            pass

        # 将 Tab 键绑定为“按住显示指示器”：若按住则把鼠标屏幕坐标转换为世界像素坐标并显示指示器
        try:
            keys_state = pygame.key.get_pressed()
            if keys_state[pygame.K_TAB]:
                # Compass: 指向当前楼层记录的 exit_pos（若存在）
                if exit_pos is not None:
                    ex, ey = exit_pos
                    pending_target = (ex * TILE_SIZE + TILE_SIZE//2, ey * TILE_SIZE + TILE_SIZE//2)
                else:
                    pending_target = None
            else:
                pending_target = None
        except Exception:
            pending_target = None

        if pending_target is not None:
            ui.draw_target_indicator(screen, player, pending_target, cam_x, cam_y, ox, oy, view_px_w, view_px_h, font_path=used_path)

        # 持续按键处理：自动移动与冲刺逻辑（若不在对话或楼层过场中）
        if not dialog_active and not floor_transition:
            keys = pygame.key.get_pressed()
            # 方向输入优先级：只允许一个方向（或选择最近按下的）
            kx = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            kx_l = keys[pygame.K_LEFT] or keys[pygame.K_a]
            ky_u = keys[pygame.K_UP] or keys[pygame.K_w]
            ky_d = keys[pygame.K_DOWN] or keys[pygame.K_s]

            dx = dy = 0
            if kx and not kx_l:
                dx = 1
            elif kx_l and not kx:
                dx = -1
            elif ky_u and not ky_d:
                dy = -1
            elif ky_d and not ky_u:
                dy = 1

            # 冲刺键：左 Shift 或右 Shift
            is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

            # Delegate movement and stamina handling to Player
            moved_result = {'moved': False}
            if dx != 0 or dy != 0:
                moved_result = player.attempt_move(level, dx, dy, is_sprinting, dt, WIDTH, HEIGHT)

                if moved_result.get('moved'):
                    px, py = moved_result.get('old')
                    nx, ny = moved_result.get('new')
                    target = moved_result.get('target')
                    # if stepped on exit X, trigger floor transition
                    if target == 'X':
                        import time
                        # clear previous exit_pos immediately to avoid compass pointing to old floor
                        exit_pos = None
                        try:
                            floor_number += 1
                        except NameError:
                            floor_number = 2
                        game_log(f'Starting floor transition to {floor_number}')
                        if seed is None:
                            gen_seed = int(time.time() * 1000)
                        else:
                            try:
                                gen_seed = int(seed) + floor_number
                            except Exception:
                                gen_seed = int(time.time() * 1000)
                        
                        # CRITICAL FIX: Set pending_floor with generation parameters
                        pending_floor = {
                            'seed': gen_seed,
                            'floor': floor_number,
                            'width': mw,
                            'height': mh,
                            'rooms': rooms,
                            'enemies': enemies,
                            'min_room': min_room,
                            'max_room': max_room,
                            'corridor_radius': corridor_radius
                        }
                        
                        floor_transition = {'time': 1100, 'text': f'第 {floor_number} 层'}
                        write_exit_log(f'Floor transition triggered: floor {floor_number}, seed {gen_seed}')

                    # spawn sprint particles when sprinting
                    if moved_result.get('sprinting'):
                        # spawn particle via player helper
                        player.spawn_sprint_particle(px, py, dx, dy)
            else:
                # no movement input: passive stamina regen
                player.passive_stamina_update(dt)

        # sprint cooldown transition: play ready sound when it just ended
        if prev_sprint_cd > 0 and player.sprint_cooldown == 0:
            if sprint_ready_sound:
                try:
                    sprint_ready_sound.play()
                except Exception:
                    pass
        # update cooldown animation (pulse while cooling)
        try:
            sprint_cd_anim = min(1.0, max(0.0, player.sprint_cooldown / player.SPRINT_COOLDOWN_AFTER_EXHAUST))
        except Exception:
            sprint_cd_anim = 0.0

        # HUD 绘制由 ui.draw_player_hud 统一处理（已经在上方调用），无需在此重复绘制体力/冷却图标

        # 更新并渲染冲刺粒子（由 ui 模块统一渲染）
        try:
            player.update_particles(dt, TILE_SIZE)
            ui.draw_sprint_particles(screen, player, world_to_screen, font)
        except Exception:
            pass

        # 楼层切换过场：若存在，绘制覆盖并倒计时；倒计时结束时执行实际的楼层生成/切换
        if floor_transition:
            # 绘制半透明遮罩
            try:
                overlay = pygame.Surface((view_px_w, view_px_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                # 居中显示文本
                big = utils.load_preferred_font(36)[0]
                txt = floor_transition.get('text', '')
                surf = big.render(txt, True, (240, 240, 240))
                sx = (view_px_w - surf.get_width()) // 2
                sy = (view_px_h - surf.get_height()) // 2
                screen.blit(surf, (sx, sy))
            except Exception:
                pass

            # 倒计时并在结束时应用 pending floor
            floor_transition['time'] -= dt
            if floor_transition['time'] <= 0:
                # 执行楼层生成（使用 pending_floor 中的 seed 等参数）
                try:
                    params = pending_floor or {}
                    gen_seed = params.get('seed')
                    floor_number = params.get('floor', getattr(sys.modules[__name__], 'floor_number', 2))
                    gen_width = params.get('width', mw)
                    gen_height = params.get('height', mh)
                    gen_rooms = params.get('rooms', rooms)
                    gen_enemies = params.get('enemies', enemies)
                    gen_min_room = params.get('min_room', min_room)
                    gen_max_room = params.get('max_room', max_room)
                    gen_corridor_radius = params.get('corridor_radius', corridor_radius)
                    
                    write_exit_log(f'Generating floor {floor_number} with seed {gen_seed}, size {gen_width}x{gen_height}')
                    
                    # 重新生成地牢
                    level = utils.generate_dungeon(gen_width, gen_height, room_attempts=gen_rooms, 
                                                 num_enemies=gen_enemies, seed=gen_seed, 
                                                 min_room=gen_min_room, max_room=gen_max_room, 
                                                 corridor_radius=gen_corridor_radius)
                    WIDTH = len(level[0]) if level else 0
                    HEIGHT = len(level)
                    # 重建实体管理器
                    entity_mgr = entities.EntityManager()
                    enemies_path = os.path.join(os.path.dirname(__file__), 'data', 'enemies.json')
                    if os.path.exists(enemies_path):
                        for y, row in enumerate(level):
                            for x, ch in enumerate(row):
                                if ch == 'E':
                                    set_tile(level, x, y, '.')
                    entity_mgr.load_from_file(enemies_path, level=level)
                    if not any(isinstance(e, entities.Enemy) for e in entity_mgr.entities_by_id.values()):
                        entity_mgr.load_from_level(level)
                        entity_mgr.place_entity_near(level, WIDTH, HEIGHT)

                    # 重置视觉/对话状态
                    enemy_flash = {}
                    floating_texts = []
                    dialog_active = False
                    dialog_lines = []
                    dialog_index = 0
                    # 重新加载 NPCs
                    npcs = dialogs_mod.load_npcs(level, WIDTH, HEIGHT)
                    # (exit/player placement responsibility moved into generate_dungeon)
                    # compute exit_pos for the new level so compass uses stable value
                    try:
                        found = None
                        for yrow, row in enumerate(level):
                            xcol = row.find('X')
                            if xcol != -1:
                                found = (xcol, yrow)
                                break
                        exit_pos = found
                    except Exception:
                        exit_pos = None
                    
                    # Find player position before writing debug snapshots
                    new_pos = find_player(level)
                    
                    # dump debug snapshot for this floor
                    try:
                        dbg_dir = os.path.join(os.path.dirname(__file__), 'data', 'debug')
                        os.makedirs(dbg_dir, exist_ok=True)
                        dbg_path = os.path.join(dbg_dir, f'last_level_floor_{floor_number}.txt')
                        with open(dbg_path, 'w', encoding='utf-8') as df:
                            df.write('\n'.join(level))
                            df.write('\n\n')
                            df.write(f'floor={floor_number} exit_pos={exit_pos} player_pos={new_pos}\n')
                        write_exit_log(f'Wrote floor snapshot: {dbg_path}')
                    except Exception as e:
                        write_exit_log(f'Failed to write floor snapshot: {e}')
                    # also write a post-entity-load snapshot (after entities/npcs placed)
                    try:
                        dbg_path2 = os.path.join(dbg_dir, f'last_level_floor_{floor_number}_after_entities.txt')
                        with open(dbg_path2, 'w', encoding='utf-8') as df2:
                            df2.write('\n'.join(level))
                            df2.write('\n\n')
                            df2.write(f'floor={floor_number} exit_pos={exit_pos} player_pos={new_pos}\n')
                        write_exit_log(f'Wrote post-entity floor snapshot: {dbg_path2}')
                    except Exception as e:
                        write_exit_log(f'Failed to write post-entity floor snapshot: {e}')
                    # 重新定位玩家和相机（保留 Player 对象，更新位置）
                    if new_pos:
                        player.x, player.y = new_pos
                    cam_x = player.x * TILE_SIZE - view_px_w // 2
                    cam_y = player.y * TILE_SIZE - view_px_h // 2
                    cam_x = max(0, min(cam_x, max(0, WIDTH * TILE_SIZE - view_px_w)))
                    cam_y = max(0, min(cam_y, max(0, HEIGHT * TILE_SIZE - view_px_h)))
                except Exception:
                    # on failure, just log and continue
                    game_log('floor transition generation failed')
                # 清理过场状态
                floor_transition = None
                pending_floor = None

        # render in-game logs so the user can see debug messages when console isn't visible
        log_font = utils.load_preferred_font(14)[0]
        lx = 6
        ly = 6
        for i, msg in enumerate(game_logs):
            try:
                surf = log_font.render(msg, True, (200, 200, 200))
                screen.blit(surf, (lx, ly + i * 16))
            except Exception:
                pass

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
