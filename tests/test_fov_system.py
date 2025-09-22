"""
基础视野系统测试脚本
测试FOV系统的各项功能
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from game.fov import FOVSystem, TileVisibility


def test_fov_basic():
    """测试基础FOV功能"""
    print("=== 测试基础FOV功能 ===")
    
    # 创建一个简单的测试地图
    test_map = [
        "########",
        "#......#",
        "#..@...#",
        "#......#",
        "########"
    ]
    
    # 创建FOV系统
    fov = FOVSystem(sight_radius=3)
    
    # 玩家在 (3, 2)
    player_x, player_y = 3, 2
    
    # 计算可见区域
    visible = fov.calculate_fov(player_x, player_y, test_map)
    
    print(f"玩家位置: ({player_x}, {player_y})")
    print(f"视野半径: {fov.get_sight_radius()}")
    print(f"可见瓦片数量: {len(visible)}")
    
    # 打印可见性地图
    print("\n可见性地图 (V=可见, E=已探索, H=隐藏):")
    for y in range(len(test_map)):
        line = ""
        for x in range(len(test_map[y])):
            visibility = TileVisibility.get_visibility_state(x, y, fov)
            if visibility == TileVisibility.VISIBLE:
                line += "V"
            elif visibility == TileVisibility.EXPLORED:
                line += "E"
            else:
                line += "H"
        print(line)
    
    # 测试特定位置
    test_positions = [(3, 2), (3, 1), (1, 1), (0, 0), (7, 4)]
    print(f"\n位置可见性测试:")
    for x, y in test_positions:
        visible = fov.is_visible(x, y)
        explored = fov.is_explored(x, y)
        print(f"  ({x}, {y}): 可见={visible}, 已探索={explored}")


def test_fov_movement():
    """测试移动后的FOV更新"""
    print("\n=== 测试FOV移动更新 ===")
    
    test_map = [
        "##########",
        "#........#",
        "#........#",
        "#...@....#",
        "#........#",
        "#........#",
        "##########"
    ]
    
    fov = FOVSystem(sight_radius=2)
    
    # 初始位置
    x, y = 4, 3
    fov.calculate_fov(x, y, test_map)
    print(f"初始位置 ({x}, {y}), 可见瓦片: {len(fov.get_visible_tiles())}")
    print(f"已探索瓦片: {len(fov.get_explored_tiles())}")
    
    # 移动后
    x, y = 6, 3
    fov.calculate_fov(x, y, test_map)
    print(f"移动后位置 ({x}, {y}), 可见瓦片: {len(fov.get_visible_tiles())}")
    print(f"已探索瓦片: {len(fov.get_explored_tiles())}")
    
    # 验证之前探索的区域仍然被记录
    if fov.is_explored(4, 3):
        print("✅ 之前的位置仍然标记为已探索")
    else:
        print("❌ 之前的位置未标记为已探索")


def test_fov_radius():
    """测试不同视野半径"""
    print("\n=== 测试不同视野半径 ===")
    
    test_map = [
        "############",
        "#..........#",
        "#..........#",
        "#..........#",
        "#.....@....#",
        "#..........#",
        "#..........#",
        "#..........#",
        "############"
    ]
    
    player_x, player_y = 6, 4
    
    for radius in [2, 4, 6]:
        fov = FOVSystem(sight_radius=radius)
        visible = fov.calculate_fov(player_x, player_y, test_map)
        print(f"视野半径 {radius}: 可见瓦片数量 {len(visible)}")


def test_fov_clear():
    """测试清除探索记录"""
    print("\n=== 测试清除探索记录 ===")
    
    test_map = [
        "#####",
        "#...#",
        "#.@.#",
        "#...#",
        "#####"
    ]
    
    fov = FOVSystem(sight_radius=2)
    fov.calculate_fov(2, 2, test_map)
    
    print(f"探索前: 已探索瓦片 {len(fov.get_explored_tiles())}")
    
    fov.clear_exploration()
    
    print(f"清除后: 已探索瓦片 {len(fov.get_explored_tiles())}")
    print(f"清除后: 可见瓦片 {len(fov.get_visible_tiles())}")
    
    if len(fov.get_explored_tiles()) == 0 and len(fov.get_visible_tiles()) == 0:
        print("✅ 探索记录清除成功")
    else:
        print("❌ 探索记录清除失败")


if __name__ == "__main__":
    print("开始FOV系统测试...\n")
    
    try:
        test_fov_basic()
        test_fov_movement()
        test_fov_radius()
        test_fov_clear()
        
        print("\n✅ 所有FOV测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()