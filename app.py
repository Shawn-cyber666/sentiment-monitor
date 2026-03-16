import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse
import re

# 1. 页面级配置：开启全屏沉浸模式与暗黑高科技风
st.set_page_config(page_title="旗舰产品 UGC 痛点透视舱", layout="wide", initial_sidebar_state="expanded")
# 1. 页面级配置：科技感与宽屏模式
st.set_page_config(page_title="旗舰产品 舆情战略指挥中心", layout="wide", initial_sidebar_state="expanded")

# 自定义极简高科技 CSS
# 极简高科技 CSS
st.markdown("""
    <style>
    /* 隐藏顶部默认导航条和底部水印 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* 调整全局字体和间距 */
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    /* 科技感主标题 */
    .tech-title {font-family: 'Helvetica Neue', sans-serif; font-weight: 300; color: #E0E0E0; letter-spacing: 2px;}
    .tech-title {font-family: 'Helvetica Neue', sans-serif; font-weight: 300; letter-spacing: 1px;}
    .highlight-red {color: #FF4B4B; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 2. 核心分析字典：将槽点分类，用于透视表
# 2. 核心分类字典（精准捕捉硬件参数吐槽）
CATEGORIES = {
    "影像系统": ["超广角", "主摄", "长焦", "传感器", "jn1", "828", "拍照", "偏色", "抹抹感"],
    "性能与体验": ["发热", "卡顿", "死机", "断触", "马达", "信号"],
    "影像系统": ["超广角", "主摄", "长焦", "传感器", "jn1", "828", "拍照", "偏色", "抹抹感", "镜头"],
    "性能与体验": ["发热", "卡顿", "死机", "断触", "马达", "信号", "网络"],
    "续航与充电": ["电池", "续航", "快充", "掉电", "充电慢"],
    "外观与设计": ["手感", "重量", "太重", "厚度", "丑", "塑料", "缝隙"],
    "定价与综合": ["贵", "智商税", "背刺", "没诚意", "没升级", "遗憾", "阉割"]
    "外观与设计": ["手感", "重量", "太重", "厚度", "丑", "塑料", "缝隙", "屏幕"],
    "定价与综合": ["贵", "智商税", "背刺", "没诚意", "没升级", "遗憾", "阉割", "缩水"]
}
# 负面触发词
NEG_TRIGGERS = ["差", "烂", "不行", "避雷", "吐槽", "失望", "太贵", "没升级", "阉割", "遗憾"]

# 3. 侧边栏：极简控制台
# 3. 侧边栏：监控台
with st.sidebar:
    st.markdown("<h3 class='tech-title'>⚙️ 控制台</h3>", unsafe_allow_html=True)
    st.markdown("<h3 class='tech-title'>⚙️ 指挥台配置</h3>", unsafe_allow_html=True)
    target_model = st.selectbox("核心监测对象", ["vivo X300 Ultra", "vivo X300s", "OPPO Find X8 Ultra", "小米 17 Ultra"])
    st.caption("引擎状态：UGC 评论碎片深度嗅探中...")
    custom_q = st.text_input("附加定向搜索 (可选，如: 超广角)", "")
    
    st.divider()
    st.caption("系统状态：UGC + 媒体双线并发检索中...")

final_search = f"{target_model} {custom_q}".strip()

# 4. 数据抓取与分类引擎
@st.cache_data(ttl=600) # 加入缓存机制，避免频繁请求被ban
def fetch_and_categorize(keyword):
    # 强制搜索论坛回复类关键词
    q = f"{keyword} (评论说 OR 网友吐槽 OR 回复贴 OR 缺点)"
@st.cache_data(ttl=300)
def fetch_omnidata(keyword):
    # 综合搜索：包含新闻资讯与论坛讨论
    q = f"{keyword} (缺点 OR 吐槽 OR 遗憾 OR 评价)"
    encoded_q = urllib.parse.quote(q)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

    feed = feedparser.parse(rss_url)
    data = []

    for entry in feed.entries[:80]: # 扩大采样
    for entry in feed.entries[:80]:
        title = entry.title.split(" - ")[0]
        source = entry.title.split(" - ")[1] if " - " in entry.title else "社区平台"
        source = entry.title.split(" - ")[1] if " - " in entry.title else "全网抓取"

        # 简化来源名称，方便透视
        # 来源清洗
        if "weibo" in entry.link or "微博" in source: source_clean = "微博"
        elif "tieba" in entry.link or "贴吧" in source: source_clean = "贴吧"
        else: source_clean = "综合论坛"
        else: source_clean = "综合媒体/论坛"

        # 分类归属逻辑
        assigned_cat = "未分类/杂项"
        # 分类归属
        assigned_cat = "未分类/综合"
        for cat, keywords in CATEGORIES.items():
            if any(k in title.lower() for k in keywords):
                assigned_cat = cat
                break # 归入第一个匹配的类别
                break

        # 判定是否为负面情感 (简单逻辑：包含贬义词或属于核心吐槽类别)
        is_negative = assigned_cat != "未分类/杂项" or any(w in title for w in ["差", "烂", "不行", "避雷"])
        # 情感判定
        is_negative = assigned_cat != "未分类/综合" and any(w in title for w in NEG_TRIGGERS)
        sentiment = "负向" if is_negative else "正向"

        if is_negative:
            data.append({
                "关联模块": assigned_cat,
                "平台来源": source_clean,
                "用户评论碎片": title,
                "原文链接": entry.link
            })
        data.append({
            "状态": "🔴 槽点" if sentiment == "负向" else "🟢 资讯",
            "所属模块": assigned_cat,
            "平台来源": source_clean,
            "情报内容摘要": title,
            "倾向": sentiment,
            "原文链接": entry.link,
            "发布时间": entry.published
        })

    return pd.DataFrame(data)

# 5. 主界面渲染
st.markdown(f"<h1 class='tech-title'>DATA LAB // <span class='highlight-red'>{target_model}</span> 痛点透视舱</h1>", unsafe_allow_html=True)
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
    with st.spinner('正在解构底层 UGC 数据...'):
        df = fetch_and_categorize(target_model)
    with st.spinner('正在聚合全网碎片，构建分析矩阵...'):
        df = fetch_omnidata(final_search)

    if not df.empty:
        # --- 核心：数据透视表 (Pivot Table) ---
        st.write("---")
        st.markdown("### 💠 痛点分布矩阵 (Pivot Matrix)")
        
        # 使用 Pandas 生成透视表：行是硬件模块，列是来源平台，值是吐槽数量
        pivot_df = pd.pivot_table(
            df, 
            index="关联模块", 
            columns="平台来源", 
            values="用户评论碎片", 
            aggfunc="count", 
            fill_value=0,
            margins=True,
            margins_name="🔥 总计痛点"
        )
        neg_df = df[df["倾向"] == "负向"]

        # 渲染透视表，使用渐变背景色突出重灾区
        st.dataframe(
            pivot_df.style.background_gradient(cmap="Reds", axis=None),
            use_container_width=True
        )
        # 顶部核心指标
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("全网数据采样", f"{len(df)} 组")
        c2.metric("捕获核心槽点", f"{len(neg_df)} 条")
        c3.metric("负面情绪浓度", f"{int((len(neg_df)/len(df))*100)}%", delta_color="inverse")
        c4.metric("舆论健康度", f"{100 - int((len(neg_df)/len(df))*100)}")

        st.write("---")
        # --- 下半部分：双列深度数据 ---
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.markdown("### 💬 核心痛点采样录")
            st.dataframe(
                df[["关联模块", "用户评论碎片", "原文链接"]],
                column_config={
                    "关联模块": st.column_config.TextColumn("分类", width="small"),
                    "用户评论碎片": st.column_config.TextColumn("内容", width="large"),
                    "原文链接": st.column_config.LinkColumn("溯源", display_text="🔗")
                },
                hide_index=True, use_container_width=True, height=400
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
            
        with col2:
            st.markdown("### 📊 槽点模块占比")
            # 过滤掉未分类，画一个极简的环形图
            pie_data = df[df["关联模块"] != "未分类/杂项"]["关联模块"].value_counts()
            if not pie_data.empty:
                st.bar_chart(pie_data, color="#FF4B4B")
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
                wc1 = WordCloud(font_path='font.ttf', width=600, height=350, background_color="white", colormap='Blues').generate(all_text)
                fig1, ax1 = plt.subplots(); ax1.imshow(wc1); ax1.axis("off"); st.pyplot(fig1)

        with cw2:
            st.subheader("🔴 核心痛点云 (吐槽区)")
            if not neg_df.empty:
                neg_text = " ".join(neg_df["情报内容摘要"].tolist())
                # 过滤防干扰词，让具体的传感器型号或配置显现
                for w in [target_model.split(" ")[0], target_model.split(" ")[-1], '手机', '对比']:
                    neg_text = neg_text.lower().replace(w.lower(), "")
                
                wc2 = WordCloud(font_path='font.ttf', width=600, height=350, background_color="white", colormap='Reds').generate(neg_text)
                fig2, ax2 = plt.subplots(); ax2.imshow(wc2); ax2.axis("off"); st.pyplot(fig2)
            else:
                st.info("数据量不足以生成占比图。")
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
        st.warning("📡 暂未捕获到足量的碎片数据，请尝试更换监测对象。")
        st.warning("暂未捕获到有效数据，请检查网络或放宽搜索词限制。")

except Exception as e:
    st.error(f"⚠️ 矩阵通讯中断: {e}")
    st.error(f"分析系统运行异常: {e}")

st.caption(f"SYS_TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} // DATA_MODE: UGC_SNIPPET_PIVOT")
st.caption(f"系统运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据融合: UGC + 全网资讯")
