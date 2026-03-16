import streamlit as st
import feedparser
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse  # 新增：用于处理URL编码

# 页面配置
st.set_page_config(page_title="vivo X300u 实时舆论监控", layout="wide")

st.title("📱 vivo X300 Ultra (X300u) 实时舆论大数据看板")
st.sidebar.info("数据来源：Google News RSS (实时更新)")

# 1. 数据抓取函数
def fetch_data(keyword):
    # 【核心修复】对关键词进行URL编码，将空格转为 %20
    encoded_keyword = urllib.parse.quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    
    data = []
    if not feed.entries:
        return pd.DataFrame()

    for entry in feed.entries[:20]:
        # 简单情感分析
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

    if not df.empty:
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
        
        # 4. 词云展示
        st.divider()
        st.subheader("☁️ 舆论关键词云")
        all_titles = " ".join(df["标题"].tolist())
        
        try:
            # 尝试加载自定义字体
            wordcloud = WordCloud(
                font_path='font.ttf', 
                width=800, 
                height=400, 
                background_color="white",
                collocations=False 
            ).generate(all_titles)

            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        except Exception as font_error:
            st.warning(f"词云字体加载失败，请确保仓库中有 font.ttf 文件。错误: {font_error}")

        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("未能抓取到相关数据，请尝试更换关键词或稍后再试。")

except Exception as e:
    st.error(f"发生错误: {e}")

st.caption(f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
