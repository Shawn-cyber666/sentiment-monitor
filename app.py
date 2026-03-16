import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse
import collections

# 1. 页面配置：黑色科技感主题
st.set_page_config(page_title="vivo 旗舰舆情战略指挥中心", layout="wide")

# 2. 侧边栏：机型与深度配置
st.sidebar.header("🕹️ 监控指挥台")
target_model = st.sidebar.selectbox(
    "核心监控目标", 
    ["vivo X300 Ultra", "vivo X300s", "小米 17 Ultra", "OPPO Find X8 Ultra", "荣耀 Magic 8 至臻版"]
)
warning_level = st.sidebar.slider("预警敏感度", 10, 50, 20)

# 定义核心监控雷点 (这些词会直接触发红色预警)
CORE_PAIN_POINTS = ['828', 'jn1', '超广角', '没升级', '旧款', '阉割', '缩水', '发热', '太贵', '背刺']
NEG_WORDS = CORE_PAIN_POINTS + ['差', '烂', '断触', '后悔', '避雷', '吐槽', '失望']

# 3. 智能数据引擎：多源抓取并聚合
def fetch_strategic_data(keyword):
    # 构造两个搜索任务：一个搜全网资讯，一个搜深度槽点
    queries = [
        f"{keyword}", # 基础流量
        f"{keyword} (缺点 OR 遗憾 OR 吐槽 OR 相比前代)" # 深度负面穿透
    ]
    
    all_data = []
    seen_titles = set()

    for q in queries:
        encoded_q = urllib.parse.quote(q)
        rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:40]:
            if entry.title in seen_titles: continue
            seen_titles.add(entry.title)
            
            title = entry.title.split(" - ")[0]
            source = entry.title.split(" - ")[1] if " - " in entry.title else "全网搜索"
            
            # 智能识别负面标签
            found_pains = [p for p in CORE_PAIN_POINTS if p in title.lower()]
            sentiment = "负向" if found_pains or any(n in title.lower() for n in NEG_WORDS) else "正向"
            
            all_data.append({
                "级别": "🔴 预警" if sentiment == "负向" else "🟢 稳健",
                "情报标题": title,
                "来源": source,
                "痛点标签": " / ".join(found_pains) if found_pains else "无",
                "倾向": sentiment,
                "链接": entry.link,
                "时间": entry.published
            })
    return pd.DataFrame(all_data)

# 4. 看板主体
st.title(f"📡 {target_model} 实时舆情战略看板")
st.markdown(f"**数据更新至：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}** | 监控范围：全网媒体 + 社交平台 UGC")

try:
    with st.spinner('正在分析全球情报源并提炼核心痛点...'):
        df = fetch_strategic_data(target_model)

    if not df.empty:
        neg_df = df[df["倾向"] == "负向"]
        neg_percent = int((len(neg_df) / len(df)) * 100)

        # 第一行：核心指标
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("监测样本量", f"{len(df)} 篇")
        c2.metric("负面声量占比", f"{neg_percent}%", delta="重点关注" if neg_percent > warning_level else "正常")
        c3.metric("口碑健康度", f"{100 - neg_percent}/100")
        c4.metric("关键痛点捕获", f"{len(neg_df)} 条")

        # 第二行：多平台直达链接（优化排版）
        st.write("---")
        l1, l2, l3, l4 = st.columns(4)
        q_code = urllib.parse.quote(target_model)
        l1.link_button("👁️ 微博实时搜索", f"https://s.weibo.com/weibo?q={q_code}")
        l2.link_button("💬 贴吧深度反馈", f"https://tieba.baidu.com/f/search/res?qw={q_code}")
        l3.link_button("📕 小红书参数吐槽", f"https://www.xiaohongshu.com/search_result?keyword={q_code}%20吐槽")
        l4.link_button("🎞️ B站避雷评测", f"https://search.bilibili.com/all?keyword={q_code}%20避雷")

        # 第三行：核心情报列表
        st.subheader("📑 核心情报分析流")
        st.dataframe(
            df,
            column_config={
                "级别": st.column_config.TextColumn("状态", width="small"),
                "情报标题": st.column_config.TextColumn("内容摘要", width="large"),
                "痛点标签": st.column_config.TextColumn("捕获痛点", width="medium"),
                "链接": st.column_config.LinkColumn("原文", display_text="🔗")
            },
            hide_index=True, use_container_width=True
        )

        # 第四行：可视化分析
        st.divider()
        v1, v2 = st.columns([1, 1])
        
        with v1:
            st.subheader("🔵 全网舆论热词")
            all_text = " ".join(df["情报标题"].tolist())
            wc1 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Blues').generate(all_text)
            fig1, ax1 = plt.subplots(); ax1.imshow(wc1); ax1.axis("off"); st.pyplot(fig1)

        with v2:
            st.subheader("🔴 核心槽点提炼 (无需点开链接)")
            if not neg_df.empty:
                # 统计痛点标签的频率
                pain_list = []
                for row in neg_df["痛点标签"]:
                    if row != "无": pain_list.extend(row.split(" / "))
                
                if pain_list:
                    # 如果有具体标签，做个精美的条形图
                    pain_counts = pd.Series(pain_list).value_counts()
                    st.bar_chart(pain_counts, color="#FF4B4B")
                
                # 负面词云
                neg_text = " ".join(neg_df["情报标题"].tolist())
                for w in [target_model, 'vivo', 'x300', 'ultra', '小米', 'oppo']:
                    neg_text = neg_text.lower().replace(w.lower(), "")
                wc2 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Reds').generate(neg_text)
                fig2, ax2 = plt.subplots(); ax2.imshow(wc2); ax2.axis("off"); st.pyplot(fig2)
            else:
                st.success("✨ 当前全网舆论平稳，暂无显著槽点。")

    else:
        st.error("无法调取实时数据，请确认网络连接或稍后再试。")

except Exception as e:
    st.error(f"分析引擎故障: {e}")
