#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能模型路由器
负责管理多个AI适配器的负载均衡、故障转移和智能选择
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Type
from .config_manager import get_config_manager
from .ai_adapters.base_adapter import BaseAIAdapter, AIAnalysisResult
from .ai_adapters.openai_adapter import OpenAIAdapter
from .ai_adapters.claude_adapter import ClaudeAdapter
from .ai_adapters.gemini_adapter import GeminiAdapter
from .ai_adapters.openrouter_adapter import OpenRouterAdapter
from .ai_adapters.grok_adapter import GrokAdapter

logger = logging.getLogger(__name__)

class ModelRouter:
    """智能模型路由器"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.adapters: Dict[str, BaseAIAdapter] = {}
        self._adapter_classes = {
            'openai': OpenAIAdapter,
            'claude': ClaudeAdapter,
            'gemini': GeminiAdapter,
            'openrouter': OpenRouterAdapter,
            'grok': GrokAdapter
        }
        
        # 路由统计
        self.routing_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'fallback_count': 0,
            'last_health_check': 0
        }
        
        # 初始化适配器
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """初始化所有配置的AI适配器"""
        models = self.config_manager.get_ai_models()
        
        for model_config in models:
            model_id = model_config.get('id')
            model_type = model_config.get('type')
            
            if model_type in self._adapter_classes:
                try:
                    # 检查配置是否完整
                    if not model_config.get('api_key'):
                        logger.warning(f"模型 {model_id} 缺少API密钥，跳过初始化")
                        continue
                    
                    # 创建适配器实例
                    adapter_class = self._adapter_classes[model_type]
                    adapter = adapter_class(model_config)
                    
                    if adapter.is_configured():
                        self.adapters[model_id] = adapter
                        logger.info(f"成功初始化适配器: {model_id}")
                    else:
                        logger.warning(f"适配器 {model_id} 配置不完整")
                        
                except Exception as e:
                    logger.error(f"初始化适配器 {model_id} 失败: {e}")
            else:
                logger.warning(f"不支持的模型类型: {model_type}")
        
        logger.info(f"成功初始化 {len(self.adapters)} 个AI适配器")
    
    async def analyze_news(self, news_content: str, news_source: str) -> AIAnalysisResult:
        """分析新闻，自动选择最佳可用的AI模型"""
        self.routing_stats['total_requests'] += 1
        
        # 获取健康的适配器列表，按优先级排序
        healthy_adapters = await self._get_healthy_adapters()
        
        if not healthy_adapters:
            logger.error("没有可用的AI适配器")
            self.routing_stats['failed_requests'] += 1
            return self._create_fallback_result("所有AI服务均不可用")
        
        # 尝试使用适配器进行分析
        for adapter_id, adapter in healthy_adapters:
            try:
                logger.debug(f"使用适配器 {adapter_id} 进行分析")
                result = await adapter.analyze_news(news_content, news_source)
                
                # 检查结果质量
                if self._is_valid_result(result):
                    self.routing_stats['successful_requests'] += 1
                    logger.info(f"适配器 {adapter_id} 分析成功")
                    return result
                else:
                    logger.warning(f"适配器 {adapter_id} 返回了低质量结果")
                    
            except Exception as e:
                logger.error(f"适配器 {adapter_id} 分析失败: {e}")
                continue
        
        # 所有适配器都失败了
        self.routing_stats['failed_requests'] += 1
        self.routing_stats['fallback_count'] += 1
        logger.error("所有AI适配器都分析失败，返回后备结果")
        
        return self._create_fallback_result("AI分析失败，请稍后重试")
    
    async def _get_healthy_adapters(self) -> List[tuple]:
        """获取健康的适配器列表，按优先级排序"""
        current_time = time.time()
        
        # 如果距离上次健康检查超过5分钟，执行健康检查
        if current_time - self.routing_stats['last_health_check'] > 300:
            await self._perform_health_checks()
            self.routing_stats['last_health_check'] = current_time
        
        # 获取所有模型配置，按优先级排序
        models = self.config_manager.get_ai_models()
        healthy_adapters = []
        
        for model_config in models:
            model_id = model_config.get('id')
            if model_id in self.adapters:
                adapter = self.adapters[model_id]
                if adapter._is_healthy:
                    healthy_adapters.append((model_id, adapter))
        
        return healthy_adapters
    
    async def _perform_health_checks(self):
        """并发执行所有适配器的健康检查"""
        if not self.adapters:
            return
        
        logger.debug("开始执行适配器健康检查")
        
        # 创建并发任务
        health_check_tasks = []
        for adapter_id, adapter in self.adapters.items():
            task = asyncio.create_task(
                self._check_adapter_health(adapter_id, adapter)
            )
            health_check_tasks.append(task)
        
        # 等待所有健康检查完成
        await asyncio.gather(*health_check_tasks, return_exceptions=True)
        
        # 统计健康状态
        healthy_count = sum(1 for adapter in self.adapters.values() if adapter._is_healthy)
        logger.info(f"健康检查完成，{healthy_count}/{len(self.adapters)} 个适配器健康")
    
    async def _check_adapter_health(self, adapter_id: str, adapter: BaseAIAdapter):
        """检查单个适配器的健康状态"""
        try:
            is_healthy = await adapter.health_check()
            status = "健康" if is_healthy else "不健康"
            logger.debug(f"适配器 {adapter_id} 状态: {status}")
        except Exception as e:
            logger.error(f"适配器 {adapter_id} 健康检查异常: {e}")
            adapter._is_healthy = False
    
    def _is_valid_result(self, result: AIAnalysisResult) -> bool:
        """检查分析结果是否有效"""
        if not result:
            return False
        
        # 检查基本字段
        if not result.market_prediction or not result.trading_suggestion:
            return False
        
        # 检查影响评分是否在合理范围内
        if not (0 <= result.impact_score <= 1):
            return False
        
        # 检查信心度是否在合理范围内
        if not (0 <= result.confidence <= 1):
            return False
        
        # 检查情感分析是否有效
        if result.sentiment not in ['positive', 'negative', 'neutral']:
            return False
        
        return True
    
    def _create_fallback_result(self, error_message: str) -> AIAnalysisResult:
        """创建后备分析结果"""
        return AIAnalysisResult(
            impact_score=0.3,
            market_prediction=f"AI分析服务暂时不可用: {error_message}",
            trading_suggestion="由于AI分析服务异常，建议暂停自动交易，等待服务恢复后再做决策",
            sentiment="neutral",
            confidence=0.1,
            key_points=[
                "AI服务异常",
                "建议人工分析",
                "谨慎投资",
                "等待服务恢复"
            ]
        )
    
    def get_router_stats(self) -> Dict:
        """获取路由器统计信息"""
        total_requests = self.routing_stats['total_requests']
        success_rate = (self.routing_stats['successful_requests'] / 
                       max(total_requests, 1)) * 100
        
        # 获取各适配器统计
        adapter_stats = {}
        for adapter_id, adapter in self.adapters.items():
            adapter_stats[adapter_id] = adapter.get_usage_stats()
        
        return {
            'router_stats': {
                'total_requests': total_requests,
                'successful_requests': self.routing_stats['successful_requests'],
                'failed_requests': self.routing_stats['failed_requests'],
                'success_rate': f"{success_rate:.2f}%",
                'fallback_count': self.routing_stats['fallback_count'],
                'active_adapters': len([a for a in self.adapters.values() if a._is_healthy]),
                'total_adapters': len(self.adapters)
            },
            'adapter_stats': adapter_stats
        }
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return list(self.adapters.keys())
    
    def get_healthy_models(self) -> List[str]:
        """获取健康的模型列表"""
        return [adapter_id for adapter_id, adapter in self.adapters.items() 
                if adapter._is_healthy]
    
    async def force_health_check(self):
        """强制执行健康检查"""
        await self._perform_health_checks()
    
    def reload_config(self):
        """重新加载配置并重新初始化适配器"""
        logger.info("重新加载模型路由器配置")
        self.config_manager.reload_config()
        
        # 清除现有适配器
        self.adapters.clear()
        
        # 重新初始化
        self._initialize_adapters()

# 全局路由器实例
_model_router = None

def get_model_router() -> ModelRouter:
    """获取全局模型路由器实例"""
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router 