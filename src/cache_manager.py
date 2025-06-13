#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理器
提供新闻数据的缓存功能，减少重复请求和提高性能
"""

import json
import time
import hashlib
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # 确保缓存目录存在
        self.cache_dir.mkdir(exist_ok=True)
        
        # 内存缓存
        self.memory_cache = {}
        self.memory_cache_timestamps = {}
        
        # 缓存配置
        self.default_ttl = 300  # 5分钟默认TTL
        self.memory_cache_limit = 1000  # 内存缓存最大条目数
        
        # 统计信息
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'deletes': 0,
            'evictions': 0
        }
    
    def _generate_cache_key(self, namespace: str, key: str) -> str:
        """生成缓存键"""
        combined = f"{namespace}:{key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, namespace: str, key: str, default=None) -> Any:
        """获取缓存数据"""
        cache_key = self._generate_cache_key(namespace, key)
        
        # 先检查内存缓存
        if cache_key in self.memory_cache:
            timestamp = self.memory_cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self.default_ttl:
                self.stats['hits'] += 1
                logger.debug(f"内存缓存命中: {namespace}:{key}")
                return self.memory_cache[cache_key]
            else:
                # 过期，从内存缓存中删除
                self._remove_from_memory_cache(cache_key)
        
        # 检查文件缓存
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # 检查是否过期
                if cache_data.get('expires_at', 0) > time.time():
                    data = cache_data.get('data')
                    
                    # 加载到内存缓存
                    self._add_to_memory_cache(cache_key, data)
                    
                    self.stats['hits'] += 1
                    logger.debug(f"文件缓存命中: {namespace}:{key}")
                    return data
                else:
                    # 过期，删除文件
                    cache_file.unlink()
                    logger.debug(f"缓存过期已删除: {namespace}:{key}")
                    
            except Exception as e:
                logger.error(f"读取缓存文件失败: {e}")
                # 删除损坏的缓存文件
                try:
                    cache_file.unlink()
                except:
                    pass
        
        self.stats['misses'] += 1
        logger.debug(f"缓存未命中: {namespace}:{key}")
        return default
    
    def set(self, namespace: str, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存数据"""
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._generate_cache_key(namespace, key)
        expires_at = time.time() + ttl
        
        try:
            # 添加到内存缓存
            self._add_to_memory_cache(cache_key, data)
            
            # 保存到文件缓存
            cache_data = {
                'data': data,
                'created_at': time.time(),
                'expires_at': expires_at,
                'namespace': namespace,
                'key': key
            }
            
            cache_file = self._get_cache_file_path(cache_key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.stats['writes'] += 1
            logger.debug(f"缓存写入成功: {namespace}:{key}, TTL: {ttl}s")
            
            # 检查缓存大小
            self._cleanup_if_needed()
            
            return True
            
        except Exception as e:
            logger.error(f"缓存写入失败: {e}")
            return False
    
    def delete(self, namespace: str, key: str) -> bool:
        """删除缓存数据"""
        cache_key = self._generate_cache_key(namespace, key)
        
        # 从内存缓存删除
        self._remove_from_memory_cache(cache_key)
        
        # 从文件缓存删除
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                cache_file.unlink()
                self.stats['deletes'] += 1
                logger.debug(f"缓存删除成功: {namespace}:{key}")
                return True
            except Exception as e:
                logger.error(f"缓存删除失败: {e}")
                return False
        
        return True
    
    def clear_namespace(self, namespace: str) -> int:
        """清除指定命名空间的所有缓存"""
        cleared_count = 0
        
        # 清除内存缓存中的相关条目
        keys_to_remove = []
        for cache_key in list(self.memory_cache.keys()):
            cache_file = self._get_cache_file_path(cache_key)
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    if cache_data.get('namespace') == namespace:
                        keys_to_remove.append(cache_key)
                except:
                    pass
        
        for cache_key in keys_to_remove:
            self._remove_from_memory_cache(cache_key)
        
        # 清除文件缓存中的相关条目
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if cache_data.get('namespace') == namespace:
                    cache_file.unlink()
                    cleared_count += 1
                    
            except Exception as e:
                logger.error(f"清除缓存文件失败: {e}")
        
        logger.info(f"命名空间 {namespace} 缓存清除完成，共清除 {cleared_count} 条")
        return cleared_count
    
    def clear_all(self) -> int:
        """清除所有缓存"""
        cleared_count = 0
        
        # 清除内存缓存
        self.memory_cache.clear()
        self.memory_cache_timestamps.clear()
        
        # 清除文件缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                cleared_count += 1
            except Exception as e:
                logger.error(f"清除缓存文件失败: {e}")
        
        logger.info(f"所有缓存清除完成，共清除 {cleared_count} 条")
        return cleared_count
    
    def _add_to_memory_cache(self, cache_key: str, data: Any):
        """添加到内存缓存"""
        # 如果内存缓存已满，删除最旧的条目
        if len(self.memory_cache) >= self.memory_cache_limit:
            oldest_key = min(self.memory_cache_timestamps.keys(), 
                           key=self.memory_cache_timestamps.get)
            self._remove_from_memory_cache(oldest_key)
            self.stats['evictions'] += 1
        
        self.memory_cache[cache_key] = data
        self.memory_cache_timestamps[cache_key] = time.time()
    
    def _remove_from_memory_cache(self, cache_key: str):
        """从内存缓存中移除"""
        self.memory_cache.pop(cache_key, None)
        self.memory_cache_timestamps.pop(cache_key, None)
    
    def _cleanup_if_needed(self):
        """如果需要，清理缓存"""
        current_size = self._get_cache_size()
        
        if current_size > self.max_size_bytes:
            logger.info(f"缓存大小超限 ({current_size / 1024 / 1024:.2f}MB)，开始清理")
            self._cleanup_old_cache()
    
    def _get_cache_size(self) -> int:
        """获取缓存目录大小"""
        total_size = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                total_size += cache_file.stat().st_size
            except:
                pass
        return total_size
    
    def _cleanup_old_cache(self):
        """清理旧缓存"""
        cache_files = []
        
        # 收集所有缓存文件及其创建时间
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                created_at = cache_data.get('created_at', 0)
                cache_files.append((cache_file, created_at))
                
            except:
                # 损坏的文件直接删除
                try:
                    cache_file.unlink()
                except:
                    pass
        
        # 按创建时间排序，删除最旧的一半
        cache_files.sort(key=lambda x: x[1])
        files_to_delete = cache_files[:len(cache_files) // 2]
        
        deleted_count = 0
        for cache_file, _ in files_to_delete:
            try:
                cache_file.unlink()
                deleted_count += 1
            except:
                pass
        
        logger.info(f"缓存清理完成，删除了 {deleted_count} 个旧文件")
    
    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / max(total_requests, 1)) * 100
        
        cache_size = self._get_cache_size()
        cache_count = len(list(self.cache_dir.glob("*.json")))
        
        return {
            'hit_rate': f"{hit_rate:.2f}%",
            'total_requests': total_requests,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'writes': self.stats['writes'],
            'deletes': self.stats['deletes'],
            'evictions': self.stats['evictions'],
            'cache_size_mb': f"{cache_size / 1024 / 1024:.2f}",
            'cache_count': cache_count,
            'memory_cache_count': len(self.memory_cache),
            'max_size_mb': self.max_size_mb
        }
    
    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        current_time = time.time()
        expired_count = 0
        
        # 清理内存缓存中的过期条目
        expired_memory_keys = []
        for cache_key, timestamp in self.memory_cache_timestamps.items():
            if current_time - timestamp > self.default_ttl:
                expired_memory_keys.append(cache_key)
        
        for cache_key in expired_memory_keys:
            self._remove_from_memory_cache(cache_key)
            expired_count += 1
        
        # 清理文件缓存中的过期条目
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if cache_data.get('expires_at', 0) < current_time:
                    cache_file.unlink()
                    expired_count += 1
                    
            except Exception as e:
                logger.error(f"清理过期缓存失败: {e}")
                # 删除损坏的文件
                try:
                    cache_file.unlink()
                    expired_count += 1
                except:
                    pass
        
        if expired_count > 0:
            logger.info(f"清理了 {expired_count} 个过期缓存条目")
        
        return expired_count

# 全局缓存管理器实例
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager 