#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
免费数据收集器 - 从RSS、公开API等免登录源收集金融新闻数据
"""

import asyncio
import aiohttp
import feedparser
import time
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config_manager import get_config_manager

logger = logging.getLogger(__name__)

class FreeDataCollector:
    """免费数据收集器"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or get_config_manager()
        self.session = None
        self.rss_cache = {}
        self.cache_duration = 300  # 5分钟缓存
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def collect_all_free_data(self) -> List[Dict]:
        """收集所有免费数据源的新闻"""
        all_news = []
        
        try:
            # 并发收集各种数据源
            tasks = [
                self.collect_rss_news(),
                self.collect_public_api_data()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"数据收集任务 {i} 失败: {result}")
                elif isinstance(result, list):
                    all_news.extend(result)
                    logger.info(f"数据收集任务 {i} 成功，获得 {len(result)} 条数据")
            
            # 去重和排序
            all_news = self._deduplicate_news(all_news)
            all_news.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            logger.info(f"免费数据收集完成，共获得 {len(all_news)} 条新闻")
            return all_news
            
        except Exception as e:
            logger.error(f"免费数据收集失败: {e}")
            return []
    
    async def collect_rss_news(self) -> List[Dict]:
        """收集RSS订阅源新闻"""
        rss_config = self.config_manager.get_free_sources().get('rss_feeds', {})
        
        if not rss_config.get('enabled', False):
            logger.debug("RSS收集已禁用")
            return []
        
        feeds = rss_config.get('feeds', [])
        if not feeds:
            logger.warning("没有配置RSS订阅源")
            return []
        
        all_rss_news = []
        
        # 并发处理所有RSS源
        for feed_config in feeds:
            try:
                result = await self._process_rss_feed(feed_config)
                all_rss_news.extend(result)
            except Exception as e:
                logger.error(f"RSS源处理失败: {e}")
        
        logger.info(f"RSS收集完成，共获得 {len(all_rss_news)} 条新闻")
        return all_rss_news
    
    async def _process_rss_feed(self, feed_config: Dict) -> List[Dict]:
        """处理单个RSS订阅源"""
        feed_url = feed_config.get('url')
        feed_name = feed_config.get('name', 'Unknown')
        
        try:
            async with self.session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 解析RSS
                    feed = feedparser.parse(content)
                    news_items = []
                    
                    for entry in feed.entries[:20]:  # 限制每个源最多20条
                        news_item = self._parse_rss_entry(entry, feed_name)
                        if news_item and self._is_financial_relevant(news_item['content']):
                            news_items.append(news_item)
                    
                    logger.debug(f"RSS源 {feed_name} 解析完成，获得 {len(news_items)} 条相关新闻")
                    return news_items
                else:
                    logger.warning(f"RSS源 {feed_name} 访问失败: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"处理RSS源 {feed_name} 失败: {e}")
            return []
    
    def _parse_rss_entry(self, entry, source_name: str) -> Optional[Dict]:
        """解析RSS条目"""
        try:
            # 获取发布时间
            published_time = getattr(entry, 'published_parsed', None)
            if published_time:
                timestamp = datetime(*published_time[:6]).isoformat()
            else:
                timestamp = datetime.now().isoformat()
            
            # 清理内容
            content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            content = self._clean_html(content)
            
            return {
                'source': f"RSS/{source_name}",
                'title': getattr(entry, 'title', ''),
                'content': content,
                'url': getattr(entry, 'link', ''),
                'timestamp': timestamp,
                'type': 'rss'
            }
        except Exception as e:
            logger.error(f"解析RSS条目失败: {e}")
            return None
    
    async def collect_public_api_data(self) -> List[Dict]:
        """收集公开API数据"""
        api_config = self.config_manager.get_free_sources().get('public_apis', {})
        
        if not api_config.get('enabled', False):
            logger.debug("公开API收集已禁用")
            return []
        
        api_sources = api_config.get('sources', [])
        enabled_sources = [s for s in api_sources if s.get('enabled', False)]
        
        if not enabled_sources:
            logger.warning("没有启用的公开API源")
            return []
        
        all_api_news = []
        
        # 处理各种API源
        for api_config in enabled_sources:
            try:
                if api_config.get('type') == 'crypto_data':
                    result = await self._collect_coingecko_data(api_config)
                    all_api_news.extend(result)
            except Exception as e:
                logger.error(f"处理API源失败: {e}")
        
        logger.info(f"公开API收集完成，共获得 {len(all_api_news)} 条数据")
        return all_api_news
    
    async def _collect_coingecko_data(self, config: Dict) -> List[Dict]:
        """收集CoinGecko加密货币数据"""
        try:
            url = f"{config['base_url']}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    coins = await response.json()
                    news_items = []
                    
                    for coin in coins:
                        price_change = coin.get('price_change_percentage_24h', 0)
                        
                        # 只关注价格变化超过5%的情况
                        if abs(price_change) > 5:
                            direction = "上涨" if price_change > 0 else "下跌"
                            news_item = {
                                'source': 'CoinGecko/Crypto Market',
                                'title': f"{coin['name']} 24小时{direction} {abs(price_change):.2f}%",
                                'content': f"加密货币 {coin['name']} ({coin['symbol'].upper()}) 在过去24小时内{direction} {abs(price_change):.2f}%，当前价格 ${coin['current_price']}",
                                'url': f"https://www.coingecko.com/en/coins/{coin['id']}",
                                'timestamp': datetime.now().isoformat(),
                                'type': 'crypto_data'
                            }
                            news_items.append(news_item)
                    
                    return news_items
                else:
                    logger.warning(f"CoinGecko API访问失败: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"CoinGecko数据收集失败: {e}")
            return []
    
    def _is_financial_relevant(self, content: str) -> bool:
        """检查内容是否与金融相关"""
        financial_keywords = [
            'market', 'stock', 'trading', 'investment', 'economy', 'finance',
            'bitcoin', 'crypto', 'currency', 'fed', 'inflation', 'gdp',
            '市场', '股票', '交易', '投资', '经济', '金融', '比特币', '加密', 
            '货币', '美联储', '通胀', '央行'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in financial_keywords)
    
    def _clean_html(self, html_content: str) -> str:
        """清理HTML内容"""
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception:
            text = re.sub(r'<[^>]+>', '', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """新闻去重"""
        seen_content = set()
        unique_news = []
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            content_key = f"{title}_{content[:100]}".lower().strip()
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_news.append(news)
        
        return unique_news

# 便捷函数
    async def collect_rss_feeds(self) -> List[Dict]:
        """收集RSS订阅源数据 - 别名方法"""
        return await self.collect_rss_news()
    
    async def collect_crypto_data(self) -> Dict:
        """收集加密货币数据"""
        try:
            # 获取CoinGecko配置
            public_apis = self.config_manager.get_public_apis()
            coingecko_config = None
            
            for api in public_apis:
                if api.get('type') == 'crypto_data' and api.get('name') == 'CoinGecko':
                    coingecko_config = api
                    break
            
            if not coingecko_config:
                logger.warning("CoinGecko配置未找到")
                return {}
            
            # 获取加密货币市场数据
            url = f"{coingecko_config['base_url']}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    crypto_dict = {}
                    
                    for coin in data:
                        crypto_dict[coin['id']] = {
                            'current_price': coin.get('current_price', 0),
                            'price_change_24h': coin.get('price_change_24h', 0),
                            'price_change_percentage_24h': coin.get('price_change_percentage_24h', 0),
                            'market_cap': coin.get('market_cap', 0),
                            'volume_24h': coin.get('total_volume', 0)
                        }
                    
                    logger.info(f"成功获取 {len(crypto_dict)} 个加密货币数据")
                    return crypto_dict
                else:
                    logger.warning(f"CoinGecko API请求失败: HTTP {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"收集加密货币数据失败: {e}")
            return {}
    
    async def collect_market_data(self) -> List[Dict]:
        """收集市场数据"""
        try:
            market_news = []
            
            # 获取公开API配置
            public_apis = self.config_manager.get_public_apis()
            
            for api_config in public_apis:
                if api_config.get('type') == 'market_data' and api_config.get('enabled', False):
                    try:
                        if api_config.get('name') == 'Yahoo Finance':
                            # 获取主要指数数据
                            symbols = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
                            
                            for symbol in symbols:
                                url = f"{api_config['base_url']}/{symbol}"
                                
                                async with self.session.get(url) as response:
                                    if response.status == 200:
                                        data = await response.json()
                                        
                                        # 解析Yahoo Finance数据
                                        if 'chart' in data and data['chart']['result']:
                                            result = data['chart']['result'][0]
                                            meta = result.get('meta', {})
                                            
                                            current_price = meta.get('regularMarketPrice', 0)
                                            prev_close = meta.get('previousClose', 0)
                                            change = current_price - prev_close if current_price and prev_close else 0
                                            change_pct = (change / prev_close * 100) if prev_close else 0
                                            
                                            if abs(change_pct) >= 1:  # 只关注1%以上的变化
                                                content = f"{symbol} 当前价格 {current_price:.2f}，变动 {change_pct:.2f}%"
                                                
                                                market_news.append({
                                                    'source': 'Yahoo Finance',
                                                    'content': content,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'url': f"https://finance.yahoo.com/quote/{symbol}",
                                                    'type': 'market_data'
                                                })
                                    
                    except Exception as e:
                        logger.error(f"处理市场数据API {api_config.get('name')} 失败: {e}")
            
            logger.info(f"市场数据收集完成，获得 {len(market_news)} 条数据")
            return market_news
            
        except Exception as e:
            logger.error(f"收集市场数据失败: {e}")
            return []

async def collect_free_financial_data() -> List[Dict]:
    """收集免费金融数据的便捷函数"""
    async with FreeDataCollector() as collector:
        return await collector.collect_all_free_data() 