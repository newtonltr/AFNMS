#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Gemini API适配器
支持Google Gemini Pro API
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict
from .base_adapter import BaseAIAdapter, AIAnalysisResult

logger = logging.getLogger(__name__)

class GeminiAdapter(BaseAIAdapter):
    """Google Gemini API适配器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.headers = {
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
            
            logger.debug(f"Gemini分析完成，耗时: {response_time:.2f}s")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_usage_stats(False, response_time)
            logger.error(f"Gemini分析失败: {e}")
            
            # 返回错误处理结果
            return AIAnalysisResult(
                impact_score=0.3,
                market_prediction=f"Gemini AI分析服务暂时不可用: {str(e)}",
                trading_suggestion="请等待服务恢复后再次分析，谨慎投资",
                sentiment="neutral",
                confidence=0.1,
                key_points=["服务异常", "建议人工分析"]
            )
    
    async def _make_api_request(self, prompt: str) -> str:
        """发送Gemini API请求"""
        # Gemini API URL格式
        url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
                "topP": 0.8,
                "topK": 10
            }
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
                    candidates = result.get('candidates', [])
                    
                    if candidates and len(candidates) > 0:
                        content_parts = candidates[0].get('content', {}).get('parts', [])
                        if content_parts and len(content_parts) > 0:
                            text_content = content_parts[0].get('text', '')
                            return text_content
                    
                    logger.warning("Gemini API返回空响应")
                    return "无法获取有效响应"
                    
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API错误 {response.status}: {error_text}")
                    raise Exception(f"API请求失败: HTTP {response.status}")
    
    async def health_check(self) -> bool:
        """Gemini健康检查"""
        try:
            # 发送简单的测试请求
            test_prompt = "请回答：2+2等于几？"
            response = await asyncio.wait_for(
                self._make_api_request(test_prompt),
                timeout=15
            )
            
            # 检查响应是否合理
            is_healthy = len(response.strip()) > 0 and ('4' in response or '四' in response)
            self._is_healthy = is_healthy
            self._last_health_check = time.time()
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Gemini健康检查失败: {e}")
            self._is_healthy = False
            self._last_health_check = time.time()
            return False 