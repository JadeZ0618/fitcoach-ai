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

# 兼容性补丁：老浏览器/内嵌 webview 缺少 structuredClone
# 强制显示滚动条（WorkBuddy 内嵌浏览器默认不显示）
st.markdown(
    """
    <script>
    if (typeof structuredClone === 'undefined') {
        window.structuredClone = function(obj) {
            return JSON.parse(JSON.stringify(obj));
        };
    }
    </script>
    <style>
    html, body { overflow-y: scroll !important; }
    [data-testid="stAppViewContainer"] { overflow-y: scroll !important; }
    ::-webkit-scrollbar { -webkit-appearance: none; width: 10px; }
    ::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,.3); border-radius: 5px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="进度追踪", page_icon="📈")
st.title("📈 进度追踪")
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

    # 画折线图
    fig = px.line(
        df,
        x="date",
        y="weight",
        title="体重变化",
        markers=True,
    )
    fig.update_layout(
        xaxis_title="日期",
        yaxis_title="体重 (kg)",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # 统计数据（用自定义 HTML 避开 st.metric 触发 structuredClone 报错）
    st.markdown("---")
    start_w = df['weight'].iloc[0]
    current_w = df['weight'].iloc[-1]
    diff = current_w - start_w
    diff_color = "#2ca02c" if diff < 0 else "#ff7f0e" if diff > 0 else "#666"
    diff_sign = "+" if diff > 0 else ""
    st.markdown(
        f'<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 16px 0;">'
        f'<div style="background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 16px; text-align: center; border-top: 3px solid #1f77b4;">'
        f'<div style="font-size: 13px; color: #666; margin-bottom: 8px;">起始体重</div>'
        f'<div style="font-size: 24px; font-weight: bold; color: #1f77b4;">{start_w}</div>'
        f'<div style="font-size: 12px; color: #999; margin-top: 4px;">kg</div>'
        f'</div>'
        f'<div style="background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 16px; text-align: center; border-top: 3px solid #2ca02c;">'
        f'<div style="font-size: 13px; color: #666; margin-bottom: 8px;">当前体重</div>'
        f'<div style="font-size: 24px; font-weight: bold; color: #2ca02c;">{current_w}</div>'
        f'<div style="font-size: 12px; color: #999; margin-top: 4px;">kg</div>'
        f'</div>'
        f'<div style="background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 16px; text-align: center; border-top: 3px solid {diff_color};">'
        f'<div style="font-size: 13px; color: #666; margin-bottom: 8px;">总变化</div>'
        f'<div style="font-size: 24px; font-weight: bold; color: {diff_color};">{diff_sign}{diff:.1f}</div>'
        f'<div style="font-size: 12px; color: #999; margin-top: 4px;">kg</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 数据表格（用 st.table 避免 st.dataframe 内部依赖 structuredClone）
    st.subheader("历史记录")
    st.table(df)
else:
    st.info("还没有体重记录。在上方记录你的第一次体重吧！")
