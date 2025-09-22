#!/usr/bin/env python3
"""
测试出口指示器渲染
"""

import os
import sys
import pygame
import time

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import Game

def test_indicator_rendering():
    """Test exit indicator rendering in actual game"""
    print("=== 测试出口指示器渲染 ===")
    
    try:
        # Create game instance
        print("1. 创建游戏实例...")
        game = Game()
        
        print("2. 检查初始状态...")
        print(f"   exit_pos: {game.game_state.exit_pos}")
        print(f"   pending_target: {game.game_state.pending_target}")
        
        # Test Tab key processing
        print("\n3. 模拟Tab键按下...")
        import pygame
        pygame.init()
        
        # Simulate Tab keydown event
        tab_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
        result = game.input_handler.handle_keydown(tab_event)
        
        print(f"   Tab处理结果: {result}")
        print(f"   处理后的pending_target: {game.game_state.pending_target}")
        
        # Check if pending_target is within reasonable bounds
        if game.game_state.pending_target:
            px, py = game.game_state.pending_target
            print(f"   指示器位置: ({px}, {py})")
            print(f"   地图尺寸: {game.game_state.width} x {game.game_state.height}")
            print(f"   像素尺寸: {game.game_state.width * game.config.tile_size} x {game.game_state.height * game.config.tile_size}")
            
            # Check if coordinates are reasonable
            max_x = game.game_state.width * game.config.tile_size
            max_y = game.game_state.height * game.config.tile_size
            
            if 0 <= px <= max_x and 0 <= py <= max_y:
                print("   ✅ 指示器坐标在合理范围内")
            else:
                print("   ❌ 指示器坐标超出地图范围")
        
        # Test camera position impact
        print("\n4. 检查相机位置...")
        print(f"   相机位置: ({game.game_state.cam_x}, {game.game_state.cam_y})")
        print(f"   视口尺寸: {game.renderer.view_px_w} x {game.renderer.view_px_h}")
        
        if game.game_state.pending_target:
            px, py = game.game_state.pending_target
            # Calculate screen position
            screen_x = px - game.game_state.cam_x
            screen_y = py - game.game_state.cam_y
            print(f"   指示器屏幕位置: ({screen_x}, {screen_y})")
            
            # Check if indicator is on screen
            if 0 <= screen_x <= game.renderer.view_px_w and 0 <= screen_y <= game.renderer.view_px_h:
                print("   ✅ 指示器在屏幕可见范围内")
            else:
                print("   ⚠️  指示器在屏幕外，应该显示边缘箭头")
        
        # Test renderer call directly
        print("\n5. 测试渲染器直接调用...")
        if hasattr(game.renderer, '_render_ui'):
            print("   渲染器有_render_ui方法")
            if game.game_state.pending_target:
                print("   pending_target不为空，应该会渲染指示器")
            else:
                print("   pending_target为空，不会渲染指示器")
        
        print("\n=== 测试完成 ===")
        
        # Test toggle functionality
        print("\n6. 测试切换功能...")
        print("   第二次按Tab键（应该隐藏指示器）...")
        tab_event2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
        game.input_handler.handle_keydown(tab_event2)
        print(f"   处理后的pending_target: {game.game_state.pending_target}")
        
        print("   第三次按Tab键（应该显示指示器）...")
        tab_event3 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
        game.input_handler.handle_keydown(tab_event3)
        print(f"   处理后的pending_target: {game.game_state.pending_target}")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_indicator_rendering()