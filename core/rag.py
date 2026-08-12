"""
RAG（检索增强生成）模块 — 给 AI 配一本"参考书"

这个模块做什么？
1. 读取 knowledge/ 目录下的所有 .md 文档（就是 Jade 写的减脂经验）
2. 把文档切成小块（chunk），每块转成向量存到 ChromaDB 里
3. 用户提问时，从知识库里搜索最相关的几段内容
4. 把搜到的内容拼到 prompt 里，让 DeepSeek 结合这些经验来回答

什么是向量？
- 就是把一段文字变成一串数字（比如 384 个数字）
- 意思相近的文字，数字也接近
- 搜索时把用户的问题也变成数字，找最接近的几段文字
- ChromaDB 自动帮你做这件事，不用手动算

什么是 ChromaDB？
- 一个开源的向量数据库，专门用来存和搜索向量
- 类似 SQLite 存表格数据，ChromaDB 存的是文字的向量
"""

import os
from pathlib import Path

import chromadb


# knowledge 目录的绝对路径（和 rag.py 同级的 knowledge 文件夹）
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

# ChromaDB 数据存储路径（向量化后的数据存在这里，下次启动不用重新算）
CHROMA_DB_DIR = Path(__file__).parent.parent / "chroma_db"

# 集合名称（ChromaDB 里用集合来分类管理文档）
COLLECTION_NAME = "fitcoach_knowledge"

# 全局缓存，避免每次调用都重新初始化数据库连接
_collection = None


def _split_markdown(content: str, source: str) -> list[dict]:
    """
    把 Markdown 文档按 ## 标题切成小块

    为什么要切块？
    - 一整篇文档太长了，直接塞给 AI 会超字数限制
    - 切成小块后，可以只把最相关的几块发给 AI
    - 按 ## 标题切，每块是一个完整的主题，比按固定字数切更有意义

    参数:
        content: Markdown 文档的文本内容
        source: 文件名（用来记录这段内容来自哪个文件）

    返回:
        列表，每个元素是 {"text": 文本, "source": 来源, "title": 标题}
    """
    chunks = []
    current_title = ""
    current_lines = []

    for line in content.split("\n"):
        # 遇到 ## 标题，把之前积累的内容存为一个 chunk
        if line.startswith("## "):
            # 先把之前的内容存起来
            if current_lines:
                text = "\n".join(current_lines).strip()
                if text:  # 跳过空块
                    chunks.append({
                        "text": f"{current_title}\n{text}" if current_title else text,
                        "source": source,
                        "title": current_title,
                    })
            # 开始新的块
            current_title = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    # 最后一块
    if current_lines:
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append({
                "text": f"{current_title}\n{text}" if current_title else text,
                "source": source,
                "title": current_title,
            })

    return chunks


def _load_documents() -> list[dict]:
    """
    读取 knowledge/ 目录下所有 .md 文件，切成小块

    返回:
        列表，每个元素是 {"text": 文本, "source": 文件名, "title": 标题}
    """
    all_chunks = []

    if not KNOWLEDGE_DIR.exists():
        return all_chunks

    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        # 跳过大纲文件和 README
        if md_file.name in ("WRITING_GUIDE.md", "README.md"):
            continue

        content = md_file.read_text(encoding="utf-8")
        chunks = _split_markdown(content, md_file.name)
        all_chunks.extend(chunks)

    return all_chunks


def _get_collection():
    """
    获取 ChromaDB 的集合（如果还没初始化就初始化）

    第一次调用时会：
    1. 连接 ChromaDB（数据存在 chroma_db/ 目录）
    2. 读取 knowledge/ 下所有文档
    3. 把文档切块、向量化、存入数据库
    4. 后续调用直接用缓存，不用重复处理
    """
    global _collection

    if _collection is not None:
        return _collection

    # 创建 ChromaDB 持久化客户端（数据存在磁盘上，重启不丢）
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "FitCoach AI 减脂知识库"},
    )

    # 如果集合里已经有数据，说明之前加载过，直接用
    if collection.count() > 0:
        _collection = collection
        return _collection

    # 第一次：加载文档并存入
    chunks = _load_documents()

    if not chunks:
        # 知识库为空（Jade 还没写文档），返回空集合
        # 后续 search 时会返回空结果
        _collection = collection
        return _collection

    # 把每个 chunk 存入 ChromaDB
    # ChromaDB 会自动把文本转成向量存储
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {"source": chunk["source"], "title": chunk["title"]}
        for chunk in chunks
    ]
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    _collection = collection
    return _collection


def search_knowledge(query: str, n_results: int = 3) -> list[dict]:
    """
    根据用户的问题，从知识库中搜索最相关的内容

    参数:
        query: 用户的提问，比如"减脂期怎么吃碳水"
        n_results: 返回最相关的几条（默认 3 条）

    返回:
        列表，每个元素是 {"text": 文本, "source": 来源, "score": 相似度}
        如果知识库为空，返回空列表
    """
    collection = _get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )

    # 整理结果
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    search_results = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        search_results.append({
            "text": doc,
            "source": meta.get("source", ""),
            "title": meta.get("title", ""),
            "score": 1 - dist,  # 距离越小越相似，转成相似度分数
        })

    return search_results


def get_context_for_prompt(query: str, n_results: int = 3) -> str:
    """
    搜索知识库，把结果格式化为可以直接拼到 prompt 里的文本

    如果搜不到相关内容，返回空字符串（不影响正常对话）

    参数:
        query: 用户的提问
        n_results: 搜索几条

    返回:
        格式化的知识库参考内容，比如：
        【参考知识 1】（来源：my_diet.md）
        热量缺口是减脂的唯一真理...
        【参考知识 2】（来源：my_training.md）
        ...
    """
    results = search_knowledge(query, n_results)

    if not results:
        return ""

    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(
            f"【参考知识 {i}】（来源：{result['source']}）\n{result['text']}"
        )

    return "\n\n".join(context_parts)


def get_knowledge_stats() -> dict:
    """
    获取知识库统计信息（用于在页面上显示知识库状态）

    返回:
        {"total_chunks": 文档块数, "is_ready": 是否有数据}
    """
    try:
        collection = _get_collection()
        count = collection.count()
        return {"total_chunks": count, "is_ready": count > 0}
    except Exception:
        return {"total_chunks": 0, "is_ready": False}


def rebuild_knowledge_base():
    """
    重建知识库（当 Jade 更新了文档后调用）

    删除旧数据，重新加载文档
    """
    global _collection

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    # 删除旧集合
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    # 清除缓存，下次调用 _get_collection 会重新加载
    _collection = None
    _get_collection()
