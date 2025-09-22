import pygame
import random


class Player:
    def __init__(self, x, y, hp=10, move_cooldown=150, max_stamina=100.0, stamina_regen=6.0, sprint_cost=35.0, sprint_cooldown_ms=2000, sprint_multiplier=0.6):
        self.x = x
        self.y = y
        self.hp = hp
        # visual/iframes
        self.flash_time = 0
        self.PLAYER_FLASH_DURATION = 400
        self.i_frames = 0
        self.PLAYER_IFRAMES = 800

        # movement timing
        self.MOVE_COOLDOWN = move_cooldown
        self.move_timer = 0
        self.SPRINT_MULTIPLIER = sprint_multiplier

        # stamina
        self.max_stamina = float(max_stamina)
        self.stamina = float(self.max_stamina)
        self.stamina_regen_per_sec = float(stamina_regen)
        self.sprint_cost_per_sec = float(sprint_cost)

        # sprint cooldown after exhaust
        self.sprint_cooldown = 0
        self.SPRINT_COOLDOWN_AFTER_EXHAUST = int(sprint_cooldown_ms)

        # regen pause (ms) after sprint action
        self.REGEN_PAUSE_AFTER_SPRINT_MS = 300
        self.regen_pause_timer = 0

        # sprint particles for visual tail (list of dicts with x_px,y_px,vx,vy,time)
        self.sprint_particles = []

    def spawn_sprint_particle(self, tile_x, tile_y, dx, dy):
        bx = tile_x * 24 + 24 // 2
        by = tile_y * 24 + 24 // 2
        p_vx = -dx * (1 + random.random() * 0.6) * 0.6
        p_vy = -dy * (1 + random.random() * 0.6) * 0.6
        self.sprint_particles.append({'x_px': bx, 'y_px': by, 'vx': p_vx, 'vy': p_vy, 'time': 300})

    def update_particles(self, dt, TILE_SIZE=24):
        # progress and remove expired particles
        for p in list(self.sprint_particles):
            p['time'] -= dt
            if p['time'] <= 0:
                try:
                    self.sprint_particles.remove(p)
                except Exception:
                    pass
                continue
            p['x_px'] += p['vx'] * (dt / 16.0)
            p['y_px'] += p['vy'] * (dt / 16.0)

    @classmethod
    def from_level(cls, level, **kwargs):
        for y, row in enumerate(level):
            x = row.find('@')
            if x != -1:
                return cls(x, y, **kwargs)
        return None

    def position(self):
        return (self.x, self.y)

    def apply_damage(self, dmg):
        if self.i_frames > 0:
            return False
        self.hp -= int(dmg)
        self.flash_time = self.PLAYER_FLASH_DURATION
        self.i_frames = self.PLAYER_IFRAMES
        return True

    def update_timers(self, dt):
        if self.flash_time > 0:
            self.flash_time -= dt
            if self.flash_time < 0:
                self.flash_time = 0
        if self.i_frames > 0:
            self.i_frames -= dt
            if self.i_frames < 0:
                self.i_frames = 0
        if self.move_timer > 0:
            self.move_timer -= dt
            if self.move_timer < 0:
                self.move_timer = 0
        if self.sprint_cooldown > 0:
            self.sprint_cooldown -= dt
            if self.sprint_cooldown < 0:
                self.sprint_cooldown = 0
        if self.regen_pause_timer > 0:
            self.regen_pause_timer -= dt
            if self.regen_pause_timer < 0:
                self.regen_pause_timer = 0

    def _compute_sprint_consumption(self, delta_ms):
        frac = max(0.0, min(1.0, self.stamina / self.max_stamina))
        mult = 1.0 + (1.0 - frac) ** 1.5 * 1.2
        return self.sprint_cost_per_sec * mult * (delta_ms / 1000.0)

    def _compute_stamina_regen(self, delta_ms):
        frac = max(0.0, min(1.0, self.stamina / self.max_stamina))
        factor = 0.25 + 0.75 * (frac ** 0.5)
        return self.stamina_regen_per_sec * factor * (delta_ms / 1000.0)

    def attempt_move(self, level, dx, dy, is_sprinting, dt, WIDTH, HEIGHT):
        # returns dict: {moved:bool, old:(x,y), new:(x,y), target:ch, sprinting:bool, drained:bool}
        result = {'moved': False, 'old': (self.x, self.y), 'new': (self.x, self.y), 'target': None, 'sprinting': False, 'drained': False}

        # decide sprinting_this_frame based on stamina and cooldown
        sprinting_this_frame = is_sprinting and self.stamina > 0.0 and self.sprint_cooldown <= 0
        result['sprinting'] = sprinting_this_frame

        # determine cooldown for movement
        cur_cooldown = self.MOVE_COOLDOWN
        if sprinting_this_frame:
            cur_cooldown = max(30, int(self.MOVE_COOLDOWN * self.SPRINT_MULTIPLIER))

        # decrement move timer handled externally via update_timers; here check
        if self.move_timer > 0:
            # cannot move yet
            # still consume stamina if sprinting but not moving? only consume on move
            return result

        if dx == 0 and dy == 0:
            # no movement input
            # regen or pause handled in stamina update
            return result

        nx = self.x + dx
        ny = self.y + dy
        if not (0 <= nx < WIDTH and 0 <= ny < HEIGHT):
            return result
        target = level[ny][nx]
        if target in ('#', 'N', 'E'):
            return result

        # perform move
        level[self.y] = level[self.y][:self.x] + '.' + level[self.y][self.x+1:]
        level[ny] = level[ny][:nx] + '@' + level[ny][nx+1:]
        self.x = nx
        self.y = ny
        result['moved'] = True
        result['new'] = (self.x, self.y)
        result['target'] = target

        # set new move timer
        self.move_timer = cur_cooldown

        # stamina consumption or pause
        if sprinting_this_frame:
            amt = self._compute_sprint_consumption(dt)
            self.stamina -= amt
            self.regen_pause_timer = self.REGEN_PAUSE_AFTER_SPRINT_MS
            result['drained'] = True
        else:
            # if regen paused, don't regen here
            if self.regen_pause_timer <= 0:
                self.stamina += self._compute_stamina_regen(dt)

        # clamp and exhaustion
        if self.stamina <= 0.0:
            self.stamina = 0.0
            if result['drained']:
                self.sprint_cooldown = self.SPRINT_COOLDOWN_AFTER_EXHAUST
        else:
            self.stamina = min(self.max_stamina, self.stamina)

        return result

    def passive_stamina_update(self, dt):
        # called when not moving; handles regen pause and natural regen
        if self.regen_pause_timer > 0:
            self.regen_pause_timer -= dt
            if self.regen_pause_timer < 0:
                self.regen_pause_timer = 0
            return
        self.stamina += self._compute_stamina_regen(dt)
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina
