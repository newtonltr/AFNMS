#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI适配器基类
定义统一的AI模型接口和通用功能
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIAnalysisResult:
    """AI分析结果数据结构"""
    impact_score: float
    market_prediction: str
    trading_suggestion: str
    sentiment: str
    confidence: float
    key_points: list

@dataclass
class UsageStats:
    """API使用统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    last_request_time: float = 0
    avg_response_time: float = 0

class BaseAIAdapter(ABC):
    """AI适配器基类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_id = config.get('id', 'unknown')
        self.model_type = config.get('type', 'unknown')
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', '')
        self.model_name = config.get('model', '')
        self.max_tokens = config.get('max_tokens', 1000)
        self.temperature = config.get('temperature', 0.3)
        self.timeout = config.get('timeout', 30)
        
        # 使用统计
        self.usage_stats = UsageStats()
        self._last_health_check = 0
        self._health_check_interval = 300  # 5分钟
        self._is_healthy = True
    
    @abstractmethod
    async def analyze_news(self, news_content: str, news_source: str) -> AIAnalysisResult:
        """分析新闻内容 - 子类必须实现"""
        pass
    
    @abstractmethod
    async def _make_api_request(self, prompt: str) -> str:
        """发送API请求 - 子类必须实现"""
        pass
    
    def _build_analysis_prompt(self, content: str, source: str) -> str:
        """构建分析提示词"""
        return f"""
你是一位专业的金融分析师，请分析以下新闻对股市和加密货币市场的影响：

新闻来源: {source}
新闻内容: {content}

请从以下几个维度进行分析，并以JSON格式返回结果：

1. 影响评分 (impact_score): 0-1之间的数值，表示对市场的影响程度
2. 市场预测 (market_prediction): 详细分析对股市、加密货币市场的具体影响
3. 交易建议 (trading_suggestion): 基于分析给出的交易建议
4. 情感倾向 (sentiment): positive/negative/neutral
5. 信心度 (confidence): 0-1之间，表示分析的可信度
6. 关键要点 (key_points): 3-5个关键分析要点的列表

请确保分析客观、专业，并包含风险提示。返回格式：
{{
    "impact_score": 0.7,
    "market_prediction": "...",
    "trading_suggestion": "...",
    "sentiment": "negative",
    "confidence": 0.8,
    "key_points": ["要点1", "要点2", "要点3"]
}}

当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def _parse_response(self, response: str) -> AIAnalysisResult:
        """解析AI响应"""
        import json
        import re
        
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                return AIAnalysisResult(
                    impact_score=float(data.get('impact_score', 0.5)),
                    market_prediction=data.get('market_prediction', ''),
                    trading_suggestion=data.get('trading_suggestion', ''),
                    sentiment=data.get('sentiment', 'neutral'),
                    confidence=float(data.get('confidence', 0.5)),
                    key_points=data.get('key_points', [])
                )
        except Exception as e:
            logger.error(f"解析AI响应失败: {e}")
        
        # 如果JSON解析失败，返回默认结果
        return self._create_fallback_result(response)
    
    def _create_fallback_result(self, response: str) -> AIAnalysisResult:
        """创建后备分析结果"""
        # 基于关键词的简单分析
        impact_score = 0.5
        sentiment = 'neutral'
        
        response_lower = response.lower()
        if any(word in response_lower for word in ['重大', 'significant', 'major', 'critical']):
            impact_score = 0.8
        elif any(word in response_lower for word in ['轻微', 'minor', 'limited', 'small']):
            impact_score = 0.3
        
        if any(word in response_lower for word in ['积极', 'positive', 'bullish', 'up']):
            sentiment = 'positive'
        elif any(word in response_lower for word in ['消极', 'negative', 'bearish', 'down']):
            sentiment = 'negative'
        
        return AIAnalysisResult(
            impact_score=impact_score,
            market_prediction=response[:300] + "..." if len(response) > 300 else response,
            trading_suggestion="请基于分析结果谨慎投资，注意风险控制",
            sentiment=sentiment,
            confidence=0.4,
            key_points=["AI解析异常，建议人工审核"]
        )
    
    async def health_check(self) -> bool:
        """健康检查"""
        current_time = time.time()
        
        # 如果距离上次检查时间太短，返回缓存结果
        if current_time - self._last_health_check < self._health_check_interval:
            return self._is_healthy
        
        try:
            # 发送简单的测试请求
            test_prompt = "请简要回答：今天是星期几？"
            start_time = time.time()
            
            response = await asyncio.wait_for(
                self._make_api_request(test_prompt),
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            # 更新健康状态
            self._is_healthy = len(response.strip()) > 0 and response_time < 10
            self._last_health_check = current_time
            
            if self._is_healthy:
                logger.debug(f"模型 {self.model_id} 健康检查通过，响应时间: {response_time:.2f}s")
            else:
                logger.warning(f"模型 {self.model_id} 健康检查失败")
            
            return self._is_healthy
            
        except Exception as e:
            logger.error(f"模型 {self.model_id} 健康检查异常: {e}")
            self._is_healthy = False
            self._last_health_check = current_time
            return False
    
    def get_usage_stats(self) -> Dict:
        """获取使用统计"""
        success_rate = (self.usage_stats.successful_requests / 
                       max(self.usage_stats.total_requests, 1)) * 100
        
        return {
            'model_id': self.model_id,
            'model_type': self.model_type,
            'total_requests': self.usage_stats.total_requests,
            'successful_requests': self.usage_stats.successful_requests,
            'failed_requests': self.usage_stats.failed_requests,
            'success_rate': f"{success_rate:.2f}%",
            'total_tokens': self.usage_stats.total_tokens,
            'avg_response_time': f"{self.usage_stats.avg_response_time:.2f}s",
            'last_request_time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                             time.localtime(self.usage_stats.last_request_time)),
            'is_healthy': self._is_healthy
        }
    
    def _update_usage_stats(self, success: bool, response_time: float, tokens: int = 0):
        """更新使用统计"""
        self.usage_stats.total_requests += 1
        self.usage_stats.last_request_time = time.time()
        
        if success:
            self.usage_stats.successful_requests += 1
            self.usage_stats.total_tokens += tokens
            
            # 更新平均响应时间
            total_successful = self.usage_stats.successful_requests
            current_avg = self.usage_stats.avg_response_time
            self.usage_stats.avg_response_time = (
                (current_avg * (total_successful - 1) + response_time) / total_successful
            )
        else:
            self.usage_stats.failed_requests += 1
    
    def is_configured(self) -> bool:
        """检查是否已正确配置"""
        return bool(self.api_key and self.base_url and self.model_name)
    
    def __str__(self):
        return f"{self.model_type.upper()}Adapter({self.model_id})" 