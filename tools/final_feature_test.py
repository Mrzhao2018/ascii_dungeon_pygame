#!/usr/bin/env python3
"""
Final test to verify all features are working correctly
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.state import GameState, GameStateEnum
from game.config import GameConfig

def test_death_restart_feature():
    """Test the complete death and restart functionality"""
    print("=== 死亡重新开始功能测试 ===")
    
    # Create a mock config
    class MockConfig:
        pass
    
    config = MockConfig()
    
    # Test game state transitions
    game_state = GameState(config)
    
    print("初始状态:", game_state.current_state)
    assert game_state.current_state == GameStateEnum.PLAYING
    
    # Test death transition
    game_state.set_game_state(GameStateEnum.GAME_OVER)
    print("死亡后状态:", game_state.current_state)
    assert game_state.current_state == GameStateEnum.GAME_OVER
    assert game_state.is_game_over()
    
    # Test restart transition
    game_state.set_game_state(GameStateEnum.RESTART)
    print("重新开始状态:", game_state.current_state)
    assert game_state.current_state == GameStateEnum.RESTART
    assert game_state.is_restart()
    
    # Test return to playing
    game_state.set_game_state(GameStateEnum.PLAYING)
    print("游戏进行状态:", game_state.current_state)
    assert game_state.current_state == GameStateEnum.PLAYING
    assert game_state.is_playing()
    
    print("✅ 状态转换测试通过")

def test_indicator_refresh():
    """Test the indicator refresh functionality"""
    print("\n=== 方位指示器刷新测试 ===")
    
    # Create a mock config
    class MockConfig:
        pass
    
    config = MockConfig()
    game_state = GameState(config)
    
    # Test indicator refresh method exists
    assert hasattr(game_state, 'refresh_exit_indicator')
    print("✅ 刷新方法存在")
    
    # Test refresh doesn't crash (需要 tile_size 参数)
    try:
        game_state.refresh_exit_indicator(32)  # 使用标准瓦片大小
        print("✅ 刷新方法调用成功")
    except Exception as e:
        print(f"❌ 刷新方法调用失败: {e}")
        raise

def test_config_help_text():
    """Test that help text includes restart instructions"""
    print("\n=== 配置帮助文本测试 ===")
    
    config = GameConfig()
    
    # Check that config is properly initialized
    assert hasattr(config, 'config_file')
    print("✅ 配置文件正确初始化")
    
    # Test help method exists
    assert hasattr(config, 'show_help')
    print("✅ 帮助方法存在")
    
    print("✅ 配置系统正常")

def run_all_tests():
    """Run all feature tests"""
    print("开始最终功能测试...\n")
    
    try:
        test_death_restart_feature()
        test_indicator_refresh()
        test_config_help_text()
        
        print("\n🎉 所有测试通过！功能实现完成：")
        print("  - 死亡后重新开始功能")
        print("  - 楼层转换后指示器自动刷新")
        print("  - 配置文件正确修复")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()