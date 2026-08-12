"""
AI 对话页面 - 和减脂助手聊天

在模拟模式下使用预设回答，配置 API Key 后调用真实 DeepSeek AI
使用 Streamlit 原生 chat_input + chat_message 实现聊天界面
"""

import streamlit as st
from core.llm import chat_with_ai, is_mock_mode
from core.ui import apply_theme, render_bottom_nav

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(
    page_title="AI 对话",
    page_icon="🤖",
    initial_sidebar_state="collapsed",  # 默认收起侧边栏
)

# 应用统一主题
apply_theme()

# 页面标题（小一点，留出空间给底部 Tab）
st.markdown(
    '<div style="text-align:center;padding:16px 0 8px;">'
    '<h1 style="margin:0;">🤖 AI 减脂助手</h1>'
    '<div style="font-size:13px;color:var(--fc-text-muted);margin-top:4px;">'
    '问问饮食、训练、平台期突破……已接入 DeepSeek + RAG 知识库</div>'
    '</div>',
    unsafe_allow_html=True,
)

if is_mock_mode():
    st.warning(
        "模拟模式：回答是预设的。配置 API Key 后获得真实 AI 对话。\n"
        "试试输入：减脂、饮食、运动、平台期"
    )
else:
    st.success("已连接 DeepSeek AI + RAG 知识库，可以自由提问！")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 显示聊天历史
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入框（原生 chat_input，回车即发送，手机端固定底部）
user_input = st.chat_input("问我任何关于减脂的问题...")

if user_input:
    # 显示并保存用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # 获取 AI 回复
    user_profile = st.session_state.get("user_profile", None)
    response = chat_with_ai(user_input, user_profile)

    # 显示并保存 AI 回复
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state["messages"].append({"role": "assistant", "content": response})

# 底部导航栏（必须最后渲染，CSS 自动 fixed 到底部）
render_bottom_nav(current="chat")
