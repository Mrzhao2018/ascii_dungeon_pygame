#!/usr/bin/env python3
"""
FPS显示测试脚本
测试调试模式中的FPS是否正确显示
"""
import pygame
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from game.config import GameConfig
from game.debug import DebugOverlay
from game.logging import Logger


def test_fps_display():
    """测试FPS显示功能"""
    
    # 初始化pygame
    pygame.init()
    
    # 创建配置和日志
    config = GameConfig()
    config.debug_mode = True
    config.show_fps = True
    
    logger = Logger(config)
    
    # 创建调试覆盖层
    debug_overlay = DebugOverlay(config, logger)
    
    # 创建时钟
    clock = pygame.time.Clock()
    debug_overlay.clock = clock
    
    # 创建屏幕
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("FPS Test")
    
    # 测试循环
    running = True
    frame_count = 0
    start_time = time.time()
    
    print("测试FPS显示功能...")
    print("应该能看到右上角显示非零的FPS值")
    print("按ESC退出测试")
    
    while running and frame_count < 300:  # 运行5秒 (假设60FPS)
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill((0, 0, 0))
        
        # 渲染FPS计数器
        debug_overlay._render_fps_counter(screen)
        
        # 显示帧计数信息
        if debug_overlay.font:
            info_text = f"Frame: {frame_count} | Expected FPS: ~{clock.get_fps():.1f}"
            text_surf = debug_overlay.font.render(info_text, True, (255, 255, 255))
            screen.blit(text_surf, (10, 10))
        
        # 更新显示
        pygame.display.flip()
        
        # 限制帧率
        clock.tick(60)
        frame_count += 1
        
        # 每60帧打印一次FPS
        if frame_count % 60 == 0:
            current_fps = clock.get_fps()
            elapsed = time.time() - start_time
            avg_fps = frame_count / elapsed
            print(f"Frame {frame_count}: Clock FPS = {current_fps:.1f}, Average FPS = {avg_fps:.1f}")
    
    # 最终统计
    total_time = time.time() - start_time
    final_fps = clock.get_fps()
    avg_fps = frame_count / total_time
    
    print(f"\n测试完成:")
    print(f"总帧数: {frame_count}")
    print(f"总时间: {total_time:.2f}秒")
    print(f"最终Clock FPS: {final_fps:.1f}")
    print(f"平均FPS: {avg_fps:.1f}")
    
    if final_fps > 0:
        print("✅ FPS显示功能正常!")
    else:
        print("❌ FPS显示仍有问题")
    
    pygame.quit()
    

if __name__ == "__main__":
    test_fps_display()