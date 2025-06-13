#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI增强的自动化金融新闻播报系统
结合程序自动抓取 + AI大模型智能分析
监控各大平台的新闻动态，分析对股市和加密货币的影响
"""

import requests
import tweepy
import time
import json
import re
import openai
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import anthropic  # Claude API
from openai import AsyncOpenAI  # OpenAI API
import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入新架构组件
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from config_manager import ConfigManager
    from free_data_collector import FreeDataCollector
    ENHANCED_MODE = True
    logger.info("增强模式已启用：支持免费数据源")
except ImportError as e:
    logger.warning(f"无法导入增强组件: {e}")
    logger.info("使用基础模式：仅支持API数据源")
    ENHANCED_MODE = False

@dataclass
class AIAnalysisResult:
    """AI分析结果数据结构"""
    impact_score: float
    market_prediction: str
    trading_suggestion: str
    sentiment: str
    confidence: float
    key_points: List[str]

@dataclass
class NewsItem:
    """新闻项目数据结构"""
    timestamp: str
    source: str
    title: str
    content: str
    url: str
    ai_analysis: Optional[AIAnalysisResult] = None
    
class AIFinancialAnalyzer:
    """AI金融分析器 - 支持多种大模型"""
    
    def __init__(self, model_config: Dict):
        self.model_config = model_config
        self.model_type = model_config.get('type', 'openai')
        
        # 初始化不同的AI客户端
        if self.model_type == 'openai':
            self.client = AsyncOpenAI(api_key=model_config['api_key'])
            self.model_name = model_config.get('model', 'gpt-4')
        elif self.model_type == 'claude':
            self.client = anthropic.Anthropic(api_key=model_config['api_key'])
            self.model_name = model_config.get('model', 'claude-3-sonnet-20240229')
        elif self.model_type == 'custom':
            # 支持自定义API端点（如本地部署的模型）
            self.api_url = model_config['api_url']
            self.headers = {'Authorization': f"Bearer {model_config['api_key']}"}
    
    async def analyze_news_with_ai(self, news_content: str, news_source: str) -> AIAnalysisResult:
        """使用AI分析新闻"""
        
        # 构建分析提示词
        analysis_prompt = self._build_analysis_prompt(news_content, news_source)
        
        try:
            if self.model_type == 'openai':
                result = await self._analyze_with_openai(analysis_prompt)
            elif self.model_type == 'claude':
                result = await self._analyze_with_claude(analysis_prompt)
            elif self.model_type == 'custom':
                result = await self._analyze_with_custom_api(analysis_prompt)
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")
            
            return self._parse_ai_response(result)
            
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            # 返回默认分析结果
            return AIAnalysisResult(
                impact_score=0.5,
                market_prediction="AI分析暂时无法完成，建议人工判断",
                trading_suggestion="请谨慎投资，等待更多信息",
                sentiment="neutral",
                confidence=0.3,
                key_points=["AI分析异常"]
            )
    
    def _build_analysis_prompt(self, content: str, source: str) -> str:
        """构建AI分析提示词"""
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

当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    async def _analyze_with_openai(self, prompt: str) -> str:
        """使用OpenAI API分析"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "你是一位专业的金融分析师，擅长分析新闻对市场的影响。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    async def _analyze_with_claude(self, prompt: str) -> str:
        """使用Claude API分析"""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.content[0].text
    
    async def _analyze_with_custom_api(self, prompt: str) -> str:
        """使用自定义API分析"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            async with session.post(
                self.api_url, 
                json=payload, 
                headers=self.headers
            ) as response:
                result = await response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
    
    def _parse_ai_response(self, response: str) -> AIAnalysisResult:
        """解析AI响应"""
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
        
        # 如果JSON解析失败，尝试文本解析
        return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> AIAnalysisResult:
        """解析文本格式的AI响应"""
        # 基于关键词的简单解析
        impact_score = 0.5
        sentiment = 'neutral'
        
        response_lower = response.lower()
        if any(word in response_lower for word in ['强烈', 'significant', 'major', 'critical']):
            impact_score = 0.8
        elif any(word in response_lower for word in ['轻微', 'minor', 'limited', 'small']):
            impact_score = 0.3
        
        if any(word in response_lower for word in ['积极', 'positive', 'bullish', 'up']):
            sentiment = 'positive'
        elif any(word in response_lower for word in ['消极', 'negative', 'bearish', 'down']):
            sentiment = 'negative'
        
        return AIAnalysisResult(
            impact_score=impact_score,
            market_prediction=response[:200] + "..." if len(response) > 200 else response,
            trading_suggestion="请基于AI分析结果谨慎投资",
            sentiment=sentiment,
            confidence=0.6,
            key_points=["AI文本分析结果"]
        )

class FinancialNewsMonitor:
    def __init__(self):
        # 初始化配置管理器
        global ENHANCED_MODE
        if ENHANCED_MODE:
            try:
                logger.debug("开始创建ConfigManager...")
                self.config_manager = ConfigManager()
                logger.debug("ConfigManager创建成功")
                
                logger.debug("开始加载增强配置...")
                self.config = self._load_enhanced_config()
                logger.debug("增强配置加载成功")
                
                logger.debug("开始创建FreeDataCollector...")
                self.free_data_collector = FreeDataCollector(self.config_manager)
                logger.debug("FreeDataCollector创建成功")
                
                logger.info("增强配置加载成功")
            except Exception as e:
                logger.error(f"增强配置加载失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                self.config = self._get_default_config()
                ENHANCED_MODE = False
        else:
            self.config = self._get_default_config()
        
        # 初始化AI分析器
        self.ai_analyzer = AIFinancialAnalyzer(self.config['ai_model'])
        
        # 初始化关键词和缓存
        self._init_keywords_and_cache()
    
    def _load_enhanced_config(self):
        """加载增强配置"""
        logger.debug("开始获取AI模型配置...")
        ai_models = self.config_manager.get_ai_models()
        logger.debug("开始获取认证数据源配置...")
        auth_sources = self.config_manager.get_authenticated_sources()
        logger.debug("配置获取完成")
        
        # 使用第一个可用的AI模型
        ai_model_config = None
        if ai_models:
            model_config = ai_models[0]  # 已经按优先级排序
            ai_model_config = {
                'type': model_config['type'],
                'api_key': model_config.get('api_key', ''),
                'model': model_config.get('model', ''),
                'api_url': model_config.get('base_url', '')
            }
        
        if not ai_model_config:
            ai_model_config = self._get_default_ai_config()
        
        return {
            'ai_model': ai_model_config,
            'twitter_api_key': auth_sources.get('twitter', {}).get('api_key', ''),
            'twitter_api_secret': auth_sources.get('twitter', {}).get('api_secret', ''),
            'twitter_access_token': auth_sources.get('twitter', {}).get('access_token', ''),
            'twitter_access_token_secret': auth_sources.get('twitter', {}).get('access_token_secret', ''),
            'twitter_bearer_token': auth_sources.get('twitter', {}).get('bearer_token', ''),
            'youtube_api_key': auth_sources.get('youtube', {}).get('api_key', ''),
            'news_api_key': auth_sources.get('news_api', {}).get('api_key', ''),
        }
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            # 数据源API配置
            'twitter_api_key': 'YOUR_TWITTER_API_KEY',
            'twitter_api_secret': 'YOUR_TWITTER_API_SECRET',
            'twitter_access_token': 'YOUR_ACCESS_TOKEN',
            'twitter_access_token_secret': 'YOUR_ACCESS_TOKEN_SECRET',
            'twitter_bearer_token': 'YOUR_BEARER_TOKEN',
            'youtube_api_key': 'YOUR_YOUTUBE_API_KEY',
            'news_api_key': 'YOUR_NEWS_API_KEY',
            'ai_model': self._get_default_ai_config()
        }
    
    def _get_default_ai_config(self):
        """获取默认AI配置"""
        return {
            'type': 'openai',  # 可选: 'openai', 'claude', 'custom'
            'api_key': 'YOUR_OPENAI_API_KEY',
            'model': 'gpt-4'  # 或 'gpt-3.5-turbo'
        }
    
    def _init_keywords_and_cache(self):
        """初始化关键词和缓存"""
        # 智能关键词配置 - 用于初步筛选
        self.smart_keywords = {
            'high_priority': [
                # 央行和货币政策
                'federal reserve', 'fed', 'interest rate', 'inflation', 'monetary policy',
                '美联储', '央行', '利率', '通胀', '货币政策',
                
                # 地缘政治
                'war', 'conflict', 'sanctions', 'trade war', 'geopolitical',
                '战争', '冲突', '制裁', '贸易战', '地缘政治',
                
                # 重大经济事件
                'recession', 'crisis', 'bailout', 'stimulus', 'gdp',
                '衰退', '危机', '救助', '刺激', '经济'
            ],
            
            'medium_priority': [
                # 加密货币
                'bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi',
                '比特币', '以太坊', '加密货币', '区块链',
                
                # 科技股
                'tech stock', 'ai', 'artificial intelligence', 'metaverse',
                '科技股', '人工智能', '元宇宙',
                
                # 能源和商品
                'oil price', 'gold', 'commodity', 'energy',
                '油价', '黄金', '大宗商品', '能源'
            ],
            
            'company_focus': [
                # 重要公司和CEO
                'apple', 'microsoft', 'tesla', 'amazon', 'google',
                'elon musk', 'warren buffett', 'jerome powell',
                '苹果', '微软', '特斯拉', '亚马逊', '谷歌'
            ]
        }
        
        self.news_cache = []
    
    async def get_free_rss_news(self) -> List[Dict]:
        """获取免费RSS新闻"""
        if not (ENHANCED_MODE and hasattr(self, 'free_data_collector')):
            return []
        
        try:
            # 使用异步上下文管理器
            async with self.free_data_collector as collector:
                rss_data = await collector.collect_rss_feeds()
                news_items = []
                
                for item in rss_data:
                    # 应用智能关键词过滤
                    is_relevant, relevance_level = self.smart_keyword_filter(item.get('title', '') + ' ' + item.get('description', ''))
                    
                    if is_relevant:
                        news_items.append({
                            'source': f"RSS/{item.get('source', 'Unknown')}",
                            'content': f"{item.get('title', '')}. {item.get('description', '')}",
                            'timestamp': item.get('published', datetime.now().isoformat()),
                            'url': item.get('link', ''),
                            'priority': 'medium',
                            'relevance': relevance_level
                        })
                
                logger.info(f"RSS数据收集完成，获得 {len(news_items)} 条相关新闻")
                return news_items
            
        except Exception as e:
            logger.error(f"获取RSS新闻失败: {e}")
            return []
    
    async def get_free_crypto_news(self) -> List[Dict]:
        """获取免费加密货币新闻"""
        if not (ENHANCED_MODE and hasattr(self, 'free_data_collector')):
            return []
        
        try:
            # 使用异步上下文管理器
            async with self.free_data_collector as collector:
                crypto_data = await collector.collect_crypto_data()
                news_items = []
                
                # 处理价格变动新闻
                for coin, data in crypto_data.items():
                    if data.get('price_change_24h', 0) != 0:
                        change_pct = data.get('price_change_percentage_24h', 0)
                        
                        # 只关注显著变化
                        if abs(change_pct) >= 5:
                            content = f"{coin.upper()} 价格24小时变动 {change_pct:.2f}%，当前价格 ${data.get('current_price', 0):.4f}"
                            
                            news_items.append({
                                'source': 'CoinGecko/价格监控',
                                'content': content,
                                'timestamp': datetime.now().isoformat(),
                                'url': f"https://www.coingecko.com/en/coins/{coin}",
                                'priority': 'high' if abs(change_pct) >= 10 else 'medium',
                                'relevance': 'high'
                            })
                
                logger.info(f"加密货币数据收集完成，获得 {len(news_items)} 条价格变动新闻")
                return news_items
            
        except Exception as e:
            logger.error(f"获取加密货币新闻失败: {e}")
            return []
    
    async def get_free_market_news(self) -> List[Dict]:
        """获取免费市场新闻"""
        if not (ENHANCED_MODE and hasattr(self, 'free_data_collector')):
            return []
        
        try:
            # 使用异步上下文管理器
            async with self.free_data_collector as collector:
                market_data = await collector.collect_market_data()
                news_items = []
                
                # 处理市场数据
                for item in market_data:
                    is_relevant, relevance_level = self.smart_keyword_filter(item.get('content', ''))
                    
                    if is_relevant:
                        news_items.append({
                            'source': f"免费市场数据/{item.get('source', 'Unknown')}",
                            'content': item.get('content', ''),
                            'timestamp': item.get('timestamp', datetime.now().isoformat()),
                            'url': item.get('url', ''),
                            'priority': 'medium',
                            'relevance': relevance_level
                        })
                
                logger.info(f"市场数据收集完成，获得 {len(news_items)} 条相关新闻")
                return news_items
            
        except Exception as e:
            logger.error(f"获取市场新闻失败: {e}")
            return []
        
    def setup_twitter_api(self):
        """设置Twitter API"""
        try:
            auth = tweepy.OAuthHandler(
                self.config['twitter_api_key'], 
                self.config['twitter_api_secret']
            )
            auth.set_access_token(
                self.config['twitter_access_token'], 
                self.config['twitter_access_token_secret']
            )
            
            self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
            self.twitter_client = tweepy.Client(
                bearer_token=self.config['twitter_bearer_token'],
                wait_on_rate_limit=True
            )
            logger.info("Twitter API 配置成功")
            return True
        except Exception as e:
            logger.error(f"Twitter API 配置失败: {e}")
            return False
    
    def smart_keyword_filter(self, text: str) -> Tuple[bool, str]:
        """智能关键词过滤 - 确定新闻优先级"""
        text_lower = text.lower()
        
        # 检查高优先级关键词
        for keyword in self.smart_keywords['high_priority']:
            if keyword.lower() in text_lower:
                return True, 'high'
        
        # 检查中优先级关键词
        for keyword in self.smart_keywords['medium_priority']:
            if keyword.lower() in text_lower:
                return True, 'medium'
        
        # 检查公司焦点关键词
        for keyword in self.smart_keywords['company_focus']:
            if keyword.lower() in text_lower:
                return True, 'company'
        
        return False, 'none'
    
    async def get_enhanced_twitter_news(self) -> List[Dict]:
        """增强版Twitter新闻获取"""
        if not hasattr(self, 'twitter_client'):
            return []
            
        news_items = []
        
        # 分级账户监控
        priority_accounts = {
            'critical': ['federalreserve', 'SecYellen', 'WSJ', 'Reuters'],
            'important': ['elonmusk', 'POTUS', 'IMFNews', 'BloombergNews'],
            'watchlist': ['RayDalio', 'naval', 'APComplexity', 'SatoshiLite']
        }
        
        try:
            for priority, accounts in priority_accounts.items():
                for account in accounts:
                    # 获取用户信息
                    user = self.twitter_client.get_user(username=account)
                    if user.data:
                        # 获取用户推文
                        tweets = self.twitter_client.get_users_tweets(
                            id=user.data.id,
                            max_results=15,
                            tweet_fields=['created_at', 'public_metrics', 'context_annotations'],
                            exclude='retweets'
                        )
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            is_relevant, relevance_level = self.smart_keyword_filter(tweet.text)
                            
                            if is_relevant:
                                news_items.append({
                                    'source': f'Twitter/@{account}',
                                    'content': tweet.text,
                                    'timestamp': tweet.created_at.isoformat(),
                                    'url': f'https://twitter.com/{account}/status/{tweet.id}',
                                    'priority': priority,
                                    'relevance': relevance_level,
                                    'engagement': tweet.public_metrics
                                })
        except Exception as e:
            logger.error(f"获取Twitter数据失败: {e}")
        
        return news_items
    
    async def get_ai_filtered_news(self) -> List[Dict]:
        """AI辅助过滤的新闻获取"""
        news_items = []
        
        # 使用更精准的搜索关键词
        search_queries = [
            'stock market crash OR rally',
            'federal reserve interest rates',
            'cryptocurrency regulation bitcoin',
            'inflation CPI data economy',
            'geopolitical crisis war sanctions',
            'earnings report beat miss guidance'
        ]
        
        for query in search_queries:
            try:
                url = 'https://newsapi.org/v2/everything'
                params = {
                    'apiKey': self.config['news_api_key'],
                    'q': query,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 10,
                    'from': (datetime.now() - timedelta(hours=12)).isoformat()
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if data['status'] == 'ok':
                    for article in data['articles']:
                        content = article['title'] + '. ' + (article['description'] or '')
                        is_relevant, relevance_level = self.smart_keyword_filter(content)
                        
                        if is_relevant:
                            news_items.append({
                                'source': article['source']['name'],
                                'content': content,
                                'timestamp': article['publishedAt'],
                                'url': article['url'],
                                'query': query,
                                'relevance': relevance_level
                            })
                            
            except Exception as e:
                logger.error(f"获取新闻API数据失败 (查询: {query}): {e}")
        
        return news_items
    
    def get_news_api_data(self) -> List[Dict]:
        """获取新闻API数据"""
        news_items = []
        
        # 使用NewsAPI获取财经新闻
        url = 'https://newsapi.org/v2/everything'
        params = {
            'apiKey': self.config['news_api_key'],
            'q': 'stock market OR cryptocurrency OR federal reserve OR geopolitical',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 50,
            'from': (datetime.now() - timedelta(hours=24)).isoformat()
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok':
                for article in data['articles']:
                    if self.is_market_relevant(article['title'] + ' ' + (article['description'] or '')):
                        news_items.append({
                            'source': article['source']['name'],
                            'content': article['title'] + '. ' + (article['description'] or ''),
                            'timestamp': article['publishedAt'],
                            'url': article['url']
                        })
        except Exception as e:
            logger.error(f"获取新闻API数据失败: {e}")
        
        return news_items
    
    async def get_youtube_news(self) -> List[Dict]:
        """获取YouTube新闻"""
        news_items = []
        
        # 重要的财经YouTube频道
        channels = [
            'UCrp_UI8XtuYfpiqluWLD7Lw',  # CNBC
            'UCF9IOB2TExg3QIBupFtBDxg',  # BBC News
            'UCupvZG-5ko_eiXAupbDfxWw'   # CNN
        ]
        
        try:
            for channel_id in channels:
                url = f'https://www.googleapis.com/youtube/v3/search'
                params = {
                    'key': self.config['youtube_api_key'],
                    'channelId': channel_id,
                    'part': 'snippet',
                    'order': 'date',
                    'maxResults': 10,
                    'publishedAfter': (datetime.now() - timedelta(hours=24)).isoformat()
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if 'items' in data:
                    for item in data['items']:
                        title = item['snippet']['title']
                        description = item['snippet']['description']
                        
                        if self.is_market_relevant(title + ' ' + description):
                            news_items.append({
                                'source': f'YouTube/{item["snippet"]["channelTitle"]}',
                                'content': f'{title}. {description[:200]}...',
                                'timestamp': item['snippet']['publishedAt'],
                                'url': f'https://www.youtube.com/watch?v={item["id"]["videoId"]}'
                            })
        except Exception as e:
            logger.error(f"获取YouTube数据失败: {e}")
        
        return news_items
    
    def is_market_relevant(self, text: str) -> bool:
        """判断文本是否与市场相关 - 增强版相关性检测"""
        text_lower = text.lower()
        relevance_score = 0
        
        # 1. 基础关键词检测
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    relevance_score += self.impact_weights[category]
        
        # 2. 金融术语检测
        financial_terms = [
            'stock', 'market', 'trading', 'investment', 'portfolio', 'dividend',
            'earnings', 'revenue', 'profit', 'loss', 'valuation', 'ipo',
            '股票', '市场', '交易', '投资', '收益', '亏损', '估值'
        ]
        
        for term in financial_terms:
            if term in text_lower:
                relevance_score += 0.3
        
        # 3. 经济指标检测
        economic_indicators = [
            'gdp', 'unemployment', 'cpi', 'ppi', 'pmi', 'retail sales',
            'consumer confidence', 'housing starts', '失业率', '通胀率', 'gdp'
        ]
        
        for indicator in economic_indicators:
            if indicator in text_lower:
                relevance_score += 0.4
        
        # 4. 公司财报相关
        earnings_terms = [
            'quarterly results', 'annual report', 'guidance', 'outlook',
            'beat estimates', 'miss estimates', '财报', '业绩', '预期'
        ]
        
        for term in earnings_terms:
            if term in text_lower:
                relevance_score += 0.5
        
        # 5. 监管政策相关
        regulatory_terms = [
            'regulation', 'policy', 'law', 'compliance', 'sec', 'fda',
            'antitrust', 'merger', 'acquisition', '监管', '政策', '法规'
        ]
        
        for term in regulatory_terms:
            if term in text_lower:
                relevance_score += 0.4
        
        # 阈值判断：相关性分数大于0.5才认为与市场相关
        return relevance_score >= 0.5
    
    def analyze_market_impact(self, text: str) -> Tuple[float, str, str]:
        """分析市场影响 - 增强版影响评估算法"""
        text_lower = text.lower()
        impact_score = 0.0
        categories_found = []
        
        # 1. 基础关键词匹配和加权
        for category, keywords in self.keywords.items():
            category_score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    category_score += 1
            
            if category_score > 0:
                categories_found.append(category)
                impact_score += category_score * self.impact_weights[category]
        
        # 2. 情感分析增强 - 检测积极/消极词汇
        positive_words = ['rise', 'up', 'bull', 'growth', 'increase', 'boost', 'surge', '上涨', '增长', '看涨']
        negative_words = ['fall', 'down', 'bear', 'crash', 'decline', 'drop', 'plunge', '下跌', '暴跌', '看跌']
        
        sentiment_multiplier = 1.0
        if any(word in text_lower for word in positive_words):
            sentiment_multiplier += 0.2
        if any(word in text_lower for word in negative_words):
            sentiment_multiplier += 0.3  # 负面新闻通常影响更大
        
        # 3. 紧急程度检测
        urgency_words = ['breaking', 'urgent', 'emergency', 'crisis', 'alert', '紧急', '突发', '危机']
        if any(word in text_lower for word in urgency_words):
            sentiment_multiplier += 0.4
        
        # 4. 数字/百分比检测 - 包含具体数据的新闻影响更大
        import re
        if re.search(r'\d+%|\$\d+|\d+\.\d+%', text):
            sentiment_multiplier += 0.2
        
        # 5. 时间敏感性检测
        time_sensitive = ['today', 'tonight', 'tomorrow', 'this week', '今天', '今晚', '明天', '本周']
        if any(word in text_lower for word in time_sensitive):
            sentiment_multiplier += 0.2
        
        # 应用情感和紧急程度乘数
        impact_score *= sentiment_multiplier
        
        # 6. 信息源可信度调整
        impact_score = self.adjust_for_source_credibility(impact_score, text)
        
        # 标准化影响分数 (0-1)
        impact_score = min(impact_score / 15, 1.0)  # 调整分母适应新的评分系统
        
        # 生成市场预测
        market_prediction = self.generate_market_prediction(text_lower, categories_found, impact_score)
        
        # 生成交易建议
        trading_suggestion = self.generate_trading_suggestion(text_lower, categories_found, impact_score)
        
        return impact_score, market_prediction, trading_suggestion
    
    def adjust_for_source_credibility(self, score: float, text: str) -> float:
        """根据信息源可信度调整影响分数"""
        # 高可信度来源
        high_credibility = ['reuters', 'bloomberg', 'wsj', 'financial times', 'cnbc', 'ap news']
        # 中等可信度来源
        medium_credibility = ['cnn', 'bbc', 'guardian', 'nytimes']
        # 社交媒体需要更谨慎
        social_media = ['twitter', 'facebook', 'youtube']
        
        text_lower = text.lower()
        
        if any(source in text_lower for source in high_credibility):
            return score * 1.2  # 提高20%
        elif any(source in text_lower for source in medium_credibility):
            return score * 1.0  # 保持不变
        elif any(source in text_lower for source in social_media):
            return score * 0.8  # 降低20%
        
        return score
    
    def generate_market_prediction(self, text: str, categories: List[str], impact_score: float) -> str:
        """生成市场预测"""
        if impact_score < 0.3:
            return "市场影响较小，预计波动有限"
        
        predictions = []
        
        if 'geopolitical' in categories:
            if any(word in text for word in ['war', 'conflict', '战争', '冲突']):
                predictions.append("地缘政治风险上升，避险资产可能受益，风险资产承压")
            
        if 'monetary' in categories:
            if any(word in text for word in ['rate cut', '降息']):
                predictions.append("宽松货币政策预期，股市可能上涨，美元走弱")
            elif any(word in text for word in ['rate hike', 'raise rates', '加息']):
                predictions.append("紧缩货币政策预期，股市可能下跌，美元走强")
        
        if 'crypto' in categories:
            if any(word in text for word in ['regulation', 'ban', '监管', '禁止']):
                predictions.append("加密货币监管收紧，数字资产可能下跌")
            elif any(word in text for word in ['adoption', 'institutional', '采用', '机构']):
                predictions.append("加密货币采用增加，数字资产可能上涨")
        
        if not predictions:
            return "市场情绪可能出现波动，建议密切关注后续发展"
        
        return "; ".join(predictions)
    
    def generate_trading_suggestion(self, text: str, categories: List[str], impact_score: float) -> str:
        """生成交易建议"""
        if impact_score < 0.2:
            return "持币观望，无明确交易信号"
        
        suggestions = []
        
        # 基于新闻内容的交易建议逻辑
        if 'geopolitical' in categories:
            suggestions.append("考虑增持黄金、美债等避险资产")
        
        if 'monetary' in categories:
            if any(word in text for word in ['dovish', 'cut', '鸽派', '降息']):
                suggestions.append("可考虑买入成长股、科技股")
            elif any(word in text for word in ['hawkish', 'hike', '鹰派', '加息']):
                suggestions.append("可考虑减持高估值股票，增持价值股")
        
        if 'crypto' in categories:
            if any(word in text for word in ['positive', 'adoption', '积极', '采用']):
                suggestions.append("可适量配置主流加密货币")
            else:
                suggestions.append("建议减少加密货币敞口")
        
        if not suggestions:
            return "建议分散投资，控制风险"
        
        return "; ".join(suggestions) + " (仅供参考，请谨慎投资)"
    
    def format_news_output(self, news_item: NewsItem) -> str:
        """格式化新闻输出"""
        timestamp = datetime.fromisoformat(news_item.timestamp.replace('Z', '+00:00'))
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
📈 【财经新闻播报】
🕐 时间: {formatted_time}
📺 来源: {news_item.source}
📰 事件: {news_item.title}
📊 影响分析: {news_item.market_prediction}
💡 交易建议: {news_item.trading_suggestion}
🔗 链接: {news_item.url}
{"="*60}
"""
    
    async def collect_and_analyze_news(self) -> List[NewsItem]:
        """收集并分析所有新闻 - AI增强版"""
        all_raw_news = []
        
        logger.info("开始收集新闻数据...")
        
        # 1. 并发收集各平台数据
        tasks = [
            self.get_enhanced_twitter_news(),
            self.get_ai_filtered_news(),
            self.get_youtube_news()
        ]
        
        # 添加免费数据源（如果增强模式可用）
        if ENHANCED_MODE and hasattr(self, 'free_data_collector'):
            tasks.append(self.get_free_rss_news())
            tasks.append(self.get_free_crypto_news())
            tasks.append(self.get_free_market_news())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_raw_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"数据收集任务失败: {result}")
        
        logger.info(f"原始新闻收集完成，共 {len(all_raw_news)} 条")
        
        # 2. 去重和初步过滤
        unique_news = self.deduplicate_news(all_raw_news)
        logger.info(f"去重后剩余 {len(unique_news)} 条新闻")
        
        # 3. AI分析阶段
        analyzed_news = []
        analysis_tasks = []
        
        # 优先处理高优先级新闻
        high_priority_news = []
        medium_priority_news = []
        
        for n in unique_news:
            if n.get('priority') == 'critical' or n.get('relevance') == 'high':
                high_priority_news.append(n)
            else:
                medium_priority_news.append(n)
        
        # 分批进行AI分析以控制API调用成本
        max_analysis_count = 20  # 每次最多分析20条新闻
        news_to_analyze = (high_priority_news + medium_priority_news)[:max_analysis_count]
        
        logger.info(f"开始AI分析，处理 {len(news_to_analyze)} 条新闻")
        
        for news_item in news_to_analyze:
            try:
                # 异步调用AI分析
                ai_analysis = await self.ai_analyzer.analyze_news_with_ai(
                    news_item['content'], 
                    news_item['source']
                )
                
                # 只保留AI认为有足够影响的新闻
                if ai_analysis.impact_score >= 0.3:
                    news_obj = NewsItem(
                        timestamp=news_item['timestamp'],
                        source=news_item['source'],
                        title=news_item['content'][:150] + "..." if len(news_item['content']) > 150 else news_item['content'],
                        content=news_item['content'],
                        url=news_item['url'],
                        ai_analysis=ai_analysis
                    )
                    analyzed_news.append(news_obj)
                
                # 添加延迟以避免API限制
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"AI分析新闻失败: {e}")
                continue
        
        # 按AI评分排序
        analyzed_news.sort(key=lambda x: x.ai_analysis.impact_score if x.ai_analysis else 0, reverse=True)
        
        logger.info(f"AI分析完成，筛选出 {len(analyzed_news)} 条重要新闻")
        return analyzed_news
    
    def deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """新闻去重"""
        seen_content = set()
        unique_news = []
        
        for news in news_list:
            # 使用内容的前100个字符作为去重标识
            content_key = news['content'][:100].lower().strip()
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_news.append(news)
        
        return unique_news
    
    def format_ai_news_output(self, news_item: NewsItem) -> str:
        """格式化AI分析的新闻输出"""
        if not news_item.ai_analysis:
            return f"新闻: {news_item.title} (AI分析失败)"
        
        timestamp = datetime.fromisoformat(news_item.timestamp.replace('Z', '+00:00'))
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        # 影响等级显示
        impact_level = "🔴 高影响" if news_item.ai_analysis.impact_score >= 0.7 else \
                     "🟡 中影响" if news_item.ai_analysis.impact_score >= 0.4 else "🟢 低影响"
        
        # 情感图标
        sentiment_icon = "📈" if news_item.ai_analysis.sentiment == "positive" else \
                        "📉" if news_item.ai_analysis.sentiment == "negative" else "➡️"
        
        output = f"""
🤖 【AI财经新闻分析】
🕐 时间: {formatted_time}
📺 来源: {news_item.source}
{impact_level} 影响评分: {news_item.ai_analysis.impact_score:.2f}
{sentiment_icon} 市场情感: {news_item.ai_analysis.sentiment}
🎯 AI信心度: {news_item.ai_analysis.confidence:.2f}

📰 新闻摘要: {news_item.title}

🔍 AI市场分析:
{news_item.ai_analysis.market_prediction}

💡 AI交易建议:
{news_item.ai_analysis.trading_suggestion}
"""
        
        if news_item.ai_analysis.key_points:
            output += f"\n📌 关键要点:\n"
            for i, point in enumerate(news_item.ai_analysis.key_points[:3], 1):
                output += f"   {i}. {point}\n"
        
        output += f"\n🔗 原文链接: {news_item.url}\n"
        output += "="*70 + "\n"
        
        return output
    
    def save_news_to_file(self, news_items: List[NewsItem], filename: str = None):
        """保存新闻到文件"""
        if not filename:
            filename = f"financial_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"财经新闻播报 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for news in news_items:
                f.write(self.format_news_output(news))
                f.write("\n")
        
        logger.info(f"新闻已保存到文件: {filename}")
    
    async def run_monitor(self, interval_minutes: int = 30):
        """运行监控程序"""
        logger.info(f"启动财经新闻监控，检查间隔: {interval_minutes}分钟")
        
        # 初始化API
        self.setup_twitter_api()
        
        while True:
            try:
                logger.info("开始新一轮新闻收集...")
                
                # 收集新闻
                news_items = await self.collect_and_analyze_news()
                
                if news_items:
                    logger.info(f"发现 {len(news_items)} 条重要新闻")
                    
                    # 输出新闻
                    for news in news_items[:10]:  # 只显示前10条最重要的
                        print(self.format_news_output(news))
                    
                    # 保存到文件
                    self.save_news_to_file(news_items)
                else:
                    logger.info("未发现重要财经新闻")
                
                # 等待下次检查
                logger.info(f"等待 {interval_minutes} 分钟后进行下次检查...")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("用户中断，程序退出")
                break
            except Exception as e:
                logger.error(f"监控过程中出现错误: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再重试

def main():
    """主函数"""
    print("🚀 财经新闻自动播报系统启动")
    print("-" * 50)
    
    if ENHANCED_MODE:
        print("✅ 增强模式已启用")
        print("📊 可用数据源:")
        print("   - RSS新闻订阅 (免费)")
        print("   - CoinGecko加密货币数据 (免费)")
        print("   - 公开市场数据 (免费)")
        print("   - Twitter API (需要密钥)")
        print("   - YouTube API (需要密钥)")
        print("   - News API (需要密钥)")
        print("💡 即使没有API密钥也可以获取基础新闻数据")
    else:
        print("⚠️  基础模式 - 使用前请先配置以下API密钥:")
        print("   - Twitter API密钥")
        print("   - YouTube API密钥") 
        print("   - News API密钥")
    
    print("-" * 50)
    
    monitor = FinancialNewsMonitor()
    
    # 运行监控
    try:
        asyncio.run(monitor.run_monitor(30))  # 每30分钟检查一次
    except KeyboardInterrupt:
        print("\n程序已退出")

if __name__ == "__main__":
    main()