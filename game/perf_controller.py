"""
Performance logging helper decoupled from Game class.
"""

import pygame


def log_performance_stats(performance_optimizer, logger, config, game_state):
    """Log and react to performance statistics using PerformanceOptimizer.

    Maintains the exact behavior previously implemented in Game._log_performance_stats.
    """
    # Use the performance monitor's summary
    performance_optimizer.monitor.log_performance_summary()

    # Check for performance issues
    stats = performance_optimizer.get_stats()
    if stats.get('drop_rate', 0) > 5:  # More than 5% dropped frames
        logger.warning(f"High frame drop rate: {stats['drop_rate']:.1f}%", "PERFORMANCE")

    if stats.get('avg_frame_time', 0) > 40:  # Worse than 25 FPS
        logger.warning(f"Poor frame time: {stats['avg_frame_time']:.1f}ms", "PERFORMANCE")

    # Apply optimizations if performance is poor (only in debug mode)
    if getattr(config, 'debug_mode', False) and (
        stats.get('drop_rate', 0) > 10 or stats.get('avg_frame_time', 0) > 50
    ):
        logger.info("Applying performance optimizations...", "PERFORMANCE")
        performance_optimizer.optimize_rendering(config, game_state, pygame.display.get_surface())

    # Check for performance issues via logger-collected stats
    frame_stats = logger.get_performance_stats("frame_total")
    if frame_stats and frame_stats['avg'] > 33.0:  # More than 33ms per frame (less than 30 FPS)
        logger.warning(
            f"Performance issue detected: average frame time {frame_stats['avg']:.1f}ms", "PERFORMANCE"
        )
