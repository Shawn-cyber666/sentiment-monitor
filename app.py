import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面配置
st.set_page_config(page_title="vivo 深度舆情监测系统", layout="wide")

# 2. 侧边栏配置
st.sidebar.header("🎯 监控配置")
search_keyword = st.sidebar.text_input("目标型号", "vivo X300 Ultra")
warning_val = st.sidebar.slider("预警阈值 (%)", 0, 100, 25)

# 智能语义库
NEG_WORDS = ['差', '烂', '断触', '发热', '烫', '卡顿', '死机', '黑屏', '后悔', '避雷', '吐槽', '不值', '智商税', '割韭菜', '翻车', '故障', '信号差']
EXCLUDE_WORDS = ['差别', '差不多', '差旅', '出差', '价差', '偏差']

# 3. 核心算法：语义识别与数据抓取
def smart_analyze(text):
    text = text.lower()
    # 排除逻辑：包含排除词则不算负面
    if any(ex in text for ex in EXCLUDE_WORDS):
        return "正向"
    # 命中逻辑
    if any(neg in text for neg in NEG_WORDS):
        return "负向"
    return "正向"

def fetch_data(keyword):
    # 组合搜索：增加"缺点"等后缀来穿透公关稿
    search_query = f"{keyword} (缺点 OR 吐槽 OR 真实评价 OR 测评)"
    encoded_q = urllib.parse.quote(search_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    data = []
    
    if not feed.entries:
        return pd.DataFrame()

    for entry in feed.entries[:50]:
        full_title = entry.title
        source = full_title.rsplit(" - ", 1)[1] if " - " in full_title else "媒体"
        clean_title = full_title.rsplit(" - ", 1)[0] if " - " in full_title else full_title
        
        sentiment = smart_analyze(clean_title)
        
        data.append({
            "级别": "🔴 预警" if sentiment == "负向" else "🟢 正常",
            "情报标题": clean_title,
            "媒体来源": source,
            "发布时间": entry.published,
            "原文链接": entry.link,
            "倾向": sentiment
        })
    return pd.DataFrame(data)

# 4. 主界面渲染
st.title(f"📱 {search_keyword} 实时全网情报站")

# 国内平台一键直达 (修正版链接)
q_code = urllib.parse.quote(search_keyword)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"[📱 酷安搜索](https://www.coolapk.com/search?q={q_code})")
c2.markdown(f"[💬 贴吧讨论](https://tieba.baidu.com/f/search/res?qw={q_code})")
c3.markdown(f"[📕 小红书槽点](https://www.xiaohongshu.com/search_result?keyword={q_code}%20缺点)")
c4.markdown(f"[🎞️ B站避雷](https://search.bilibili.com/all?keyword={q_code}%20避雷)")

try:
    with st.spinner('正在同步国内各平台舆论...'):
        df = fetch_data(search_keyword)

    if not df.empty:
        # 数据统计
        neg_df = df[df["倾向"] == "负向"]
        neg_percent = int((len(neg_df) / len(df)) * 100)

        # 预警条
        if neg_percent >= warning_val:
            st.error(f"🚨 预警：负面声量占比 ({neg_percent}%) 已超过设定阈值！")
        else:
            st.success(f"✅ 口碑状态：良好 (负面占比 {neg_percent}%)")

        # 数据看板
        k1, k2, k3 = st.columns(3)
        k1.metric("样本总数", f"{len(df)} 篇")
        k2.metric("负面情报", f"{len(neg_df)} 篇")
        k3.metric("实时口碑", f"{100 - neg_percent} 分")

        # 情报流表格 (找回跳转功能)
        st.subheader("📋 实时情报流")
        st.dataframe(
            df,
            column_config={"原文链接": st.column_config.LinkColumn("直达", display_text="🔗")},
            hide_index=True, use_container_width=True
        )

        # 词云可视化 (找回双词云)
        st.divider()
        cw1, cw2 = st.columns(2)
        
        with cw1:
            st.subheader("🔵 全网讨论热词")
            all_txt = " ".join(df["情报标题"].tolist())
            if all_txt:
                try:
                    wc1 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Blues').generate(all_txt)
                    fig1, ax1 = plt.subplots()
                    ax1.imshow(wc1)
                    ax1.axis("off")
                    st.pyplot(fig1)
                except: st.warning("请确保 font.ttf 字体文件已上传")

        with cw2:
            st.subheader("🔴 核心痛点词云")
            if not neg_df.empty:
                neg_txt = " ".join(neg_df["情报标题"].tolist())
                # 过滤掉型号干扰词
                for w in [search_keyword, 'vivo', 'x300', 'ultra']:
                    neg_txt = neg_txt.lower().replace(w.lower(), "")
                
                try:
                    wc2 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Reds').generate(neg_txt)
                    fig2, ax2 = plt.subplots()
                    ax2.imshow(wc2)
                    ax2.axis("off")
                    st.pyplot(fig2)
                except: st.info("字体加载中...")
            else:
                st.write("暂无明显负面关键词")

    else:
        st.warning("暂未发现有效情报，请检查搜索词。")

except Exception as e:
    st.error(f"连接异常，请尝试刷新页面。错误详情: {e}")

st.caption(f"最后同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
