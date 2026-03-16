import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面配置
st.set_page_config(page_title="vivo 参数口碑预研系统", layout="wide")

# 2. 侧边栏：机型库
st.sidebar.header("🎯 2026 旗舰舆情监控")
target_model = st.sidebar.selectbox(
    "选择监控型号", 
    ["vivo X300 Ultra", "vivo X300s", "小米 17 Ultra", "OPPO Find X8 Ultra", "荣耀 Magic 8 至臻版"]
)
search_keyword = st.sidebar.text_input("或自定义搜索 (如: X300u 超广角)", "")
final_keyword = search_keyword if search_keyword else target_model

# 深度负面语义库：专门针对“参数泄露”阶段的吐槽
NEG_WORDS = ['没升级', '阉割', '遗憾', '失望', '旧款', '828', 'jn1', '传感器差', '没诚意', '丑', '贵', '智商税', '吐槽', '避雷', '差评', '不如前代']
EXCLUDE_WORDS = ['差别', '差不多', '出差']

# 3. UGC 数据穿透引擎
def fetch_ugc_data(keyword):
    # 策略：锁定微博和贴吧，强行搜索“不满/遗憾”
    # site:weibo.com 确保搜到的是微博用户的发言
    query = f"(site:weibo.com OR site:tieba.baidu.com) {keyword} (没升级 OR 遗憾 OR 槽点 OR 失望)"
    encoded_q = urllib.parse.quote(query)
    # 使用 Google 索引的 UGC 内容（时效性极高）
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    data = []
    
    for entry in feed.entries[:60]:
        title = entry.title
        # 清洗标题中的微博后缀
        clean_title = title.split(" - ")[0]
        source = "微博/贴吧用户" if "weibo" in title.lower() or "tieba" in title.lower() else "社交平台"
        
        # 语义识别
        sentiment = "正向"
        if any(neg in clean_title.lower() for neg in NEG_WORDS):
            if not any(ex in clean_title.lower() for ex in EXCLUDE_WORDS):
                sentiment = "负向"
        
        data.append({
            "级别": "🔴 槽点" if sentiment == "负向" else "🟢 讨论",
            "用户发言摘要": clean_title,
            "平台": source,
            "倾向": sentiment,
            "链接": entry.link,
            "发布时间": entry.published
        })
    return pd.DataFrame(data)

# 4. 界面渲染
st.title(f"🔍 {final_keyword} 用户参数不满/槽点分析")
st.warning("当前模式：UGC 穿透（专门抓取微博、贴吧真实用户对参数的吐槽）")

# 平台直达：修正链接
q_code = urllib.parse.quote(final_keyword)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"[👁️ 微博实时动态](https://s.weibo.com/weibo?q={q_code})")
c2.markdown(f"[💬 贴吧用户发帖](https://tieba.baidu.com/f/search/res?qw={q_code})")
c3.markdown(f"[📕 小红书真实反馈](https://www.xiaohongshu.com/search_result?keyword={q_code}%20吐槽)")
c4.markdown(f"[🎞️ B站弹幕/评论](https://search.bilibili.com/all?keyword={q_code}%20避雷)")

try:
    with st.spinner(f'正在深入微博/贴吧爬取关于 {final_keyword} 的真实不满...'):
        df = fetch_ugc_data(final_keyword)

    if not df.empty:
        neg_df = df[df["倾向"] == "负向"]
        neg_percent = int((len(neg_df) / len(df)) * 100)

        # 核心指标
        m1, m2, m3 = st.columns(3)
        m1.metric("UGC 采样数", f"{len(df)} 条")
        m2.metric("参数不满占比", f"{neg_percent}%", delta="实测反馈", delta_color="inverse")
        m3.metric("硬件舆论分", f"{100 - neg_percent}")

        # 情报表
        st.subheader("📋 用户真实吐槽/动态列表")
        st.dataframe(
            df,
            column_config={"链接": st.column_config.LinkColumn("直达原文", display_text="🔗")},
            hide_index=True, use_container_width=True
        )

        # 词云可视化
        st.divider()
        cw1, cw2 = st.columns(2)
        
        with cw1:
            st.subheader("🔵 核心议题（参数/配置）")
            all_text = " ".join(df["用户发言摘要"].tolist())
            if all_text:
                wc1 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Blues').generate(all_text)
                fig1, ax1 = plt.subplots(); ax1.imshow(wc1); ax1.axis("off"); st.pyplot(fig1)

        with cw2:
            st.subheader("🔴 负面预警词（用户最不满的点）")
            if not neg_df.empty:
                neg_text = " ".join(neg_df["用户发言摘要"].tolist())
                # 过滤冗余词，突出传感器等硬件名
                for w in [final_keyword, 'vivo', 'ultra', 'x300', '小米', 'oppo']:
                    neg_text = neg_text.lower().replace(w.lower(), "")
                
                wc2 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Reds').generate(neg_text)
                fig2, ax2 = plt.subplots(); ax2.imshow(wc2); ax2.axis("off"); st.pyplot(fig2)
            else:
                st.write("目前尚未发现集中的参数吐槽。")

    else:
        st.info("24小时内微博/贴吧暂无大规模吐槽，建议点击上方链接手动确认。")

except Exception as e:
    st.error(f"连接异常: {e}")

st.caption(f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
