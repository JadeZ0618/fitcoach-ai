"""
AI 对话页面 - 和减脂助手聊天

在模拟模式下使用预设回答，配置 API Key 后调用真实 DeepSeek AI

使用 Streamlit 原生 chat_input + chat_message 实现聊天界面
（需要 Streamlit 1.24+，已通过 pip 升级解决）
"""

import streamlit as st
from core.llm import chat_with_ai, is_mock_mode

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

st.set_page_config(page_title="AI 对话", page_icon="🤖")
st.title("🤖 AI 对话")
st.markdown("和 FitCoach AI 聊聊减脂相关问题")

if is_mock_mode():
    st.warning(
        "模拟模式：回答是预设的。配置 API Key 后获得真实 AI 对话。\n"
        "试试输入：减脂、饮食、运动、平台期"
    )
else:
    st.success("已连接 DeepSeek AI，可以自由提问！")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 显示聊天历史
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入框（原生 chat_input，回车即发送）
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
