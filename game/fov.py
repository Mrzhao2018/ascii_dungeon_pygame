import math
from typing import List, Set, Tuple

"""
基础视野系统 (Field of View)
实现简单的圆形视野计算，后续可以扩展为更复杂的视线系统
"""



class FOVSystem:
    """基础视野系统类"""

    def __init__(self, sight_radius: int = 6):
        """
        初始化视野系统

        Args:
            sight_radius: 玩家视野半径（以瓦片为单位）
        """
        self.sight_radius = sight_radius
        self.visible_tiles: Set[Tuple[int, int]] = set()
        self.previously_seen: Set[Tuple[int, int]] = set()

    def calculate_fov(self, player_x: int, player_y: int, level: List[str]) -> Set[Tuple[int, int]]:
        """
        计算玩家当前可见的所有瓦片

        Args:
            player_x: 玩家X坐标
            player_y: 玩家Y坐标
            level: 地图数据

        Returns:
            可见瓦片坐标的集合
        """
        visible = set()

        # 简单的圆形视野计算
        for dy in range(-self.sight_radius, self.sight_radius + 1):
            for dx in range(-self.sight_radius, self.sight_radius + 1):
                x = player_x + dx
                y = player_y + dy

                # 检查是否在地图边界内
                if not self._is_valid_position(x, y, level):
                    continue

                # 计算距离
                distance = math.sqrt(dx * dx + dy * dy)

                # 在视野半径内
                if distance <= self.sight_radius:
                    visible.add((x, y))

        # 更新可见瓦片集合
        self.visible_tiles = visible

        # 将当前可见的瓦片加入已探索区域
        self.previously_seen.update(visible)

        return visible

    def _is_valid_position(self, x: int, y: int, level: List[str]) -> bool:
        """检查坐标是否在地图边界内"""
        return 0 <= y < len(level) and 0 <= x < len(level[y]) if level else False

    def is_visible(self, x: int, y: int) -> bool:
        """检查特定坐标是否在当前视野内"""
        return (x, y) in self.visible_tiles

    def is_explored(self, x: int, y: int) -> bool:
        """检查特定坐标是否已被探索过"""
        return (x, y) in self.previously_seen

    def get_visible_tiles(self) -> Set[Tuple[int, int]]:
        """获取当前可见的瓦片"""
        return self.visible_tiles.copy()

    def get_explored_tiles(self) -> Set[Tuple[int, int]]:
        """获取所有已探索的瓦片"""
        return self.previously_seen.copy()

    def clear_exploration(self):
        """清除探索记录（用于换层时）"""
        self.visible_tiles.clear()
        self.previously_seen.clear()

    def set_sight_radius(self, radius: int):
        """设置视野半径"""
        self.sight_radius = max(1, radius)

    def get_sight_radius(self) -> int:
        """获取当前视野半径"""
        return self.sight_radius


class TileVisibility:
    """瓦片可见性状态"""

    HIDDEN = 0  # 完全不可见（未探索）
    EXPLORED = 1  # 已探索但当前不可见（雾化）
    VISIBLE = 2  # 当前可见

    @staticmethod
    def get_visibility_state(x: int, y: int, fov_system: FOVSystem) -> int:
        """
        获取瓦片的可见性状态

        Args:
            x: 瓦片X坐标
            y: 瓦片Y坐标
            fov_system: 视野系统实例

        Returns:
            可见性状态（HIDDEN/EXPLORED/VISIBLE）
        """
        if fov_system.is_visible(x, y):
            return TileVisibility.VISIBLE
        elif fov_system.is_explored(x, y):
            return TileVisibility.EXPLORED
        else:
            return TileVisibility.HIDDEN


# 便捷函数
def create_fov_system(sight_radius: int = 6) -> FOVSystem:
    """创建FOV系统实例"""
    return FOVSystem(sight_radius)
