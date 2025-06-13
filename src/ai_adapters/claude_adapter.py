#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude API适配器
支持Anthropic Claude API
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict
from .base_adapter import BaseAIAdapter, AIAnalysisResult

logger = logging.getLogger(__name__)

class ClaudeAdapter(BaseAIAdapter):
    """Claude API适配器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
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
            
            logger.debug(f"Claude分析完成，耗时: {response_time:.2f}s")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_usage_stats(False, response_time)
            logger.error(f"Claude分析失败: {e}")
            
            # 返回错误处理结果
            return AIAnalysisResult(
                impact_score=0.3,
                market_prediction=f"Claude AI分析服务暂时不可用: {str(e)}",
                trading_suggestion="请等待服务恢复后再次分析，谨慎投资",
                sentiment="neutral",
                confidence=0.1,
                key_points=["服务异常", "建议人工分析"]
            )
    
    async def _make_api_request(self, prompt: str) -> str:
        """发送Claude API请求"""
        url = f"{self.base_url}/v1/messages"
        
        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
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
                    content = result.get('content', [{}])[0].get('text', '')
                    
                    # 更新token使用统计
                    usage = result.get('usage', {})
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)
                    total_tokens = input_tokens + output_tokens
                    
                    return content
                    
                else:
                    error_text = await response.text()
                    logger.error(f"Claude API错误 {response.status}: {error_text}")
                    raise Exception(f"API请求失败: HTTP {response.status}")
    
    async def health_check(self) -> bool:
        """Claude健康检查"""
        try:
            # 发送简单的测试请求
            test_prompt = "请回答：今天天气如何？（简短回答即可）"
            response = await asyncio.wait_for(
                self._make_api_request(test_prompt),
                timeout=15
            )
            
            # 检查响应是否合理
            is_healthy = len(response.strip()) > 0
            self._is_healthy = is_healthy
            self._last_health_check = time.time()
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Claude健康检查失败: {e}")
            self._is_healthy = False
            self._last_health_check = time.time()
            return False 