import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面配置
st.set_page_config(page_title="vivo 舆情监控 & 决策看板", layout="wide")

# 2. 侧边栏
st.sidebar.header("🎯 战略搜索配置")
search_keyword = st.sidebar.text_input("输入监控型号", "vivo X300 Ultra")

# 极致中文负面词库 (包含手机行业黑话)
NEG_KEYWORDS = [
    '差', '烂', '断触', '发热', '烫', '卡顿', '死机', '黑屏', '偏色', '进灰',
    '失望', '退货', '后悔', '避雷', '吐槽', '不值', '智商税', '割韭菜', '翻车',
    '不如', '输给', '吊打', '被虐', '降价', '背刺', '虚标', '造假', '虚假宣传',
    '缺少', '阉割', '缩水', '遗憾', '难受', '溢价', '太贵', '信号差', '续航崩'
]

# 3. 核心逻辑
def analyze_sentiment(title):
    # 只要命中任何一个负面关键词，就判定为负面
    for word in NEG_KEYWORDS:
        if word in title.lower(): # 转小写匹配
            return "负向"
    return "正向"

def fetch_data(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    # 扩大搜索范围
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    feed = feedparser.parse(rss_url)
    
    data = []
    if not feed.entries:
        return pd.DataFrame()

    for entry in feed.entries[:50]:
        title = entry.title
        source = title.rsplit(" - ", 1)[1] if " - " in title else "未知来源"
        clean_title = title.rsplit(" - ", 1)[0] if " - " in title else title
        
        sentiment = analyze_sentiment(clean_title)
        
        data.append({
            "级别": "🔴 警告" if sentiment == "负向" else "🟢 正常",
            "情报标题": clean_title,
            "来源": source,
            "发布时间": entry.published,
            "链接": entry.link,
            "倾向": sentiment
        })
    return pd.DataFrame(data)

# 4. 主界面布局
st.title(f"📊 {search_keyword} 实时监测站")

# 国内平台一键直达
encoded_q = urllib.parse.quote(search_keyword)
cols = st.columns(4)
cols[0].markdown(f"[📕 小红书吐槽](https://www.xiaohongshu.com/search_result?keyword={encoded_q}%20吐槽)")
cols[1].markdown(f"[👁️ 微博搜索](https://s.weibo.com/weibo?q={encoded_q})")
cols[2].markdown(f"[🔍 百度资讯](https://www.baidu.com/s?tn=news&word={encoded_q})")
cols[3].markdown(f"[📦 知乎评价](https://www.zhihu.com/search?q={encoded_q}%20评价)")

try:
    with st.spinner('数据同步中...'):
        df = fetch_data(search_keyword)

    if not df.empty:
        # 统计
        neg_df = df[df["倾向"] == "负向"]
        neg_percent = int((len(neg_df) / len(df)) * 100)

        # 头部指标
        m1, m2, m3 = st.columns(3)
        m1.metric("总样本量", f"{len(df)} 篇")
        m2.metric("负面占比", f"{neg_percent}%", delta_color="inverse")
        m3.metric("口碑分", f"{100 - neg_percent}")

        # 实时动态流 (加回了链接)
        st.subheader("📋 实时情报流")
        st.dataframe(
            df,
            column_config={"链接": st.column_config.LinkColumn("原文链接", display_text="点击跳转")},
            hide_index=True, use_container_width=True
        )

        # --- 重点：找回词云部分 ---
        st.divider()
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.subheader("🌊 全量舆论热词")
            all_text = " ".join(df["情报标题"].tolist())
            if all_text.strip():
                try:
                    wc_all = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Blues').generate(all_text)
                    fig1, ax1 = plt.subplots()
                    ax1.imshow(wc_all)
                    ax1.axis("off")
                    st.pyplot(fig1)
                except: st.info("请确保 font.ttf 已上传")

        with col_c2:
            st.subheader("🔥 负面预警词云")
            if not neg_df.empty:
                neg_text = " ".join(neg_df["情报标题"].tolist())
                try:
                    wc_neg = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='autumn').generate(neg_text)
                    fig2, ax2 = plt.subplots()
                    ax2.imshow(wc_neg)
                    ax2.axis("off")
                    st.pyplot(fig2)
                except: st.info("等待负面数据...")
            else:
                st.write("目前暂无负面词云（口碑良好）")

    else:
        st.warning("未检索到数据，请尝试更换关键词。")

except Exception as e:
    st.error(f"出错啦: {e}")

st.caption(f"更新时间: {datetime.now().strftime('%H:%M:%S')}")
