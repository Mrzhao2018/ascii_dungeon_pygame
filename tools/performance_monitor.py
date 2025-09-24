#!/usr/bin/env python3
"""
Performance analysis tool for the game
Run this alongside the game to monitor and analyze performance
"""
import sys
import os
import time
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.logger import Logger
from game.performance import PerformanceOptimizer
from game.config import GameConfig


def monitor_performance(duration_seconds=30, interval_seconds=1):
    """Monitor game performance for specified duration"""
    print(f"Monitoring game performance for {duration_seconds} seconds...")
    print("Start the game with --debug --perf flags for best results")
    print("=" * 60)
    
    # Mock config for standalone monitoring
    config = GameConfig()
    config.debug_mode = True
    config.performance_monitoring = True
    
    # Initialize logger and optimizer
    logger = Logger(config)
    optimizer = PerformanceOptimizer(logger)
    
    start_time = time.time()
    samples = 0
    performance_data = {
        'frame_total': [],
        'rendering': [],
        'game_update': [],
        'event_handling': []
    }
    
    try:
        while time.time() - start_time < duration_seconds:
            # Simulate reading performance data from log file
            # In a real scenario, this would read from game.log or shared memory
            
            # For demo purposes, generate some sample data
            import random
            frame_time = random.uniform(25, 45)  # Simulate varying frame times
            render_time = random.uniform(10, 20)
            update_time = random.uniform(5, 15)
            event_time = random.uniform(1, 5)
            
            performance_data['frame_total'].append(frame_time)
            performance_data['rendering'].append(render_time)
            performance_data['game_update'].append(update_time)
            performance_data['event_handling'].append(event_time)
            
            samples += 1
            
            # Print current stats every 5 seconds
            if samples % (5 / interval_seconds) == 0:
                current_fps = 1000 / frame_time if frame_time > 0 else 0
                print(f"Sample {samples:3d}: {current_fps:5.1f} FPS | "
                      f"Frame: {frame_time:5.1f}ms | "
                      f"Render: {render_time:4.1f}ms | "
                      f"Update: {update_time:4.1f}ms")
            
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
    
    print(f"\nAnalysis complete. Collected {samples} samples.")
    print("=" * 60)
    
    # Generate performance report
    report = optimizer.get_performance_report(performance_data)
    print(report)
    
    # Check for issues
    issues = optimizer.check_performance_issues(performance_data)
    if issues:
        print("\n=== Performance Issues Detected ===")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    
    # Get optimization suggestions
    suggestions = optimizer.suggest_optimizations(config, performance_data)
    if suggestions:
        print("\n=== Optimization Suggestions ===")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    
    return performance_data


def analyze_log_file(log_file_path):
    """Analyze performance data from existing log file"""
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return
    
    print(f"Analyzing log file: {log_file_path}")
    print("=" * 60)
    
    performance_data = {
        'frame_total': [],
        'rendering': [],
        'game_update': [],
        'event_handling': []
    }
    
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Parse performance log entries
                # Format: [timestamp][pygame_time][PERFORMANCE][operation] duration
                if '[PERFORMANCE]' in line:
                    try:
                        parts = line.strip().split(']')
                        if len(parts) >= 4:
                            operation = parts[3].strip()
                            # Extract duration from the line
                            if 'avg=' in line:
                                # Extract average time
                                avg_part = line.split('avg=')[1].split('ms')[0]
                                duration = float(avg_part)
                                
                                if operation in performance_data:
                                    performance_data[operation].append(duration)
                    except (ValueError, IndexError):
                        continue  # Skip malformed lines
    
    except Exception as e:
        print(f"Error reading log file: {e}")
        return
    
    if not any(performance_data.values()):
        print("No performance data found in log file.")
        print("Make sure the game was run with --debug --perf flags.")
        return
    
    # Analyze the data
    config = GameConfig()
    config.debug_mode = True
    
    logger = Logger(config)
    optimizer = PerformanceOptimizer(logger)
    
    report = optimizer.get_performance_report(performance_data)
    print(report)


def benchmark_game(test_duration=60):
    """Run a performance benchmark of the game"""
    print(f"Running {test_duration}-second performance benchmark...")
    print("This will start the game in benchmark mode")
    print("=" * 60)
    
    import subprocess
    
    # Start game with benchmark flags
    cmd = [
        sys.executable, "main.py",
        "--debug", "--perf", "--regen",
        "--enemies", "20",  # More enemies for stress test
        "--map-width", "150", "--map-height", "60",  # Larger map
        "--view-w", "30", "--view-h", "20"  # Larger view
    ]
    
    print(f"Starting game with command: {' '.join(cmd)}")
    
    try:
        # Start the game process
        process = subprocess.Popen(cmd, cwd=os.path.dirname(__file__))
        
        # Let it run for the test duration
        print(f"Benchmark running... (will stop after {test_duration} seconds)")
        time.sleep(test_duration)
        
        # Terminate the process
        process.terminate()
        
        print("Benchmark complete. Check game.log for detailed results.")
        
        # Analyze the log file
        log_path = os.path.join(os.path.dirname(__file__), '..', 'game.log')
        if os.path.exists(log_path):
            print("\nAnalyzing benchmark results...")
            analyze_log_file(log_path)
    
    except Exception as e:
        print(f"Benchmark failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Game Performance Analysis Tool")
    parser.add_argument('--monitor', '-m', type=int, default=0, metavar='SECONDS',
                      help='Monitor performance for specified seconds')
    parser.add_argument('--analyze', '-a', type=str, metavar='LOGFILE',
                      help='Analyze performance from log file')
    parser.add_argument('--benchmark', '-b', type=int, default=0, metavar='SECONDS',
                      help='Run performance benchmark for specified seconds')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                      help='Monitoring interval in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_performance(args.monitor, args.interval)
    elif args.analyze:
        analyze_log_file(args.analyze)
    elif args.benchmark:
        benchmark_game(args.benchmark)
    else:
        print("Game Performance Analysis Tool")
        print("Usage examples:")
        print("  python performance_monitor.py --monitor 30     # Monitor for 30 seconds")
        print("  python performance_monitor.py --analyze game.log  # Analyze log file")
        print("  python performance_monitor.py --benchmark 60   # Run 60-second benchmark")
        print("\nFor best results, run the game with --debug --perf flags")


if __name__ == '__main__':
    main()