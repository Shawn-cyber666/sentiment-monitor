const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
 
const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });
 
app.use(cors());
app.use(express.json());
 
// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});
 
// Root
app.get('/', (req, res) => {
  res.json({ message: 'API is running' });
});
 
// API
app.get('/api/dashboard', (req, res) => {
  res.json({
    xiaohongshu: { positive: 1245, neutral: 456, negative: 123 },
    weibo: { positive: 856, neutral: 345, negative: 89 },
    bilibili: { positive: 523, neutral: 234, negative: 45 }
  });
});
 
// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
 
