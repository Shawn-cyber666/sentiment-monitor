import streamlit as st
import feedparser
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面基本配置
st.set_page_config(page_title="全网手机舆论监控预警站", layout="wide")

# 2. 侧边栏：搜索与配置
st.sidebar.header("🔍 搜索配置")
search_keyword = st.sidebar.text_input("输入监控型号", "vivo X300 Ultra")
warning_threshold = st.sidebar.slider("预警阈值 (负面占比 %)", 0, 100, 30)
st.sidebar.info(f"正在监控: {search_keyword}")

# 简单的中文负面词库（增强预警准确性）
NEG_KEYWORDS = ['差', '烂', '贵', '断触', '发热', '卡顿', '失望', '缺陷', '退货', '避雷']

# 3. 数据处理逻辑
def fetch_data(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    feed = feedparser.parse(rss_url)
    
    data = []
    if not feed.entries:
        return pd.DataFrame()

    for entry in feed.entries[:30]: # 增加到30条数据
        title = entry.title
        # 情感判定逻辑：优先匹配负面词库，其次使用TextBlob
        is_neg = any(word in title for word in NEG_KEYWORDS)
        if is_neg:
            sentiment = "负向"
            score = -1
        else:
            # 兼容性处理
            analysis = TextBlob(title)
            sentiment = "正向" if analysis.sentiment.polarity >= 0 else "负向"
            score = 1 if sentiment == "正向" else -1
        
        data.append({
            "标题": title,
            "发布时间": entry.published,
            "链接": entry.link,
            "倾向": sentiment,
            "得分": score
        })
    return pd.DataFrame(data)

# 4. 主界面渲染
st.title(f"📊 {search_keyword} 舆论实时情报站")

try:
    with st.spinner('正在分析全网数据...'):
        df = fetch_data(search_keyword)

    if not df.empty:
        # --- 实时预警功能 ---
        neg_count = len(df[df["倾向"] == "负向"])
        total_count = len(df)
        neg_percent = int((neg_count / total_count) * 100)
        
        # 预警逻辑判断
        if neg_percent >= warning_threshold:
            st.error(f"🚨 舆论预警：{search_keyword} 当前负面舆论占比高达 {neg_percent}%！(超过预警线 {warning_threshold}%)")
        else:
            st.success(f"✅ 舆论平稳：{search_keyword} 当前负面占比为 {neg_percent}%，处于安全区间。")

        # 数据看板
        c1, c2, c3 = st.columns(3)
        c1.metric("监测条目", f"{total_count} 条")
        c2.metric("负面占比", f"{neg_percent}%")
        c3.metric("健康度评分", f"{100 - neg_percent}/100")

        # 数据分布图表
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.subheader("📝 最新情报列表")
            st.dataframe(df[["标题", "发布时间", "倾向"]], use_container_width=True)
        
        with col_right:
            st.subheader("📈 情感构成")
            st.bar_chart(df["倾向"].value_counts())

        # 词云展示
        st.divider()
        st.subheader("☁️ 实时舆论热词云")
        all_titles = " ".join(df["标题"].tolist())
        
        # 注意：请确保你已经按照之前的步骤上传了 font.ttf
        try:
            wordcloud = WordCloud(
                font_path='font.ttf', 
                width=1000, height=500, 
                background_color="white"
            ).generate(all_titles)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud)
            ax.axis("off")
            st.pyplot(fig)
        except:
            st.warning("词云加载中...（请确保已上传 font.ttf 字体文件）")

    else:
        st.warning("未找到相关数据，请尝试精简关键词（例如只搜索 'vivo X300'）。")

except Exception as e:
    st.error(f"系统运行异常: {e}")

st.caption(f"数据实时同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
