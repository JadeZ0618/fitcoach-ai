"""
进度追踪页面 - 记录体重变化，可视化趋势
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from db.database import (
    save_weight_log,
    get_weight_history,
    get_latest_user,
)
from core.ui import apply_theme, render_nav, render_metric_cards

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(page_title="进度追踪", page_icon="📈")

# 应用统一主题
apply_theme()

# 顶部导航栏
render_nav(current="progress")

st.title("进度追踪")
st.markdown("记录体重变化，追踪减脂进度")

# 检查是否有用户数据
if "user_id" not in st.session_state:
    latest = get_latest_user()
    if latest:
        st.session_state["user_id"] = latest[0]
    else:
        st.warning("请先在首页填写身体数据")
        st.stop()

# 记录今日体重
st.subheader("记录今日体重")
col1, col2 = st.columns([2, 1])

with col1:
    today_weight = st.number_input(
        "今日体重 (kg)",
        min_value=30.0,
        max_value=300.0,
        value=70.0,
        step=0.1,
    )
with col2:
    st.write("")  # 占位对齐
    st.write("")
    if st.button("记录体重", type="primary"):
        save_weight_log(st.session_state["user_id"], today_weight)
        st.success(f"已记录：{today_weight} kg")
        st.rerun()

# 体重历史图表
st.subheader("体重变化趋势")
history = get_weight_history(st.session_state["user_id"])

if history and len(history) > 0:
    # 转成 DataFrame 方便画图
    df = pd.DataFrame(history, columns=["date", "weight"])

    # 画折线图（使用主题配色）
    fig = px.line(
        df,
        x="date",
        y="weight",
        title="体重变化",
        markers=True,
    )
    fig.update_traces(
        line_color="#0F6E56",
        line_width=2,
        marker=dict(size=6, color="#0F6E56"),
    )
    fig.update_layout(
        xaxis_title="日期",
        yaxis_title="体重 (kg)",
        height=400,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=13, color="#2C2C2A"),
        title_font=dict(size=16, color="#2C2C2A"),
        xaxis=dict(gridcolor="#F1EFE8"),
        yaxis=dict(gridcolor="#F1EFE8"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 统计卡片（桌面 3 列，手机自动 2 列）
    st.markdown("---")
    start_w = df['weight'].iloc[0]
    current_w = df['weight'].iloc[-1]
    diff = current_w - start_w

    # 减重=好(teal)，增重=注意(coral)，不变=灰
    if diff < 0:
        diff_color = "fc-teal"
    elif diff > 0:
        diff_color = "fc-coral"
    else:
        diff_color = "fc-gray"
    diff_sign = "+" if diff > 0 else ""

    items = [
        ("起始体重", f"{start_w}", "kg", "fc-blue"),
        ("当前体重", f"{current_w}", "kg", "fc-teal"),
        ("总变化", f"{diff_sign}{diff:.1f}", "kg", diff_color),
    ]
    render_metric_cards(items, cols=3)

    # 数据表格
    st.subheader("历史记录")
    st.table(df)
else:
    st.info("还没有体重记录。在上方记录你的第一次体重吧！")
