/**
 * Vivo X300U 舆论监测 - Express 后端服务器
 * 功能：数据聚合、实时推送、数据分析
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const redis = require('redis');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

// 中间件
app.use(cors());
app.use(express.json());

// Redis 客户端
// 这里的 process.env.REDIS_URL 会自动读取你在 Railway 设置的那个变量
const client = require('redis').createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

client.on('error', (err) => console.log('Redis Client Error', err));
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379
});

redisClient.connect();

// MongoDB 连接
mongoose.connect(
  process.env.MONGODB_URI || 'mongodb://localhost:27017/sentiment-monitor',
  { useNewUrlParser: true, useUnifiedTopology: true }
);

// ============================================
// 数据库 Schema 定义
// ============================================

const commentSchema = new mongoose.Schema({
  platform: { type: String, enum: ['xiaohongshu', 'weibo', 'bilibili'] },
  content: String,
  author: String,
  likes: { type: Number, default: 0 },
  sentiment_score: { type: Number, min: 0, max: 100 },
  keywords: [String],
  url: String,
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

const keywordSchema = new mongoose.Schema({
  word: { type: String, unique: true },
  frequency: { type: Number, default: 0 },
  sentiment_avg: { type: Number, default: 50 },
  trend: { type: String, enum: ['up', 'down', 'neutral'], default: 'neutral' },
  platforms: {
    xiaohongshu: { type: Number, default: 0 },
    weibo: { type: Number, default: 0 },
    bilibili: { type: Number, default: 0 }
  },
  first_seen: { type: Date, default: Date.now },
  last_updated: { type: Date, default: Date.now }
});

const statisticsSchema = new mongoose.Schema({
  date: { type: Date, default: Date.now },
  platform: String,
  total_comments: Number,
  avg_sentiment: Number,
  keyword_list: [
    {
      word: String,
      frequency: Number
    }
  ]
});

commentSchema.index({ platform: 1, createdAt: -1 });
commentSchema.index({ sentiment_score: -1 });
keywordSchema.index({ frequency: -1 });

const Comment = mongoose.model('Comment', commentSchema);
const Keyword = mongoose.model('Keyword', keywordSchema);
const Statistics = mongoose.model('Statistics', statisticsSchema);

// ============================================
// 数据处理服务
// ============================================

/**
 * 关键词提取 (模拟，实际应使用jieba)
 */
function extractKeywords(text) {
  // 简单的关键词提取逻辑，实际应使用 jieba 分词
  const keywords = [];
  
  // 预定义的关键词列表
  const predefinedKeywords = [
    '屏幕', '拍照', '续航', '散热', '芯片', '性能',
    '系统', '流畅', '价格', '性价比', '做工', '质感',
    '信号', '刷新', '屏幕素质', '拍照能力', '续航能力',
    '散热控制', '系统流畅度', '价格性价比', '做工质感', '屏幕刷新'
  ];
  
  for (const keyword of predefinedKeywords) {
    if (text.includes(keyword)) {
      keywords.push(keyword);
    }
  }
  
  return keywords.length > 0 ? keywords : ['其他'];
}

/**
 * 情感分析 (模拟，实际应使用 SnowNLP 或 BERT)
 */
function analyzeSentiment(text) {
  // 简单的情感分析规则
  const positiveWords = ['很棒', '绝了', '完美', '超强', '优秀', '不错', '喜欢', '推荐', '满意', '强'];
  const negativeWords = ['垃圾', '差', '失望', '坑', '问题', '有点', '不行', '后悔', '不建议'];
  
  let score = 50; // 中立分数
  
  for (const word of positiveWords) {
    if (text.includes(word)) score += 5;
  }
  
  for (const word of negativeWords) {
    if (text.includes(word)) score -= 5;
  }
  
  return Math.max(0, Math.min(100, score));
}

/**
 * 获取平台统计信息
 */
async function getPlatformStats() {
  try {
    const stats = {};
    const platforms = ['xiaohongshu', 'weibo', 'bilibili'];
    
    for (const platform of platforms) {
      const comments = await Comment.find({ platform });
      const sentiments = comments.map(c => c.sentiment_score);
      const avgSentiment = sentiments.length > 0
        ? Math.round(sentiments.reduce((a, b) => a + b) / sentiments.length)
        : 0;
      
      stats[platform] = {
        count: comments.length,
        sentiment: avgSentiment
      };
    }
    
    return stats;
  } catch (error) {
    console.error('Error getting platform stats:', error);
    return {};
  }
}

/**
 * 获取关键词排行
 */
async function getTopKeywords(limit = 10) {
  try {
    return await Keyword.find()
      .sort({ frequency: -1 })
      .limit(limit)
      .lean();
  } catch (error) {
    console.error('Error getting top keywords:', error);
    return [];
  }
}

/**
 * 更新关键词统计
 */
async function updateKeywordStats(keywords, sentiment, platform) {
  try {
    for (const keyword of keywords) {
      const existingKeyword = await Keyword.findOne({ word: keyword });
      
      if (existingKeyword) {
        // 更新现有关键词
        existingKeyword.frequency += 1;
        existingKeyword[`platforms.${platform}`] += 1;
        existingKeyword.sentiment_avg = 
          (existingKeyword.sentiment_avg * (existingKeyword.frequency - 1) + sentiment) / 
          existingKeyword.frequency;
        existingKeyword.last_updated = new Date();
        await existingKeyword.save();
      } else {
        // 创建新关键词
        const newKeyword = new Keyword({
          word: keyword,
          frequency: 1,
          sentiment_avg: sentiment,
          platforms: { [platform]: 1 }
        });
        await newKeyword.save();
      }
    }
  } catch (error) {
    console.error('Error updating keyword stats:', error);
  }
}

// ============================================
// API 路由
// ============================================

/**
 * 获取仪表板数据
 */
app.get('/api/dashboard', async (req, res) => {
  try {
    const platformStats = await getPlatformStats();
    const topKeywords = await getTopKeywords(10);
    const topComments = await Comment.find()
      .sort({ likes: -1, createdAt: -1 })
      .limit(5)
      .lean();
    
    // 从缓存获取或计算时间序列数据
    let timeSeriesData = await redisClient.get('timeseries:24h');
    
    if (!timeSeriesData) {
      // 计算时间序列数据 (这是一个简化版本)
      timeSeriesData = generateTimeSeriesData();
      await redisClient.setEx('timeseries:24h', 3600, JSON.stringify(timeSeriesData));
    } else {
      timeSeriesData = JSON.parse(timeSeriesData);
    }
    
    res.json({
      platformStats,
      topKeywords,
      topComments,
      timeSeriesData
    });
  } catch (error) {
    console.error('Error in /api/dashboard:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * 添加新评论
 */
app.post('/api/comments', async (req, res) => {
  try {
    const { platform, content, author, likes, url } = req.body;
    
    // 提取关键词和分析情感
    const keywords = extractKeywords(content);
    const sentiment_score = analyzeSentiment(content);
    
    // 保存评论
    const comment = new Comment({
      platform,
      content,
      author,
      likes,
      sentiment_score,
      keywords,
      url
    });
    
    await comment.save();
    
    // 更新关键词统计
    await updateKeywordStats(keywords, sentiment_score, platform);
    
    // 广播给所有连接的客户端
    io.emit('new-comment', {
      comment: comment.toObject(),
      keywords,
      sentiment: sentiment_score
    });
    
    // 更新缓存的统计数据
    await redisClient.del('dashboard:stats');
    
    res.json({ success: true, comment });
  } catch (error) {
    console.error('Error adding comment:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * 获取特定关键词的评论
 */
app.get('/api/comments/keyword/:keyword', async (req, res) => {
  try {
    const { keyword } = req.params;
    const comments = await Comment.find({
      keywords: keyword
    }).sort({ createdAt: -1 }).limit(20);
    
    res.json(comments);
  } catch (error) {
    console.error('Error fetching comments:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * 获取情感分布
 */
app.get('/api/sentiment-distribution', async (req, res) => {
  try {
    const comments = await Comment.find();
    
    const distribution = {
      veryPositive: 0,    // 85-100
      positive: 0,        // 70-84
      neutral: 0,         // 55-69
      negative: 0,        // 35-54
      veryNegative: 0     // 0-34
    };
    
    for (const comment of comments) {
      const score = comment.sentiment_score;
      if (score >= 85) distribution.veryPositive++;
      else if (score >= 70) distribution.positive++;
      else if (score >= 55) distribution.neutral++;
      else if (score >= 35) distribution.negative++;
      else distribution.veryNegative++;
    }
    
    // 转换为百分比
    const total = comments.length;
    const result = {
      '非常积极': Math.round((distribution.veryPositive / total) * 100),
      '积极': Math.round((distribution.positive / total) * 100),
      '中立': Math.round((distribution.neutral / total) * 100),
      '消极': Math.round((distribution.negative / total) * 100),
      '非常消极': Math.round((distribution.veryNegative / total) * 100)
    };
    
    res.json(result);
  } catch (error) {
    console.error('Error calculating sentiment distribution:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * 获取趋势分析
 */
app.get('/api/trends', async (req, res) => {
  try {
    const keywords = await Keyword.find()
      .sort({ last_updated: -1 })
      .limit(20)
      .lean();
    
    res.json({
      keywords: keywords.map(k => ({
        word: k.word,
        trend: k.trend,
        frequencyChange: k.frequency,
        sentimentChange: k.sentiment_avg
      }))
    });
  } catch (error) {
    console.error('Error getting trends:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ============================================
// WebSocket 实时连接
// ============================================

io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);
  
  // 定期推送更新数据
  const updateInterval = setInterval(async () => {
    try {
      const platformStats = await getPlatformStats();
      const topKeywords = await getTopKeywords(10);
      
      socket.emit('data-update', {
        platformStats,
        topKeywords,
        timestamp: new Date()
      });
    } catch (error) {
      console.error('Error sending update:', error);
    }
  }, 3000); // 每3秒更新一次
  
  // 监听客户端请求
  socket.on('request-dashboard', async () => {
    try {
      const data = await redisClient.get('dashboard:stats');
      socket.emit('dashboard-data', data ? JSON.parse(data) : {});
    } catch (error) {
      console.error('Error getting dashboard data:', error);
    }
  });
  
  // 连接断开
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
    clearInterval(updateInterval);
  });
});

// ============================================
// 辅助函数
// ============================================

/**
 * 生成时间序列数据
 */
function generateTimeSeriesData() {
  const hours = [
    '00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:00'
  ];
  
  return hours.map(hour => ({
    time: hour,
    xiaohongshu: Math.floor(Math.random() * 50) + 10,
    weibo: Math.floor(Math.random() * 60) + 15,
    bilibili: Math.floor(Math.random() * 35) + 8
  }));
}

/**
 * 定期任务：清理旧数据
 */
setInterval(async () => {
  try {
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    await Comment.deleteMany({ createdAt: { $lt: thirtyDaysAgo } });
    console.log('Cleaned up old data');
  } catch (error) {
    console.error('Error cleaning up data:', error);
  }
}, 24 * 60 * 60 * 1000); // 每天执行一次

// ============================================
// 服务器启动
// ============================================

const PORT = process.env.PORT || 5000;

server.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`WebSocket server is ready on ws://localhost:${PORT}`);
});

// 优雅关闭
process.on('SIGINT', async () => {
  console.log('\nGracefully shutting down...');
  await mongoose.connection.close();
  await redisClient.quit();
  process.exit(0);
});
