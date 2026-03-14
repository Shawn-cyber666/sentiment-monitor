# Vivo X300U 舆论监测系统

实时舆论监测仪表板，监控小红书、微博、B站的用户评论和舆论动向。

## 功能特性

- ✅ 实时数据仪表板
- ✅ WebSocket 实时更新
- ✅ MongoDB 数据存储
- ✅ REST API 接口
- ✅ 情感分析
- ✅ 热门关键词追踪
- ✅ 趋势图表

## 快速开始

### 本地开发

```bash
# 安装依赖
npm install

# 启动服务
npm start

# 开发模式（自动重启）
npm run dev
```

访问 http://localhost:3000

### 环境变量

创建 `.env` 文件：

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
NODE_ENV=production
PORT=3000
```

### Docker 部署

```bash
docker build -t sentiment-monitor .
docker run -p 3000:3000 -e MONGODB_URI=your_uri sentiment-monitor
```

## API 端点

- `GET /` - 获取 API 信息
- `GET /health` - 健康检查
- `GET /api/dashboard` - 仪表板数据
- `GET /api/comments` - 评论列表
- `GET /api/keywords` - 关键词列表
- `GET /api/trends` - 趋势数据
- `GET /api/sentiment-distribution` - 情感分布

## WebSocket 事件

- `dashboard` - 仪表板数据
- `comments` - 评论列表
- `keywords` - 关键词列表
- `trends` - 趋势数据
- `data_update` - 数据更新（每3秒）

## 技术栈

- Node.js 18
- Express 4.18
- Socket.io 4.7
- MongoDB 8.0
- Mongoose 8.0

## 部署

### Railway

1. 连接 GitHub 仓库
2. 设置环境变量 MONGODB_URI
3. 自动部署

## 许可证

MIT
