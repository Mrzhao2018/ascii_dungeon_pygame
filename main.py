#!/usr/bin/env python3
"""
PyGame 字符地牢探索游戏
重构版本 - 使用模块化架构
"""

import sys
import logging
from game.game import Game


def main():
    """主函数 - 现在只是简单地创建和运行游戏"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        logging.info("游戏被用户中断")
    except Exception as e:
        logging.exception("游戏运行时发生错误: %s", e)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())