# AFNMS - AI Financial News Monitoring System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![AI Models](https://img.shields.io/badge/AI%20Models-5+-orange.svg)
![Data Sources](https://img.shields.io/badge/Data%20Sources-10+-red.svg)

**🤖 AI驱动的智能金融新闻分析与投资建议系统**

*结合多平台数据抓取 + 多AI大模型智能分析，实时监控市场动态*

[快速开始](#quick-start) • [功能特性](#features) • [技术架构](#architecture) • [配置指南](#configuration) • [API文档](#api-documentation)

</div>

---

## 📖 项目简介

AFNMS (AI Financial News Monitoring System) 是一个基于人工智能的金融新闻监控和分析系统，能够：

- 🔍 **多源数据抓取**: 自动从Twitter、YouTube、新闻API、RSS源等平台收集金融新闻
- 🤖 **多AI模型分析**: 支持OpenAI、Claude、Gemini、OpenRouter、Grok等5+种AI模型
- 📊 **智能影响评估**: 实时分析新闻对股市、加密货币市场的影响程度
- 💡 **投资建议生成**: 基于AI分析结果提供专业的交易建议和风险提示
- ⚡ **故障转移机制**: 智能路由和负载均衡，确保服务高可用性
- 🔐 **安全配置管理**: 支持环境变量、配置文件和API密钥管理

## ✨ 功能特性

### 🎯 核心功能

| 功能模块 | 描述 | 支持状态 |
|---------|------|---------|
| **多AI模型支持** | OpenAI、Claude、Gemini、OpenRouter、Grok | ✅ 完全支持 |
| **智能路由系统** | 自动故障转移、负载均衡、健康检查 | ✅ 完全支持 |
| **多数据源集成** | API认证源 + 免费RSS源 | ✅ 完全支持 |
| **实时新闻分析** | 影响评分、情感分析、交易建议 | ✅ 完全支持 |
| **配置热重载** | 无需重启即可更新配置 | ✅ 完全支持 |
| **使用统计监控** | API调用次数、成本跟踪 | ✅ 完全支持 |

### 🔗 支持的数据源

#### 认证数据源 (需要API密钥)
- **Twitter API v2**: 实时推文监控，智能关键词过滤
- **YouTube Data API**: 财经频道视频和评论分析
- **News API**: 全球新闻源聚合和筛选

#### 免费数据源 (无需认证)
- **RSS聚合**: 主流财经媒体RSS订阅
- **CoinGecko API**: 加密货币市场数据
- **Alpha Vantage API**: 股票市场免费数据
- **Financial Modeling Prep**: 财务数据和新闻
- **网页抓取**: 合规的公开信息收集

### 🤖 支持的AI模型

| 提供商 | 模型示例 | API格式 | 特点 |
|--------|----------|---------|------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | OpenAI Compatible | 通用分析能力强 |
| **Anthropic** | Claude-3 Sonnet/Opus | Claude API | 长文本理解优秀 |
| **Google** | Gemini Pro/Ultra | Gemini API | 多模态分析支持 |
| **OpenRouter** | 混合模型路由 | OpenAI Compatible | 成本优化 |
| **xAI** | Grok-1 | OpenAI Compatible | 实时数据访问 |
| **第三方** | DeepSeek, 通义千问等 | OpenAI Compatible | 成本效益高 |

## 🏗️ 技术架构

```
AFNMS
├── 🎯 核心系统
│   ├── Afnms.py              # 主程序入口和传统功能
│   └── src/
│       ├── config_manager.py     # 配置管理系统
│       ├── model_router.py       # AI模型智能路由
│       ├── free_data_collector.py # 免费数据源收集
│       └── cache_manager.py      # 缓存管理系统
│
├── 🤖 AI适配器层
│   └── src/ai_adapters/
│       ├── base_adapter.py       # 基础适配器接口
│       ├── openai_adapter.py     # OpenAI兼容格式
│       ├── claude_adapter.py     # Claude API
│       ├── gemini_adapter.py     # Google Gemini
│       ├── openrouter_adapter.py # OpenRouter服务
│       └── grok_adapter.py       # xAI Grok
│
├── ⚙️ 配置系统
│   └── config/
│       ├── ai_config.json        # AI模型配置
│       └── sources_config.json   # 数据源配置
│
└── 📚 文档系统
    └── docs/
        ├── OpenAI_Compatible_API_Guide.md
        └── gitignore_guide.md
```

### 设计理念

- **模块化架构**: 每个组件独立可测试，松耦合设计
- **策略模式**: AI适配器使用统一接口，支持动态切换
- **观察者模式**: 配置变更自动通知相关组件
- **责任链模式**: 故障转移和负载均衡的智能路由

## 🚀 快速开始 {#quick-start}

### 环境要求

- **Python**: 3.8+ (推荐 3.10+)
- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **内存**: 建议 4GB+ RAM
- **网络**: 稳定的互联网连接

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/AFNMS.git
cd AFNMS
```

2. **创建虚拟环境**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置API密钥**
```bash
# 方法1: 复制配置模板
cp config/ai_config.json config/local_ai_config.json

# 方法2: 使用环境变量
echo "OPENAI_API_KEY=your_openai_key" > .env
echo "CLAUDE_API_KEY=your_claude_key" >> .env
```

5. **运行系统**
```bash
# 基础模式运行
python Afnms.py

# 或使用增强模式(推荐)
python -c "from src.model_router import ModelRouter; import asyncio; asyncio.run(ModelRouter().test_all_models())"
```

### 快速配置示例

创建 `config/local_ai_config.json`:
```json
{
  "models": [
    {
      "name": "openai-gpt4",
      "type": "openai",
      "api_key": "sk-your-openai-key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4",
      "priority": 1,
      "enabled": true
    },
    {
      "name": "claude-sonnet",
      "type": "claude", 
      "api_key": "sk-ant-your-claude-key",
      "model": "claude-3-sonnet-20240229",
      "priority": 2,
      "enabled": true
    }
  ]
}
```

## ⚙️ 配置指南 {#configuration}

### AI模型配置

AFNMS支持多种AI模型配置方式，详细配置请参考：
📖 [OpenAI兼容API配置指南](docs/OpenAI_Compatible_API_Guide.md)

#### 配置文件结构
```json
{
  "models": [
    {
      "name": "模型唯一标识",
      "type": "openai|claude|gemini|openrouter|grok", 
      "api_key": "API密钥",
      "base_url": "API端点URL",
      "model": "具体模型名称",
      "priority": 1-10,
      "enabled": true|false,
      "max_tokens": null,
      "temperature": 0.3,
      "timeout": 30
    }
  ],
  "routing": {
    "strategy": "priority|round_robin|random",
    "health_check_interval": 300,
    "retry_attempts": 3,
    "fallback_enabled": true
  }
}
```

#### 环境变量支持
```bash
# AI API密钥
OPENAI_API_KEY=sk-your-openai-key
CLAUDE_API_KEY=sk-ant-your-claude-key  
GEMINI_API_KEY=your-gemini-key
OPENROUTER_API_KEY=sk-or-your-key
GROK_API_KEY=your-grok-key

# 数据源API密钥
TWITTER_BEARER_TOKEN=your-twitter-token
YOUTUBE_API_KEY=your-youtube-key
NEWS_API_KEY=your-news-api-key
```

### 数据源配置

#### 认证数据源
```json
{
  "authenticated_sources": {
    "twitter": {
      "enabled": true,
      "bearer_token": "your_twitter_bearer_token",
      "keywords": ["Bitcoin", "股市", "加密货币"],
      "max_tweets": 50
    },
    "youtube": {
      "enabled": true, 
      "api_key": "your_youtube_api_key",
      "channels": ["UC财经频道ID"],
      "max_videos": 20
    }
  }
}
```

#### 免费数据源
```json
{
  "free_sources": {
    "rss_feeds": [
      {
        "name": "财联社",
        "url": "https://example-rss-url.com/feed",
        "category": "finance"
      }
    ],
    "public_apis": [
      {
        "name": "coingecko",
        "base_url": "https://api.coingecko.com/api/v3",
        "endpoints": {
          "news": "/news"
        }
      }
    ]
  }
}
```

## 📋 使用示例 {#api-documentation}

### 基础使用

```python
import asyncio
from src.model_router import ModelRouter
from src.free_data_collector import FreeDataCollector

async def main():
    # 初始化系统组件
    router = ModelRouter()
    collector = FreeDataCollector()
    
    # 收集新闻数据
    news_data = await collector.collect_all_free_news()
    print(f"收集到 {len(news_data)} 条新闻")
    
    # AI分析新闻
    for news in news_data[:3]:  # 分析前3条
        analysis = await router.analyze_news(
            content=news['content'],
            source=news['source']
        )
        print(f"影响评分: {analysis.impact_score}")
        print(f"投资建议: {analysis.trading_suggestion}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 高级配置使用

```python
from src.config_manager import ConfigManager

# 加载自定义配置
config_manager = ConfigManager()
config_manager.load_config('config/local_ai_config.json')

# 动态添加新模型
new_model = {
    "name": "custom-llm",
    "type": "openai",
    "api_key": "sk-custom-key", 
    "base_url": "https://api.custom-llm.com/v1",
    "model": "custom-model-v1",
    "priority": 1
}

config_manager.add_model_config(new_model)
```

### API健康检查

```python
async def check_system_health():
    router = ModelRouter()
    health_status = await router.health_check_all()
    
    for model_name, status in health_status.items():
        print(f"{model_name}: {'✅' if status['healthy'] else '❌'}")
        if not status['healthy']:
            print(f"  错误: {status['error']}")
```

## 📁 项目结构

```
AFNMS/                              # 项目根目录
├── README.md                       # 📖 项目说明文档  
├── requirements.txt                # 📦 Python依赖包
├── .gitignore                      # 🚫 Git忽略文件
├── Afnms.py                        # 🎯 主程序入口(兼容传统功能)
│
├── config/                         # ⚙️ 配置文件目录
│   ├── ai_config.json             # 🤖 AI模型配置模板
│   └── sources_config.json        # 📡 数据源配置模板
│
├── src/                           # 💻 源代码目录
│   ├── config_manager.py          # ⚙️ 配置管理器
│   ├── model_router.py            # 🔀 AI模型路由器
│   ├── free_data_collector.py     # 📡 免费数据收集器
│   ├── cache_manager.py           # 💾 缓存管理系统
│   └── ai_adapters/               # 🤖 AI适配器模块
│       ├── base_adapter.py        # 📋 基础适配器接口
│       ├── openai_adapter.py      # 🟢 OpenAI适配器
│       ├── claude_adapter.py      # 🟣 Claude适配器
│       ├── gemini_adapter.py      # 🔵 Gemini适配器
│       ├── openrouter_adapter.py  # 🟡 OpenRouter适配器
│       └── grok_adapter.py        # ⚫ Grok适配器
│
├── docs/                          # 📚 文档目录
│   ├── OpenAI_Compatible_API_Guide.md  # OpenAI兼容API指南
│   └── gitignore_guide.md         # Git忽略文件指南
│
└── logs/                          # 📝 日志文件目录(运行时生成)
    ├── afnms.log                  # 系统运行日志
    ├── api_usage.log              # API使用统计
    └── errors.log                 # 错误日志
```

## 🔧 故障排除

### 常见问题

#### 1. API密钥错误
```bash
错误: OpenAI API authentication failed
解决: 检查API密钥格式，确保以'sk-'开头
```

#### 2. 网络连接问题
```bash
错误: Connection timeout to API endpoint
解决: 检查网络连接，考虑使用代理或更换端点
```

#### 3. 配置文件错误
```bash
错误: JSON decode error in config file
解决: 验证JSON格式，使用在线JSON验证器检查
```

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
from src.config_manager import ConfigManager
config = ConfigManager(debug=True)
```

### 性能优化建议

1. **并发设置**: 根据API限制调整并发数
2. **缓存策略**: 启用适当的缓存以减少API调用
3. **数据过滤**: 使用关键词过滤减少不必要的分析
4. **模型选择**: 根据成本和准确性需求选择合适的模型

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 贡献方式

1. **报告问题**: 在GitHub Issues中提交bug报告
2. **功能建议**: 提出新功能的需求和想法
3. **代码贡献**: 提交Pull Request改进代码
4. **文档改进**: 完善文档和使用指南

### 开发环境设置

```bash
# 1. Fork项目并克隆
git clone https://github.com/your-username/AFNMS.git

# 2. 创建开发分支
git checkout -b feature/your-feature-name

# 3. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果存在

# 4. 运行测试
python -m pytest tests/

# 5. 提交更改
git commit -am "Add your feature"
git push origin feature/your-feature-name
```

### 代码规范

- 遵循 PEP 8 Python代码规范
- 添加适当的类型注释
- 编写单元测试覆盖新功能
- 更新相关文档

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

感谢以下开源项目和服务提供商：

- **AI服务提供商**: OpenAI, Anthropic, Google, xAI, OpenRouter
- **数据源**: Twitter API, YouTube API, News API, CoinGecko
- **Python生态**: requests, aiohttp, beautifulsoup4, pandas
- **开源社区**: 所有贡献者和用户的支持

## 📞 联系方式

- **项目主页**: [GitHub Repository](https://github.com/your-username/AFNMS)
- **问题反馈**: [GitHub Issues](https://github.com/your-username/AFNMS/issues)
- **讨论社区**: [GitHub Discussions](https://github.com/your-username/AFNMS/discussions)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star! ⭐**

Made with ❤️ by AI Financial News Monitoring System Team

</div> 