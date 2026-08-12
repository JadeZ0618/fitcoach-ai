"""
FitCoach AI - 共享 UI 主题模块

设计理念（2026-08-12 重构）：
1. 配色统一管理 - 改一处全局生效
2. 响应式 - 手机 < 768px 自动切换 2 列布局
3. 移动端友好 - 侧边栏默认收起 / 隐藏，底部固定 Tab 栏
4. 兼容性补丁 - structuredClone polyfill + 滚动条
"""

import streamlit as st


# ============================================================
# 主题 CSS（所有页面共享，一处修改全局生效）
# ============================================================

_THEME_CSS = """
<script>
// 兼容老浏览器 / 内嵌 webview（WorkBuddy 浏览器缺少 structuredClone）
if (typeof structuredClone === 'undefined') {
    window.structuredClone = function(obj) { return JSON.parse(JSON.stringify(obj)); };
}
// ========== 底部 Tab 栏 class 自动注入 ==========
// 给所有 "含 page_link 的 stHorizontalBlock" 加 fc-nav-ready class，
// 这样 CSS 可以用普通 class 选择器定位，避开 :has() 的兼容性问题
function _fcMarkBottomNav() {
    var blocks = document.querySelectorAll('[data-testid="stHorizontalBlock"]');
    for (var i = 0; i < blocks.length; i++) {
        var b = blocks[i];
        if (b.querySelector('[data-testid="stPageLink-NavLink"]') && !b.classList.contains('fc-nav-ready')) {
            b.classList.add('fc-nav-ready');
        }
    }
}
_fcMarkBottomNav();
// 监听 DOM 变化（Streamlit rerun 时会替换元素）
try {
    var _fcObserver = new MutationObserver(function() { _fcMarkBottomNav(); });
    _fcObserver.observe(document.body, {childList: true, subtree: true});
} catch(e) { /* 老浏览器不支持 MutationObserver 时跳过 */ }
</script>
<style>
/* ===== 配色变量（统一管理，改这里全局生效） ===== */
:root {
    --fc-teal: #0F6E56;
    --fc-teal-light: #E1F5EE;
    --fc-blue: #185FA5;
    --fc-blue-light: #E6F1FB;
    --fc-coral: #D85A30;
    --fc-coral-light: #FAECE7;
    --fc-amber: #854F0B;
    --fc-amber-light: #FAEEDA;
    --fc-purple: #534AB7;
    --fc-purple-light: #EEEDFE;
    --fc-gray: #5F5E5A;
    --fc-gray-light: #F1EFE8;
    --fc-bg: #F7F9FC;
    --fc-text: #2C2C2A;
    --fc-text-muted: #888780;
    --fc-radius: 12px;
    --fc-radius-sm: 8px;
}

/* ===== 全局背景 ===== */
html, body {
    overflow-y: scroll !important;
    background-color: var(--fc-bg);
}
[data-testid="stAppViewContainer"] {
    overflow-y: scroll !important;
    background-color: var(--fc-bg);
    /* 关键：让底部 Tab 栏不遮挡最后内容 */
    padding-bottom: 72px !important;
}

/* ===== 滚动条 ===== */
::-webkit-scrollbar { -webkit-appearance: none; width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,.15); border-radius: 4px; }
::-webkit-scrollbar-track { background: transparent; }

/* ===== 标题样式 ===== */
h1 {
    font-size: 24px !important;
    font-weight: 600 !important;
    color: var(--fc-text) !important;
}
h2, h3 {
    font-weight: 500 !important;
    color: var(--fc-text) !important;
}

/* ===== 侧边栏美化（桌面端默认收起；移动端完全隐藏） ===== */
[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #eee;
}
[data-testid="stSidebar"] header {
    color: var(--fc-teal) !important;
    border-bottom: 2px solid var(--fc-teal-light);
    padding-bottom: 8px;
}

/* ===== 按钮美化 ===== */
.stButton > button {
    border-radius: var(--fc-radius-sm) !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* ===== 表单输入圆角 ===== */
.stSelectbox > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {
    border-radius: var(--fc-radius-sm) !important;
}

/* ===== 卡片网格（响应式核心） ===== */
.fc-grid {
    display: grid;
    gap: 12px;
    margin: 16px 0;
}
.fc-grid-2 { grid-template-columns: repeat(2, 1fr); }
.fc-grid-3 { grid-template-columns: repeat(3, 1fr); }
.fc-grid-4 { grid-template-columns: repeat(4, 1fr); }

/* ===== 卡片样式 ===== */
.fc-card {
    border-radius: var(--fc-radius);
    padding: 16px;
    text-align: center;
    border-top: 3px solid;
    transition: transform 0.2s, box-shadow 0.2s;
}
.fc-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.fc-card .fc-label {
    font-size: 13px;
    color: var(--fc-text-muted);
    margin-bottom: 8px;
}
.fc-card .fc-value {
    font-size: 26px;
    font-weight: 700;
}
.fc-card .fc-unit {
    font-size: 12px;
    color: var(--fc-text-muted);
    margin-top: 4px;
}

/* ===== 卡片配色（背景浅色 + 顶部色条 + 数字深色） ===== */
.fc-teal   { background: var(--fc-teal-light);   border-top-color: var(--fc-teal); }
.fc-teal .fc-value   { color: var(--fc-teal); }
.fc-blue   { background: var(--fc-blue-light);   border-top-color: var(--fc-blue); }
.fc-blue .fc-value   { color: var(--fc-blue); }
.fc-coral  { background: var(--fc-coral-light);  border-top-color: var(--fc-coral); }
.fc-coral .fc-value  { color: var(--fc-coral); }
.fc-amber  { background: var(--fc-amber-light);  border-top-color: var(--fc-amber); }
.fc-amber .fc-value  { color: var(--fc-amber); }
.fc-purple { background: var(--fc-purple-light); border-top-color: var(--fc-purple); }
.fc-purple .fc-value { color: var(--fc-purple); }
.fc-gray   { background: var(--fc-gray-light);   border-top-color: var(--fc-gray); }
.fc-gray .fc-value   { color: var(--fc-gray); }

/* ===== Hero 摘要卡片（首页大号展示） ===== */
.fc-hero {
    border-radius: var(--fc-radius);
    padding: 20px;
    margin: 12px 0;
    background: var(--fc-teal-light);
    border: 1px solid #9FE1CB;
    text-align: center;
}
.fc-hero .fc-hero-label {
    font-size: 14px;
    color: var(--fc-teal);
    margin-bottom: 4px;
}
.fc-hero .fc-hero-value {
    font-size: 32px;
    font-weight: 700;
    color: var(--fc-teal);
}
.fc-hero .fc-hero-sub {
    font-size: 13px;
    color: var(--fc-text-muted);
    margin-top: 6px;
}

/* ===== Hero 欢迎语（首页顶部） ===== */
.fc-welcome {
    text-align: center;
    padding: 24px 16px 8px;
}
.fc-welcome h1 {
    font-size: 28px !important;
    color: var(--fc-teal) !important;
    margin-bottom: 8px !important;
}
.fc-welcome p {
    font-size: 14px;
    color: var(--fc-text-muted);
    margin: 0;
}

/* ===== 表单容器（首页中央表单卡） ===== */
.fc-form-card {
    background: white;
    border-radius: var(--fc-radius);
    padding: 24px;
    margin: 16px 0;
    border: 1px solid #eee;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.fc-form-card .fc-form-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--fc-text);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ===== 快速示例按钮 ===== */
.fc-quick-examples {
    background: var(--fc-teal-light);
    border-radius: var(--fc-radius);
    padding: 16px;
    margin: 12px 0;
}
.fc-quick-examples .fc-quick-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--fc-teal);
    margin-bottom: 10px;
}
.fc-quick-examples .stButton > button {
    background: white !important;
    border: 1px solid var(--fc-teal) !important;
    color: var(--fc-teal) !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
    min-height: auto !important;
}

/* ===== 聊天消息圆角 ===== */
[data-testid="stChatMessage"] {
    border-radius: var(--fc-radius) !important;
}

/* ===== 食物记录列表项 ===== */
.fc-log-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    margin: 6px 0;
    background: white;
    border-radius: var(--fc-radius-sm);
    border: 1px solid #eee;
}
.fc-log-item .fc-log-name {
    font-size: 14px;
    color: var(--fc-text);
}
.fc-log-item .fc-log-cal {
    font-size: 14px;
    font-weight: 600;
    color: var(--fc-blue);
}

/* ============================================================
   底部 Tab 栏（移动端友好，桌面端也显示）
   JS 脚本会扫描所有 stHorizontalBlock，
   给含 page_link 的那个加 .fc-nav-ready class
   ============================================================ */
.fc-nav-ready {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    background: white !important;
    border-top: 1px solid #e8e8e8 !important;
    padding: 4px 8px !important;
    padding-bottom: calc(4px + env(safe-area-inset-bottom, 0px)) !important;
    z-index: 999 !important;
    box-shadow: 0 -2px 12px rgba(0,0,0,0.06) !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
}

.fc-nav-ready [data-testid="column"] {
    flex: 1 1 0% !important;
    min-width: 0 !important;
    width: auto !important;
    padding: 0 4px !important;
}

.fc-nav-ready a[data-testid="stPageLink-NavLink"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    padding: 6px 4px !important;
    font-size: 12px !important;
    line-height: 1.3 !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: var(--fc-radius-sm) !important;
    margin: 0 !important;
    min-height: 50px !important;
    color: var(--fc-text-muted) !important;
    text-decoration: none !important;
}

.fc-nav-ready a[data-testid="stPageLink-NavLink"]:hover {
    background: var(--fc-gray-light) !important;
    border-color: var(--fc-gray-light) !important;
    color: var(--fc-teal) !important;
}

/* 激活态（当前页面） */
.fc-nav-active {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    padding: 6px 4px !important;
    min-height: 50px !important;
    font-size: 12px !important;
    line-height: 1.3 !important;
    color: var(--fc-teal) !important;
    background: var(--fc-teal-light) !important;
    border-radius: var(--fc-radius-sm) !important;
    font-weight: 600 !important;
}

/* ===== 响应式：手机端 (< 768px) ===== */
@media (max-width: 768px) {
    /* 移动端完全隐藏侧边栏（不需要，已经有底部 Tab） */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* 卡片自动变为 2 列 */
    .fc-grid-3, .fc-grid-4 {
        grid-template-columns: repeat(2, 1fr) !important;
    }
    /* 卡片内边距缩小 */
    .fc-card { padding: 12px; }
    .fc-card .fc-value { font-size: 22px; }
    .fc-card .fc-label { font-size: 12px; }
    /* Hero 缩小 */
    .fc-hero { padding: 16px; }
    .fc-hero .fc-hero-value { font-size: 26px; }
    /* 标题缩小 */
    h1 { font-size: 20px !important; }
    .fc-welcome h1 { font-size: 22px !important; }
    /* 按钮加大触控区 */
    .stButton > button {
        min-height: 44px;
    }
    /* 减少页面内边距 */
    [data-testid="stAppViewContainer"] .block-container {
        padding-left: 12px !important;
        padding-right: 12px !important;
        padding-top: 12px !important;
    }
    /* 表单卡缩小内边距 */
    .fc-form-card {
        padding: 16px !important;
    }
}

/* ===== 响应式：大屏桌面 (>= 1200px) ===== */
@media (min-width: 1200px) {
    /* 限制内容最大宽度，避免太宽难读 */
    [data-testid="stAppViewContainer"] .block-container {
        max-width: 900px;
    }
}

/* ===== 聊天输入框位置优化（移动端不与底部 Tab 重叠） ===== */
[data-testid="stChatInput"] {
    z-index: 998;
}
</style>
"""


def apply_theme():
    """在每个页面顶部调用，应用统一主题样式。

    包含：配色变量、响应式布局、卡片样式、滚动条、structuredClone 补丁、
    移动端侧边栏隐藏、底部 Tab 栏 fixed 定位。
    """
    st.markdown(_THEME_CSS, unsafe_allow_html=True)


def render_bottom_nav(current="home"):
    """渲染底部 Tab 栏（手机和桌面都显示）。

    通过 JS 自动给含 page_link 的 stHorizontalBlock 加 fc-nav-ready class，
    CSS 再用 class 选择器把它 fixed 到屏幕底部。
    当前页面用高亮激活样式显示。

    Args:
        current: 当前页面标识
            "home" / "chat" / "diet" / "progress"
    """
    pages = [
        ("main.py", "🔥", "首页", "home"),
        ("pages/1_🤖_AI对话.py", "🤖", "AI", "chat"),
        ("pages/2_🍽️_饮食记录.py", "🍽️", "饮食", "diet"),
        ("pages/3_📈_进度追踪.py", "📈", "进度", "progress"),
    ]
    cols = st.columns(4)
    for i, (page, icon, label, key) in enumerate(pages):
        with cols[i]:
            if key == current:
                # 当前页面：显示高亮激活样式（不是链接，不能点击）
                st.markdown(
                    f'<div class="fc-nav-active">{icon}<span>{label}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                # 其他页面：用 st.page_link 渲染为可点击按钮（Streamlit 处理路由）
                st.page_link(page, label=f"{icon} {label}", use_container_width=True)


def render_metric_cards(items, cols=3):
    """渲染指标卡片网格（响应式）。

    手机自动 2 列，桌面按 cols 指定列数。

    Args:
        items: list of (label, value, unit, color_class) tuples
            color_class 可选: "fc-teal", "fc-blue", "fc-coral",
                              "fc-amber", "fc-purple", "fc-gray"
        cols: 桌面端列数 (2, 3, 或 4)
    """
    grid_class = f"fc-grid-{cols}"
    cards_html = "".join(
        f'<div class="fc-card {color}">'
        f'<div class="fc-label">{label}</div>'
        f'<div class="fc-value">{value}</div>'
        f'<div class="fc-unit">{unit}</div>'
        f'</div>'
        for label, value, unit, color in items
    )
    st.markdown(
        f'<div class="fc-grid {grid_class}">{cards_html}</div>',
        unsafe_allow_html=True,
    )


def render_hero(label, value, subtitle=""):
    """渲染首页的摘要卡片（大号，突出显示）。"""
    sub_html = f'<div class="fc-hero-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="fc-hero">'
        f'<div class="fc-hero-label">{label}</div>'
        f'<div class="fc-hero-value">{value}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_welcome(title, subtitle=""):
    """渲染首页顶部欢迎语。"""
    sub_html = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="fc-welcome">'
        f'<h1>{title}</h1>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_form_card(title, icon="📝"):
    """渲染一个表单容器卡（替代把表单塞进侧边栏）。

    用法（with 语法）：
        with render_form_card("你的身体数据", "🧍"):
            st.text_input(...)
            if st.form_submit_button("提交"):
                ...

    注意：实际渲染的是一个 <div> 容器，markdown 标签无法 with，
    所以请用 render_form_card_open/close 或简化版本。
    """
    pass  # 占位，实际不用 with，直接渲染


def render_diet_log_item(name, grams, calories):
    """渲染饮食记录列表项（比 st.text 更好看）。"""
    st.markdown(
        f'<div class="fc-log-item">'
        f'<span class="fc-log-name">{name} {grams}g</span>'
        f'<span class="fc-log-cal">{calories} 大卡</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
