"""
LLM 调用模块 - 连接 DeepSeek AI

两种模式：
1. 模拟模式（默认）：不需要 API Key，用预设回答，方便先跑起来
2. 真实模式：填入 DeepSeek API Key 后，调用真实 AI

什么是 API？
- API 就像一个服务员：你告诉他要点什么菜（发送请求），
  他去厨房传话（调用 DeepSeek 的服务器），然后把菜端给你（返回 AI 回答）
- API Key 就是你的会员卡，证明"这个请求是你发的"，也用来计费

切换方式：在 .env 文件中设置
- USE_MOCK_LLM=true  -> 模拟模式
- USE_MOCK_LLM=false -> 真实模式（需要 DEEPSEEK_API_KEY）

怎么获取 DeepSeek API Key：
1. 打开 https://platform.deepseek.com 注册
2. 充值（最低 1 元就能用很久，做这个项目几块钱够了）
3. 点击"API Keys" -> "创建 API Key"
4. 复制那串字符，粘贴到 .env 文件的 DEEPSEEK_API_KEY= 后面
5. 把 USE_MOCK_LLM 改成 false
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件里的配置（本地开发用）
load_dotenv()


def _get_config(key, default=""):
    """
    获取配置：优先从 Streamlit Cloud 的 secrets 读取，其次从 .env 读取

    为什么需要这个？
    - 本地开发时，配置存在 .env 文件里
    - 部署到 Streamlit Cloud 后，配置存在云端 secrets 面板里（更安全）
    - 这个函数自动适配两种环境，不用改代码
    """
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


def is_mock_mode():
    """
    检查是否在模拟模式

    逻辑：
    - 如果明确设置了 USE_MOCK_LLM=true，就用模拟模式
    - 如果没设 USE_MOCK_LLM 但有 API Key，自动用真实模式
    - 如果没有 API Key，用模拟模式
    """
    use_mock = str(_get_config("USE_MOCK_LLM", "")).lower() == "true"
    api_key = _get_config("DEEPSEEK_API_KEY", "")
    # 只有明确要求模拟模式，或者没有 API Key 时才用模拟
    return use_mock or not api_key


# 模拟回答库 - 常见减脂问题的预设回答
MOCK_RESPONSES = {
    "减脂": (
        "减脂的核心是热量缺口——每天消耗的热量大于摄入的热量。\n\n"
        "建议：\n"
        "1. 每天少吃 500 大卡，一周约减 0.5kg\n"
        "2. 蛋白质吃够（2g/kg 体重），防止掉肌肉\n"
        "3. 力量训练 + 有氧结合效果最好\n"
        "4. 不要节食，节食会降低代谢\n\n"
        "--- 模拟模式回答，配置 API Key 后可获得个性化建议 ---"
    ),
    "饮食": (
        "减脂期饮食建议：\n\n"
        "1. 主食选粗粮（糙米、燕麦、红薯），少吃精米白面\n"
        "2. 蛋白质优先：鸡胸肉、鱼虾、鸡蛋、豆腐\n"
        "3. 蔬菜多吃，热量低饱腹感强\n"
        "4. 少油少糖，但不要完全不吃脂肪\n"
        "5. 每天喝水 2L 以上\n\n"
        "--- 模拟模式回答，配置 API Key 后可获得个性化建议 ---"
    ),
    "运动": (
        "减脂期运动建议：\n\n"
        "1. 力量训练（3-4次/周）：深蹲、硬拉、卧推等复合动作\n"
        "2. 有氧运动（2-3次/周）：跑步、游泳、骑车 30-45 分钟\n"
        "3. 日常多走路，NEAT（非运动性热量消耗）很重要\n"
        "4. 训练后补充蛋白质，帮助恢复\n\n"
        "--- 模拟模式回答，配置 API Key 后可获得个性化建议 ---"
    ),
    "平台期": (
        "减脂平台期怎么破：\n\n"
        "1. 重新计算 TDEE（体重下降后消耗也会降）\n"
        "2. 安排一次 refeed day（吃回维持热量的碳水）\n"
        "3. 增加运动量或改变训练方式\n"
        "4. 检查是不是记录不准确（很多人低估了摄入）\n"
        "5. 放松心态，平台期是正常的生理适应\n\n"
        "--- 模拟模式回答，配置 API Key 后可获得个性化建议 ---"
    ),
}

DEFAULT_MOCK_RESPONSE = (
    "我是 FitCoach AI 减脂助手，可以帮你解答减脂相关的饮食、运动、营养问题。\n\n"
    "试试问我：\n"
    "- 减脂怎么吃？\n"
    "- 运动怎么安排？\n"
    "- 遇到平台期怎么办？\n\n"
    "--- 模拟模式回答，配置 API Key 后获得完整 AI 对话 ---"
)


def get_mock_response(user_input):
    """根据用户输入返回模拟回答"""
    for keyword, response in MOCK_RESPONSES.items():
        if keyword in user_input:
            return response
    return DEFAULT_MOCK_RESPONSE


def chat_with_ai(user_input, user_profile=None):
    """
    和 AI 对话

    参数:
        user_input: 用户输入的消息
        user_profile: 用户身体数据字典（可选，用于个性化回答）
            例如: {"height": 170, "weight": 70, "age": 25, "gender": "male"}

    返回:
        AI 的回复文本
    """
    if is_mock_mode():
        return get_mock_response(user_input)

    # === 真实模式：调用 DeepSeek API ===
    from openai import OpenAI

    api_key = _get_config("DEEPSEEK_API_KEY")
    # DeepSeek 兼容 OpenAI 接口，所以用 OpenAI 的库来调用
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # 构建 system prompt（系统提示词，告诉 AI 它的角色）
    system_prompt = (
        "你是 FitCoach AI，一个专业的减脂助手。"
        "根据用户的身体数据提供个性化的饮食和运动建议。"
        "回答要简洁、实用、接地气。"
    )

    # 如果有用户数据，加到提示词里
    if user_profile:
        system_prompt += (
            f"\n\n用户数据：身高 {user_profile.get('height', '未知')}cm，"
            f"体重 {user_profile.get('weight', '未知')}kg，"
            f"年龄 {user_profile.get('age', '未知')}岁，"
            f"性别 {user_profile.get('gender', '未知')}。"
        )

    # 调用 API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        stream=False,
    )

    return response.choices[0].message.content
