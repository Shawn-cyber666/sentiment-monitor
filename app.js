const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
require('dotenv').config();
 
const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: { origin: "*" }
});
 
app.use(cors());
app.use(express.json());
 
// 模拟数据
const mockData = {
  xiaohongshu: { positive: 1245, neutral: 456, negative: 123, total: 1824 },
  weibo: { positive: 856, neutral: 345, negative: 89, total: 1290 },
  bilibili: { positive: 523, neutral: 234, negative: 45, total: 802 }
};
 
// API 路由
app.get('/', (req, res) => {
  res.json({ message: 'Sentiment Monitor API is running' });
});
 
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});
 
app.get('/api/dashboard', (req, res) => {
  res.json(mockData);
});
 
app.get('/api/comments', (req, res) => {
  res.json([
    { platform: '小红书', text: 'Vivo X300U 拍照效果绝了', sentiment: '正面', likes: 245 },
    { platform: '微博', text: '续航能力很给力', sentiment: '正面', likes: 189 },
    { platform: 'B站', text: '处理器性能稳定', sentiment: '正面', likes: 156 }
  ]);
});
 
app.get('/api/keywords', (req, res) => {
  res.json([
    { word: 'Vivo X300U', count: 245, sentiment: 8.5, trend: '+12%' },
    { word: '拍照效果', count: 189, sentiment: 8.2, trend: '+8%' },
    { word: '续航能力', count: 156, sentiment: 7.8, trend: '+5%' }
  ]);
});
 
// WebSocket
io.on('connection', (socket) => {
  console.log('Client connected');
  socket.emit('data', mockData);
  
  setInterval(() => {
    socket.emit('update', { timestamp: new Date() });
  }, 3000);
 
  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});
 
// 启动服务器
const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
});
 
module.exports = app;
 
