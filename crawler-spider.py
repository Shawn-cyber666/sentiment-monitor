"""
Vivo X300U 舆论监测爬虫
采集来自小红书、微博、B站的用户评论
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict
import logging
from abc import ABC, abstractmethod
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================
# 数据库连接
# ============================================

class DatabaseManager:
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['sentiment-monitor']
        self.comments_collection = self.db['comments']
        self.keywords_collection = self.db['keywords']
        
        # 创建索引
        self.comments_collection.create_index([('platform', 1), ('createdAt', -1)])
        self.comments_collection.create_index([('sentiment_score', -1)])
    
    def insert_comment(self, comment: Dict) -> bool:
        """插入评论"""
        try:
            comment['createdAt'] = datetime.now()
            comment['updatedAt'] = datetime.now()
            result = self.comments_collection.insert_one(comment)
            logger.info(f"Comment inserted: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"Error inserting comment: {e}")
            return False
    
    def get_comment_count(self, platform: str) -> int:
        """获取评论计数"""
        return self.comments_collection.count_documents({'platform': platform})
    
    def close(self):
        """关闭数据库连接"""
        self.client.close()


# ============================================
# 爬虫基类
# ============================================

class PlatformSpider(ABC):
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @abstractmethod
    def search(self, keyword: str) -> List[Dict]:
        """搜索评论"""
        pass
    
    @abstractmethod
    def parse_comments(self, data) -> List[Dict]:
        """解析评论"""
        pass
    
    def extract_keywords(self, text: str) -> List[str]:
        """简单的关键词提取"""
        keywords = []
        predefined = [
            '屏幕', '拍照', '续航', '散热', '芯片', '性能',
            '系统', '流畅', '价格', '性价比', '做工', '质感',
            '信号', '刷新', '屏幕素质', '拍照能力', '续航能力',
            '散热控制', '系统流畅度', '价格性价比', '做工质感'
        ]
        
        for keyword in predefined:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords if keywords else ['其他']
    
    def analyze_sentiment(self, text: str) -> int:
        """简单的情感分析"""
        positive_words = ['很棒', '绝了', '完美', '超强', '优秀', '不错', '喜欢', '推荐', '满意']
        negative_words = ['垃圾', '差', '失望', '坑', '问题', '不行', '后悔', '不建议']
        
        score = 50
        
        for word in positive_words:
            if word in text:
                score += 5
        
        for word in negative_words:
            if word in text:
                score -= 5
        
        return max(0, min(100, score))
    
    def run(self, keyword: str = 'vivo x300u', limit: int = 100):
        """运行爬虫"""
        logger.info(f"Starting {self.__class__.__name__} crawler for '{keyword}'")
        try:
            results = self.search(keyword)
            comments = self.parse_comments(results)
            
            saved_count = 0
            for comment in comments[:limit]:
                if self.db.insert_comment(comment):
                    saved_count += 1
                    time.sleep(0.1)  # 避免过快请求
            
            logger.info(f"Saved {saved_count} comments from {self.__class__.__name__}")
            return saved_count
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            return 0


# ============================================
# 小红书爬虫 (示例实现)
# ============================================

class XiaohongShuSpider(PlatformSpider):
    """
    小红书爬虫
    注意：实际使用需要购买或申请小红书数据API权限
    此示例展示数据结构和处理流程
    """
    
    def __init__(self, db_manager: DatabaseManager, api_key: str = None):
        super().__init__(db_manager)
        self.api_key = api_key or os.getenv('XIAOHONGSHU_API_KEY')
        self.platform = 'xiaohongshu'
    
    def search(self, keyword: str) -> List[Dict]:
        """调用小红书 API 搜索"""
        # 这是一个示例实现，实际需要使用官方API
        logger.info(f"Searching XiaoHongShu for: {keyword}")
        
        # 示例：使用第三方数据服务 API
        # url = 'https://api.xiaohongshu-data.com/search'
        # params = {
        #     'keyword': keyword,
        #     'api_key': self.api_key,
        #     'page': 1,
        #     'limit': 100
        # }
        # response = self.session.get(url, params=params)
        # return response.json().get('data', [])
        
        # 返回模拟数据
        return self._generate_mock_data(keyword)
    
    def parse_comments(self, data: List[Dict]) -> List[Dict]:
        """解析小红书评论"""
        comments = []
        
        for item in data:
            content = item.get('content', '')
            if not content:
                continue
            
            keywords = self.extract_keywords(content)
            sentiment = self.analyze_sentiment(content)
            
            comment = {
                'platform': self.platform,
                'content': content,
                'author': item.get('author', 'Unknown'),
                'likes': item.get('likes', 0),
                'sentiment_score': sentiment,
                'keywords': keywords,
                'url': item.get('url', ''),
                'timestamp': item.get('timestamp', datetime.now())
            }
            comments.append(comment)
        
        return comments
    
    def _generate_mock_data(self, keyword: str) -> List[Dict]:
        """生成模拟数据用于测试"""
        mock_comments = [
            {
                'content': 'X300U的屏幕素质真的绝了，这块屏幕在同价位真的难找对手',
                'author': 'user_001',
                'likes': 1245,
                'url': 'https://xiaohongshu.com/...',
                'timestamp': datetime.now()
            },
            {
                'content': '拍照能力超强，这次vivo在影像上真的下功夫了',
                'author': 'user_002',
                'likes': 892,
                'url': 'https://xiaohongshu.com/...',
                'timestamp': datetime.now()
            },
            {
                'content': '续航确实是短板，一天得充两次电，其他方面还不错',
                'author': 'user_003',
                'likes': 567,
                'url': 'https://xiaohongshu.com/...',
                'timestamp': datetime.now()
            },
            {
                'content': '做工质感很棒，感觉很有档次',
                'author': 'user_004',
                'likes': 734,
                'url': 'https://xiaohongshu.com/...',
                'timestamp': datetime.now()
            },
            {
                'content': '芯片性能很强，日常使用完全没有压力',
                'author': 'user_005',
                'likes': 891,
                'url': 'https://xiaohongshu.com/...',
                'timestamp': datetime.now()
            }
        ]
        
        return mock_comments


# ============================================
# 微博爬虫
# ============================================

class WeiboSpider(PlatformSpider):
    """
    微博爬虫
    使用微博官方API (需要申请权限)
    """
    
    def __init__(self, db_manager: DatabaseManager, access_token: str = None):
        super().__init__(db_manager)
        self.access_token = access_token or os.getenv('WEIBO_ACCESS_TOKEN')
        self.platform = 'weibo'
        self.base_url = 'https://api.weibo.com/2'
    
    def search(self, keyword: str) -> List[Dict]:
        """使用微博API搜索"""
        logger.info(f"Searching Weibo for: {keyword}")
        
        # 调用微博搜索接口
        # url = f'{self.base_url}/search/statuses.json'
        # params = {
        #     'q': keyword,
        #     'access_token': self.access_token,
        #     'count': 100
        # }
        # response = self.session.get(url, params=params)
        # return response.json().get('statuses', [])
        
        return self._generate_mock_data(keyword)
    
    def parse_comments(self, data: List[Dict]) -> List[Dict]:
        """解析微博评论"""
        comments = []
        
        for item in data:
            content = item.get('text', '')
            if not content:
                continue
            
            # 移除HTML标签
            content = self._clean_html(content)
            
            keywords = self.extract_keywords(content)
            sentiment = self.analyze_sentiment(content)
            
            comment = {
                'platform': self.platform,
                'content': content,
                'author': item.get('user', {}).get('screen_name', 'Unknown'),
                'likes': item.get('attitudes_count', 0),
                'sentiment_score': sentiment,
                'keywords': keywords,
                'url': item.get('source_url', ''),
                'timestamp': item.get('created_at', datetime.now())
            }
            comments.append(comment)
        
        return comments
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        import re
        return re.sub(r'<[^>]+>', '', text)
    
    def _generate_mock_data(self, keyword: str) -> List[Dict]:
        """生成模拟数据"""
        mock_tweets = [
            {
                'text': '散热有点问题，玩游戏手机温度有点高',
                'user': {'screen_name': 'user_601'},
                'attitudes_count': 567,
                'source_url': 'https://weibo.com/...',
                'created_at': datetime.now()
            },
            {
                'text': 'X300U系统优化做得很到位，日常使用没有卡顿',
                'user': {'screen_name': 'user_602'},
                'attitudes_count': 1834,
                'source_url': 'https://weibo.com/...',
                'created_at': datetime.now()
            },
            {
                'text': '屏幕刷新率很流畅，看视频很舒服',
                'user': {'screen_name': 'user_603'},
                'attitudes_count': 923,
                'source_url': 'https://weibo.com/...',
                'created_at': datetime.now()
            }
        ]
        
        return mock_tweets


# ============================================
# B站爬虫
# ============================================

class BilibiliSpider(PlatformSpider):
    """
    B站爬虫
    采集相关视频的评论区数据
    """
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.platform = 'bilibili'
        self.base_url = 'https://api.bilibili.com/x'
    
    def search(self, keyword: str, video_ids: List[str] = None) -> List[Dict]:
        """搜索B站视频并获取评论"""
        logger.info(f"Searching Bilibili for: {keyword}")
        
        # 如果提供了视频ID，直接获取这些视频的评论
        if not video_ids:
            video_ids = self._search_videos(keyword)
        
        all_comments = []
        for video_id in video_ids[:5]:  # 限制获取前5个视频
            comments = self._get_video_comments(video_id)
            all_comments.extend(comments)
            time.sleep(1)  # 避免请求过快
        
        return all_comments
    
    def _search_videos(self, keyword: str) -> List[str]:
        """搜索B站视频"""
        # 示例视频ID (实际应调用搜索API)
        return ['BV1234567', 'BV7654321']
    
    def _get_video_comments(self, video_id: str) -> List[Dict]:
        """获取视频评论"""
        # 实现获取视频评论的逻辑
        # url = f'{self.base_url}/v2/reply'
        # params = {'oid': video_id, 'type': 1}
        # response = self.session.get(url, params=params)
        # return response.json().get('data', {}).get('replies', [])
        
        return self._generate_mock_data(video_id)
    
    def parse_comments(self, data: List[Dict]) -> List[Dict]:
        """解析B站评论"""
        comments = []
        
        for item in data:
            content = item.get('content', '')
            if not content:
                continue
            
            keywords = self.extract_keywords(content)
            sentiment = self.analyze_sentiment(content)
            
            comment = {
                'platform': self.platform,
                'content': content,
                'author': item.get('author', 'Unknown'),
                'likes': item.get('like', 0),
                'sentiment_score': sentiment,
                'keywords': keywords,
                'url': item.get('url', ''),
                'timestamp': item.get('timestamp', datetime.now())
            }
            comments.append(comment)
        
        return comments
    
    def _generate_mock_data(self, video_id: str) -> List[Dict]:
        """生成模拟数据"""
        return [
            {
                'content': '拍照能力超强，这次vivo在影像上真的下功夫了',
                'author': 'user_701',
                'like': 2156,
                'url': 'https://bilibili.com/...',
                'timestamp': datetime.now()
            },
            {
                'content': '屏幕刷新率很棒，玩游戏体验很好',
                'author': 'user_702',
                'like': 1567,
                'url': 'https://bilibili.com/...',
                'timestamp': datetime.now()
            },
            {
                'content': '续航确实需要改进',
                'author': 'user_703',
                'like': 834,
                'url': 'https://bilibili.com/...',
                'timestamp': datetime.now()
            }
        ]


# ============================================
# 爬虫调度器
# ============================================

class CrawlerScheduler:
    """爬虫调度器 - 定期运行各平台爬虫"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.spiders = [
            XiaohongShuSpider(self.db),
            WeiboSpider(self.db),
            BilibiliSpider(self.db)
        ]
    
    def run_all(self, keyword: str = 'vivo x300u'):
        """运行所有爬虫"""
        logger.info(f"Starting all crawlers for: {keyword}")
        
        total_saved = 0
        for spider in self.spiders:
            count = spider.run(keyword, limit=50)
            total_saved += count
        
        logger.info(f"Total comments saved: {total_saved}")
        return total_saved
    
    def run_scheduled(self, interval_hours: int = 4):
        """定期运行爬虫"""
        import schedule
        
        # 每隔 interval_hours 小时运行一次
        schedule.every(interval_hours).hours.do(self.run_all)
        
        logger.info(f"Scheduler running - will crawl every {interval_hours} hours")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()


# ============================================
# 主程序
# ============================================

if __name__ == '__main__':
    # 单次运行
    scheduler = CrawlerScheduler()
    scheduler.run_all(keyword='vivo x300u')
    scheduler.close()
    
    # 或定期运行 (取消注释以启用)
    # scheduler.run_scheduled(interval_hours=4)
