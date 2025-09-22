#!/usr/bin/env python3
"""
实际游戏中的Tab键功能测试
"""
import sys
import os
import pygame
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_tab_in_actual_game():
    """在实际游戏环境中测试Tab键功能"""
    
    print("=== 实际游戏Tab键测试 ===")
    print("游戏启动后，按Tab键查看指示器是否工作")
    print("按ESC退出测试")
    print("")
    
    try:
        from game.game import Game
        
        # 创建游戏实例
        game = Game()
        
        # 简单的游戏循环用于测试
        clock = pygame.time.Clock()
        running = True
        frame_count = 0
        
        while running:
            dt = clock.tick(60)
            frame_count += 1
            
            # 处理事件
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        
            # 处理输入
            input_results = game.input_handler.handle_events(events)
            continuous_input = game.input_handler.handle_continuous_input()
            
            # 每秒输出一次状态
            if frame_count % 60 == 0:
                print(f"帧 {frame_count//60}s:")
                print(f"  exit_pos: {game.game_state.exit_pos}")
                print(f"  pending_target: {game.game_state.pending_target}")
                
                # 检查Tab键状态
                keys = pygame.key.get_pressed()
                if keys[pygame.K_TAB]:
                    print("  Tab键被按下!")
                else:
                    print("  Tab键未按下")
                    
            # 简单渲染（可选）
            try:
                game.screen.fill((0, 0, 0))
                pygame.display.flip()
            except:
                pass
                
        print("\n测试结束")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == '__main__':
    test_tab_in_actual_game()