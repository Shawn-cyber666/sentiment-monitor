import React, { useState, useEffect } from 'react';
import { TrendingUp, MessageSquare, Heart, AlertCircle, BarChart3, Clock, Zap } from 'lucide-react';
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const SentimentMonitor = () => {
  // 平台数据
  const [platformStats] = useState({
    xiaohongshu: { name: '小红书', count: 2847, sentiment: 72, color: '#E6405E' },
    weibo: { name: '微博', count: 3621, sentiment: 68, color: '#EB6100' },
    bilibili: { name: 'B站', count: 1892, sentiment: 75, color: '#00B0F0' }
  });

  // 关键词数据 - 实时更新效果
  const [keywords, setKeywords] = useState([
    { word: '屏幕素质', frequency: 342, sentiment: 85, trend: 'up' },
    { word: '拍照能力', frequency: 298, sentiment: 79, trend: 'up' },
    { word: '续航能力', frequency: 267, sentiment: 62, trend: 'down' },
    { word: '散热控制', frequency: 245, sentiment: 58, trend: 'down' },
    { word: '系统流畅度', frequency: 201, sentiment: 76, trend: 'up' },
    { word: '价格性价比', frequency: 189, sentiment: 71, trend: 'neutral' },
    { word: '芯片性能', frequency: 156, sentiment: 81, trend: 'up' },
    { word: '做工质感', frequency: 142, sentiment: 83, trend: 'up' },
    { word: '信号质量', frequency: 128, sentiment: 65, trend: 'neutral' },
    { word: '屏幕刷新', frequency: 115, sentiment: 88, trend: 'up' }
  ]);

  const [timeData] = useState([
    { time: '00:00', xiaohongshu: 12, weibo: 18, bilibili: 8 },
    { time: '04:00', xiaohongshu: 8, weibo: 12, bilibili: 6 },
    { time: '08:00', xiaohongshu: 24, weibo: 31, bilibili: 18 },
    { time: '12:00', xiaohongshu: 42, weibo: 58, bilibili: 32 },
    { time: '16:00', xiaohongshu: 38, weibo: 52, bilibili: 28 },
    { time: '20:00', xiaohongshu: 45, weibo: 62, bilibili: 35 },
    { time: '23:00', xiaohongshu: 28, weibo: 38, bilibili: 20 }
  ]);

  const [sentimentDist] = useState([
    { name: '非常积极', value: 32, color: '#10B981' },
    { name: '积极', value: 40, color: '#34D399' },
    { name: '中立', value: 18, color: '#6B7280' },
    { name: '消极', value: 8, color: '#F59E0B' },
    { name: '非常消极', value: 2, color: '#EF4444' }
  ]);

  const [topComments] = useState([
    {
      id: 1,
      platform: '小红书',
      content: 'X300U的屏幕素质真的绝了，这块屏幕在同价位真的难找对手',
      likes: 1245,
      sentiment: 'positive',
      time: '2小时前'
    },
    {
      id: 2,
      platform: '微博',
      content: '续航确实是短板，一天得充两次电，其他方面还不错',
      likes: 892,
      sentiment: 'neutral',
      time: '3小时前'
    },
    {
      id: 3,
      platform: 'B站',
      content: '拍照能力超强，这次vivo在影像上真的下功夫了',
      likes: 2156,
      sentiment: 'positive',
      time: '1小时前'
    },
    {
      id: 4,
      platform: '微博',
      content: '散热有点问题，玩游戏手机温度有点高',
      likes: 567,
      sentiment: 'negative',
      time: '4小时前'
    },
    {
      id: 5,
      platform: 'B站',
      content: '系统优化做得很到位，日常使用没有卡顿',
      likes: 1834,
      sentiment: 'positive',
      time: '2小时前'
    }
  ]);

  const [updateTime, setUpdateTime] = useState(new Date());

  // 模拟实时更新
  useEffect(() => {
    const timer = setInterval(() => {
      setUpdateTime(new Date());
      setKeywords(prev => 
        prev.map(k => ({
          ...k,
          frequency: k.frequency + Math.floor(Math.random() * 5 - 1)
        }))
      );
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  const getSentimentColor = (sentiment) => {
    if (sentiment >= 80) return '#10B981';
    if (sentiment >= 70) return '#34D399';
    if (sentiment >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const TrendIcon = ({ trend }) => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (trend === 'down') return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />;
    return <div className="w-4 h-4" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">
      {/* 背景装饰 */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* 头部 */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-5xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
                Vivo X300U 舆论监测台
              </h1>
              <p className="text-slate-400 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                最后更新: {updateTime.toLocaleTimeString('zh-CN')}
              </p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500/50 rounded-lg">
              <Zap className="w-5 h-5 text-green-400" />
              <span className="text-sm">实时监控中</span>
            </div>
          </div>

          {/* KPI 卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(platformStats).map(([key, stat]) => (
              <div
                key={key}
                className="bg-gradient-to-br from-slate-800/60 to-slate-700/40 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm hover:border-slate-600/80 transition-all duration-300 group"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-lg">{stat.name}</h3>
                  <MessageSquare className="w-5 h-5 opacity-50 group-hover:opacity-100 transition-opacity" />
                </div>
                <div className="space-y-2">
                  <div>
                    <p className="text-slate-400 text-sm">评论总数</p>
                    <p className="text-3xl font-bold text-blue-400">{stat.count.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">情感评分</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-700/50 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-green-400 to-blue-400"
                          style={{ width: `${stat.sentiment}%` }}
                        ></div>
                      </div>
                      <span className="text-2xl font-bold" style={{ color: getSentimentColor(stat.sentiment) }}>
                        {stat.sentiment}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 主要内容区 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* 关键词云 */}
          <div className="lg:col-span-1">
            <div className="bg-gradient-to-br from-slate-800/60 to-slate-700/40 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm h-full">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-400" />
                高频关键词
              </h2>
              <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                {keywords.map((kw, idx) => (
                  <div
                    key={idx}
                    className="group cursor-pointer bg-slate-700/30 hover:bg-slate-700/50 rounded-lg p-3 transition-colors duration-200"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className="font-semibold text-blue-300 group-hover:text-blue-200">{kw.word}</p>
                        <p className="text-xs text-slate-400">提及: {kw.frequency}次</p>
                      </div>
                      <TrendIcon trend={kw.trend} />
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-600/50 rounded-full h-1.5">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${kw.sentiment}%`,
                            background: getSentimentColor(kw.sentiment)
                          }}
                        ></div>
                      </div>
                      <span className="text-xs font-semibold" style={{ color: getSentimentColor(kw.sentiment) }}>
                        {kw.sentiment}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 时间趋势 */}
          <div className="lg:col-span-2">
            <div className="bg-gradient-to-br from-slate-800/60 to-slate-700/40 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                24小时评论趋势
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={timeData}>
                  <defs>
                    <linearGradient id="colorXiaohongshu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#E6405E" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#E6405E" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorWeibo" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EB6100" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#EB6100" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorBilibili" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00B0F0" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#00B0F0" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                  <XAxis dataKey="time" stroke="rgba(148,163,184,0.5)" />
                  <YAxis stroke="rgba(148,163,184,0.5)" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15,23,42,0.95)',
                      border: '1px solid rgba(148,163,184,0.3)',
                      borderRadius: '8px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="xiaohongshu"
                    stroke="#E6405E"
                    fillOpacity={1}
                    fill="url(#colorXiaohongshu)"
                    name="小红书"
                  />
                  <Area
                    type="monotone"
                    dataKey="weibo"
                    stroke="#EB6100"
                    fillOpacity={1}
                    fill="url(#colorWeibo)"
                    name="微博"
                  />
                  <Area
                    type="monotone"
                    dataKey="bilibili"
                    stroke="#00B0F0"
                    fillOpacity={1}
                    fill="url(#colorBilibili)"
                    name="B站"
                  />
                  <Legend />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* 底部两列 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 情感分布 */}
          <div className="bg-gradient-to-br from-slate-800/60 to-slate-700/40 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Heart className="w-5 h-5 text-red-400" />
              情感分布
            </h2>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={sentimentDist}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name} ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(15,23,42,0.95)',
                    border: '1px solid rgba(148,163,184,0.3)',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 高赞评论 */}
          <div className="bg-gradient-to-br from-slate-800/60 to-slate-700/40 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-blue-400" />
              代表评论
            </h2>
            <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
              {topComments.map(comment => (
                <div
                  key={comment.id}
                  className="bg-slate-700/30 hover:bg-slate-700/50 rounded-lg p-3 transition-colors duration-200 border-l-2"
                  style={{
                    borderColor:
                      comment.sentiment === 'positive'
                        ? '#10B981'
                        : comment.sentiment === 'negative'
                        ? '#EF4444'
                        : '#F59E0B'
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-xs px-2 py-1 rounded bg-slate-600/50 text-slate-300">
                      {comment.platform}
                    </span>
                    <span className="text-xs text-slate-400">{comment.time}</span>
                  </div>
                  <p className="text-sm text-slate-200 mb-2 line-clamp-2">{comment.content}</p>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Heart className="w-3 h-3" />
                    <span>{comment.likes.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentMonitor;
