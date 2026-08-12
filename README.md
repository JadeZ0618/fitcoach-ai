# 智能减脂助手

基于 AI 的个性化减脂管理工具，提供 TDEE 计算、饮食记录、AI 对话和进度追踪功能。

## 功能

- **TDEE 计算器**：根据身体数据计算基础代谢和每日消耗，生成减脂方案
- **饮食记录**：记录每日饮食，自动计算热量和宏量素，对比目标
- **AI 对话**：和 AI 减脂助手聊天，获取个性化建议（支持模拟模式）
- **进度追踪**：记录体重变化，可视化趋势图表

## 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 前端 | Streamlit | 纯 Python Web 框架 |
| AI | DeepSeek API + LangChain | 大模型对话 |
| 数据库 | SQLite | 轻量级关系型数据库 |
| 向量库 | ChromaDB | RAG 知识库（开发中） |
| 可视化 | Plotly | 交互式图表 |

## 快速开始

### 1. 安装依赖

```bash
cd fitcoach-ai
pip install -r requirements.txt
```

### 2. 运行

```bash
streamlit run main.py
```

浏览器会自动打开 http://localhost:8501

### 3. 配置 AI 对话（可选）

默认运行在模拟模式，AI 对话使用预设回答。要启用真实 AI：

1. 打开 https://platform.deepseek.com 注册
2. 充值（最低 1 元，做这个项目几块钱够用）
3. 创建 API Key，复制
4. 编辑 `.env` 文件：
   ```
   USE_MOCK_LLM=false
   DEEPSEEK_API_KEY=你复制的key
   ```
5. 重新运行 `streamlit run main.py`

## 项目结构

```
fitcoach-ai/
├── main.py                  # Streamlit 主入口（仪表盘）
├── pages/                   # 多页面
│   ├── 1_🤖_AI对话.py       # AI 对话
│   ├── 2_🍽️_饮食记录.py     # 饮食记录
│   └── 3_📈_进度追踪.py     # 进度追踪
├── core/                    # 核心业务逻辑
│   ├── tdee.py              # TDEE 计算
│   ├── llm.py               # LLM 调用（模拟/真实）
│   └── food_data.py         # 食物营养数据库
├── db/                      # 数据库
│   └── database.py          # SQLite 操作
├── knowledge/               # 减脂知识库（RAG 用，开发中）
├── data/                    # 数据库文件
├── .env                     # 环境变量配置
├── requirements.txt         # Python 依赖
└── README.md
```

## 开发计划

- [x] TDEE 计算器
- [x] 饮食记录 + 食物数据库
- [x] AI 对话（模拟模式 + DeepSeek API）
- [x] 进度追踪 + 体重图表
- [ ] RAG 知识库（个人减脂经验 -> 向量检索）
- [ ] 个性化饮食计划生成
- [ ] 运动计划推荐
- [ ] Docker 部署
