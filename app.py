import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面配置
st.set_page_config(page_title="vivo 2026 旗舰舆情决策系统", layout="wide")

# 2. 侧边栏：动态加载最新的竞品库
st.sidebar.header("🚀 2026 旗舰实时监控")

try:
    with open("keywords.txt", "r", encoding="utf-8") as f:
        competitors = [line.strip() for line in f.readlines() if line.strip()]
except:
    competitors = ["小米 17 Ultra", "OPPO Find X8 Ultra", "荣耀 Magic 8"]

# 下拉菜单：默认包含 vivo 最新型号
target_model = st.sidebar.selectbox("选择当前监控对象", ["vivo X300 Ultra", "vivo X400 Ultra"] + competitors)
search_keyword = st.sidebar.text_input("或精准搜索特定硬件 (如: X300u 超广角)", "")
final_keyword = search_keyword if search_keyword else target_model

# 针对 2026 硬件槽点的专项词库
NEG_WORDS = ['差', '烂', '断触', '发热', '烫', '卡顿', '死机', '黑屏', '后悔', '避雷', '吐槽', '不值', 
             '智商税', '割韭菜', '翻车', '阉割', '没升级', '遗憾', '缺陷', '缩水', '配置低', '828', 'JN1', '偏色']
EXCLUDE_WORDS = ['差别', '差不多', '出差', '价差']

# 3. 实时数据引擎 (增加 when:1d 强制获取 24小时内数据)
def fetch_realtime_data(keyword):
    # 策略：型号 + 负面触发词 + 时间限制
    # when:1d 代表过去24小时，when:7d 代表过去一周
    encoded_q = urllib.parse.quote(f"{keyword} (遗憾 OR 缺点 OR 没升级 OR 吐槽) when:7d")
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    data = []
    
    for entry in feed.entries[:60]:
        title = entry.title
        source = title.rsplit(" - ", 1)[1] if " - " in title else "社交媒体"
        clean_title = title.rsplit(" - ", 1)[0] if " - " in title else title
        
        # 语义分析
        sentiment = "正向"
        if any(neg in clean_title.lower() for neg in NEG_WORDS):
            if not any(ex in clean_title.lower() for ex in EXCLUDE_WORDS):
                sentiment = "负向"
        
        data.append({
            "状态": "🔴 预警" if sentiment == "负向" else "🟢 正常",
            "情报标题": clean_title,
            "媒体来源": source,
            "倾向": sentiment,
            "链接": entry.link,
            "时间": entry.published
        })
    return pd.DataFrame(data)

# 4. UI 布局
st.title(f"🔍 {final_keyword} 24h 实时舆情看板")

# 平台直达
q_code = urllib.parse.quote(final_keyword)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"[📱 酷安最新动态](https://www.coolapk.com/search?q={q_code})")
c2.markdown(f"[💬 贴吧用户反馈](https://tieba.baidu.com/f/search/res?qw={q_code})")
c3.markdown(f"[📕 小红书真实评价](https://www.xiaohongshu.com/search_result?keyword={q_code})")
c4.markdown(f"[🎞️ B站视频评测](https://search.bilibili.com/all?keyword={q_code})")

try:
    with st.spinner(f'正在穿透 2026 年 {final_keyword} 的底层舆论...'):
        df = fetch_realtime_data(final_keyword)

    if not df.empty:
        neg_df = df[df["倾向"] == "负向"]
        
        # 关键指标
        k1, k2, k3 = st.columns(3)
        k1.metric("活跃样本 (7日内)", f"{len(df)} 组")
        k2.metric("负面声量", f"{len(neg_df)} 条", delta=f"{int(len(neg_df)/len(df)*100)}%", delta_color="inverse")
        k3.metric("市场情绪指数", f"{100 - int(len(neg_df)/len(df)*100)}")

        # 情报表
        st.subheader("📋 实时情报流 (点击链接查看原文)")
        st.dataframe(
            df,
            column_config={"链接": st.column_config.LinkColumn("直达", display_text="🔗")},
            hide_index=True, use_container_width=True
        )

        # 词云可视化
        st.divider()
        cw1, cw2 = st.columns(2)
        
        with cw1:
            st.subheader("🔵 今日热议焦点")
            all_txt = " ".join(df["情报标题"].tolist())
            if all_txt:
                wc1 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Blues').generate(all_txt)
                fig1, ax1 = plt.subplots(); ax1.imshow(wc1); ax1.axis("off"); st.pyplot(fig1)

        with cw2:
            st.subheader("🔴 核心槽点/负面分布")
            if not neg_df.empty:
                neg_txt = " ".join(neg_df["情报标题"].tolist())
                # 过滤冗余型号词
                for w in [final_keyword, 'vivo', 'ultra', '小米', 'oppo', 'magic']:
                    neg_txt = neg_txt.lower().replace(w.lower(), "")
                
                wc2 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Reds').generate(neg_txt)
                fig2, ax2 = plt.subplots(); ax2.imshow(wc2); ax2.axis("off"); st.pyplot(fig2)
            else:
                st.write("暂无明显负面槽点（或公关覆盖较好）。")
    else:
        st.warning("24小时内未发现有效负面情报，建议扩大搜索词或查看直达链接。")

except Exception as e:
    st.error(f"数据获取异常: {e}")

st.caption(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据源: 全网实时资讯及社区索引")
