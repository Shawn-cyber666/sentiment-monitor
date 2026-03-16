import streamlit as st
import feedparser
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面基本配置
st.set_page_config(page_title="全网手机舆论情报站", layout="wide")

# 2. 侧边栏：搜索与配置
st.sidebar.header("🔍 监控配置")
search_keyword = st.sidebar.text_input("输入监控型号", "vivo X300 Ultra")
warning_threshold = st.sidebar.slider("预警阈值 (负面占比 %)", 0, 100, 25)

# 增强型负面词库
NEG_KEYWORDS = ['差', '烂', '贵', '断触', '发热', '卡顿', '失望', '缺陷', '退货', '避雷', '吐槽', '不值']

# 3. 数据处理逻辑
def fetch_data(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    # 使用 Google News RSS (Streamlit海外服务器可顺畅访问)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    feed = feedparser.parse(rss_url)
    
    data = []
    if not feed.entries:
        return pd.DataFrame()

    for entry in feed.entries[:40]:
        title = entry.title
        # 来源解析：通常在标题末尾的 " - 来源"
        source = "未知来源"
        clean_title = title
        if " - " in title:
            clean_title = title.rsplit(" - ", 1)[0]
            source = title.rsplit(" - ", 1)[1]

        # 情感判定
        is_neg = any(word in clean_title for word in NEG_KEYWORDS)
        sentiment = "负向" if is_neg or TextBlob(clean_title).sentiment.polarity < 0 else "正向"
        
        data.append({
            "情报标题": clean_title,
            "来源": source,
            "发布时间": entry.published,
            "访问原文": entry.link,
            "倾向": sentiment
        })
    return pd.DataFrame(data)

# 4. 主界面渲染
st.title(f"📱 {search_keyword} 全网情报追踪")

# --- 新增：国内平台快捷追踪 (解决小红书/微博实时访问) ---
st.subheader("🚀 国内平台一键直达")
encoded_q = urllib.parse.quote(search_keyword)
col_link1, col_link2, col_link3, col_link4 = st.columns(4)
with col_link1:
    st.markdown(f"[📕 小红书最新评价](https://www.xiaohongshu.com/search_result?keyword={encoded_q})")
with col_link2:
    st.markdown(f"[👁️ 微博实时动态](https://s.weibo.com/weibo?q={encoded_q})")
with col_link3:
    st.markdown(f"[🔍 百度资讯搜索](https://www.baidu.com/s?tn=news&word={encoded_q})")
with col_link4:
    st.markdown(f"[📦 知乎深度评测](https://www.zhihu.com/search?type=content&q={encoded_q})")

try:
    with st.spinner('正在调取全球情报源...'):
        df = fetch_data(search_keyword)

    if not df.empty:
        # 预警逻辑
        neg_percent = int((len(df[df["倾向"] == "负向"]) / len(df)) * 100)
        if neg_percent >= warning_threshold:
            st.error(f"🚨 预警：当前负面声量占比 {neg_percent}%，建议立即查看详情。")
        else:
            st.success(f"✅ 状态：当前口碑稳定，负面占比仅为 {neg_percent}%。")

        # 数据看板
        st.subheader("📰 实时动态列表")
        # 【关键更新】使用 LinkColumn 让原文链接可直接点击
        st.dataframe(
            df,
            column_config={
                "访问原文": st.column_config.LinkColumn("原文链接", display_text="点击跳转"),
                "发布时间": st.column_config.DatetimeColumn("发布时间", format="D MMM YYYY, h:mm a"),
            },
            hide_index=True,
            use_container_width=True
        )

        # 图表与词云
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("📊 情感构成图")
            st.bar_chart(df["倾向"].value_counts())
        
        with c2:
            st.subheader("☁️ 舆论关键词云")
            all_titles = " ".join(df["情报标题"].tolist())
            try:
                wordcloud = WordCloud(font_path='font.ttf', width=600, height=300, background_color="white").generate(all_titles)
                fig, ax = plt.subplots()
                ax.imshow(wordcloud)
                ax.axis("off")
                st.pyplot(fig)
            except:
                st.info("正在加载词云...")

    else:
        st.warning("暂无实时情报，请尝试缩短搜索词。")

except Exception as e:
    st.error(f"系统运行异常: {e}")

st.caption(f"数据更新于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
