#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - AFNMS数据源验证
测试Twitter、YouTube、News API等主要数据源的连接状态
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
from typing import Dict, Tuple

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 已加载.env环境变量")
except ImportError:
    print("⚠️  未安装python-dotenv包，将使用系统环境变量")

class APITester:
    """API测试器类"""
    
    def __init__(self):
        self.results = {}
        
    def test_twitter_api(self) -> Tuple[bool, str]:
        """测试Twitter API v2"""
        print("\n🐦 测试Twitter API v2...")
        
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            return False, "未找到TWITTER_BEARER_TOKEN环境变量"
            
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'User-Agent': 'AFNMS-API-Tester/1.0'
        }
        
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            'query': 'Bitcoin OR 股市 OR cryptocurrency',
            'max_results': 10,
            'tweet.fields': 'created_at,author_id,public_metrics'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tweet_count = len(data.get('data', []))
                return True, f"成功获取 {tweet_count} 条推文"
            elif response.status_code == 401:
                return False, "认证失败，请检查Bearer Token"
            elif response.status_code == 429:
                return False, "请求过于频繁，已达到速率限制"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def test_youtube_api(self) -> Tuple[bool, str]:
        """测试YouTube Data API v3"""
        print("\n📺 测试YouTube Data API v3...")
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            return False, "未找到YOUTUBE_API_KEY环境变量"
            
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': 'financial news 财经新闻',
            'type': 'video',
            'maxResults': 5,
            'order': 'date',
            'key': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                video_count = len(data.get('items', []))
                return True, f"成功获取 {video_count} 个视频"
            elif response.status_code == 400:
                error_msg = response.json().get('error', {}).get('message', '请求参数错误')
                return False, f"请求错误: {error_msg}"
            elif response.status_code == 403:
                error_data = response.json().get('error', {})
                if 'quotaExceeded' in error_data.get('errors', [{}])[0].get('reason', ''):
                    return False, "API配额已用完"
                else:
                    return False, "API密钥无效或权限不足"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def test_news_api(self) -> Tuple[bool, str]:
        """测试News API"""
        print("\n📰 测试News API...")
        
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            return False, "未找到NEWS_API_KEY环境变量"
            
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'finance OR Bitcoin OR stock market',
            'sortBy': 'publishedAt',
            'pageSize': 5,
            'language': 'en',
            'apiKey': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                article_count = len(data.get('articles', []))
                total_results = data.get('totalResults', 0)
                return True, f"成功获取 {article_count} 篇文章 (总计 {total_results} 条结果)"
            elif response.status_code == 401:
                return False, "API密钥无效"
            elif response.status_code == 429:
                return False, "请求过于频繁或已达到每日限额"
            else:
                error_msg = response.json().get('message', response.text)
                return False, f"HTTP {response.status_code}: {error_msg}"
                
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def test_fred_api(self) -> Tuple[bool, str]:
        """测试FRED API (可选)"""
        print("\n💰 测试FRED API...")
        
        api_key = os.getenv('FRED_API_KEY')
        if not api_key:
            return False, "未找到FRED_API_KEY环境变量"
            
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': 'GDP',
            'api_key': api_key,
            'file_type': 'json',
            'limit': 5
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                obs_count = len(data.get('observations', []))
                return True, f"成功获取 {obs_count} 条经济数据"
            elif response.status_code == 400:
                return False, "API密钥无效或请求参数错误"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def test_coingecko_api(self) -> Tuple[bool, str]:
        """测试CoinGecko API (免费)"""
        print("\n🪙 测试CoinGecko API...")
        
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 5,
            'page': 1
        }
        
        # CoinGecko Pro API密钥（可选）
        api_key = os.getenv('COINGECKO_API_KEY')
        if api_key:
            headers = {'X-CG-Pro-API-Key': api_key}
        else:
            headers = {}
            
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                coin_count = len(data)
                return True, f"成功获取 {coin_count} 种加密货币数据"
            elif response.status_code == 429:
                return False, "请求过于频繁，已达到速率限制"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def test_alpha_vantage_api(self) -> Tuple[bool, str]:
        """测试Alpha Vantage API (可选)"""
        print("\n📈 测试Alpha Vantage API...")
        
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not api_key:
            return False, "未找到ALPHA_VANTAGE_API_KEY环境变量"
            
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': 'AAPL',
            'interval': '5min',
            'apikey': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'Error Message' in data:
                    return False, data['Error Message']
                elif 'Note' in data:
                    return False, "API调用频率过高，请稍后重试"
                elif 'Time Series (5min)' in data:
                    series_count = len(data['Time Series (5min)'])
                    return True, f"成功获取 {series_count} 条股票数据"
                else:
                    return False, "响应格式异常"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def run_all_tests(self):
        """运行所有API测试"""
        print("🧪 开始API连接测试...")
        print("=" * 50)
        
        # 必需的API测试
        required_apis = [
            ("Twitter API v2", self.test_twitter_api),
            ("YouTube Data API", self.test_youtube_api),
            ("News API", self.test_news_api)
        ]
        
        # 可选的API测试
        optional_apis = [
            ("FRED API", self.test_fred_api),
            ("CoinGecko API", self.test_coingecko_api),
            ("Alpha Vantage API", self.test_alpha_vantage_api)
        ]
        
        success_count = 0
        total_count = 0
        
        # 测试必需的API
        print("\n📋 必需的API测试:")
        for name, test_func in required_apis:
            total_count += 1
            success, message = test_func()
            
            if success:
                print(f"✅ {name}: {message}")
                success_count += 1
            else:
                print(f"❌ {name}: {message}")
            
            self.results[name] = {"success": success, "message": message}
            time.sleep(1)  # 避免过快请求
        
        # 测试可选的API
        print("\n🔧 可选的API测试:")
        for name, test_func in optional_apis:
            total_count += 1
            success, message = test_func()
            
            if success:
                print(f"✅ {name}: {message}")
                success_count += 1
            else:
                print(f"⚠️  {name}: {message}")
            
            self.results[name] = {"success": success, "message": message}
            time.sleep(1)  # 避免过快请求
        
        # 生成测试报告
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print(f"✅ 成功: {success_count}/{total_count} 个API")
        print(f"❌ 失败: {total_count - success_count}/{total_count} 个API")
        
        if success_count == 0:
            print("\n🚨 所有API测试均失败，请检查:")
            print("1. 网络连接是否正常")
            print("2. API密钥是否正确配置")
            print("3. 环境变量是否正确设置")
        elif success_count < len(required_apis):
            print("\n⚠️  部分必需API测试失败，建议:")
            print("1. 检查失败API的密钥配置")
            print("2. 查看API服务商的状态页面")
            print("3. 确认API使用限额")
        else:
            print("\n🎉 主要API测试通过，系统可以正常运行!")
        
        return self.results

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️  Python版本过低: {python_version.major}.{python_version.minor}.{python_version.micro} (建议3.8+)")
    
    # 检查必需的包
    required_packages = ['requests']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 包已安装")
        except ImportError:
            print(f"❌ {package} 包未安装")
    
    # 检查环境变量
    env_vars = [
        'TWITTER_BEARER_TOKEN',
        'YOUTUBE_API_KEY', 
        'NEWS_API_KEY'
    ]
    
    print("\n🔑 环境变量检查:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 只显示前几位和后几位，中间用*代替
            masked_value = value[:8] + '*' * (len(value) - 16) + value[-8:] if len(value) > 16 else value[:4] + '*' * (len(value) - 8) + value[-4:]
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"⚠️  {var}: 未设置")

def save_test_results(results: Dict):
    """保存测试结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_test_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存到: {filename}")
    except Exception as e:
        print(f"\n❌ 保存测试结果失败: {e}")

def main():
    """主函数"""
    print("🚀 AFNMS API测试工具")
    print("=" * 50)
    
    # 检查环境
    check_environment()
    
    # 运行API测试
    tester = APITester()
    results = tester.run_all_tests()
    
    # 保存结果
    save_test_results(results)
    
    print("\n📖 更多帮助信息:")
    print("- API获取指南: docs/API获取指南.md")
    print("- 项目文档: README.md")
    print("- 配置示例: config/sources_config.json")

if __name__ == "__main__":
    main() 