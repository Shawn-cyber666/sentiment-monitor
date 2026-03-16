import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面配置
st.set_page_config(page_title="vivo 舆情战略决策看板", layout="wide")

# 2. 侧边栏：搜索与极致负面配置
st.sidebar.header("🎯 战略搜索配置")
search_keyword = st.sidebar.text_input("输入监控型号", "vivo X300 Ultra")

# 【重点：自定义负面词库】—— 只要包含这些词，系统会立刻判定为负面
# 你可以根据最近的业务反馈，随时在这里添加新的“雷点”
NEG_KEYWORDS = [
    # 质量问题
    '差', '烂', '断触', '发热', '烫', '卡顿', '死机', '黑屏', '裂', '缝隙', '偏色', '进灰',
    # 用户心态
    '失望', '退货', '后悔', '避雷', '吐槽', '不值', '智商税', '割韭菜', '翻车', '翻车了',
    # 竞品对比
    '不如', '输给', '吊打', '被虐', '降价', '背刺', '虚标', '造假', '虚假宣传',
    # 功能缺失
    '缺少', '阉割', '缩水', '没有', '遗憾', '难受'
]

# 3. 增强型情感判定引擎
def analyze_sentiment(title):
    # 只要命中任何一个负面关键词，就判定为负面
    for word in NEG_KEYWORDS:
        if word in title:
            return "负向", 0 # 给 0 分或负分
    return "正向", 1

def fetch_data(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    # 增加抓取量到 50 条，确保覆盖范围够广
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    feed = feedparser.parse(rss_url)
    
    data = []
    if not feed.entries:
        return pd.DataFrame()

    for entry in feed.entries[:50]:
        title = entry.title
        source = "未知"
        clean_title = title
        if " - " in title:
            clean_title = title.rsplit(" - ", 1)[0]
            source = title.rsplit(" - ", 1)[1]

        # 调用我们自己的逻辑
        sentiment, score = analyze_sentiment(clean_title)
        
        data.append({
            "级别": "🔴 警告" if sentiment == "负向" else "🟢 正常",
            "情报标题": clean_title,
            "来源": source,
            "发布时间": entry.published,
            "访问原文": entry.link,
            "倾向": sentiment
        })
    return pd.DataFrame(data)

# 4. 主界面
st.title(f"📊 {search_keyword} 负面舆论实时监测")
st.markdown("---")

# 国内平台一键直达
col_link1, col_link2, col_link3, col_link4 = st.columns(4)
encoded_q = urllib.parse.quote(search_keyword)
col_link1.markdown(f"[📕 小红书负面搜索](https://www.xiaohongshu.com/search_result?keyword={encoded_q}%20吐槽)")
col_link2.markdown(f"[👁️ 微博实时动态](https://s.weibo.com/weibo?q={encoded_q})")
col_link3.markdown(f"[🔍 百度资讯](https://www.baidu.com/s?tn=news&word={encoded_q})")
col_link4.markdown(f"[📦 社区/论坛反馈](https://www.zhihu.com/search?type=content&q={encoded_q}%20缺点)")

try:
    with st.spinner('正在检索全网负面信号...'):
        df = fetch_data(search_keyword)

    if not df.empty:
        # 统计分析
        neg_df = df[df["倾向"] == "负向"]
        neg_count = len(neg_df)
        total_count = len(df)
        neg_percent = int((neg_count / total_count) * 100)

        # 头部指标显示
        m1, m2, m3 = st.columns(3)
        m1.metric("总监测样本", f"{total_count} 篇")
        m2.metric("负面情报数", f"{neg_count} 篇", delta=f"{neg_percent}%", delta_color="inverse")
        m3.metric("口碑指数", f"{100 - neg_percent} 分")

        # 重点预警区
        if neg_count > 0:
            st.error(f"⚠️ 发现 {neg_count} 条可疑负面舆论！请公关/产品部门重点关注。")
            with st.expander("👉 点击展开所有负面情报，制定宣传调整策略"):
                st.table(neg_df[["来源", "情报标题", "访问原文"]])
        else:
            st.success("✨ 当前样本内未发现明显负面关键词。")

        # 全量列表
        st.subheader("📋 实时动态流")
        st.dataframe(
            df,
            column_config={"访问原文": st.column_config.LinkColumn("查看详情", display_text="🔗")},
            hide_index=True,
            use_container_width=True
        )

        # 战略词云：专看负面
        if not neg_df.empty:
            st.subheader("☁️ 负面关键词分布")
            neg_titles = " ".join(neg_df["情报标题"].tolist())
            wordcloud = WordCloud(font_path='font.ttf', width=1000, height=400, background_color="white", colormap='autumn').generate(neg_titles)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud)
            ax.axis("off")
            st.pyplot(fig)

    else:
        st.warning("暂无数据。")

except Exception as e:
    st.error(f"运行出错: {e}")
