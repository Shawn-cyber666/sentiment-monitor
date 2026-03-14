const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
require('dotenv').config();

// ==================== 初始化 ====================
const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
    credentials: true
  }
});

// ==================== 中间件 ====================
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// ==================== MongoDB 连接 ====================
const connectDB = async () => {
  try {
    const mongoUri = process.env.MONGODB_URI;
    
    if (!mongoUri) {
      throw new Error('MONGODB_URI environment variable is not set');
    }

    await mongoose.connect(mongoUri, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      connectTimeoutMS: 10000,
      socketTimeoutMS: 45000,
    });

    console.log('✅ MongoDB connected successfully');
    return true;
  } catch (error) {
    console.error('❌ MongoDB connection error:', error.message);
    // 如果数据库连接失败，继续运行（使用模拟数据）
    console.log('⚠️  Continuing with mock data mode');
    return false;
  }
};

// ==================== 数据库模型 ====================
const commentSchema = new mongoose.Schema({
  platform: { type: String, required: true },
  text: { type: String, required: true },
  sentiment: { type: String, enum: ['正面', '中立', '负面'] },
  likes: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

const keywordSchema = new mongoose.Schema({
  word: { type: String, required: true },
  count: { type: Number, default: 0 },
  sentiment: { type: Number, default: 0 },
  trend: String,
  createdAt: { type: Date, default: Date.now }
});

let Comment, Keyword;
let dbConnected = false;

// ==================== 模拟数据 ====================
const mockComments = [
  { platform: '小红书', text: 'Vivo X300U 的拍照效果真的绝了，白天清晰，夜景也很棒！', sentiment: '正面', likes: 245 },
  { platform: '微博', text: '续航能力很给力，一天用下来还有 15% 电量', sentiment: '正面', likes: 189 },
  { platform: 'B站', text: '处理器性能稳定，玩游戏没有卡顿', sentiment: '正面', likes: 156 },
  { platform: '小红书', text: '屏幕显示效果一流，色彩还原度高', sentiment: '正面', likes: 123 },
  { platform: '微博', text: '价格有点贵，但配置确实不错', sentiment: '中立', likes: 89 }
];

const mockKeywords = [
  { word: 'Vivo X300U', count: 245, sentiment: 8.5, trend: '+12%' },
  { word: '拍照效果', count: 189, sentiment: 8.2, trend: '+8%' },
  { word: '续航能力', count: 156, sentiment: 7.8, trend: '+5%' },
  { word: '处理器性能', count: 134, sentiment: 8.1, trend: '+10%' },
  { word: '屏幕显示', count: 98, sentiment: 7.9, trend: '+6%' }
];

const mockTrends = [
  { time: '00:00', xiaohongshu: 45, weibo: 38, bilibili: 25 },
  { time: '04:00', xiaohongshu: 52, weibo: 42, bilibili: 28 },
  { time: '08:00', xiaohongshu: 68, weibo: 55, bilibili: 35 },
  { time: '12:00', xiaohongshu: 82, weibo: 68, bilibili: 45 },
  { time: '16:00', xiaohongshu: 76, weibo: 62, bilibili: 40 },
  { time: '20:00', xiaohongshu: 89, weibo: 72, bilibili: 50 },
  { time: '23:59', xiaohongshu: 95, weibo: 78, bilibili: 52 }
];

// ==================== REST API 路由 ====================

// 健康检查
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'Server is running',
    dbConnected: dbConnected
  });
});

// 首页
app.get('/', (req, res) => {
  res.json({ 
    message: 'Vivo X300U Sentiment Monitor API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      dashboard: '/api/dashboard',
      comments: '/api/comments',
      keywords: '/api/keywords',
      trends: '/api/trends',
      sentiment: '/api/sentiment-distribution'
    }
  });
});

// 仪表板数据
app.get('/api/dashboard', (req, res) => {
  try {
    res.json({
      xiaohongshu: { positive: 1245, neutral: 456, negative: 123, total: 1824 },
      weibo: { positive: 856, neutral: 345, negative: 89, total: 1290 },
      bilibili: { positive: 523, neutral: 234, negative: 45, total: 802 },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 评论列表
app.get('/api/comments', async (req, res) => {
  try {
    if (dbConnected && Comment) {
      const comments = await Comment.find().limit(10);
      res.json(comments.length > 0 ? comments : mockComments);
    } else {
      res.json(mockComments);
    }
  } catch (error) {
    console.error('Error fetching comments:', error);
    res.json(mockComments);
  }
});

// 关键词列表
app.get('/api/keywords', async (req, res) => {
  try {
    if (dbConnected && Keyword) {
      const keywords = await Keyword.find().limit(5);
      res.json(keywords.length > 0 ? keywords : mockKeywords);
    } else {
      res.json(mockKeywords);
    }
  } catch (error) {
    console.error('Error fetching keywords:', error);
    res.json(mockKeywords);
  }
});

// 趋势数据
app.get('/api/trends', (req, res) => {
  try {
    res.json(mockTrends);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 情感分布
app.get('/api/sentiment-distribution', (req, res) => {
  try {
    res.json([
      { name: '正面', value: 45, fill: '#10b981' },
      { name: '中立', value: 35, fill: '#6b7280' },
      { name: '负面', value: 20, fill: '#ef4444' }
    ]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== WebSocket 事件 ====================
io.on('connection', (socket) => {
  console.log(`✅ Client connected: ${socket.id}`);

  // 发送初始数据
  socket.emit('dashboard', {
    xiaohongshu: { positive: 1245, neutral: 456, negative: 123, total: 1824 },
    weibo: { positive: 856, neutral: 345, negative: 89, total: 1290 },
    bilibili: { positive: 523, neutral: 234, negative: 45, total: 802 }
  });

  socket.emit('comments', mockComments);
  socket.emit('keywords', mockKeywords);
  socket.emit('trends', mockTrends);

  // 每3秒推送一次数据更新
  const updateInterval = setInterval(() => {
    socket.emit('data_update', {
      timestamp: new Date().toISOString(),
      dashboard: {
        xiaohongshu: { positive: Math.floor(Math.random() * 2000), neutral: Math.floor(Math.random() * 500), negative: Math.floor(Math.random() * 200) },
        weibo: { positive: Math.floor(Math.random() * 1000), neutral: Math.floor(Math.random() * 400), negative: Math.floor(Math.random() * 150) },
        bilibili: { positive: Math.floor(Math.random() * 800), neutral: Math.floor(Math.random() * 300), negative: Math.floor(Math.random() * 100) }
      }
    });
  }, 3000);

  socket.on('disconnect', () => {
    console.log(`❌ Client disconnected: ${socket.id}`);
    clearInterval(updateInterval);
  });

  socket.on('error', (error) => {
    console.error(`Socket error: ${error}`);
  });
});

// ==================== 错误处理 ====================
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

// ==================== 启动服务器 ====================
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

const start = async () => {
  try {
    // 连接数据库
    dbConnected = await connectDB();
    
    // 如果连接成功，初始化模型
    if (dbConnected) {
      Comment = mongoose.model('Comment', commentSchema);
      Keyword = mongoose.model('Keyword', keywordSchema);
    }

    // 启动服务器
    httpServer.listen(PORT, () => {
      console.log(`\n${'='.repeat(50)}`);
      console.log(`🚀 Server started successfully!`);
      console.log(`Environment: ${NODE_ENV}`);
      console.log(`Port: ${PORT}`);
      console.log(`Database: ${dbConnected ? '✅ Connected' : '⚠️  Using Mock Data'}`);
      console.log(`Visit: http://localhost:${PORT}`);
      console.log(`${'='.repeat(50)}\n`);
    });

    // 优雅关闭
    process.on('SIGTERM', () => {
      console.log('SIGTERM signal received: closing HTTP server');
      httpServer.close(() => {
        console.log('HTTP server closed');
        if (dbConnected) {
          mongoose.disconnect();
        }
        process.exit(0);
      });
    });

  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

start();

module.exports = { app, io };
