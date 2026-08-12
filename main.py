"""
FitCoach AI - 智能减脂助手
主页面：仪表盘 + TDEE 计算器

运行方式：在项目根目录执行
    streamlit run main.py
"""

import streamlit as st
from core.tdee import calculate_tdee, ACTIVITY_LEVELS
from core.llm import is_mock_mode
from db.database import init_db, save_user_profile

# 初始化数据库（第一次运行会创建表）
init_db()


# 自定义 metric 卡片渲染函数（避开 st.metric 内部的 structuredClone）
def _render_metrics(result: dict) -> str:
    """渲染减脂方案的六个指标卡片。"""
    items = [
        ("基础代谢 (BMR)", f"{result['bmr']}", "大卡", "#1f77b4"),
        ("每日消耗 (TDEE)", f"{result['tdee']}", "大卡", "#2ca02c"),
        ("减脂建议摄入", f"{result['fat_loss_calories']}", "大卡", "#ff7f0e"),
        ("蛋白质", f"{result['protein']}", "g", "#d62728"),
        ("碳水", f"{result['carbs']}", "g", "#9467bd"),
        ("脂肪", f"{result['fat']}", "g", "#8c564b"),
    ]
    cards_html = "".join(
        f"""
        <div style="background: #fafafa; border: 1px solid #eee;
                    border-radius: 8px; padding: 16px; text-align: center;
                    border-top: 3px solid {color};">
            <div style="font-size: 13px; color: #666; margin-bottom: 8px;">{label}</div>
            <div style="font-size: 26px; font-weight: bold; color: {color};">{value}</div>
            <div style="font-size: 12px; color: #999; margin-top: 4px;">{unit}</div>
        </div>
        """
        for label, value, unit, color in items
    )
    return f"""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr);
                gap: 12px; margin: 16px 0;">
        {cards_html}
    </div>
    """


# 兼容性补丁：为老版浏览器/内嵌 webview 提供 structuredClone polyfill
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

# 页面配置
st.set_page_config(
    page_title="FitCoach AI",
    page_icon="🔥",
    layout="wide",
)

# 标题
st.title("FitCoach AI")
st.markdown("基于 AI 的个性化减脂管理工具")

# 模式提示
if is_mock_mode():
    st.info(
        "当前运行在模拟模式。配置 DeepSeek API Key 后可启用完整 AI 对话。"
        "查看 `.env` 文件了解如何配置。"
    )

# 侧边栏 - 用户数据录入
st.sidebar.header("你的身体数据")

with st.sidebar.form("user_data_form"):
    name = st.text_input("昵称", value="Jade")
    gender = st.selectbox(
        "性别",
        ["male", "female"],
        format_func=lambda x: "男" if x == "male" else "女",
    )
    age = st.number_input("年龄", min_value=10, max_value=100, value=25)
    height = st.number_input("身高 (cm)", min_value=100, max_value=250, value=170)
    weight = st.number_input("体重 (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.1)
    activity = st.selectbox("活动水平", list(ACTIVITY_LEVELS.keys()))

    submitted = st.form_submit_button("计算我的减脂方案")

# 主区域
if submitted:
    # 计算
    result = calculate_tdee(weight, height, age, gender, activity)

    # 保存到数据库
    user_id = save_user_profile(name, gender, age, height, weight, activity)
    st.session_state["user_id"] = user_id
    st.session_state["user_profile"] = {
        "name": name,
        "gender": gender,
        "age": age,
        "height": height,
        "weight": weight,
        "activity_level": activity,
    }

    st.success("数据已保存！")

    # 展示结果（用自定义 HTML 避免 st.metric 触发 structuredClone 报错）
    st.header("你的减脂方案")
    st.markdown(_render_metrics(result), unsafe_allow_html=True)

    st.info(
        f"每天吃 {result['fat_loss_calories']} 大卡，"
        f"预计每周减重约 0.5kg。"
        f"蛋白质 {result['protein']}g 帮你保住肌肉。"
    )

elif "user_profile" in st.session_state:
    # 显示之前保存的数据
    p = st.session_state["user_profile"]
    result = calculate_tdee(p["weight"], p["height"], p["age"], p["gender"], p["activity_level"])

    st.header("你的减脂方案")
    st.markdown(_render_metrics(result), unsafe_allow_html=True)

else:
    st.markdown("👈 在左侧填入你的身体数据，点击「计算我的减脂方案」开始")

st.markdown("---")
st.markdown("📋 在左侧菜单选择其他功能：**AI 对话**、**饮食记录**、**进度追踪**")
