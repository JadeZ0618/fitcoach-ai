"""
饮食记录页面 - 记录每天吃了什么，自动计算热量和宏量素
"""

import streamlit as st
from core.food_data import get_food_nutrition, FOOD_DATABASE
from core.ui import apply_theme, render_nav, render_metric_cards, render_diet_log_item
from db.database import (
    save_diet_log,
    get_today_diet_logs,
    get_latest_user,
)

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(page_title="饮食记录", page_icon="🍽️")

# 应用统一主题
apply_theme()

# 顶部导航栏
render_nav(current="diet")

st.title("饮食记录")
st.markdown("记录你今天吃了什么")

# 检查是否有用户数据
if "user_id" not in st.session_state:
    latest = get_latest_user()
    if latest:
        st.session_state["user_id"] = latest[0]
    else:
        st.warning("请先在首页填写身体数据")
        st.stop()

# 食物选择和重量输入（手机端自动堆叠）
col1, col2 = st.columns([3, 1])

with col1:
    food_name = st.selectbox("选择食物", list(FOOD_DATABASE.keys()))
with col2:
    grams = st.number_input("重量 (g)", min_value=10, max_value=2000, value=100, step=10)

# 显示营养信息
nutrition = get_food_nutrition(food_name, grams)
if nutrition:
    st.info(
        f"{food_name} {grams}g  |  "
        f"热量 {nutrition['calories']} 大卡  |  "
        f"蛋白质 {nutrition['protein']}g  |  "
        f"碳水 {nutrition['carbs']}g  |  "
        f"脂肪 {nutrition['fat']}g"
    )

    if st.button("添加到今日记录", type="primary"):
        save_diet_log(
            st.session_state["user_id"],
            food_name,
            grams,
            nutrition["calories"],
            nutrition["protein"],
            nutrition["carbs"],
            nutrition["fat"],
        )
        st.success(f"已添加：{food_name} {grams}g")
        st.rerun()

# 今日记录汇总
st.subheader("今日饮食记录")
logs = get_today_diet_logs(st.session_state["user_id"])

if logs:
    total_cal = sum(log[5] for log in logs)
    total_protein = sum(log[6] for log in logs)
    total_carbs = sum(log[7] for log in logs)
    total_fat = sum(log[8] for log in logs)

    # 用卡片样式渲染每条记录（比 st.text 好看）
    for log in logs:
        render_diet_log_item(log[3], log[4], log[5])

    st.markdown("---")

    # 营养汇总卡片（桌面 4 列，手机自动 2 列）
    items = [
        ("总热量", f"{total_cal:.0f}", "大卡", "fc-blue"),
        ("蛋白质", f"{total_protein:.1f}", "g", "fc-coral"),
        ("碳水", f"{total_carbs:.1f}", "g", "fc-teal"),
        ("脂肪", f"{total_fat:.1f}", "g", "fc-amber"),
    ]
    render_metric_cards(items, cols=4)

    # 和目标对比
    if "user_profile" in st.session_state:
        from core.tdee import calculate_tdee

        p = st.session_state["user_profile"]
        result = calculate_tdee(
            p["weight"], p["height"], p["age"], p["gender"], p["activity_level"]
        )
        remaining = result["fat_loss_calories"] - total_cal
        if remaining > 0:
            st.success(f"今日还可摄入 {remaining:.0f} 大卡")
        else:
            st.warning(f"今日已超标 {abs(remaining):.0f} 大卡，注意控制！")
else:
    st.info("今天还没有记录，添加你的第一餐吧！")
