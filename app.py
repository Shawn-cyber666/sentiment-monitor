import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse
import re

# 1. 页面配置
st.set_page_config(page_title="vivo 深度舆情决策系统", layout="wide")

# 2. 侧边栏：监控参数
st.sidebar.header("🛠️ 深度监测配置")
search_keyword = st.sidebar.text_input("目标型号", "vivo X300 Ultra")

# --- 智能语义引擎 ---
# 负面核心词
NEG_WORDS = ['差', '烂', '断触', '发热', '烫', '卡顿', '死机', '黑屏', '后悔', '避雷', '吐槽', '不值', '智商税', '割韭菜', '翻车']
# 排除词（防止“差别”误报）
EXCLUDE_WORDS = ['差别', '差不多', '差旅', '出差', '价差']

def smart_analyze(text):
    # 1. 预处理
    text = text.lower()
    # 2. 排除词检测：如果包含“差别”，则不判定为负面
    if any(ex in text for ex in EXCLUDE_WORDS):
        return "正向"
    # 3. 负面词判定
    if any(neg in text for neg in NEG_WORDS):
        return "负向"
    return "正向"

# 3. 数据抓取：整合国内高质量社区数据源
def fetch_community_data(keyword):
    encoded_q = urllib.parse.quote(keyword)
    # 组合搜索：增加"评测"、"缺点"、"真实感受"等后缀，强行调取接近评论区质量的内容
    queries = [f"{keyword}+缺点", f"{keyword}+真实感受", f"{keyword}+吐槽"]
    
    all_entries = []
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        feed = feedparser.parse(rss_url)
        all_entries.extend(feed.entries[:20])
    
    data = []
    seen_titles = set()

    for entry in all_entries:
        if entry.title in seen_titles: continue
        seen_titles.add(entry.title)
        
        sentiment = smart_analyze(entry.title)
        source = entry.title.rsplit(" - ", 1)[1] if " - " in entry.title else "社区"
        
        data.append({
            "状态": "🔴 预警" if sentiment == "负向" else "🟢 正常",
            "情报内容": entry.title.rsplit(" - ", 1)[0],
            "来源": source,
            "倾向": sentiment,
            "原文": entry.link,
            "时间": entry.published
        })
    return pd.DataFrame(data)

# 4. UI 渲染
st.title(f"🔍 {search_keyword} 深度舆情分析")

# 修正后的国内平台直达 (酷安、贴吧、百度)
c1, c2, c3, c4 = st.columns(4)
q_code = urllib.parse.quote(search_keyword)
# 酷安搜索修复：改为 Web 端通用搜索链接
c1.markdown(f"[📱 酷安热评](https://www.coolapk.com/search?q={q_code})")
# 贴吧搜索：这是国内最真实的评论聚集地
c2.markdown(f"[💬 贴吧讨论](https://tieba.baidu.com/f/search/res?qw={q_code})")
c3.markdown(f"[📕 小红书槽点](https://www.xiaohongshu.com/search_result?keyword={q_code}%20缺点)")
c4.markdown(f"[🎞️ B站真实评测](https://search.bilibili.com/all?keyword={q_code}%20避雷)")

try:
    with st.spinner('正在穿透社区评论区数据...'):
        df = fetch_community_data(search_keyword)

    if not df.empty:
        neg_df = df[df["倾向"] == "负向"]
        
        # 数据看板
        col1, col2 = st.columns([1, 1])
        with col1:
            st.metric("深度样本量", f"{len(df)} 组", delta="已排除语义误报")
            st.dataframe(df, column_config={"原文": st.column_config.LinkColumn("直达链接", display_text="🔗")}, hide_index=True)
        
        with col2:
            st.subheader("🔥 真实口碑分布")
            # 统计图
            st.bar_chart(df["倾向"].value_counts())
            
            # 词云：仅针对负面内容，挖掘真实痛点
            if not neg_df.empty:
                st.subheader("⚠️ 核心负面痛点")
                text = " ".join(neg_df["情报内容"].tolist())
                # 简单过滤常见型号名，让痛点更突出
                for word in [search_keyword, "vivo", "ultra", "x300"]:
                    text = text.replace(word.lower(), "")
                
                wc = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Reds').generate(text)
                fig, ax = plt.subplots()
                ax.imshow(wc)
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.success("当前样本内未发现明显负面趋势")
    else:
        st.warning("未检测到有效数据，建议精简关键词。")

except Exception as e:
    st.error(f"连接失败: {e}")

st.caption(f"系统智能过滤已开启 | 更新于: {datetime.now().strftime('%H:%M:%S')}")
