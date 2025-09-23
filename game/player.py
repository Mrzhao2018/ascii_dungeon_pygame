import random
from .fov import FOVSystem
from .experience import (
    calculate_exp_required, 
    calculate_exp_to_next_level, 
    get_level_bonuses,
    EXPERIENCE_CONFIG
)


class Player:
    def __init__(
        self,
        x,
        y,
        hp=10,
        move_cooldown=150,
        max_stamina=100.0,
        stamina_regen=6.0,
        sprint_cost=35.0,
        sprint_cooldown_ms=2000,
        sprint_multiplier=0.6,
        sight_radius=6,
    ):
        self.x = x
        self.y = y
        
        # 经验和等级系统
        self.level = 1
        self.experience = 0
        self.base_hp = hp
        self.hp = hp
        
        # 基础属性（用于计算等级加成）
        self.base_max_stamina = float(max_stamina)
        self.base_stamina_regen = float(stamina_regen)
        self.base_sprint_cost = float(sprint_cost)
        self.base_move_cooldown = move_cooldown
        self.base_sprint_cooldown_ms = int(sprint_cooldown_ms)
        self.base_iframes = 800
        self.base_sight_radius = sight_radius
        
        # FOV系统（在应用加成之前初始化）
        self.fov_system = FOVSystem(self.base_sight_radius)
        
        # 应用当前等级的属性加成
        self._apply_level_bonuses()
        
        # visual/iframes
        self.flash_time = 0
        self.PLAYER_FLASH_DURATION = 400
        self.i_frames = 0
        self.PLAYER_IFRAMES = self.base_iframes

        # movement timing
        self.MOVE_COOLDOWN = self.base_move_cooldown
        self.move_timer = 0
        self.SPRINT_MULTIPLIER = sprint_multiplier

        # stamina
        self.max_stamina = float(self.base_max_stamina)
        self.stamina = float(self.max_stamina)
        self.stamina_regen_per_sec = float(self.base_stamina_regen)
        self.sprint_cost_per_sec = float(self.base_sprint_cost)

        # sprint cooldown after exhaust
        self.sprint_cooldown = 0
        self.SPRINT_COOLDOWN_AFTER_EXHAUST = self.base_sprint_cooldown_ms

        # regen pause (ms) after sprint action
        self.REGEN_PAUSE_AFTER_SPRINT_MS = 300
        self.regen_pause_timer = 0

        # sprint particles for visual tail (list of dicts with x_px,y_px,vx,vy,time)
        self.sprint_particles = []

        # 升级提示
        self.level_up_notification = None
        self.level_up_timer = 0

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
        
        # 更新升级提示计时器
        self.update_level_up_notification(dt)

    def _compute_sprint_consumption(self, delta_ms):
        frac = max(0.0, min(1.0, self.stamina / self.max_stamina))
        mult = 1.0 + (1.0 - frac) ** 1.5 * 1.2
        return self.sprint_cost_per_sec * mult * (delta_ms / 1000.0)

    def _compute_stamina_regen(self, delta_ms):
        frac = max(0.0, min(1.0, self.stamina / self.max_stamina))
        factor = 0.25 + 0.75 * (frac**0.5)
        return self.stamina_regen_per_sec * factor * (delta_ms / 1000.0)

    def attempt_move(self, level, dx, dy, is_sprinting, dt, WIDTH, HEIGHT):
        # returns dict: {moved:bool, old:(x,y), new:(x,y), target:ch, sprinting:bool, drained:bool}
        result = {
            'moved': False,
            'old': (self.x, self.y),
            'new': (self.x, self.y),
            'target': None,
            'sprinting': False,
            'drained': False,
        }

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
        level[self.y] = level[self.y][: self.x] + '.' + level[self.y][self.x + 1 :]
        level[ny] = level[ny][:nx] + '@' + level[ny][nx + 1 :]
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

    def update_fov(self, level):
        """更新玩家视野"""
        if self.fov_system:
            self.fov_system.calculate_fov(self.x, self.y, level)

    def is_tile_visible(self, x, y):
        """检查瓦片是否可见"""
        return self.fov_system.is_visible(x, y) if self.fov_system else True

    def is_tile_explored(self, x, y):
        """检查瓦片是否已探索"""
        return self.fov_system.is_explored(x, y) if self.fov_system else True

    def get_sight_radius(self):
        """获取视野半径"""
        return self.fov_system.get_sight_radius() if self.fov_system else 6

    def set_sight_radius(self, radius):
        """设置视野半径"""
        if self.fov_system:
            self.fov_system.set_sight_radius(radius)

    def clear_exploration(self):
        """清除探索记录（用于换层）"""
        if self.fov_system:
            self.fov_system.clear_exploration()

    # ===================
    # 经验和升级系统
    # ===================

    def _apply_level_bonuses(self):
        """应用当前等级的属性加成"""
        bonuses = get_level_bonuses(self.level)
        
        # 更新最大生命值和当前生命值
        old_max_hp = getattr(self, 'max_hp', self.base_hp)
        self.max_hp = self.base_hp + bonuses['hp_bonus']
        
        # 如果是升级，按比例增加当前生命值
        if hasattr(self, 'hp') and old_max_hp > 0:
            hp_ratio = self.hp / old_max_hp
            self.hp = int(self.max_hp * hp_ratio)
        else:
            self.hp = self.max_hp
        
        # 更新体力相关属性
        old_max_stamina = getattr(self, 'max_stamina', self.base_max_stamina)
        self.max_stamina = self.base_max_stamina + bonuses['stamina_bonus']
        
        # 按比例更新当前体力
        if hasattr(self, 'stamina') and old_max_stamina > 0:
            stamina_ratio = self.stamina / old_max_stamina
            self.stamina = self.max_stamina * stamina_ratio
        else:
            self.stamina = self.max_stamina
        
        # 更新体力恢复速度
        regen_multiplier = 1.0 + bonuses['stamina_regen_bonus']
        self.stamina_regen_per_sec = self.base_stamina_regen * regen_multiplier
        
        # 更新冲刺消耗
        cost_multiplier = 1.0 - bonuses['sprint_cost_reduction']
        self.sprint_cost_per_sec = self.base_sprint_cost * cost_multiplier
        
        # 更新移动速度（通过调整移动冷却时间）
        speed_multiplier = 1.0 + bonuses['move_speed_bonus']
        self.MOVE_COOLDOWN = max(50, int(self.base_move_cooldown / speed_multiplier))
        
        # 更新无敌时间
        iframes_multiplier = 1.0 + bonuses['iframes_bonus']
        self.PLAYER_IFRAMES = int(self.base_iframes * iframes_multiplier)
        
        # 更新视野半径
        new_sight_radius = self.base_sight_radius + bonuses['sight_radius_bonus']
        if self.fov_system:
            self.fov_system.set_sight_radius(int(new_sight_radius))

    def gain_experience(self, amount):
        """获得经验值并检查升级"""
        if self.level >= EXPERIENCE_CONFIG["max_level"]:
            return False  # 已达到最大等级
        
        self.experience += amount
        
        # 检查是否升级
        leveled_up = False
        while self.level < EXPERIENCE_CONFIG["max_level"]:
            exp_required = calculate_exp_required(self.level + 1)
            if self.experience >= exp_required:
                self.level += 1
                leveled_up = True
                self._apply_level_bonuses()
                self._trigger_level_up_notification()
            else:
                break
        
        return leveled_up

    def _trigger_level_up_notification(self):
        """触发升级提示"""
        self.level_up_notification = {
            "level": self.level,
            "message": f"升级到 {self.level} 级！",
            "bonuses": get_level_bonuses(self.level)
        }
        self.level_up_timer = 3000  # 显示3秒

    def update_level_up_notification(self, dt):
        """更新升级提示计时器"""
        if self.level_up_timer > 0:
            self.level_up_timer -= dt
            if self.level_up_timer <= 0:
                self.level_up_notification = None

    def get_experience_info(self):
        """获取经验相关信息"""
        current_level_exp = calculate_exp_required(self.level)
        next_level_exp = calculate_exp_required(self.level + 1)
        
        if self.level >= EXPERIENCE_CONFIG["max_level"]:
            return {
                "level": self.level,
                "current_exp": self.experience,
                "exp_in_level": 0,
                "exp_to_next": 0,
                "exp_progress": 1.0,
                "max_level": True
            }
        
        exp_in_level = self.experience - current_level_exp
        exp_to_next = next_level_exp - self.experience
        exp_progress = exp_in_level / (next_level_exp - current_level_exp) if next_level_exp > current_level_exp else 1.0
        
        return {
            "level": self.level,
            "current_exp": self.experience,
            "exp_in_level": exp_in_level,
            "exp_to_next": exp_to_next,
            "exp_progress": exp_progress,
            "max_level": False
        }

    def get_level_bonuses_info(self):
        """获取当前等级的属性加成信息"""
        return get_level_bonuses(self.level)

    def reset_experience(self):
        """重置经验和等级（用于重新开始游戏）"""
        self.level = 1
        self.experience = 0
        self.level_up_notification = None
        self.level_up_timer = 0
        self._apply_level_bonuses()
