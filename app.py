import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面配置：更专业的战略看板风格
st.set_page_config(page_title="vivo 手机国内舆情监测站", layout="wide")

# 2. 侧边栏：精准关键词配置
st.sidebar.header("🔍 国内舆情监控设置")
search_keyword = st.sidebar.text_input("监控型号", "vivo X300 Ultra")

# 针对国内手机圈深度定制的负面词库
NEG_KEYWORDS = [
    '差', '烂', '断触', '发热', '烫', '卡顿', '死机', '黑屏', '偏色', '进灰',
    '失望', '退货', '后悔', '避雷', '吐槽', '不值', '智商税', '割韭菜', '翻车',
    '不如', '输给', '吊打', '被虐', '降价', '背刺', '虚标', '造假', '虚假宣传',
    '缺少', '阉割', '缩水', '遗憾', '难受', '溢价', '太贵', '信号差', '续航崩',
    '塑料', '手感差', '拍照糊', '抹抹感', '算法垃圾', '马达弱'
]

# 3. 国内数据引擎 (优化搜索参数，强制指向中文资讯)
def fetch_domestic_data(keyword):
    # 使用针对中国区优化的搜索协议
    encoded_keyword = urllib.parse.quote(keyword)
    # 强制搜索中文资讯流
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}+when:7d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    data = []
    
    if not feed.entries:
        return pd.DataFrame()

    for entry in feed.entries[:60]: # 增加采样深度到60条
        title = entry.title
        # 精准拆分来源（国内媒体通常在标题末尾）
        source = "国内媒体"
        clean_title = title
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            clean_title = parts[0]
            source = parts[1]

        # 情感判定：硬核匹配关键词
        sentiment = "正向"
        for neg_word in NEG_KEYWORDS:
            if neg_word in clean_title:
                sentiment = "负向"
                break
        
        data.append({
            "级别": "🔴 预警" if sentiment == "负向" else "🟢 稳健",
            "情报标题": clean_title,
            "媒体来源": source,
            "发布时间": entry.published,
            "链接": entry.link,
            "倾向": sentiment
        })
    return pd.DataFrame(data)

# 4. 界面渲染
st.title(f"🇨🇳 {search_keyword} 国内实时舆情看板")
st.info("说明：本系统直接追踪国内主流科技媒体（IT之家、中关村在线、太平洋电脑等）的实时报道。")

# 国内平台一键深入追踪
encoded_q = urllib.parse.quote(search_keyword)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"[📕 小红书实时槽点](https://www.xiaohongshu.com/search_result?keyword={encoded_q}%20吐槽)")
c2.markdown(f"[👁️ 微博博主评价](https://s.weibo.com/weibo?q={encoded_q})")
c3.markdown(f"[📰 百度实时资讯](https://www.baidu.com/s?tn=news&word={encoded_q})")
c4.markdown(f"[💬 酷安社区讨论](https://www.coolapk.com/search?q={encoded_q})")

try:
    with st.spinner('正在调取国内媒体数据库...'):
        df = fetch_domestic_data(search_keyword)

    if not df.empty:
        # 核心数据统计
        neg_df = df[df["倾向"] == "负向"]
        neg_percent = int((len(neg_df) / len(df)) * 100)

        # 决策指标看板
        m1, m2, m3 = st.columns(3)
        m1.metric("国内情报总量", f"{len(df)} 篇")
        m2.metric("负面声量占比", f"{neg_percent}%", delta=f"{len(neg_df)} 条", delta_color="inverse")
        m3.metric("市场信心指数", f"{100 - neg_percent}")

        # 实时情报表
        st.subheader("📋 最新情报动态流")
        st.dataframe(
            df,
            column_config={"链接": st.column_config.LinkColumn("原文跳转", display_text="🔗")},
            hide_index=True, use_container_width=True
        )

        # 词云可视化
        st.divider()
        col_wc1, col_wc2 = st.columns(2)
        
        with col_wc1:
            st.subheader("🔵 全网高频词")
            all_text = " ".join(df["情报标题"].tolist())
            if all_text:
                wc = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='winter').generate(all_text)
                fig1, ax1 = plt.subplots()
                ax1.imshow(wc)
                ax1.axis("off")
                st.pyplot(fig1)

        with col_wc2:
            st.subheader("🔴 核心槽点分布")
            if not neg_df.empty:
                neg_text = " ".join(neg_df["情报标题"].tolist())
                wc_neg = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Reds').generate(neg_text)
                fig2, ax2 = plt.subplots()
                ax2.imshow(wc_neg)
                ax2.axis("off")
                st.pyplot(fig2)
            else:
                st.write("目前暂无集中负面槽点。")

    else:
        st.warning("未检测到国内相关新闻报道，请简化关键词。")

except Exception as e:
    st.error(f"数据连接中断: {e}")

st.caption(f"监测周期：过去7天 | 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
