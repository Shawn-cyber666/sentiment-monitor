import streamlit as st
import feedparser
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime

# 页面配置
st.set_page_config(page_title="vivo X300u 实时舆论监控", layout="wide")

st.title("📱 vivo X300 Ultra (X300u) 实时舆论大数据看板")
st.sidebar.info("数据来源：Google News RSS (实时更新)")

# 1. 数据抓取函数
def fetch_data(keyword):
    # 构建RSS搜索链接 (针对 vivo X300u)
    rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    feed = feedparser.parse(rss_url)
    
    data = []
    for entry in feed.entries[:20]:  # 取最新的20条
        # 简单情感分析 (0-1 之间)
        analysis = TextBlob(entry.title)
        sentiment = "正向" if analysis.sentiment.polarity >= 0 else "负向"
        
        data.append({
            "标题": entry.title,
            "发布时间": entry.published,
            "链接": entry.link,
            "情感倾向": sentiment
        })
    return pd.DataFrame(data)

# 2. 运行抓取
try:
    with st.spinner('正在同步全网舆论数据...'):
        df = fetch_data("vivo X300 Ultra")

    # 3. 布局布局
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🔥 最新舆论动态")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📊 情感分布")
        sentiment_count = df["情感倾向"].value_counts()
        st.bar_chart(sentiment_count)

    # 4. 词云展示
    st.divider()
    st.subheader("☁️ 舆论关键词云")
    all_titles = " ".join(df["标题"].tolist())
    
    # 针对中文环境的简单词云处理
    wordcloud = WordCloud(
        font_path=None, # 如果部署到Linux服务器需指定中文字体路径
        width=800, 
        height=400, 
        background_color="white"
    ).generate(all_titles)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

except Exception as e:
    st.error(f"暂时无法获取数据，请检查网络连接。错误: {e}")

st.caption(f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
