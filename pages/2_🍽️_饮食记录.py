"""
饮食记录页面 - 记录每天吃了什么，自动计算热量和宏量素

功能：
1. 选择食物 + 重量 + 餐次，自动计算热量
2. 三餐打卡检测：全部完成可生成打卡海报
3. 海报生成：上传照片 + 选择励志话术 + 输出 16:9 海报
"""

import streamlit as st
from core.food_data import get_food_nutrition, FOOD_DATABASE
from core.ui import apply_theme, render_bottom_nav, render_metric_cards, render_diet_log_item
from core.poster import (
    get_random_quotes,
    calculate_diet_score,
    generate_poster,
    get_today_date_str,
)
from db.database import (
    save_diet_log,
    get_today_diet_logs,
    get_meal_completion,
    get_latest_user,
)

# 餐次选项：key -> (中文标签, emoji)
MEAL_OPTIONS = [
    ("breakfast", "早餐 🌅"),
    ("lunch", "午餐 ☀️"),
    ("dinner", "晚餐 🌙"),
    ("snack", "加餐 🍪"),
]


def render_poster_section(user_id, logs):
    """渲染海报生成区域（仅在用户 3 餐全打卡时调用）

    注意：必须先定义再调用，否则 Python 会报 NameError。
    """
    st.markdown(
        '<div class="fc-form-card" style="margin:16px 0;">'
        '<div class="fc-form-title">🎨 生成打卡海报</div>',
        unsafe_allow_html=True,
    )

    # 计算打分
    user_profile = st.session_state.get("user_profile")
    score = calculate_diet_score(logs, user_profile)

    # 显示当前分数（给用户预期）
    st.markdown(
        f'<div style="text-align:center;padding:12px 0;">'
        f'<div style="font-size:13px;color:var(--fc-text-muted);">当前完成度</div>'
        f'<div style="font-size:36px;font-weight:700;color:var(--fc-teal);">{score} 分</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 上传照片
    uploaded = st.file_uploader(
        "上传你的照片",
        type=["jpg", "jpeg", "png"],
        help="建议上传横向照片，系统会自动裁剪为 16:9 比例",
    )

    if uploaded is None:
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 显示预览
    st.markdown(
        '<div style="font-size:12px;color:var(--fc-text-muted);margin:8px 0;">'
        '预览（16:9 裁剪后）</div>',
        unsafe_allow_html=True,
    )

    # 生成 3 句励志话术（每次刷新随机）
    # 用 session_state 保存，保证用户多次尝试不会变（除非点"换一组"）
    if "poster_quotes" not in st.session_state or st.session_state.get("poster_quotes_refresh"):
        st.session_state["poster_quotes"] = get_random_quotes(3)
        st.session_state["poster_quotes_refresh"] = False

    # 励志话术选择
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            '<div style="font-size:13px;font-weight:600;margin:12px 0 4px;">'
            '选择一句你喜欢的</div>',
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("🔄 换一组", use_container_width=True, key="refresh_quotes"):
            st.session_state["poster_quotes_refresh"] = True
            st.rerun()

    selected_idx = st.radio(
        "励志话术",
        options=range(len(st.session_state["poster_quotes"])),
        format_func=lambda i: f"💬 {st.session_state['poster_quotes'][i]}",
        label_visibility="collapsed",
    )

    selected_quote = st.session_state["poster_quotes"][selected_idx]

    # 生成海报按钮
    if st.button("🎨 生成我的打卡海报", type="primary", use_container_width=True):
        with st.spinner("正在合成海报..."):
            try:
                poster_bytes = generate_poster(
                    uploaded.read(),
                    get_today_date_str(),
                    score,
                    selected_quote,
                )
                # 保存到 session_state 以便下载
                st.session_state["poster_bytes"] = poster_bytes
                st.session_state["poster_generated"] = True
            except Exception as e:
                st.error(f"生成失败：{e}")

    # 显示已生成的海报
    if st.session_state.get("poster_generated") and "poster_bytes" in st.session_state:
        st.markdown(
            '<div style="font-size:13px;font-weight:600;margin:16px 0 8px;">'
            '✨ 海报生成成功！</div>',
            unsafe_allow_html=True,
        )
        st.image(st.session_state["poster_bytes"], use_column_width=True)

        # 下载按钮
        st.download_button(
            "⬇️ 下载海报（PNG）",
            data=st.session_state["poster_bytes"],
            file_name=f"fitcoach_checkin_{get_today_date_str().replace(' ', '_')}.png",
            mime="image/png",
            use_container_width=True,
            type="primary",
        )

    st.markdown('</div>', unsafe_allow_html=True)


# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(
    page_title="饮食记录",
    page_icon="🍽️",
    initial_sidebar_state="collapsed",
)

# 应用统一主题
apply_theme()

# 页面标题
st.markdown(
    '<div style="text-align:center;padding:16px 0 8px;">'
    '<h1 style="margin:0;">🍽️ 饮食记录</h1>'
    '<div style="font-size:13px;color:var(--fc-text-muted);margin-top:4px;">'
    '记录每一餐，自动统计热量和三大营养素</div>'
    '</div>',
    unsafe_allow_html=True,
)

# 检查是否有用户数据
if "user_id" not in st.session_state:
    latest = get_latest_user()
    if latest:
        st.session_state["user_id"] = latest[0]
    else:
        st.warning("请先在首页填写身体数据")
        st.markdown('<div style="height:120px;"></div>', unsafe_allow_html=True)
        render_bottom_nav(current="diet")
        st.stop()

# ============================================================
# 食物添加区（手机端自动堆叠）
# ============================================================
st.markdown(
    '<div class="fc-form-card" style="margin:12px 0;">'
    '<div class="fc-form-title">🍴 添加食物</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 1])
with col1:
    food_name = st.selectbox("选择食物", list(FOOD_DATABASE.keys()), label_visibility="collapsed")
with col2:
    grams = st.number_input("重量 (g)", min_value=10, max_value=2000, value=100, step=10, label_visibility="collapsed")

# 餐次选择（4 个 radio 平铺）
meal_keys = [m[0] for m in MEAL_OPTIONS]
meal_labels = [m[1] for m in MEAL_OPTIONS]
meal_type = st.radio(
    "餐次",
    options=meal_keys,
    format_func=lambda k: meal_labels[meal_keys.index(k)],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown('</div>', unsafe_allow_html=True)

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

    if st.button("添加到今日记录", type="primary", use_container_width=True):
        save_diet_log(
            st.session_state["user_id"],
            food_name,
            grams,
            nutrition["calories"],
            nutrition["protein"],
            nutrition["carbs"],
            nutrition["fat"],
            meal_type=meal_type,
        )
        st.success(f"已添加：{food_name} {grams}g")
        st.rerun()

# ============================================================
# 今日记录汇总
# ============================================================
st.subheader("今日饮食记录")
logs = get_today_diet_logs(st.session_state["user_id"])

if logs:
    total_cal = sum(log[5] for log in logs)
    total_protein = sum(log[6] for log in logs)
    total_carbs = sum(log[7] for log in logs)
    total_fat = sum(log[8] for log in logs)

    for log in logs:
        render_diet_log_item(log[3], log[4], log[5])

    st.markdown("---")

    items = [
        ("总热量", f"{total_cal:.0f}", "大卡", "fc-blue"),
        ("蛋白质", f"{total_protein:.1f}", "g", "fc-coral"),
        ("碳水", f"{total_carbs:.1f}", "g", "fc-teal"),
        ("脂肪", f"{total_fat:.1f}", "g", "fc-amber"),
    ]
    render_metric_cards(items, cols=4)

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

# ============================================================
# 三餐打卡区
# ============================================================
st.markdown("---")
st.markdown(
    '<div style="text-align:center;margin:24px 0 8px;">'
    '<h2 style="margin:0;font-size:20px;">📋 今日打卡</h2>'
    '<div style="font-size:12px;color:var(--fc-text-muted);margin-top:4px;">'
    '三餐都记录才能生成打卡海报哦</div>'
    '</div>',
    unsafe_allow_html=True,
)

completion = get_meal_completion(st.session_state["user_id"])

# 3 个餐次卡片（手机 2 列 + 1 列 / 桌面 3 列）
meals_display = [
    ("breakfast", "早餐", "🌅", "fc-amber"),
    ("lunch", "午餐", "☀️", "fc-blue"),
    ("dinner", "晚餐", "🌙", "fc-purple"),
]
meal_cards = "".join(
    f'<div class="fc-card {color}">'
    f'<div style="font-size:28px;line-height:1;margin-bottom:6px;">{emoji}</div>'
    f'<div class="fc-label">{label}</div>'
    f'<div class="fc-value" style="font-size:18px;">{"✓ 已记录" if done else "未记录"}</div>'
    f'</div>'
    for key, label, emoji, color in [(m[0], m[1], m[2], m[3]) for m in meals_display]
    for done in [completion[key]]
)
st.markdown(
    f'<div class="fc-grid fc-grid-3">{meal_cards}</div>',
    unsafe_allow_html=True,
)

# 根据完成度显示不同内容
if completion["all_done"]:
    # 三餐全部记录 → 解锁海报生成
    st.markdown(
        '<div style="text-align:center;margin:16px 0 8px;">'
        '<div style="font-size:24px;">🎉</div>'
        '<div style="font-size:15px;font-weight:600;color:var(--fc-teal);margin-top:4px;">'
        '太棒了！今日三餐全部打卡完成</div>'
        '<div style="font-size:12px;color:var(--fc-text-muted);margin-top:2px;">'
        '上传一张照片，生成专属打卡海报</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    render_poster_section(st.session_state["user_id"], logs)
else:
    # 还没全部完成 → 鼓励提示
    remaining = 3 - completion["completed_count"]
    if completion["completed_count"] == 0:
        msg = "今天还没有打卡任何一餐\n从现在开始，添加你的第一餐吧 💪"
    elif completion["completed_count"] == 1:
        msg = "已完成 1 餐，再坚持 2 餐就能解锁海报 ✨"
    else:
        msg = f"已完成 2 餐，再坚持最后一餐就能解锁海报 ✨"

    st.markdown(
        f'<div style="background:var(--fc-amber-light);border-radius:12px;'
        f'padding:16px;text-align:center;margin:16px 0;">'
        f'<div style="font-size:14px;color:var(--fc-amber);white-space:pre-line;">{msg}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# 底部导航栏
render_bottom_nav(current="diet")
