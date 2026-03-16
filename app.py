import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse

# 1. 页面配置
st.set_page_config(page_title="vivo 旗舰舆情战略指挥中心", layout="wide")

# 2. 侧边栏
st.sidebar.header("🕹️ 监控指挥台")
target_model = st.sidebar.selectbox(
    "核心监控目标", 
    ["vivo X300 Ultra", "vivo X300s", "小米 17 Ultra", "OPPO Find X8 Ultra", "荣耀 Magic 8 至臻版"]
)

# --- 语义引擎配置 ---
# 中性硬件词（不代表负面）
HARDWARE_LIST = ['超广角', '主摄', '长焦', '屏幕', '电池', '快充', '传感器', '影像', '指纹']
# 真正的负面动作/状态
NEG_ACTIONS = ['没升级', '阉割', '缩水', '旧款', '遗憾', '吐槽', '避雷', '差', '烂', '后悔', '智商税', '偏色', '发热']
# 排除误判
EXCLUDE_WORDS = ['差别', '差不多', '出差']

# 3. 智能语义判定函数
def analyze_deep_sentiment(title):
    title_lower = title.lower()
    
    # 首先检查是否包含误判词
    if any(ex in title_lower for ex in EXCLUDE_WORDS):
        return "正向", "无"
    
    # 查找是否有硬件词被提及
    mentioned_hardware = [hw for hw in HARDWARE_LIST if hw in title_lower]
    # 查找是否有负面动作
    hit_neg_actions = [neg for neg in NEG_ACTIONS if neg in title_lower]
    
    # 逻辑：如果有负面动作，则判定为负向
    if hit_neg_actions:
        # 如果同时提到了硬件，则组合成痛点标签 (如: 超广角+没升级)
        if mentioned_hardware:
            pains = [f"{hw}{hit_neg_actions[0]}" for hw in mentioned_hardware]
            return "负向", " / ".join(pains)
        else:
            return "负向", hit_neg_actions[0]
            
    return "正向", "无"

def fetch_strategic_data(keyword):
    # 增加搜索深度，确保抓到细节
    search_q = f"{keyword} (评价 OR 吐槽 OR 规格 OR 遗憾)"
    encoded_q = urllib.parse.quote(search_q)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    data = []
    
    for entry in feed.entries[:50]:
        title = entry.title.split(" - ")[0]
        source = entry.title.split(" - ")[1] if " - " in entry.title else "全网"
        
        sentiment, pain_label = analyze_deep_sentiment(title)
        
        data.append({
            "级别": "🔴 预警" if sentiment == "负向" else "🟢 稳健",
            "内容摘要": title,
            "来源媒体": source,
            "核心痛点": pain_label,
            "倾向": sentiment,
            "链接": entry.link,
            "发布时间": entry.published
        })
    return pd.DataFrame(data)

# 4. 主看板渲染
st.title(f"📡 {target_model} 实时舆情战略看板")

try:
    with st.spinner('正在进行语义脱敏与痛点提炼...'):
        df = fetch_strategic_data(target_model)

    if not df.empty:
        neg_df = df[df["倾向"] == "负向"]
        
        # 指标区
        c1, c2, c3 = st.columns(3)
        c1.metric("样本深度", f"{len(df)} 组")
        c2.metric("有效负面占比", f"{len(neg_df)} 条", delta=f"{int(len(neg_df)/len(df)*100)}%", delta_color="inverse")
        c3.metric("口碑指数", f"{100 - int(len(neg_df)/len(df)*100)}")

        # 直达链接
        st.write("---")
        q_code = urllib.parse.quote(target_model)
        l1, l2, l3, l4 = st.columns(4)
        l1.link_button("👁️ 微博实时", f"https://s.weibo.com/weibo?q={q_code}")
        l2.link_button("💬 贴吧讨论", f"https://tieba.baidu.com/f/search/res?qw={q_code}")
        l3.link_button("📕 小红书吐槽", f"https://www.xiaohongshu.com/search_result?keyword={q_code}%20吐槽")
        l4.link_button("🎞️ B站避雷", f"https://search.bilibili.com/all?keyword={q_code}%20避雷")

        # 数据列表
        st.subheader("📑 精准舆情情报流")
        st.dataframe(
            df,
            column_config={
                "内容摘要": st.column_config.TextColumn("内容摘要", width="large"),
                "核心痛点": st.column_config.TextColumn("提炼痛点", width="medium"),
                "链接": st.column_config.LinkColumn("直达", display_text="🔗")
            },
            hide_index=True, use_container_width=True
        )

        # 词云区
        st.divider()
        v1, v2 = st.columns(2)
        
        with v1:
            st.subheader("🔵 全网高频词 (大家在聊什么)")
            all_txt = " ".join(df["内容摘要"].tolist())
            wc1 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Blues').generate(all_txt)
            fig1, ax1 = plt.subplots(); ax1.imshow(wc1); ax1.axis("off"); st.pyplot(fig1)

        with v2:
            st.subheader("🔴 核心槽点分析 (大家在骂什么)")
            if not neg_df.empty:
                # 语义清理：生成负面词云时，过滤掉中性硬件名词
                neg_txt = " ".join(neg_df["内容摘要"].tolist()).lower()
                for stop_w in [target_model, 'vivo', 'x300', 'ultra', '小米', 'oppo'] + HARDWARE_LIST:
                    neg_txt = neg_txt.replace(stop_w.lower(), "")
                
                if neg_txt.strip():
                    wc2 = WordCloud(font_path='font.ttf', width=600, height=400, background_color="white", colormap='Reds').generate(neg_txt)
                    fig2, ax2 = plt.subplots(); ax2.imshow(wc2); ax2.axis("off"); st.pyplot(fig2)
                else:
                    st.info("检测到零散负面，但尚未形成集中痛点词。")
            else:
                st.success("✨ 当前样本内未发现显著参数槽点。")

    else:
        st.error("数据调取失败，请稍后刷新。")

except Exception as e:
    st.error(f"分析引擎故障: {e}")
