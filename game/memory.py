#!/usr/bin/env python3
"""
内存管理和优化工具
"""
import gc
import sys
import time
import psutil
import pygame
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
import threading
import weakref


class MemoryMonitor:
    """实时内存使用监控"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.process = psutil.Process()
        
        # 内存使用历史
        self.memory_history = deque(maxlen=100)
        self.peak_memory = 0
        self.baseline_memory = 0
        
        # 监控间隔
        self.last_check = 0
        self.check_interval = 1.0  # 1秒检查一次
        
        # 内存阈值 (MB)
        self.warning_threshold = 500
        self.critical_threshold = 800
        
        # 统计数据
        self.stats = {
            'total_allocations': 0,
            'peak_memory_mb': 0,
            'avg_memory_mb': 0,
            'gc_collections': 0,
            'memory_warnings': 0
        }
        
        self.enabled = True
        
    def update(self):
        """更新内存监控数据"""
        if not self.enabled:
            return
            
        current_time = time.time()
        if current_time - self.last_check < self.check_interval:
            return
            
        try:
            # 获取内存使用信息
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # 转换为MB
            
            # 更新历史记录
            self.memory_history.append({
                'time': current_time,
                'memory_mb': memory_mb,
                'virtual_mb': memory_info.vms / 1024 / 1024
            })
            
            # 更新峰值内存
            if memory_mb > self.peak_memory:
                self.peak_memory = memory_mb
                self.stats['peak_memory_mb'] = memory_mb
                
            # 计算平均内存使用
            if len(self.memory_history) > 0:
                avg_memory = sum(entry['memory_mb'] for entry in self.memory_history) / len(self.memory_history)
                self.stats['avg_memory_mb'] = avg_memory
            
            # 检查内存阈值
            self._check_memory_thresholds(memory_mb)
            
            # 记录日志
            if self.logger:
                self.logger.debug(f"MEMORY_DATA|rss|{memory_mb:.2f}|vms|{memory_info.vms/1024/1024:.2f}")
                
            self.last_check = current_time
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Memory monitoring failed: {e}")
                
    def _check_memory_thresholds(self, memory_mb: float):
        """检查内存阈值并发出警告"""
        if memory_mb > self.critical_threshold:
            self.stats['memory_warnings'] += 1
            if self.logger:
                self.logger.warning(f"CRITICAL: Memory usage {memory_mb:.1f}MB exceeds critical threshold {self.critical_threshold}MB")
                
        elif memory_mb > self.warning_threshold:
            self.stats['memory_warnings'] += 1
            if self.logger:
                self.logger.warning(f"WARNING: Memory usage {memory_mb:.1f}MB exceeds warning threshold {self.warning_threshold}MB")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        try:
            current_memory = self.process.memory_info().rss / 1024 / 1024
            return {
                'current_memory_mb': current_memory,
                'peak_memory_mb': self.peak_memory,
                'avg_memory_mb': self.stats['avg_memory_mb'],
                'memory_growth_mb': current_memory - self.baseline_memory if self.baseline_memory > 0 else 0,
                'memory_history': list(self.memory_history),
                'gc_stats': {
                    'collections': gc.get_stats(),
                    'counts': gc.get_count(),
                    'threshold': gc.get_threshold()
                }
            }
        except Exception:
            return {}
            
    def set_baseline(self):
        """设置内存基线"""
        try:
            self.baseline_memory = self.process.memory_info().rss / 1024 / 1024
            if self.logger:
                self.logger.info(f"Memory baseline set to {self.baseline_memory:.2f}MB")
        except Exception:
            pass


class SmartCacheManager:
    """智能缓存管理器"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        
        # 多层缓存系统
        self.caches = {
            'fonts': {},           # 字体对象缓存
            'font_renders': {},    # 字体渲染缓存
            'surfaces': {},        # Surface对象缓存
            'textures': {},        # 纹理缓存
            'ui_elements': {},     # UI元素缓存
            'animations': {}       # 动画帧缓存
        }
        
        # 缓存元数据
        self.access_count = defaultdict(int)
        self.access_time = defaultdict(float)
        self.cache_size = defaultdict(int)  # 估算的内存大小
        
        # 缓存策略配置
        self.ttl = defaultdict(lambda: 300.0)  # 默认5分钟TTL
        self.ttl.update({
            'font_renders': 60.0,   # 字体渲染1分钟
            'animations': 30.0,     # 动画帧30秒
            'ui_elements': 120.0    # UI元素2分钟
        })
        
        # 弱引用追踪
        self.weak_refs = {}
        
    def get_cached_item(self, cache_type: str, key: str, generator_func=None, *args, **kwargs):
        """获取缓存项目或生成新项目"""
        if cache_type not in self.caches:
            self.caches[cache_type] = {}
            
        cache = self.caches[cache_type]
        current_time = time.time()
        
        # 检查缓存命中
        if key in cache:
            item, creation_time = cache[key]
            
            # 检查TTL
            if current_time - creation_time > self.ttl[cache_type]:
                del cache[key]
                self._remove_metadata(key)
            else:
                # 更新访问统计
                self.access_count[key] += 1
                self.access_time[key] = current_time
                return item
        
        # 生成新项目
        if generator_func:
            try:
                item = generator_func(*args, **kwargs)
                self._add_to_cache(cache_type, key, item, current_time)
                return item
            except Exception:
                return None
        
        return None
    
    def _add_to_cache(self, cache_type: str, key: str, item: Any, creation_time: float):
        """添加项目到缓存"""
        cache = self.caches[cache_type]
        
        # 估算内存大小
        estimated_size = self._estimate_size(item)
        
        # 检查缓存限制
        if len(cache) >= self.max_size or self._get_total_cache_size() + estimated_size > self.max_memory_mb * 1024 * 1024:
            self._cleanup_cache(cache_type)
        
        # 添加到缓存
        cache[key] = (item, creation_time)
        self.access_count[key] = 1
        self.access_time[key] = creation_time
        self.cache_size[key] = estimated_size
        
        # 添加弱引用（如果可能）
        try:
            self.weak_refs[key] = weakref.ref(item, lambda ref: self._on_item_deleted(key))
        except TypeError:
            pass  # 对象不支持弱引用
    
    def _estimate_size(self, item: Any) -> int:
        """估算对象内存大小"""
        try:
            if isinstance(item, pygame.Surface):
                # Surface大小 = 宽度 * 高度 * 字节深度
                return item.get_width() * item.get_height() * item.get_bytesize()
            elif isinstance(item, pygame.font.Font):
                # 字体对象相对较小
                return 1024  # 估算1KB
            elif isinstance(item, str):
                return len(item.encode('utf-8'))
            else:
                # 使用sys.getsizeof作为备选
                return sys.getsizeof(item)
        except Exception:
            return 1024  # 默认1KB
    
    def _get_total_cache_size(self) -> int:
        """获取总缓存大小"""
        return sum(self.cache_size.values())
    
    def _cleanup_cache(self, cache_type: str):
        """清理缓存"""
        cache = self.caches[cache_type]
        current_time = time.time()
        
        # 收集清理候选项
        cleanup_candidates = []
        for key, (item, creation_time) in cache.items():
            # 计算优先级分数（越低越优先清理）
            access_count = self.access_count[key]
            last_access = self.access_time[key]
            age = current_time - creation_time
            
            # 分数 = 访问次数 * 最近访问时间权重 / 年龄权重
            score = access_count * (1.0 / max(1.0, current_time - last_access)) / max(1.0, age)
            cleanup_candidates.append((score, key))
        
        # 按分数排序，清理分数最低的项目
        cleanup_candidates.sort()
        items_to_remove = cleanup_candidates[:len(cleanup_candidates) // 4]  # 清理25%
        
        for _, key in items_to_remove:
            if key in cache:
                del cache[key]
            self._remove_metadata(key)
    
    def _remove_metadata(self, key: str):
        """移除项目的元数据"""
        if key in self.access_count:
            del self.access_count[key]
        if key in self.access_time:
            del self.access_time[key]
        if key in self.cache_size:
            del self.cache_size[key]
        if key in self.weak_refs:
            del self.weak_refs[key]
    
    def _on_item_deleted(self, key: str):
        """当项目被垃圾回收时的回调"""
        for cache in self.caches.values():
            if key in cache:
                del cache[key]
        self._remove_metadata(key)
    
    def force_cleanup(self, cache_type: Optional[str] = None):
        """强制清理缓存"""
        if cache_type:
            if cache_type in self.caches:
                self._cleanup_cache(cache_type)
        else:
            for cache_type in self.caches:
                self._cleanup_cache(cache_type)
    
    def clear_all_caches(self):
        """清空所有缓存"""
        for cache in self.caches.values():
            cache.clear()
        self.access_count.clear()
        self.access_time.clear()
        self.cache_size.clear()
        self.weak_refs.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {}
        total_size = 0
        total_items = 0
        
        for cache_type, cache in self.caches.items():
            cache_size = sum(self.cache_size[key] for key in cache.keys() if key in self.cache_size)
            stats[cache_type] = {
                'items': len(cache),
                'size_bytes': cache_size,
                'size_mb': cache_size / 1024 / 1024,
                'hit_rate': 0.0  # TODO: 实现命中率统计
            }
            total_size += cache_size
            total_items += len(cache)
        
        stats['total'] = {
            'items': total_items,
            'size_bytes': total_size,
            'size_mb': total_size / 1024 / 1024,
            'memory_efficiency': min(100.0, (total_size / (self.max_memory_mb * 1024 * 1024)) * 100)
        }
        
        return stats


class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self, memory_monitor: MemoryMonitor, cache_manager: SmartCacheManager, logger=None):
        self.memory_monitor = memory_monitor
        self.cache_manager = cache_manager
        self.logger = logger
        
        # 优化策略配置
        self.optimization_thresholds = {
            'memory_warning': 400,      # MB
            'memory_critical': 600,     # MB
            'cache_cleanup': 300,       # MB
            'force_gc': 500            # MB
        }
        
        # 优化历史
        self.optimization_history = deque(maxlen=50)
        
    def optimize_memory(self) -> List[str]:
        """执行内存优化"""
        optimizations = []
        current_memory = self._get_current_memory()
        
        if current_memory > self.optimization_thresholds['force_gc']:
            # 强制垃圾回收
            collected = self._force_garbage_collection()
            optimizations.append(f"Forced garbage collection: freed {collected} objects")
        
        if current_memory > self.optimization_thresholds['cache_cleanup']:
            # 清理缓存
            self.cache_manager.force_cleanup()
            optimizations.append("Performed cache cleanup")
        
        if current_memory > self.optimization_thresholds['memory_critical']:
            # 激进优化
            self._aggressive_optimization()
            optimizations.append("Applied aggressive memory optimization")
        
        # 记录优化历史
        if optimizations:
            self.optimization_history.append({
                'time': time.time(),
                'memory_before': current_memory,
                'memory_after': self._get_current_memory(),
                'optimizations': optimizations
            })
        
        return optimizations
    
    def _get_current_memory(self) -> float:
        """获取当前内存使用（MB）"""
        try:
            return self.memory_monitor.process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def _force_garbage_collection(self) -> int:
        """强制垃圾回收"""
        collected = 0
        for generation in range(3):
            collected += gc.collect(generation)
        
        if self.logger:
            self.logger.info(f"Garbage collection freed {collected} objects")
        
        return collected
    
    def _aggressive_optimization(self):
        """激进内存优化"""
        # 清空所有缓存
        self.cache_manager.clear_all_caches()
        
        # 清理pygame缓存
        try:
            pygame.font.quit()
            pygame.font.init()
        except Exception:
            pass
        
        # 强制垃圾回收
        self._force_garbage_collection()
        
        if self.logger:
            self.logger.warning("Applied aggressive memory optimization")
    
    def suggest_optimizations(self) -> List[str]:
        """建议内存优化策略"""
        suggestions = []
        current_memory = self._get_current_memory()
        cache_stats = self.cache_manager.get_cache_stats()
        
        # 基于内存使用的建议
        if current_memory > 400:
            suggestions.append("Consider reducing texture quality or resolution")
        
        if current_memory > 300:
            suggestions.append("Enable automatic cache cleanup")
        
        # 基于缓存统计的建议
        total_cache_mb = cache_stats.get('total', {}).get('size_mb', 0)
        if total_cache_mb > 50:
            suggestions.append("Cache usage is high, consider reducing cache size limits")
        
        # 基于历史数据的建议
        if len(self.optimization_history) > 5:
            recent_optimizations = list(self.optimization_history)[-5:]
            optimization_frequency = len(recent_optimizations) / 5
            if optimization_frequency > 0.5:
                suggestions.append("Frequent memory optimizations detected, consider tuning cache settings")
        
        return suggestions
    
    def get_memory_report(self) -> Dict[str, Any]:
        """生成内存报告"""
        return {
            'current_memory': self._get_current_memory(),
            'memory_stats': self.memory_monitor.get_memory_stats(),
            'cache_stats': self.cache_manager.get_cache_stats(),
            'optimization_history': list(self.optimization_history),
            'suggestions': self.suggest_optimizations()
        }