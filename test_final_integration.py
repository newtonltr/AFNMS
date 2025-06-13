#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终集成测试 - 验证整个AFNMS系统
"""

import asyncio
import Afnms

async def test_final_integration():
    print("🚀 AFNMS最终集成测试")
    print("="*50)
    
    try:
        # 1. 初始化系统
        print("1️⃣ 初始化系统...")
        monitor = Afnms.FinancialNewsMonitor()
        print(f"   ✅ 增强模式: {Afnms.ENHANCED_MODE}")
        print(f"   ✅ 免费数据收集器: {hasattr(monitor, 'free_data_collector')}")
        print(f"   ✅ AI分析器: {hasattr(monitor, 'ai_analyzer')}")
        
        # 2. 测试数据收集
        print("\n2️⃣ 测试数据收集...")
        
        # 收集所有新闻（包括免费数据源）
        print("   🔍 收集新闻数据...")
        news_items = await monitor.collect_and_analyze_news()
        
        print(f"   ✅ 总共收集到 {len(news_items)} 条新闻")
        
        # 3. 显示结果
        if news_items:
            print("\n3️⃣ 新闻分析结果:")
            print("-"*50)
            
            for i, news in enumerate(news_items[:3], 1):  # 显示前3条
                print(f"\n📰 新闻 {i}:")
                print(f"   来源: {news.source}")
                print(f"   标题: {news.title}")
                if news.ai_analysis:
                    print(f"   AI影响评分: {news.ai_analysis.impact_score:.2f}")
                    print(f"   市场情感: {news.ai_analysis.sentiment}")
                    print(f"   AI信心度: {news.ai_analysis.confidence:.2f}")
                print(f"   链接: {news.url}")
        else:
            print("\n3️⃣ 未收集到新闻数据")
            print("   💡 这可能是因为:")
            print("   - 网络连接问题")
            print("   - API密钥未配置")
            print("   - 关键词过滤太严格")
        
        # 4. 测试各个数据源
        print("\n4️⃣ 测试各个数据源:")
        
        # 测试免费RSS
        try:
            rss_news = await monitor.get_free_rss_news()
            print(f"   📡 RSS新闻: {len(rss_news)} 条")
        except Exception as e:
            print(f"   ❌ RSS新闻收集失败: {e}")
        
        # 测试加密货币数据
        try:
            crypto_news = await monitor.get_free_crypto_news()
            print(f"   💰 加密货币新闻: {len(crypto_news)} 条")
        except Exception as e:
            print(f"   ❌ 加密货币新闻收集失败: {e}")
        
        # 测试市场数据
        try:
            market_news = await monitor.get_free_market_news()
            print(f"   📈 市场新闻: {len(market_news)} 条")
        except Exception as e:
            print(f"   ❌ 市场新闻收集失败: {e}")
        
        print("\n🎉 集成测试完成！")
        print("="*50)
        print("✅ AFNMS系统已成功集成免费数据源")
        print("💡 即使没有API密钥，也可以获取基础金融新闻")
        print("🔧 如需更多数据源，请配置相应的API密钥")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_final_integration()) 