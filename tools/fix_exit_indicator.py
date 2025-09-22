#!/usr/bin/env python3
"""
出口指示器修复和增强工具
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def create_exit_indicator_fix():
    """创建一个出口指示器的修复补丁"""
    
    print("=== 创建出口指示器修复补丁 ===")
    
    # 增强的出口位置计算方法
    enhanced_compute_exit_pos = '''
    def compute_exit_pos(self):
        """Find the exit position in the current level (enhanced version)"""
        try:
            # Debug log
            if hasattr(self, 'logger') and self.logger:
                self.logger.debug(f"Computing exit_pos for level {self.width}x{self.height}", "EXIT")
            
            # Look for 'X' in the level
            found_exits = []
            for y, row in enumerate(self.level):
                for x, ch in enumerate(row):
                    if ch == 'X':
                        found_exits.append((x, y))
            
            if found_exits:
                # Use the first exit found
                self.exit_pos = found_exits[0]
                if hasattr(self, 'logger') and self.logger:
                    self.logger.debug(f"Found exit at {self.exit_pos}, total exits: {len(found_exits)}", "EXIT")
            else:
                self.exit_pos = None
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning("No exit ('X') found in level!", "EXIT")
                    
        except Exception as e:
            self.exit_pos = None
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Exception computing exit_pos: {e}", "EXIT")
                
        return self.exit_pos
    '''
    
    # 增强的Tab键处理
    enhanced_tab_handling = '''
        # Tab indicator (enhanced)
        if keys[pygame.K_TAB]:
            # Force recompute exit_pos if it's None but level has 'X'
            if self.game_state.exit_pos is None and self.game_state.level:
                x_count = sum(row.count('X') for row in self.game_state.level)
                if x_count > 0:
                    self.game_state.compute_exit_pos()
                    if hasattr(self.game_state, 'logger') and self.game_state.logger:
                        self.game_state.logger.info(f"Recomputed exit_pos on Tab: {self.game_state.exit_pos}", "TAB")
            
            if self.game_state.exit_pos is not None:
                ex, ey = self.game_state.exit_pos
                tile_size = self.config.tile_size
                self.game_state.pending_target = (ex * tile_size + tile_size // 2, ey * tile_size + tile_size // 2)
                if hasattr(self.game_state, 'logger') and self.game_state.logger:
                    self.game_state.logger.debug(f"Tab indicator set to {self.game_state.pending_target}", "TAB")
            else:
                self.game_state.pending_target = None
                if hasattr(self.game_state, 'logger') and self.game_state.logger:
                    self.game_state.logger.warning("Tab pressed but no exit_pos available", "TAB")
        else:
            self.game_state.pending_target = None
    '''
    
    print("1. 创建增强的compute_exit_pos方法...")
    print("   - 添加调试日志")
    print("   - 更全面的错误处理")
    print("   - 记录找到的所有出口")
    
    print("\n2. 创建增强的Tab键处理...")
    print("   - 自动重新计算exit_pos如果为None")
    print("   - 详细的调试日志")
    print("   - 更好的错误提示")
    
    # 应用修复
    apply_fix = input("\n是否应用这些修复? (y/n): ").lower().strip()
    
    if apply_fix == 'y':
        try:
            # 读取state.py文件
            state_file = os.path.join(os.path.dirname(__file__), '..', 'game', 'state.py')
            with open(state_file, 'r', encoding='utf-8') as f:
                state_content = f.read()
            
            # 找到并替换compute_exit_pos方法
            start_marker = "def compute_exit_pos(self):"
            end_marker = "return self.exit_pos"
            
            start_idx = state_content.find(start_marker)
            if start_idx != -1:
                # 找到方法的结束位置
                end_idx = state_content.find(end_marker, start_idx)
                if end_idx != -1:
                    end_idx = state_content.find('\n', end_idx) + 1
                    
                    # 替换方法
                    new_content = (state_content[:start_idx] + 
                                 enhanced_compute_exit_pos.strip() + '\n\n' +
                                 state_content[end_idx:])
                    
                    # 写回文件
                    with open(state_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print("✅ 已增强state.py中的compute_exit_pos方法")
                else:
                    print("❌ 无法找到compute_exit_pos方法的结束位置")
            else:
                print("❌ 无法找到compute_exit_pos方法")
            
            # 类似地处理input.py文件
            input_file = os.path.join(os.path.dirname(__file__), '..', 'game', 'input.py')
            with open(input_file, 'r', encoding='utf-8') as f:
                input_content = f.read()
            
            # 找到Tab键处理部分
            tab_marker = "# Tab indicator"
            tab_idx = input_content.find(tab_marker)
            if tab_idx != -1:
                # 找到这个代码块的结束位置
                end_tab_idx = input_content.find("return result", tab_idx)
                if end_tab_idx != -1:
                    # 找到Tab处理代码块的开始位置
                    tab_start = tab_idx
                    
                    # 替换Tab处理代码
                    new_input_content = (input_content[:tab_start] + 
                                       enhanced_tab_handling.strip() + '\n\n        ' +
                                       input_content[end_tab_idx:])
                    
                    # 写回文件
                    with open(input_file, 'w', encoding='utf-8') as f:
                        f.write(new_input_content)
                    
                    print("✅ 已增强input.py中的Tab键处理")
                else:
                    print("❌ 无法找到Tab处理代码的结束位置")
            else:
                print("❌ 无法找到Tab处理代码")
            
            print("\n✅ 修复应用完成！")
            print("请重启游戏测试出口指示器功能")
            
        except Exception as e:
            print(f"❌ 应用修复时出错: {e}")
    else:
        print("取消修复应用")
    
    print("\n=== 修复工具完成 ===")

if __name__ == '__main__':
    create_exit_indicator_fix()