# API获取指南 - AFNMS数据源配置

## 📋 概述

本指南将详细介绍如何获取AFNMS系统所需的各种API密钥，包括申请流程、配置方法和最佳实践。

### 🎯 必需的API
- **Twitter API v2** (推荐) - 实时推文监控
- **YouTube Data API** (推荐) - 视频内容分析  
- **News API** (推荐) - 新闻聚合服务

### 🔧 可选的API
- **FRED API** - 美联储经济数据
- **Alpha Vantage** - 股票数据
- **CoinGecko Pro** - 加密货币高级数据

---

## 🐦 Twitter API v2 获取指南

### 申请要求
- **个人/组织账户**: 需要验证的Twitter账户
- **使用说明**: 需要详细说明API用途
- **审核时间**: 通常1-7个工作日

### 申请步骤

#### 1. 访问Twitter开发者平台
```
🔗 https://developer.twitter.com/
```

#### 2. 创建开发者账户
1. 点击 "Apply for a developer account"
2. 选择账户类型：
   - **Personal use** (个人使用) - 推荐新手
   - **Professional use** (专业使用) - 商业项目

#### 3. 填写申请表单
```
使用目的说明模板：
"I am developing an AI-powered financial news monitoring system (AFNMS) 
that analyzes tweets related to financial markets, cryptocurrencies, 
and economic news to provide investment insights. The system will:

1. Monitor financial keywords and hashtags
2. Analyze market sentiment from tweets  
3. Generate investment recommendations
4. Provide real-time market trend analysis

This is for educational/research purposes and will comply with Twitter's 
Terms of Service and API usage policies."
```

#### 4. 创建App
1. 在开发者控制台中点击 "Create App"
2. 填写应用信息：
   - **App name**: AFNMS-Financial-Monitor
   - **Description**: AI Financial News Monitoring System
   - **Website**: 您的项目网址或GitHub链接

#### 5. 获取API密钥
```json
{
  "api_key": "your_api_key_here",
  "api_secret": "your_api_secret_here", 
  "bearer_token": "your_bearer_token_here",
  "access_token": "your_access_token_here",
  "access_token_secret": "your_access_token_secret_here"
}
```

### API限制和定价

#### 免费套餐 (Essential)
- **推文检索**: 500,000条/月
- **用户查询**: 300次/15分钟
- **适用**: 个人研究和小规模项目

#### 付费套餐 (Basic - $100/月)
- **推文检索**: 10,000,000条/月
- **实时流**: 支持
- **历史数据**: 支持

### 配置示例
```json
{
  "twitter": {
    "api_key": "your_twitter_api_key",
    "api_secret": "your_twitter_api_secret",
    "bearer_token": "your_twitter_bearer_token",
    "access_token": "your_twitter_access_token", 
    "access_token_secret": "your_twitter_access_token_secret",
    "enabled": true
  }
}
```

---

## 📺 YouTube Data API 获取指南

### 申请要求
- **Google账户**: 需要有效的Google账户
- **项目配额**: 每日10,000个配额单位(免费)
- **审核**: 无需人工审核，即时获取

### 申请步骤

#### 1. 访问Google Cloud Console
```
🔗 https://console.cloud.google.com/
```

#### 2. 创建项目
1. 点击项目下拉菜单
2. 选择 "New Project"
3. 项目名称: "AFNMS-Financial-Monitor"
4. 点击 "Create"

#### 3. 启用YouTube Data API
1. 在导航菜单中选择 "APIs & Services" > "Library"
2. 搜索 "YouTube Data API v3"
3. 点击 "Enable"

#### 4. 创建凭据
1. 转到 "APIs & Services" > "Credentials"
2. 点击 "Create Credentials" > "API Key"
3. 复制生成的API密钥
4. (可选) 点击 "Restrict Key" 限制使用范围

#### 5. 配置API限制
```
建议的限制设置:
- Application restrictions: None (或限制为特定IP)
- API restrictions: YouTube Data API v3
```

### API配额管理

#### 免费配额
- **每日配额**: 10,000单位
- **查询成本**: 
  - 搜索视频: 100单位/请求
  - 获取视频详情: 1单位/请求
  - 获取评论: 1单位/请求

#### 配额优化技巧
```python
# 批量获取视频信息减少API调用
video_ids = "video_id1,video_id2,video_id3"
# 1次调用获取多个视频信息，而不是3次单独调用
```

### 配置示例
```json
{
  "youtube": {
    "api_key": "AIzaSy...your_youtube_api_key",
    "enabled": true,
    "rate_limit": {
      "requests_per_day": 10000
    }
  }
}
```

---

## 📰 News API 获取指南

### 申请要求
- **邮箱验证**: 需要有效邮箱地址
- **使用说明**: 简单的使用目的说明
- **审核**: 即时获取，无需等待

### 申请步骤

#### 1. 访问News API官网
```
🔗 https://newsapi.org/register
```

#### 2. 注册账户
1. 填写基本信息：
   - **Name**: 您的姓名
   - **Email**: 有效邮箱地址
   - **Country**: 选择国家
2. 选择使用目的: "Personal/Education"

#### 3. 获取API密钥
- 注册成功后立即获得API密钥
- 密钥格式: `32位十六进制字符串`

### API限制和定价

#### 免费套餐 (Developer)
- **请求数量**: 1,000次/天
- **数据范围**: 过去30天的新闻
- **更新频率**: 15分钟延迟

#### 付费套餐 (Business - $449/月起)
- **请求数量**: 250,000次/天
- **实时数据**: 支持
- **历史数据**: 完整访问

### 配置示例
```json
{
  "news_api": {
    "api_key": "your_32_character_api_key",
    "enabled": true,
    "rate_limit": {
      "requests_per_day": 1000
    }
  }
}
```

---

## 💰 可选财经API获取指南

### FRED API (免费)

#### 申请流程
1. 访问: https://research.stlouisfed.org/useraccount/apikey
2. 创建免费账户
3. 申请API密钥(即时获取)

#### 配置示例
```json
{
  "fred": {
    "api_key": "your_fred_api_key",
    "base_url": "https://api.stlouisfed.org/fred",
    "enabled": true
  }
}
```

### Alpha Vantage API

#### 申请流程
1. 访问: https://www.alphavantage.co/support/#api-key
2. 填写邮箱获取免费API密钥
3. 免费套餐: 5次请求/分钟, 500次/天

#### 配置示例
```json
{
  "alpha_vantage": {
    "api_key": "your_alpha_vantage_key",
    "enabled": true,
    "rate_limit": {
      "requests_per_minute": 5,
      "requests_per_day": 500
    }
  }
}
```

### CoinGecko Pro API

#### 申请流程
1. 访问: https://www.coingecko.com/en/api/pricing
2. 选择合适的套餐
3. 免费套餐: 50次请求/分钟

---

## 🔧 API配置和测试

### 环境变量配置

创建 `.env` 文件：
```bash
# Twitter API
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key

# News API
NEWS_API_KEY=your_news_api_key

# 可选API
FRED_API_KEY=your_fred_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
COINGECKO_API_KEY=your_coingecko_pro_key
```

### API测试脚本

创建 `test_apis.py`:
```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_twitter_api():
    """测试Twitter API"""
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    headers = {'Authorization': f'Bearer {bearer_token}'}
    
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {'query': 'Bitcoin', 'max_results': 10}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        print("✅ Twitter API 测试成功")
        return True
    else:
        print(f"❌ Twitter API 测试失败: {response.status_code}")
        print(response.text)
        return False

def test_youtube_api():
    """测试YouTube API"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': 'financial news',
        'type': 'video',
        'maxResults': 5,
        'key': api_key
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print("✅ YouTube API 测试成功")
        return True
    else:
        print(f"❌ YouTube API 测试失败: {response.status_code}")
        print(response.text)
        return False

def test_news_api():
    """测试News API"""
    api_key = os.getenv('NEWS_API_KEY')
    
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'finance',
        'sortBy': 'publishedAt',
        'pageSize': 5,
        'apiKey': api_key
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print("✅ News API 测试成功")
        return True
    else:
        print(f"❌ News API 测试失败: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("🧪 开始API测试...")
    
    apis = [
        ("Twitter API", test_twitter_api),
        ("YouTube API", test_youtube_api), 
        ("News API", test_news_api)
    ]
    
    for name, test_func in apis:
        print(f"\n测试 {name}...")
        test_func()
```

### 运行测试
```bash
python test_apis.py
```

---

## 💡 成本优化建议

### 1. 免费替代方案

#### RSS源替代付费API
```json
{
  "free_rss_sources": [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.bloomberg.com/markets/news.rss", 
    "https://feeds.coindesk.com/rss",
    "https://rss.cnn.com/rss/money_latest.rss"
  ]
}
```

#### 公开API替代付费服务
- **Yahoo Finance API**: 免费股票数据
- **CoinGecko Free**: 免费加密货币数据
- **FRED API**: 免费经济数据

### 2. API调用优化

#### 缓存策略
```python
# 缓存API响应减少重复调用
import functools
import time

@functools.lru_cache(maxsize=100)
def cached_api_call(url, cache_duration=300):
    # 实现带时间戳的缓存
    pass
```

#### 批量请求
```python
# 一次请求多个数据项
video_ids = ",".join(video_list[:50])  # YouTube API支持批量查询
```

#### 智能限流
```python
import time
from datetime import datetime

class RateLimiter:
    def __init__(self, max_requests_per_minute=60):
        self.max_requests = max_requests_per_minute
        self.requests = []
    
    def wait_if_needed(self):
        now = datetime.now()
        # 清理过期请求
        self.requests = [req for req in self.requests 
                        if (now - req).seconds < 60]
        
        if len(self.requests) >= self.max_requests:
            time.sleep(60)
            self.requests = []
        
        self.requests.append(now)
```

### 3. 分层数据策略

```python
# 优先级数据源策略
data_sources = [
    {"source": "free_rss", "priority": 1, "cost": 0},
    {"source": "twitter_free", "priority": 2, "cost": 0},
    {"source": "news_api_free", "priority": 3, "cost": 0},
    {"source": "twitter_premium", "priority": 4, "cost": 100},
    {"source": "news_api_premium", "priority": 5, "cost": 449}
]
```

---

## ❓ 常见问题解答

### Q1: Twitter API申请被拒绝怎么办？
**A**: 常见原因和解决方案：
- **使用目的不明确**: 重新提交时详细说明具体用途
- **个人账户不完整**: 完善Twitter个人资料
- **商业用途**: 考虑申请Business账户

### Q2: YouTube API配额不够用怎么办？
**A**: 优化策略：
- **减少搜索频率**: 使用更精确的关键词
- **批量获取数据**: 一次请求多个视频信息
- **缓存结果**: 避免重复请求相同数据
- **升级配额**: 联系Google申请更高配额

### Q3: News API免费版限制太多？
**A**: 替代方案：
- **使用RSS源**: 大多数新闻网站提供免费RSS
- **组合多个免费API**: 分散请求到不同服务
- **Web爬虫**: 遵守robots.txt的合规爬虫

### Q4: API密钥安全如何保证？
**A**: 安全最佳实践：
- **环境变量**: 使用.env文件存储密钥
- **权限限制**: 在API控制台限制IP和域名
- **定期轮换**: 定期更换API密钥
- **监控使用**: 关注异常调用模式

### Q5: 如何测试API是否正常工作？
**A**: 测试方法：
- **使用提供的测试脚本**: 运行test_apis.py
- **检查API文档**: 参考官方示例
- **使用Postman**: 手动测试API端点
- **查看错误日志**: 分析具体错误信息

---

## 📞 获取帮助

### 官方文档链接
- **Twitter API**: https://developer.twitter.com/en/docs
- **YouTube API**: https://developers.google.com/youtube/v3
- **News API**: https://newsapi.org/docs

### 社区支持
- **Stack Overflow**: 搜索具体API问题
- **GitHub Issues**: 查看开源项目的问题讨论
- **Reddit**: r/webdev, r/apis等社区

### 联系项目维护者
- **GitHub Issues**: 在AFNMS项目中提交问题
- **讨论区**: 参与GitHub Discussions

---

## 🔄 更新日志

- **2024-12-19**: 创建初始版本
- 包含Twitter API v2、YouTube Data API、News API详细指南
- 添加成本优化和免费替代方案
- 提供API测试脚本和配置示例

---

*最后更新: 2024-12-19*  
*适用版本: AFNMS v1.0+* 