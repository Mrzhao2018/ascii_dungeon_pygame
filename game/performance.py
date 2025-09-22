"""
Performance optimization utilities
"""
import pygame
import time
import threading
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

# Import new memory management system
try:
    from .memory import MemoryMonitor, SmartCacheManager, MemoryOptimizer
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError:
    MEMORY_SYSTEM_AVAILABLE = False


class PerformanceMonitor:
    """Real-time performance monitoring and data collection"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.enabled = False
        
        # Performance data storage
        self.frame_times = deque(maxlen=120)  # Last 2 seconds at 60fps
        self.render_times = deque(maxlen=120)
        self.update_times = deque(maxlen=120)
        self.memory_usage = deque(maxlen=60)  # Last 1 second
        
        # Frame timing
        self.last_frame_time = time.perf_counter()
        self.frame_start_time = 0
        self.fps_counter = 0
        self.fps_timer = time.time()
        self.current_fps = 0
        
        # Memory monitoring (simplified without psutil)
        self.memory_timer = time.time()
        
        # Performance thresholds
        self.thresholds = {
            'target_fps': 30,
            'frame_time_ms': 33.33,  # 1000/30
            'memory_mb': 500,
            'cpu_percent': 80
        }
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'dropped_frames': 0,
            'peak_memory': 0,
            'avg_fps': 0
        }
        
        self.enable()
    
    def enable(self):
        """Enable performance monitoring"""
        self.enabled = True
        if self.logger:
            self.logger.debug("Performance monitoring enabled")
    
    def disable(self):
        """Disable performance monitoring"""
        self.enabled = False
        if self.logger:
            self.logger.debug("Performance monitoring disabled")
    
    def start_frame(self):
        """Mark the start of a frame"""
        if not self.enabled:
            return
            
        current_time = time.perf_counter()
        
        # Calculate frame time from previous frame
        if self.last_frame_time > 0:
            frame_time = (current_time - self.last_frame_time) * 1000  # Convert to ms
            self.frame_times.append(frame_time)
            
            # Check for dropped frames
            if frame_time > self.thresholds['frame_time_ms'] * 1.5:
                self.stats['dropped_frames'] += 1
                
            # Log performance data to file
            if self.logger:
                self.logger.debug(f"PERF_DATA|frame_time|{frame_time:.2f}")
        
        self.frame_start_time = current_time
        self.last_frame_time = current_time
        self.stats['total_frames'] += 1
        
        # Update FPS counter
        self.fps_counter += 1
        if current_time - self.fps_timer >= 1.0:  # Update every second
            self.current_fps = self.fps_counter
            self.stats['avg_fps'] = (self.stats['avg_fps'] + self.current_fps) / 2 if self.stats['avg_fps'] > 0 else self.current_fps
            
            # Log FPS data
            if self.logger:
                self.logger.debug(f"PERF_DATA|fps|{self.current_fps}")
                
            self.fps_counter = 0
            self.fps_timer = current_time
        
        # Update memory usage every second (simplified)
        if current_time - self.memory_timer >= 1.0:
            try:
                # Use a simple memory estimation
                memory_mb = len(str(pygame.display.get_surface())) / 1024 if pygame.display.get_surface() else 0
                self.memory_usage.append(memory_mb)
                
                if memory_mb > self.stats['peak_memory']:
                    self.stats['peak_memory'] = memory_mb
                
                if self.logger:
                    self.logger.debug(f"PERF_DATA|memory|{memory_mb:.1f}")
                
                self.memory_timer = current_time
            except Exception:
                pass  # Ignore memory monitoring errors
    
    def end_frame(self):
        """Mark the end of a frame"""
        if not self.enabled or self.frame_start_time == 0:
            return
            
        total_frame_time = (time.perf_counter() - self.frame_start_time) * 1000
        
        # Log performance issues in real-time
        if self.logger and total_frame_time > self.thresholds['frame_time_ms']:
            self.logger.warning(f"Performance issue detected: frame time {total_frame_time:.1f}ms exceeds target {self.thresholds['frame_time_ms']:.1f}ms")
    
    def record_render_time(self, render_time_ms: float):
        """Record rendering time"""
        if self.enabled:
            self.render_times.append(render_time_ms)
            if self.logger:
                self.logger.debug(f"PERF_DATA|render_time|{render_time_ms:.2f}")
    
    def record_update_time(self, update_time_ms: float):
        """Record game update time"""
        if self.enabled:
            self.update_times.append(update_time_ms)
            if self.logger:
                self.logger.debug(f"PERF_DATA|update_time|{update_time_ms:.2f}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        if not self.enabled:
            return {}
        
        stats = {
            'fps': self.current_fps,
            'avg_fps': self.stats['avg_fps'],
            'total_frames': self.stats['total_frames'],
            'dropped_frames': self.stats['dropped_frames'],
            'drop_rate': (self.stats['dropped_frames'] / max(1, self.stats['total_frames'])) * 100,
            'memory_mb': self.memory_usage[-1] if self.memory_usage else 0,
            'peak_memory_mb': self.stats['peak_memory']
        }
        
        # Add timing statistics
        if self.frame_times:
            stats['avg_frame_time'] = sum(self.frame_times) / len(self.frame_times)
            stats['min_frame_time'] = min(self.frame_times)
            stats['max_frame_time'] = max(self.frame_times)
        
        if self.render_times:
            stats['avg_render_time'] = sum(self.render_times) / len(self.render_times)
        
        if self.update_times:
            stats['avg_update_time'] = sum(self.update_times) / len(self.update_times)
        
        return stats
    
    def log_performance_summary(self):
        """Log a summary of performance statistics"""
        if not self.enabled or not self.logger:
            return
        
        stats = self.get_current_stats()
        
        self.logger.info("=== Performance Summary ===")
        self.logger.info(f"FPS: {stats.get('fps', 0):.1f} (avg: {stats.get('avg_fps', 0):.1f})")
        self.logger.info(f"Frame time: {stats.get('avg_frame_time', 0):.2f}ms (min: {stats.get('min_frame_time', 0):.2f}ms, max: {stats.get('max_frame_time', 0):.2f}ms)")
        self.logger.info(f"Memory: {stats.get('memory_mb', 0):.1f}MB (peak: {stats.get('peak_memory_mb', 0):.1f}MB)")
        self.logger.info(f"Dropped frames: {stats.get('dropped_frames', 0)} ({stats.get('drop_rate', 0):.1f}%)")
        
        if stats.get('avg_render_time'):
            self.logger.info(f"Avg render time: {stats['avg_render_time']:.2f}ms")
        if stats.get('avg_update_time'):
            self.logger.info(f"Avg update time: {stats['avg_update_time']:.2f}ms")


class PerformanceOptimizer:
    """Analyzes and optimizes game performance"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.monitor = PerformanceMonitor(logger)
        
        # Enhanced cache management
        if MEMORY_SYSTEM_AVAILABLE:
            self.cache_manager = SmartCacheManager(max_size=1000, max_memory_mb=100)
            self.memory_monitor = MemoryMonitor(logger)
            self.memory_optimizer = MemoryOptimizer(self.memory_monitor, self.cache_manager, logger)
            
            # Set memory baseline
            self.memory_monitor.set_baseline()
        else:
            # Fallback to simple cache
            self.cache_manager = None
            self.memory_monitor = None
            self.memory_optimizer = None
        
        # Legacy cache for compatibility
        self.optimization_cache = {}
        self.render_cache = {}
        self.font_cache = {}
        
        # Performance thresholds (in milliseconds)
        self.thresholds = {
            'frame_total': 33.0,  # 30 FPS
            'rendering': 16.0,    # Half of frame budget
            'game_update': 10.0,  # Game logic should be fast
            'event_handling': 5.0  # Input should be very fast
        }
        
        # Cache settings
        self.max_cache_size = 100
        self.cache_cleanup_interval = 300  # frames
        self.frame_count = 0
    
    def start_frame(self):
        """Start frame performance monitoring"""
        self.monitor.start_frame()
        
        # Update memory monitoring
        if self.memory_monitor:
            self.memory_monitor.update()
        
        self.frame_count += 1
        
        # Periodic memory optimization
        if self.memory_optimizer and self.frame_count % 300 == 0:  # Every 300 frames
            optimizations = self.memory_optimizer.optimize_memory()
            if optimizations and self.logger:
                self.logger.debug(f"Memory optimizations applied: {optimizations}")
    
    def end_frame(self):
        """End frame performance monitoring"""
        self.monitor.end_frame()
        
        # Periodic cache cleanup
        if self.frame_count % self.cache_cleanup_interval == 0:
            if self.cache_manager:
                self.cache_manager.force_cleanup()
            else:
                self._cleanup_font_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        stats = self.monitor.get_current_stats()
        
        # Add memory statistics
        if self.memory_monitor:
            memory_stats = self.memory_monitor.get_memory_stats()
            stats.update(memory_stats)
        
        # Add cache statistics
        if self.cache_manager:
            cache_stats = self.cache_manager.get_cache_stats()
            stats['cache_stats'] = cache_stats
        
        return stats
    
    def check_performance_issues(self, performance_data: Dict[str, List[float]]) -> List[str]:
        """Analyze performance data and return list of issues"""
        issues = []
        
        for operation, threshold in self.thresholds.items():
            if operation in performance_data and performance_data[operation]:
                avg_time = sum(performance_data[operation]) / len(performance_data[operation])
                max_time = max(performance_data[operation])
                
                if avg_time > threshold:
                    issues.append(f"{operation}: average {avg_time:.1f}ms exceeds {threshold}ms threshold")
                
                if max_time > threshold * 2:
                    issues.append(f"{operation}: peak {max_time:.1f}ms is critically high")
        
        return issues
    
    def optimize_rendering(self, config, game_state, screen):
        """Apply rendering optimizations"""
        optimizations_applied = []
        
        # Check if we should reduce tile rendering quality
        if hasattr(self.logger, 'get_performance_stats'):
            render_stats = self.logger.get_performance_stats('rendering')
            if render_stats and render_stats.get('avg', 0) > 20:
                # Reduce rendering quality if performance is poor
                if not hasattr(config, '_reduced_quality'):
                    config._reduced_quality = True
                    optimizations_applied.append("Reduced rendering quality due to performance")
        
        # Cache frequently rendered surfaces
        cache_key = f"{game_state.width}x{game_state.height}_{config.tile_size}"
        if cache_key not in self.render_cache:
            # Pre-create common surfaces
            self.render_cache[cache_key] = {
                'bg_surface': pygame.Surface((config.tile_size, config.tile_size)),
                'wall_surface': pygame.Surface((config.tile_size, config.tile_size)),
            }
            optimizations_applied.append("Created render cache for common tiles")
        
        return optimizations_applied
    
    def get_optimized_font(self, font_size: int, text: str):
        """Get cached font rendering with smart cache management"""
        cache_key = f"{font_size}_{text}"
        
        # Use smart cache if available
        if self.cache_manager:
            def generate_font_surface():
                from game import utils
                font, _ = utils.load_preferred_font(font_size)
                return font.render(text, True, (255, 255, 255))
            
            return self.cache_manager.get_cached_item('font_renders', cache_key, generate_font_surface)
        
        # Fallback to legacy cache
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Load font and render text
        try:
            from game import utils
            font, _ = utils.load_preferred_font(font_size)
            surface = font.render(text, True, (255, 255, 255))
            
            # Add to cache
            self.font_cache[cache_key] = surface
            
            # Clean cache if too large
            if len(self.font_cache) > self.max_cache_size:
                self._cleanup_font_cache()
            
            return surface
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Font rendering failed: {e}", "PERFORMANCE")
            return None
    
    def _cleanup_font_cache(self):
        """Remove oldest items from font cache"""
        # Simple cleanup: remove first 20 items
        items_to_remove = list(self.font_cache.keys())[:20]
        for key in items_to_remove:
            del self.font_cache[key]
        
        self.logger.debug(f"Cleaned font cache, removed {len(items_to_remove)} items", "PERFORMANCE")
    
    def suggest_optimizations(self, config, performance_data: Dict[str, List[float]]) -> List[str]:
        """Suggest specific optimizations based on performance data"""
        suggestions = []
        
        # Check frame rate
        frame_stats = performance_data.get('frame_total', [])
        if frame_stats:
            avg_frame_time = sum(frame_stats) / len(frame_stats)
            target_fps = config.fps
            actual_fps = 1000 / avg_frame_time if avg_frame_time > 0 else target_fps
            
            if actual_fps < target_fps * 0.8:  # Less than 80% of target FPS
                suggestions.append(f"Consider reducing FPS from {target_fps} to {int(actual_fps * 0.9)}")
                suggestions.append("Consider reducing view size with --view-w and --view-h")
                suggestions.append("Try --debug=false to disable debug overlays")
        
        # Check rendering performance
        render_stats = performance_data.get('rendering', [])
        if render_stats:
            avg_render_time = sum(render_stats) / len(render_stats)
            if avg_render_time > 15:  # More than 15ms rendering
                suggestions.append("Rendering is slow - consider smaller tile size")
                suggestions.append("Try reducing enemy count with --enemies")
                suggestions.append("Consider disabling floating text effects")
        
        # Check game update performance
        update_stats = performance_data.get('game_update', [])
        if update_stats:
            avg_update_time = sum(update_stats) / len(update_stats)
            if avg_update_time > 8:  # More than 8ms for game logic
                suggestions.append("Game logic is slow - check entity count")
                suggestions.append("Consider reducing map size with --map-width and --map-height")
        
        # Add memory-based suggestions
        if self.memory_optimizer:
            memory_suggestions = self.memory_optimizer.suggest_optimizations()
            suggestions.extend(memory_suggestions)
        
        return suggestions
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report"""
        if self.memory_optimizer:
            return self.memory_optimizer.get_memory_report()
        else:
            return {'error': 'Memory monitoring not available'}
    
    def force_memory_optimization(self) -> List[str]:
        """Force immediate memory optimization"""
        if self.memory_optimizer:
            return self.memory_optimizer.optimize_memory()
        else:
            # Fallback optimization
            self._cleanup_font_cache()
            return ['Performed basic cache cleanup']
        
        return suggestions
    
    def auto_optimize(self, config, game_state, performance_data: Dict[str, List[float]]) -> List[str]:
        """Automatically apply safe optimizations"""
        applied = []
        
        # Get current performance
        frame_stats = performance_data.get('frame_total', [])
        if not frame_stats:
            return applied
        
        avg_frame_time = sum(frame_stats) / len(frame_stats)
        
        # If performance is really bad, apply aggressive optimizations
        if avg_frame_time > 50:  # Less than 20 FPS
            if not hasattr(config, '_auto_optimized'):
                config._auto_optimized = True
                
                # Reduce FPS target
                config.fps = max(20, config.fps - 10)
                applied.append(f"Reduced FPS to {config.fps}")
                
                # Disable non-essential effects if really bad
                if avg_frame_time > 75:  # Less than 13 FPS
                    config._disable_effects = True
                    applied.append("Disabled visual effects due to poor performance")
        
        return applied
    
    def get_performance_report(self, performance_data: Dict[str, List[float]]) -> str:
        """Generate a comprehensive performance report"""
        report_lines = []
        report_lines.append("=== Performance Report ===")
        
        total_samples = 0
        for operation, data in performance_data.items():
            if data:
                avg_time = sum(data) / len(data)
                min_time = min(data)
                max_time = max(data)
                samples = len(data)
                total_samples = max(total_samples, samples)
                
                # Performance rating
                threshold = self.thresholds.get(operation, 50)
                if avg_time <= threshold * 0.5:
                    rating = "EXCELLENT"
                elif avg_time <= threshold:
                    rating = "GOOD"
                elif avg_time <= threshold * 1.5:
                    rating = "FAIR"
                else:
                    rating = "POOR"
                
                report_lines.append(
                    f"{operation:15} | {avg_time:6.1f}ms avg | {min_time:6.1f}ms min | "
                    f"{max_time:6.1f}ms max | {rating:9} | {samples:4d} samples"
                )
        
        # Overall assessment
        frame_data = performance_data.get('frame_total', [])
        if frame_data:
            avg_frame = sum(frame_data) / len(frame_data)
            fps = 1000 / avg_frame if avg_frame > 0 else 0
            
            report_lines.append("")
            report_lines.append(f"Overall FPS: {fps:.1f}")
            
            if fps >= 30:
                report_lines.append("Performance: EXCELLENT - Game running smoothly")
            elif fps >= 25:
                report_lines.append("Performance: GOOD - Minor frame drops possible")
            elif fps >= 20:
                report_lines.append("Performance: FAIR - Noticeable performance issues")
            else:
                report_lines.append("Performance: POOR - Significant performance problems")
        
        # Suggestions
        suggestions = self.suggest_optimizations(None, performance_data)
        if suggestions:
            report_lines.append("")
            report_lines.append("Optimization Suggestions:")
            for i, suggestion in enumerate(suggestions[:5], 1):  # Limit to 5 suggestions
                report_lines.append(f"{i}. {suggestion}")
        
        return "\n".join(report_lines)


class CacheManager:
    """Manages various game caches for performance"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.caches = {
            'font_renders': {},
            'tile_surfaces': {},
            'ui_elements': {},
        }
        self.access_count = defaultdict(int)
    
    def get_cached_surface(self, cache_type: str, key: str, generator_func, *args, **kwargs):
        """Get cached surface or generate and cache it"""
        if cache_type not in self.caches:
            self.caches[cache_type] = {}
        
        cache = self.caches[cache_type]
        
        if key in cache:
            self.access_count[key] += 1
            return cache[key]
        
        # Generate new surface
        try:
            surface = generator_func(*args, **kwargs)
            cache[key] = surface
            self.access_count[key] = 1
            
            # Clean cache if needed
            if len(cache) > self.max_size:
                self._cleanup_cache(cache_type)
            
            return surface
        except Exception:
            return None
    
    def _cleanup_cache(self, cache_type: str):
        """Remove least recently used items from cache"""
        cache = self.caches[cache_type]
        
        # Sort by access count and remove 20% of items
        items = list(cache.keys())
        items.sort(key=lambda k: self.access_count[k])
        
        items_to_remove = items[:len(items) // 5]  # Remove 20%
        
        for key in items_to_remove:
            del cache[key]
            if key in self.access_count:
                del self.access_count[key]
    
    def clear_all_caches(self):
        """Clear all caches"""
        for cache in self.caches.values():
            cache.clear()
        self.access_count.clear()
    
    def get_cache_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics about cache usage"""
        stats = {}
        for cache_type, cache in self.caches.items():
            stats[cache_type] = {
                'size': len(cache),
                'total_accesses': sum(self.access_count[k] for k in cache.keys()),
                'avg_accesses': sum(self.access_count[k] for k in cache.keys()) / len(cache) if cache else 0
            }
        return stats