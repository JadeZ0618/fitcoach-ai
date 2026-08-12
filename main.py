"""
FitCoach AI - 智能减脂助手
主页面：仪表盘 + TDEE 计算器

运行方式：在项目根目录执行
    streamlit run main.py
"""

import streamlit as st
from core.tdee import calculate_tdee, ACTIVITY_LEVELS
from core.llm import is_mock_mode
from core.ui import apply_theme, render_nav, render_metric_cards, render_hero
from db.database import init_db, save_user_profile

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(
    page_title="FitCoach AI",
    page_icon="🔥",
    layout="wide",
)

# 初始化数据库（第一次运行会创建表）
init_db()

# 应用统一主题（CSS + 响应式 + 兼容补丁）
apply_theme()

# 顶部导航栏
render_nav(current="home")

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

    # Hero 摘要卡片
    render_hero(
        label="每日减脂目标",
        value=f"{result['fat_loss_calories']} 大卡",
        subtitle=f"预计每周减重约 0.5kg | 蛋白质 {result['protein']}g 保肌肉",
    )

    # 六个指标卡片（桌面 3 列，手机自动 2 列）
    st.subheader("详细方案")
    items = [
        ("基础代谢 (BMR)", f"{result['bmr']}", "大卡", "fc-blue"),
        ("每日消耗 (TDEE)", f"{result['tdee']}", "大卡", "fc-teal"),
        ("减脂建议摄入", f"{result['fat_loss_calories']}", "大卡", "fc-coral"),
        ("蛋白质", f"{result['protein']}", "g", "fc-coral"),
        ("碳水", f"{result['carbs']}", "g", "fc-purple"),
        ("脂肪", f"{result['fat']}", "g", "fc-amber"),
    ]
    render_metric_cards(items, cols=3)

elif "user_profile" in st.session_state:
    # 显示之前保存的数据
    p = st.session_state["user_profile"]
    result = calculate_tdee(p["weight"], p["height"], p["age"], p["gender"], p["activity_level"])

    render_hero(
        label="每日减脂目标",
        value=f"{result['fat_loss_calories']} 大卡",
        subtitle=f"预计每周减重约 0.5kg | 蛋白质 {result['protein']}g 保肌肉",
    )

    st.subheader("详细方案")
    items = [
        ("基础代谢 (BMR)", f"{result['bmr']}", "大卡", "fc-blue"),
        ("每日消耗 (TDEE)", f"{result['tdee']}", "大卡", "fc-teal"),
        ("减脂建议摄入", f"{result['fat_loss_calories']}", "大卡", "fc-coral"),
        ("蛋白质", f"{result['protein']}", "g", "fc-coral"),
        ("碳水", f"{result['carbs']}", "g", "fc-purple"),
        ("脂肪", f"{result['fat']}", "g", "fc-amber"),
    ]
    render_metric_cards(items, cols=3)

else:
    st.markdown("在左侧填入你的身体数据，点击「计算我的减脂方案」开始")

st.markdown("---")
st.markdown("上方导航栏可切换功能：**AI 对话** | **饮食记录** | **进度追踪**")
