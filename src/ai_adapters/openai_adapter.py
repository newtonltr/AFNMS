#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI API适配器
支持官方OpenAI API和兼容OpenAI格式的API服务
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict
from .base_adapter import BaseAIAdapter, AIAnalysisResult

logger = logging.getLogger(__name__)

class OpenAIAdapter(BaseAIAdapter):
    """OpenAI API适配器"""
    
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
            
            logger.debug(f"OpenAI分析完成，耗时: {response_time:.2f}s")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_usage_stats(False, response_time)
            logger.error(f"OpenAI分析失败: {e}")
            
            # 返回错误处理结果
            return AIAnalysisResult(
                impact_score=0.3,
                market_prediction=f"AI分析服务暂时不可用: {str(e)}",
                trading_suggestion="请等待服务恢复后再次分析，谨慎投资",
                sentiment="neutral",
                confidence=0.1,
                key_points=["服务异常", "建议人工分析"]
            )
    
    async def _make_api_request(self, prompt: str) -> str:
        """发送OpenAI API请求"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的金融分析师，擅长分析新闻对市场的影响。请用中文回答。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature
        }
        
        # 只有当max_tokens不为null时才添加该参数
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        
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
                    logger.error(f"OpenAI API错误 {response.status}: {error_text}")
                    raise Exception(f"API请求失败: HTTP {response.status}")
    
    async def health_check(self) -> bool:
        """OpenAI健康检查"""
        try:
            # 发送简单的测试请求
            test_prompt = "请回答：1+1等于几？"
            response = await asyncio.wait_for(
                self._make_api_request(test_prompt),
                timeout=10
            )
            
            # 检查响应是否合理
            is_healthy = len(response.strip()) > 0 and '2' in response
            self._is_healthy = is_healthy
            self._last_health_check = time.time()
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"OpenAI健康检查失败: {e}")
            self._is_healthy = False
            self._last_health_check = time.time()
            return False 