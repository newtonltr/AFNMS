#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xAI Grok API适配器
支持xAI Grok模型，使用OpenAI兼容格式
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict
from .base_adapter import BaseAIAdapter, AIAnalysisResult

logger = logging.getLogger(__name__)

class GrokAdapter(BaseAIAdapter):
    """xAI Grok API适配器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def analyze_news(self, news_content: str, news_source: str) -> AIAnalysisResult:
        """分析新闻内容"""
        start_time = time.time()
        
        try:
            # 构建提示词
            prompt = self._build_analysis_prompt(news_content, news_source)
            
            # 发送API请求
            response = await self._make_api_request(prompt)
            
            # 解析响应
            result = self._parse_response(response)
            
            # 更新统计信息
            response_time = time.time() - start_time
            self._update_usage_stats(True, response_time)
            
            logger.debug(f"Grok分析完成，耗时: {response_time:.2f}s")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_usage_stats(False, response_time)
            logger.error(f"Grok分析失败: {e}")
            
            # 返回错误处理结果
            return AIAnalysisResult(
                impact_score=0.3,
                market_prediction=f"Grok AI分析服务暂时不可用: {str(e)}",
                trading_suggestion="请等待服务恢复后再次分析，谨慎投资",
                sentiment="neutral",
                confidence=0.1,
                key_points=["服务异常", "建议人工分析"]
            )
    
    async def _make_api_request(self, prompt: str) -> str:
        """发送Grok API请求"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的金融分析师，具有实时信息访问能力，擅长分析新闻对市场的影响。请用中文回答。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    # 更新token使用统计
                    usage = result.get('usage', {})
                    total_tokens = usage.get('total_tokens', 0)
                    
                    return content
                    
                else:
                    error_text = await response.text()
                    logger.error(f"Grok API错误 {response.status}: {error_text}")
                    raise Exception(f"API请求失败: HTTP {response.status}")
    
    async def health_check(self) -> bool:
        """Grok健康检查"""
        try:
            # 发送简单的测试请求
            test_prompt = "请回答：5+5等于几？"
            response = await asyncio.wait_for(
                self._make_api_request(test_prompt),
                timeout=20  # Grok可能需要更长时间
            )
            
            # 检查响应是否合理
            is_healthy = len(response.strip()) > 0 and ('10' in response or '十' in response)
            self._is_healthy = is_healthy
            self._last_health_check = time.time()
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Grok健康检查失败: {e}")
            self._is_healthy = False
            self._last_health_check = time.time()
            return False 