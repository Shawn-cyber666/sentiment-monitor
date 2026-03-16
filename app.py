import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse
from pathlib import Path

# 1. 页面级配置：科技感与宽屏模式
st.set_page_config(page_title="旗舰产品 舆情战略指挥中心", layout="wide", initial_sidebar_state="expanded")

# 极简高科技 CSS
st.markdown("""
    <style>
    .tech-title {font-family: 'Helvetica Neue', sans-serif; font-weight: 300; letter-spacing: 1px;}
    .highlight-red {color: #FF4B4B; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 2. 核心分类字典（精准捕捉硬件参数吐槽）
CATEGORIES = {
    "影像系统": ["超广角", "主摄", "长焦", "传感器", "jn1", "828", "拍照", "偏色", "抹抹感", "镜头"],
    "性能与体验": ["发热", "卡顿", "死机", "断触", "马达", "信号", "网络"],
    "续航与充电": ["电池", "续航", "快充", "掉电", "充电慢"],
    "外观与设计": ["手感", "重量", "太重", "厚度", "丑", "塑料", "缝隙", "屏幕"],
    "定价与综合": ["贵", "智商税", "背刺", "没诚意", "没升级", "遗憾", "阉割", "缩水"]
}
# 负面触发词
NEG_TRIGGERS = ["差", "烂", "不行", "避雷", "吐槽", "失望", "太贵", "没升级", "阉割", "遗憾"]


def normalize_text(text: str) -> str:
    """统一文本清洗，避免大小写/空值导致的误判。"""
    return str(text or "").strip().lower()


def classify_category(title: str) -> str:
    """基于标题关键词匹配舆情模块。"""
    normalized_title = normalize_text(title)
    for cat, keywords in CATEGORIES.items():
        if any(normalize_text(k) in normalized_title for k in keywords):
            return cat
    return "未分类/综合"


def detect_sentiment(title: str, assigned_cat: str) -> str:
    """轻量负向情绪识别，优先命中触发词。"""
    normalized_title = normalize_text(title)
    has_negative_trigger = any(normalize_text(w) in normalized_title for w in NEG_TRIGGERS)
    # 已分类内容且命中负向触发词时优先视为负向；其余归为资讯流
    if assigned_cat != "未分类/综合" and has_negative_trigger:
        return "负向"
    return "正向"


def resolve_source(link: str, source: str) -> str:
    link = normalize_text(link)
    source = normalize_text(source)
    if "weibo" in link or "微博" in source:
        return "微博"
    if "tieba" in link or "贴吧" in source:
        return "贴吧"
    return "综合媒体/论坛"


def create_wordcloud(text: str, colormap: str) -> WordCloud | None:
    """兼容字体缺失场景，避免词云生成直接失败。"""
    if not text.strip():
        return None

    font_path = "font.ttf" if Path("font.ttf").exists() else None
    return WordCloud(
        font_path=font_path,
        width=600,
        height=350,
        background_color="white",
        colormap=colormap,
    ).generate(text)

# 3. 侧边栏：监控台
with st.sidebar:
    st.markdown("<h3 class='tech-title'>⚙️ 指挥台配置</h3>", unsafe_allow_html=True)
    target_model = st.selectbox("核心监测对象", ["vivo X300 Ultra", "vivo X300s", "OPPO Find X8 Ultra", "小米 17 Ultra"])
    custom_q = st.text_input("附加定向搜索 (可选，如: 超广角)", "")
    
    st.divider()
    st.caption("系统状态：UGC + 媒体双线并发检索中...")

final_search = f"{target_model} {custom_q}".strip()

# 4. 数据抓取与分类引擎
@st.cache_data(ttl=300)
def fetch_omnidata(keyword):
    # 综合搜索：包含新闻资讯与论坛讨论
    q = f"{keyword} (缺点 OR 吐槽 OR 遗憾 OR 评价)"
    encoded_q = urllib.parse.quote(q)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    data = []
    
    seen_links = set()
    for entry in feed.entries[:80]:
        link = entry.get("link", "")
        if not link or link in seen_links:
            continue
        seen_links.add(link)

        title_text = entry.get("title", "")
        title = title_text.split(" - ")[0]
        source = title_text.split(" - ")[1] if " - " in title_text else "全网抓取"

        source_clean = resolve_source(link, source)
        assigned_cat = classify_category(title)
        sentiment = detect_sentiment(title, assigned_cat)

        data.append({
            "状态": "🔴 槽点" if sentiment == "负向" else "🟢 资讯",
            "所属模块": assigned_cat,
            "平台来源": source_clean,
            "情报内容摘要": title,
            "倾向": sentiment,
            "原文链接": link,
            "发布时间": entry.get("published", "未知")
        })
            
    return pd.DataFrame(data)

# 5. 主界面渲染
st.markdown(f"<h2 class='tech-title'>📊 <span class='highlight-red'>{final_search}</span> 全景舆情透视看板</h2>", unsafe_allow_html=True)

# 找回四大平台直达链接
st.write("---")
q_code = urllib.parse.quote(final_search)
l1, l2, l3, l4 = st.columns(4)
l1.link_button("👁️ 微博实时情报流", f"https://s.weibo.com/weibo?q={q_code}")
l2.link_button("💬 贴吧深度讨论区", f"https://tieba.baidu.com/f/search/res?qw={q_code}")
l3.link_button("📕 小红书真实反馈", f"https://www.xiaohongshu.com/search_result?keyword={q_code}%20吐槽")
l4.link_button("🎞️ B站避雷与弹幕", f"https://search.bilibili.com/all?keyword={q_code}%20避雷")
st.write("---")

try:
    with st.spinner('正在聚合全网碎片，构建分析矩阵...'):
        df = fetch_omnidata(final_search)

    if not df.empty:
        neg_df = df[df["倾向"] == "负向"]
        
        # 顶部核心指标
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("全网数据采样", f"{len(df)} 组")
        c2.metric("捕获核心槽点", f"{len(neg_df)} 条")
        c3.metric("负面情绪浓度", f"{int((len(neg_df)/len(df))*100)}%", delta_color="inverse")
        c4.metric("舆论健康度", f"{100 - int((len(neg_df)/len(df))*100)}")

        # 核心功能 1：数据透视矩阵 (Pivot Table)
        st.subheader("💠 硬件痛点交叉透视矩阵")
        if not neg_df.empty:
            pivot_df = pd.pivot_table(
                neg_df, 
                index="所属模块", 
                columns="平台来源", 
                values="情报内容摘要", 
                aggfunc="count", 
                fill_value=0,
                margins=True,
                margins_name="🔥 痛点总计"
            )
            st.dataframe(pivot_df.style.background_gradient(cmap="Reds", axis=None), use_container_width=True)
        else:
            st.success("目前尚未形成规模化的硬件痛点聚集。")

        # 核心功能 2：双红蓝词云 (直观提炼)
        st.divider()
        cw1, cw2 = st.columns(2)
        
        with cw1:
            st.subheader("🔵 全景热词 (关注度)")
            all_text = " ".join(df["情报内容摘要"].tolist())
            if all_text:
                wc1 = create_wordcloud(all_text, "Blues")
                if wc1:
                    fig1, ax1 = plt.subplots()
                    ax1.imshow(wc1)
                    ax1.axis("off")
                    st.pyplot(fig1)

        with cw2:
            st.subheader("🔴 核心痛点云 (吐槽区)")
            if not neg_df.empty:
                neg_text = " ".join(neg_df["情报内容摘要"].tolist())
                # 过滤防干扰词，让具体的传感器型号或配置显现
                for w in [target_model.split(" ")[0], target_model.split(" ")[-1], '手机', '对比']:
                    neg_text = neg_text.lower().replace(w.lower(), "")

                wc2 = create_wordcloud(neg_text, "Reds")
                if wc2:
                    fig2, ax2 = plt.subplots()
                    ax2.imshow(wc2)
                    ax2.axis("off")
                    st.pyplot(fig2)
            else:
                st.info("暂无集中负面词汇")

        # 核心功能 3：带原文链接的情报流
        st.divider()
        st.subheader("📋 实时情报数据源 (含跳转溯源)")
        st.dataframe(
            df,
            column_config={
                "原文链接": st.column_config.LinkColumn("溯源直达", display_text="🔗 查看详情"),
                "情报内容摘要": st.column_config.TextColumn("情报内容摘要", width="large")
            },
            hide_index=True, use_container_width=True
        )

    else:
        st.warning("暂未捕获到有效数据，请检查网络或放宽搜索词限制。")

except Exception as e:
    st.error(f"分析系统运行异常: {e}")

st.caption(f"系统运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据融合: UGC + 全网资讯")
