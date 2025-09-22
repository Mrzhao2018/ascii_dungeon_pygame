#!/usr/bin/env python3
"""
Debug performance monitor timing
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from game.performance import PerformanceMonitor

def debug_timing():
    monitor = PerformanceMonitor()
    monitor.enable()
    
    print("Testing performance monitor timing...")
    
    # Test 1: Short frame
    print("\nTest 1: Short frame (10ms)")
    monitor.start_frame()
    time.sleep(0.01)  # 10ms
    monitor.end_frame()
    
    if monitor.frame_times:
        print(f"Recorded frame time: {monitor.frame_times[-1]:.2f}ms")
    
    # Test 2: Long frame
    print("\nTest 2: Long frame (60ms)")
    monitor.start_frame()
    time.sleep(0.06)  # 60ms
    monitor.end_frame()
    
    if len(monitor.frame_times) > 1:
        print(f"Recorded frame time: {monitor.frame_times[-1]:.2f}ms")
    
    # Show all frame times
    print(f"\nAll frame times: {[f'{t:.2f}' for t in monitor.frame_times]}")
    
    # Test the thresholds
    print(f"\nThresholds: {monitor.thresholds}")

if __name__ == '__main__':
    debug_timing()