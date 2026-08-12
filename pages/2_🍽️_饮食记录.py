"""
饮食记录页面 - 记录每天吃了什么，自动计算热量和宏量素
"""

import streamlit as st
from core.food_data import get_food_nutrition, FOOD_DATABASE
from db.database import (
    save_diet_log,
    get_today_diet_logs,
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

st.set_page_config(page_title="饮食记录", page_icon="🍽️")
st.title("🍽️ 饮食记录")
st.markdown("记录你今天吃了什么")

# 检查是否有用户数据
if "user_id" not in st.session_state:
    latest = get_latest_user()
    if latest:
        st.session_state["user_id"] = latest[0]
    else:
        st.warning("请先在首页填写身体数据")
        st.stop()

# 食物选择和重量输入
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

    for log in logs:
        st.text(f"  {log[3]} {log[4]}g  -  {log[5]} 大卡")

    st.markdown("---")
    st.markdown(
        f'<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0;">'
        f'<div style="background: #f0f7ff; padding: 16px; border-radius: 8px; text-align: center;">'
        f'<div style="font-size: 13px; color: #666;">总热量</div>'
        f'<div style="font-size: 24px; font-weight: bold; color: #1f77b4;">{total_cal:.0f}</div>'
        f'<div style="font-size: 11px; color: #999;">大卡</div>'
        f'</div>'
        f'<div style="background: #fff5f0; padding: 16px; border-radius: 8px; text-align: center;">'
        f'<div style="font-size: 13px; color: #666;">蛋白质</div>'
        f'<div style="font-size: 24px; font-weight: bold; color: #ff7f0e;">{total_protein:.1f}</div>'
        f'<div style="font-size: 11px; color: #999;">g</div>'
        f'</div>'
        f'<div style="background: #f0fff4; padding: 16px; border-radius: 8px; text-align: center;">'
        f'<div style="font-size: 13px; color: #666;">碳水</div>'
        f'<div style="font-size: 24px; font-weight: bold; color: #2ca02c;">{total_carbs:.1f}</div>'
        f'<div style="font-size: 11px; color: #999;">g</div>'
        f'</div>'
        f'<div style="background: #fffbf0; padding: 16px; border-radius: 8px; text-align: center;">'
        f'<div style="font-size: 13px; color: #666;">脂肪</div>'
        f'<div style="font-size: 24px; font-weight: bold; color: #d4a017;">{total_fat:.1f}</div>'
        f'<div style="font-size: 11px; color: #999;">g</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

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
