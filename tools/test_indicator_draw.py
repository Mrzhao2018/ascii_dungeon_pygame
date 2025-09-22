#!/usr/bin/env python3
"""
测试指示器渲染过程中是否有错误
"""

import os
import sys
import pygame
import math

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import ui

def test_draw_target_indicator():
    """Test the draw_target_indicator function directly"""
    print("=== 测试指示器渲染函数 ===")
    
    # Initialize pygame
    pygame.init()
    surface = pygame.Surface((800, 600))
    
    # Test parameters (based on our previous test)
    target_pos = (396, 780)  # World position in pixels
    cam_x = 1392
    cam_y = 384
    ox = 0
    oy = 0
    view_px_w = 576
    view_px_h = 384
    
    print(f"目标位置: {target_pos}")
    print(f"相机位置: ({cam_x}, {cam_y})")
    print(f"视口尺寸: {view_px_w} x {view_px_h}")
    
    # Calculate screen position
    wx_px, wy_px = target_pos
    sx = wx_px - cam_x + ox
    sy = wy_px - cam_y + oy
    
    print(f"屏幕位置: ({sx}, {sy})")
    print(f"在屏幕内？ {0 <= sx < view_px_w and 0 <= sy < view_px_h}")
    
    # Manually test the indicator logic
    try:
        print("\n开始手动渲染测试...")
        
        # Copy the logic from draw_target_indicator
        if 0 <= sx < view_px_w and 0 <= sy < view_px_h:
            print("应该绘制圆圈在目标位置")
            pygame.draw.circle(surface, (240, 200, 80), (int(sx), int(sy)), 6)
        else:
            print("应该绘制边缘箭头")
            
            # Clamp position to viewport edge
            cx = max(8, min(view_px_w - 8, int(sx)))
            cy = max(8, min(view_px_h - 8, int(sy)))
            print(f"夹紧位置: ({cx}, {cy})")
            
            # Compute direction vector from center of screen to target
            center_x = view_px_w // 2
            center_y = view_px_h // 2
            print(f"屏幕中心: ({center_x}, {center_y})")
            
            dx = sx - center_x
            dy = sy - center_y
            print(f"方向向量: ({dx}, {dy})")
            
            # Normalize
            mag = math.hypot(dx, dy)
            print(f"向量长度: {mag}")
            
            if mag == 0:
                print("向量长度为0，跳过渲染")
                return
                
            ux = dx / mag
            uy = dy / mag
            print(f"单位向量: ({ux}, {uy})")
            
            # Arrow base position on edge
            edge_dist = min(center_x, center_y) - 20
            edge_x = center_x + ux * edge_dist
            edge_y = center_y + uy * edge_dist
            print(f"箭头基点: ({edge_x}, {edge_y})")
            
            # Check if arrow position is reasonable
            if edge_x < 0 or edge_x >= view_px_w or edge_y < 0 or edge_y >= view_px_h:
                print(f"⚠️ 箭头位置超出屏幕范围!")
            
            # Draw triangle arrow
            angle = math.atan2(uy, ux)
            print(f"箭头角度: {angle} 弧度 ({math.degrees(angle)} 度)")
            
            def rot(px, py, a):
                return (px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a))
            
            size = 10
            p1 = (edge_x + ux * 6, edge_y + uy * 6)
            left = rot(-size, -size / 2, angle)
            right = rot(-size, size / 2, angle)
            p2 = (edge_x + left[0], edge_y + left[1])
            p3 = (edge_x + right[0], edge_y + right[1])
            
            print(f"箭头三个点:")
            print(f"  P1 (尖端): ({p1[0]:.1f}, {p1[1]:.1f})")
            print(f"  P2 (左): ({p2[0]:.1f}, {p2[1]:.1f})")
            print(f"  P3 (右): ({p3[0]:.1f}, {p3[1]:.1f})")
            
            # Check if all points are reasonable
            points = [p1, p2, p3]
            for i, (px, py) in enumerate(points):
                if px < -100 or px > view_px_w + 100 or py < -100 or py > view_px_h + 100:
                    print(f"⚠️ 箭头点{i+1}位置异常: ({px:.1f}, {py:.1f})")
            
            pygame.draw.polygon(
                surface, (200, 200, 80), [(int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (int(p3[0]), int(p3[1]))]
            )
            print("✅ 箭头渲染完成")
            
        print("\n手动渲染测试完成，无错误!")
        
    except Exception as e:
        print(f"❌ 渲染过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    # Now test the actual UI function
    print("\n测试实际UI函数...")
    try:
        # Create a mock player object
        class MockPlayer:
            def __init__(self):
                self.x = 10
                self.y = 10
        
        player = MockPlayer()
        
        ui.draw_target_indicator(
            surface, player, target_pos, cam_x, cam_y, ox, oy, view_px_w, view_px_h, None
        )
        print("✅ UI函数调用成功，无错误!")
        
    except Exception as e:
        print(f"❌ UI函数调用出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_draw_target_indicator()