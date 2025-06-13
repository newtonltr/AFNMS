#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
负责加载、验证和管理AI模型和数据源配置
支持热重载和环境变量覆盖
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更监听器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            logger.info(f"检测到配置文件变更: {event.src_path}")
            self.config_manager.reload_config()

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.ai_config_path = self.config_dir / "ai_config.json"
        self.sources_config_path = self.config_dir / "sources_config.json"
        
        self.ai_config = {}
        self.sources_config = {}
        self._lock = threading.Lock()
        self._observer = None
        
        # 加载配置
        self.load_config()
        
        # 启动文件监控
        self.start_file_watcher()
    
    def load_config(self) -> bool:
        """加载所有配置文件"""
        try:
            with self._lock:
                # 加载AI配置
                if self.ai_config_path.exists():
                    with open(self.ai_config_path, 'r', encoding='utf-8') as f:
                        self.ai_config = json.load(f)
                    self._apply_env_overrides_ai()
                    logger.info("AI配置加载成功")
                else:
                    logger.warning(f"AI配置文件不存在: {self.ai_config_path}")
                    return False
                
                # 加载数据源配置
                if self.sources_config_path.exists():
                    with open(self.sources_config_path, 'r', encoding='utf-8') as f:
                        self.sources_config = json.load(f)
                    self._apply_env_overrides_sources()
                    logger.info("数据源配置加载成功")
                else:
                    logger.warning(f"数据源配置文件不存在: {self.sources_config_path}")
                    return False
                
                return self.validate_config()
                    
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return False
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载配置...")
        if self.load_config():
            logger.info("配置重新加载成功")
        else:
            logger.error("配置重新加载失败")
    
    def _apply_env_overrides_ai(self):
        """应用环境变量覆盖AI配置"""
        for model in self.ai_config.get('models', []):
            model_id = model.get('id', '')
            env_key = f"AI_{model_id.upper().replace('-', '_')}_API_KEY"
            if env_key in os.environ:
                model['api_key'] = os.environ[env_key]
                logger.info(f"使用环境变量覆盖 {model_id} 的API密钥")
    
    def _apply_env_overrides_sources(self):
        """应用环境变量覆盖数据源配置"""
        auth_sources = self.sources_config.get('authenticated_sources', {})
        
        # Twitter配置覆盖
        if 'twitter' in auth_sources:
            twitter_config = auth_sources['twitter']
            env_mappings = {
                'TWITTER_API_KEY': 'api_key',
                'TWITTER_API_SECRET': 'api_secret',
                'TWITTER_ACCESS_TOKEN': 'access_token',
                'TWITTER_ACCESS_TOKEN_SECRET': 'access_token_secret',
                'TWITTER_BEARER_TOKEN': 'bearer_token'
            }
            
            for env_key, config_key in env_mappings.items():
                if env_key in os.environ:
                    twitter_config[config_key] = os.environ[env_key]
        
        # YouTube配置覆盖
        if 'youtube' in auth_sources and 'YOUTUBE_API_KEY' in os.environ:
            auth_sources['youtube']['api_key'] = os.environ['YOUTUBE_API_KEY']
        
        # News API配置覆盖
        if 'news_api' in auth_sources and 'NEWS_API_KEY' in os.environ:
            auth_sources['news_api']['api_key'] = os.environ['NEWS_API_KEY']
    
    def validate_config(self) -> bool:
        """验证配置文件的完整性和正确性"""
        try:
            # 验证AI配置
            if 'models' not in self.ai_config:
                logger.error("AI配置缺少models字段")
                return False
            
            models = self.ai_config['models']
            if not isinstance(models, list) or len(models) == 0:
                logger.error("AI配置models字段必须是非空列表")
                return False
            
            # 验证数据源配置
            required_sections = ['authenticated_sources', 'free_sources']
            for section in required_sections:
                if section not in self.sources_config:
                    logger.error(f"数据源配置缺少 {section} 部分")
                    return False
            
            logger.info("配置验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置验证异常: {e}")
            return False
    
    def get_ai_models(self) -> List[Dict]:
        """获取启用的AI模型配置，按优先级排序"""
        with self._lock:
            models = [m for m in self.ai_config.get('models', []) if m.get('enabled', False)]
            return sorted(models, key=lambda x: x.get('priority', 999))
    
    def get_model_by_id(self, model_id: str) -> Optional[Dict]:
        """根据ID获取模型配置"""
        with self._lock:
            for model in self.ai_config.get('models', []):
                if model.get('id') == model_id:
                    return model
            return None
    
    def get_authenticated_sources(self) -> Dict:
        """获取认证数据源配置"""
        with self._lock:
            return self.sources_config.get('authenticated_sources', {})
    
    def get_free_sources(self) -> Dict:
        """获取免费数据源配置"""
        with self._lock:
            return self.sources_config.get('free_sources', {})
    
    def get_rss_feeds(self) -> List[Dict]:
        """获取RSS订阅源列表"""
        with self._lock:
            rss_config = self.sources_config.get('free_sources', {}).get('rss_feeds', {})
            if rss_config.get('enabled', False):
                return rss_config.get('feeds', [])
            return []
    
    def get_public_apis(self) -> List[Dict]:
        """获取公开API配置"""
        with self._lock:
            api_config = self.sources_config.get('free_sources', {}).get('public_apis', {})
            if api_config.get('enabled', False):
                return [api for api in api_config.get('sources', []) if api.get('enabled', False)]
            return []
    
    def get_ai_config_value(self, key: str, default=None):
        """获取AI配置中的特定值"""
        with self._lock:
            return self.ai_config.get(key, default)
    
    def get_sources_config_value(self, key: str, default=None):
        """获取数据源配置中的特定值"""
        with self._lock:
            return self.sources_config.get(key, default)
    
    def update_model_status(self, model_id: str, enabled: bool):
        """更新模型启用状态"""
        with self._lock:
            for model in self.ai_config.get('models', []):
                if model.get('id') == model_id:
                    model['enabled'] = enabled
                    logger.info(f"模型 {model_id} 状态更新为: {enabled}")
                    break
    
    def start_file_watcher(self):
        """启动配置文件监控"""
        try:
            if self._observer is None:
                self._observer = Observer()
                event_handler = ConfigFileHandler(self)
                self._observer.schedule(event_handler, str(self.config_dir), recursive=False)
                self._observer.start()
                logger.info("配置文件监控已启动")
        except Exception as e:
            logger.error(f"启动文件监控失败: {e}")
    
    def stop_file_watcher(self):
        """停止配置文件监控"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("配置文件监控已停止")
    
    def __del__(self):
        """析构函数，确保清理资源"""
        self.stop_file_watcher()

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def reload_global_config():
    """重新加载全局配置"""
    global _config_manager
    if _config_manager:
        _config_manager.reload_config() 