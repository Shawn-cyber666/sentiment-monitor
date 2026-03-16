import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import urllib.parse
import re

# 1. 页面级配置：开启全屏沉浸模式与暗黑高科技风
st.set_page_config(page_title="旗舰产品 UGC 痛点透视舱", layout="wide", initial_sidebar_state="expanded")

# 自定义极简高科技 CSS
st.markdown("""
    <style>
    /* 隐藏顶部默认导航条和底部水印 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* 调整全局字体和间距 */
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    /* 科技感主标题 */
    .tech-title {font-family: 'Helvetica Neue', sans-serif; font-weight: 300; color: #E0E0E0; letter-spacing: 2px;}
    .highlight-red {color: #FF4B4B; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 2. 核心分析字典：将槽点分类，用于透视表
CATEGORIES = {
    "影像系统": ["超广角", "主摄", "长焦", "传感器", "jn1", "828", "拍照", "偏色", "抹抹感"],
    "性能与体验": ["发热", "卡顿", "死机", "断触", "马达", "信号"],
    "续航与充电": ["电池", "续航", "快充", "掉电", "充电慢"],
    "外观与设计": ["手感", "重量", "太重", "厚度", "丑", "塑料", "缝隙"],
    "定价与综合": ["贵", "智商税", "背刺", "没诚意", "没升级", "遗憾", "阉割"]
}

# 3. 侧边栏：极简控制台
with st.sidebar:
    st.markdown("<h3 class='tech-title'>⚙️ 控制台</h3>", unsafe_allow_html=True)
    target_model = st.selectbox("核心监测对象", ["vivo X300 Ultra", "vivo X300s", "OPPO Find X8 Ultra", "小米 17 Ultra"])
    st.caption("引擎状态：UGC 评论碎片深度嗅探中...")

# 4. 数据抓取与分类引擎
@st.cache_data(ttl=600) # 加入缓存机制，避免频繁请求被ban
def fetch_and_categorize(keyword):
    # 强制搜索论坛回复类关键词
    q = f"{keyword} (评论说 OR 网友吐槽 OR 回复贴 OR 缺点)"
    encoded_q = urllib.parse.quote(q)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    feed = feedparser.parse(rss_url)
    data = []
    
    for entry in feed.entries[:80]: # 扩大采样
        title = entry.title.split(" - ")[0]
        source = entry.title.split(" - ")[1] if " - " in entry.title else "社区平台"
        
        # 简化来源名称，方便透视
        if "weibo" in entry.link or "微博" in source: source_clean = "微博"
        elif "tieba" in entry.link or "贴吧" in source: source_clean = "贴吧"
        else: source_clean = "综合论坛"

        # 分类归属逻辑
        assigned_cat = "未分类/杂项"
        for cat, keywords in CATEGORIES.items():
            if any(k in title.lower() for k in keywords):
                assigned_cat = cat
                break # 归入第一个匹配的类别
                
        # 判定是否为负面情感 (简单逻辑：包含贬义词或属于核心吐槽类别)
        is_negative = assigned_cat != "未分类/杂项" or any(w in title for w in ["差", "烂", "不行", "避雷"])
        
        if is_negative:
            data.append({
                "关联模块": assigned_cat,
                "平台来源": source_clean,
                "用户评论碎片": title,
                "原文链接": entry.link
            })
            
    return pd.DataFrame(data)

# 5. 主界面渲染
st.markdown(f"<h1 class='tech-title'>DATA LAB // <span class='highlight-red'>{target_model}</span> 痛点透视舱</h1>", unsafe_allow_html=True)

try:
    with st.spinner('正在解构底层 UGC 数据...'):
        df = fetch_and_categorize(target_model)

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
        
        # 渲染透视表，使用渐变背景色突出重灾区
        st.dataframe(
            pivot_df.style.background_gradient(cmap="Reds", axis=None),
            use_container_width=True
        )

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
            )
            
        with col2:
            st.markdown("### 📊 槽点模块占比")
            # 过滤掉未分类，画一个极简的环形图
            pie_data = df[df["关联模块"] != "未分类/杂项"]["关联模块"].value_counts()
            if not pie_data.empty:
                st.bar_chart(pie_data, color="#FF4B4B")
            else:
                st.info("数据量不足以生成占比图。")

    else:
        st.warning("📡 暂未捕获到足量的碎片数据，请尝试更换监测对象。")

except Exception as e:
    st.error(f"⚠️ 矩阵通讯中断: {e}")

st.caption(f"SYS_TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} // DATA_MODE: UGC_SNIPPET_PIVOT")
