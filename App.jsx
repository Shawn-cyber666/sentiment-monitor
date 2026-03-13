import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import { TrendingUp, MessageSquare, Heart } from 'lucide-react'
import io from 'socket.io-client'

export default function App() {
  const [stats, setStats] = useState({
    xiaohongshu: { positive: 0, neutral: 0, negative: 0, total: 0 },
    weibo: { positive: 0, neutral: 0, negative: 0, total: 0 },
    bilibili: { positive: 0, neutral: 0, negative: 0, total: 0 }
  })

  const [keywords, setKeywords] = useState([
    { word: 'Vivo X300U', count: 245, sentiment: 8.5, trend: '+12%' },
    { word: '拍照效果', count: 189, sentiment: 8.2, trend: '+8%' },
    { word: '续航能力', count: 156, sentiment: 7.8, trend: '+5%' },
    { word: '处理器性能', count: 134, sentiment: 8.1, trend: '+10%' },
    { word: '屏幕显示', count: 98, sentiment: 7.9, trend: '+6%' }
  ])

  const trendData = [
    { time: '00:00', xiaohongshu: 45, weibo: 38, bilibili: 25 },
    { time: '04:00', xiaohongshu: 52, weibo: 42, bilibili: 28 },
    { time: '08:00', xiaohongshu: 68, weibo: 55, bilibili: 35 },
    { time: '12:00', xiaohongshu: 82, weibo: 68, bilibili: 45 },
    { time: '16:00', xiaohongshu: 76, weibo: 62, bilibili: 40 },
    { time: '20:00', xiaohongshu: 89, weibo: 72, bilibili: 50 },
    { time: '23:59', xiaohongshu: 95, weibo: 78, bilibili: 52 }
  ]

  const sentimentData = [
    { name: '正面', value: 45, fill: '#10b981' },
    { name: '中立', value: 35, fill: '#6b7280' },
    { name: '负面', value: 20, fill: '#ef4444' }
  ]

  const comments = [
    { platform: '小红书', text: 'Vivo X300U 的拍照效果真的绝了，白天清晰，夜景也很棒！', sentiment: '正面', likes: 245 },
    { platform: '微博', text: '续航能力很给力，一天用下来还有 15% 电量', sentiment: '正面', likes: 189 },
    { platform: 'B站', text: '处理器性能稳定，玩游戏没有卡顿', sentiment: '正面', likes: 156 }
  ]

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6">
      {/* 标题 */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Vivo X300U 舆论监测</h1>
        <p className="text-slate-400">实时监测小红书、微博、B站的用户评论和舆论动向</p>
      </div>

      {/* KPI 卡片 */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 mb-2">小红书评论</p>
              <p className="text-3xl font-bold">2,456</p>
            </div>
            <MessageSquare className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 mb-2">微博提及</p>
              <p className="text-3xl font-bold">1,823</p>
            </div>
            <TrendingUp className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 mb-2">B站视频</p>
              <p className="text-3xl font-bold">945</p>
            </div>
            <Heart className="w-12 h-12 text-red-500" />
          </div>
        </div>
      </div>

      {/* 关键词和图表 */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* 关键词 */}
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">热门关键词</h2>
          <div className="space-y-3">
            {keywords.map((kw, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="font-semibold">{kw.word}</p>
                  <p className="text-sm text-slate-400">提及 {kw.count} 次</p>
                </div>
                <div className="text-right">
                  <p className="text-green-400 font-bold">{kw.sentiment}</p>
                  <p className="text-xs text-slate-400">{kw.trend}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 情感分布 */}
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">整体情感分布</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={sentimentData} cx="50%" cy="50%" outerRadius={80} dataKey="value">
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 趋势图 */}
      <div className="bg-slate-800 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">24小时评论趋势</h2>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={trendData}>
            <defs>
              <linearGradient id="colorXiaohongshu" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="xiaohongshu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorXiaohongshu)" />
            <Area type="monotone" dataKey="weibo" stroke="#10b981" fillOpacity={0.3} />
            <Area type="monotone" dataKey="bilibili" stroke="#f59e0b" fillOpacity={0.3} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* 代表性评论 */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">代表性评论</h2>
        <div className="space-y-4">
          {comments.map((comment, idx) => (
            <div key={idx} className="border-l-4 border-green-500 pl-4 py-2">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-blue-400">{comment.platform}</span>
                <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">{comment.sentiment}</span>
              </div>
              <p className="text-slate-300 mb-2">{comment.text}</p>
              <p className="text-xs text-slate-500">👍 {comment.likes} 个赞</p>
            </div>
          ))}
        </div>
      </div>

      {/* 刷新提示 */}
      <div className="mt-8 text-center text-slate-400 text-sm">
        <p>数据每 3 秒自动更新一次</p>
        <p className="text-xs text-slate-500 mt-2">Vivo X300U Sentiment Monitor v1.0</p>
      </div>
    </div>
  )
}
