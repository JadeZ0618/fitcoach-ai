"""
FitCoach AI - 智能减脂助手
主页面：仪表盘 + TDEE 计算器

布局重构（2026-08-12）：
- 表单放在主页中央（不再在侧边栏）
- 顶部欢迎语 + 引导
- 3 个快速示例按钮（一键填表，小白友好）
- 底部 Tab 栏（手机 + 桌面通用）
- 移动端自动隐藏侧边栏

运行方式：在项目根目录执行
    streamlit run main.py
"""

import streamlit as st
from core.tdee import calculate_tdee, ACTIVITY_LEVELS
from core.llm import is_mock_mode
from core.ui import (
    apply_theme,
    render_bottom_nav,
    render_metric_cards,
    render_hero,
    render_welcome,
)
from db.database import init_db, save_user_profile

# ============================================================
# 页面配置（必须是第一个 Streamlit 命令）
# ============================================================
st.set_page_config(
    page_title="FitCoach AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",  # 默认收起侧边栏
)

# 初始化数据库（第一次运行会创建表）
init_db()

# 应用统一主题
apply_theme()


# ============================================================
# 快速示例（小白友好，一键填表）
# ============================================================
QUICK_EXAMPLES = [
    {
        "name": "小刘",
        "gender": "male",
        "age": 28,
        "height": 175,
        "weight": 75.0,
        "activity": "轻度活动（每周运动 1-3 次）",
    },
    {
        "name": "小王",
        "gender": "female",
        "age": 26,
        "height": 165,
        "weight": 60.0,
        "activity": "中度活动（每周运动 3-5 次）",
    },
    {
        "name": "小张",
        "gender": "male",
        "age": 35,
        "height": 180,
        "weight": 90.0,
        "activity": "久坐不动（办公室工作，很少运动）",
    },
]


def render_result_section(p):
    """根据用户档案渲染结果区。

    Args:
        p: dict, 包含 name/gender/age/height/weight/activity_level
    """
    result = calculate_tdee(
        p["weight"], p["height"], p["age"], p["gender"], p["activity_level"]
    )

    # Hero 摘要
    render_hero(
        label="每日减脂目标",
        value=f"{result['fat_loss_calories']} 大卡",
        subtitle=f"预计每周减重约 0.5kg · 蛋白质 {result['protein']}g 保肌肉",
    )

    # 三个核心指标
    items_main = [
        ("基础代谢 (BMR)", f"{result['bmr']}", "大卡", "fc-blue"),
        ("每日总消耗 (TDEE)", f"{result['tdee']}", "大卡", "fc-teal"),
        ("减脂建议摄入", f"{result['fat_loss_calories']}", "大卡", "fc-coral"),
    ]
    render_metric_cards(items_main, cols=3)

    # 三个营养素
    items_nutri = [
        ("蛋白质", f"{result['protein']}g", "推荐量", "fc-coral"),
        ("碳水", f"{result['carbs']}g", "推荐量", "fc-purple"),
        ("脂肪", f"{result['fat']}g", "推荐量", "fc-amber"),
    ]
    render_metric_cards(items_nutri, cols=3)


def render_form(p=None):
    """渲染 TDEE 计算表单（不在侧边栏，在主页中央）。

    Args:
        p: dict, 已保存的用户档案（用于默认填充），None 则用初始值
    """
    # 用 HTML 把表单卡在一个白色背景块里
    st.markdown('<div class="fc-form-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="fc-form-title">🧍 你的身体数据</div>',
        unsafe_allow_html=True,
    )

    # 用 form 保证提交时统一收集
    with st.form("user_data_form", clear_on_submit=False):
        # 第一行：姓名 / 性别 / 年龄
        row1_col1, row1_col2, row1_col3 = st.columns([2, 1, 1])
        with row1_col1:
            name = st.text_input("昵称", value=(p or {}).get("name", "Jade"))
        with row1_col2:
            gender = st.selectbox(
                "性别",
                ["male", "female"],
                index=0 if (p or {}).get("gender", "male") == "male" else 1,
                format_func=lambda x: "男" if x == "male" else "女",
            )
        with row1_col3:
            age = st.number_input(
                "年龄",
                min_value=10,
                max_value=100,
                value=int((p or {}).get("age", 25)),
            )

        # 第二行：身高 / 体重 / 活动水平
        row2_col1, row2_col2 = st.columns([1, 1])
        with row2_col1:
            height = st.number_input(
                "身高 (cm)",
                min_value=100,
                max_value=250,
                value=int((p or {}).get("height", 170)),
            )
        with row2_col2:
            weight = st.number_input(
                "体重 (kg)",
                min_value=30.0,
                max_value=300.0,
                value=float((p or {}).get("weight", 70.0)),
                step=0.1,
            )

        activity = st.selectbox(
            "活动水平",
            list(ACTIVITY_LEVELS.keys()),
            index=list(ACTIVITY_LEVELS.keys()).index(
                (p or {}).get("activity_level", "轻度活动（每周运动 1-3 次）")
            ),
            help=f"当前值系数 = {ACTIVITY_LEVELS.get((p or {}).get('activity_level', '轻度活动（每周运动 1-3 次）'), 1.375)}",
        )

        submitted = st.form_submit_button(
            "🚀 生成我的减脂方案", type="primary", use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
    return submitted, name, gender, age, height, weight, activity


def handle_quick_example(idx: int):
    """处理快速示例按钮点击 - 把示例数据写进 session_state。"""
    example = QUICK_EXAMPLES[idx]
    st.session_state["user_profile"] = example.copy()
    st.session_state["user_profile"]["activity_level"] = example["activity"]
    # 触发重新渲染
    st.session_state["_trigger_calc"] = True


# ============================================================
# 主页内容
# ============================================================

# 顶部欢迎语
render_welcome(
    "🔥 FitCoach AI",
    "输入你的身体数据，AI 帮你算专属减脂方案（热量 + 三大营养素）",
)

# 模式提示
if is_mock_mode():
    st.info("当前运行在模拟模式。配置 DeepSeek API Key 后可启用 AI 对话。")

# 状态判定：是否已保存用户档案
has_profile = "user_profile" in st.session_state

# 主页三大区块
if has_profile and not st.session_state.pop("_show_form", False):
    # ----- 已填表状态：显示结果 + 「重新计算」按钮 -----
    p = st.session_state["user_profile"]

    # 顶部小信息条：当前用户
    user_label = f"{p['name']} · {p['weight']}kg · {p['height']}cm"
    st.markdown(
        f'<div style="text-align:center;color:var(--fc-text-muted);font-size:13px;margin:8px 0;">'
        f'📌 当前档案：{user_label}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 结果区
    render_result_section(p)

    # 「重新计算」按钮居中
    if st.button("🔄 重新计算", use_container_width=False, type="secondary"):
        st.session_state["_show_form"] = True
        st.rerun()

else:
    # ----- 未填表 / 选择重新计算状态：显示表单 -----

    # 快速示例（小白友好）
    st.markdown('<div class="fc-quick-examples">', unsafe_allow_html=True)
    st.markdown(
        '<div class="fc-quick-title">🚀 不知道填什么？点击下面的示例试试：</div>',
        unsafe_allow_html=True,
    )
    ex_cols = st.columns(len(QUICK_EXAMPLES))
    for i, ex in enumerate(QUICK_EXAMPLES):
        with ex_cols[i]:
            label = f"{'👨' if ex['gender']=='male' else '👩'} {ex['name']}"
            if st.button(label, key=f"ex_{i}", use_container_width=True):
                handle_quick_example(i)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 表单卡
    submitted, name, gender, age, height, weight, activity = render_form()

    if submitted:
        # 计算并保存
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
        st.success(f"✅ {name}，你的专属方案已生成！")
        st.rerun()

    # 表单下方的引导
    st.markdown(
        '<div style="text-align:center;color:var(--fc-text-muted);font-size:12px;margin-top:8px;">'
        '💡 不知道活动水平怎么选？办公室工作 = 久坐；每天散步 = 轻度；健身 3-5 次/周 = 中度'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# 底部导航栏（必须在页面最末，CSS 把它 fixed 到屏幕底部）
# ============================================================
render_bottom_nav(current="home")

# 页面底部说明
st.markdown(
    '<div style="text-align:center;color:var(--fc-text-muted);font-size:11px;margin:16px 0 8px;">'
    'FitCoach AI · 基于 Mifflin-St Jeor 公式 + DeepSeek 大模型'
    '</div>',
    unsafe_allow_html=True,
)
