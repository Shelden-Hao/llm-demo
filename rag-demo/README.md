# RAG Demo - 智能服装客服系统

基于 **LangChain + ChromaDB + Tongyi (通义千问)** 的检索增强生成（RAG）演示项目，实现服装领域的智能问答客服系统。

## 功能特性

- **知识库管理** — 上传 TXT 文件自动分块、向量化存入 ChromaDB，基于 MD5 去重
- **智能问答** — 结合知识库检索结果 + 对话历史，通过大模型生成专业回答
- **流式输出** — 支持 Streamlit 流式展示 AI 回复
- **会话管理** — 基于文件的对话历史持久化存储，支持多会话隔离
- **双重 UI** — 知识库上传页 + 问答对话页，均基于 Streamlit 构建

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言模型 | Tongyi (qwen3-max) |
| 嵌入模型 | text-embedding-v4 (DashScope) |
| 向量数据库 | ChromaDB |
| 框架 | LangChain |
| Web UI | Streamlit |
| 文本分割 | RecursiveCharacterTextSplitter |

## 项目结构

```
rag-demo/
├── app_file_uploader.py     # Streamlit 知识库上传页面
├── app_qa.py                # Streamlit 智能问答页面
├── rag.py                   # RAG 核心链路（检索 + 生成）
├── knowledge_base.py        # 知识库服务（文本分块、向量化、MD5 去重）
├── vector_stores.py         # ChromaDB 向量存储封装
├── file_history_store.py    # 基于文件的对话历史存储
├── config_data.py           # 全局配置（模型、分块参数、会话等）
├── data/                    # 示例知识库文件
│   ├── 尺码推荐.txt
│   ├── 颜色选择.txt
│   └── 洗涤养护.txt
├── chroma_db/               # ChromaDB 持久化目录（自动生成）
├── chat_history/            # 对话历史文件目录（自动生成）
└── md5.text                 # 已处理文件的 MD5 记录
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.10+，并通过 Miniconda 或 venv 创建虚拟环境。

### 2. 安装依赖

```bash
pip install streamlit langchain langchain-chroma langchain-community dashscope chromadb
```

### 3. 配置 API 密钥

项目使用阿里云通义千问系列模型，需配置 DashScope API Key：

```bash
# Windows PowerShell 该命令可设置环境变量（临时生效），所以只能在该 PowerShell 运行相关命令
$env:DASHSCOPE_API_KEY = "你的 API Key"

# 或设置为系统环境变量（永久生效）
```

可从 https://help.aliyun.com/zh/model-studio/ 获取 API Key。

### 4. 配置参数（可选）

编辑 `config_data.py` 调整模型、分块策略等：

```python
embedding_model_name = "text-embedding-v4"    # 嵌入模型
chat_model_name = "qwen3-max"                # 对话模型
chunk_size = 1000                            # 文本分块大小
chunk_overlap = 100                          # 分块重叠
similarity_threshold = 1                     # 检索返回 Top-K 文档数
```

### 5. 启动服务

由于 Streamlit 多页面约定，使用以下方式运行：

```bash
# 启动知识库上传页面
streamlit run app_file_uploader.py

# 启动智能问答页面（新开终端）
streamlit run app_qa.py
```

或自行整合为多页面应用后统一启动。

### 6. 使用流程

1. 打开 **知识库上传页面**（默认 http://localhost:8501）
2. 上传 TXT 文件 → 文件被分割、向量化后存入 ChromaDB
3. 打开 **智能问答页面**（默认 http://localhost:8502）
4. 输入问题 → 系统检索相关文档片段 + 结合历史对话 → 生成回答

## 架构说明

### RAG 流程

```
用户输入
    │
    ▼
┌─────────────────────────────┐
│ 1. 检索 (Retrieve)          │
│    └─ 向量化用户 query       │
│    └─ ChromaDB 相似度搜索    │
│    └─ 返回 Top-K 文档片段    │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 2. 增强 (Augment)           │
│    └─ 检索结果 + 对话历史     │
│    └─ 填入 Prompt 模板       │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 3. 生成 (Generate)          │
│    └─ Tongyi LLM 生成回答    │
│    └─ 流式输出到前端         │
└─────────────────────────────┘
```

### 核心模块

- **KnowledgeBaseService** (`knowledge_base.py`): 处理文件上传，MD5 去重，文本分块，向量化存入
- **VectorStoreService** (`vector_stores.py`): 封装 ChromaDB 检索器，供 RAG 链调用
- **RagService** (`rag.py`): 组装完整的 LCEL 链（检索 → 增强 → 生成），集成对话历史
- **FileChatMessageHistory** (`file_history_store.py`): 以 JSON 文件存储对话历史，支持多 session

## 示例知识库

`data/` 目录下包含三个示例文件，覆盖服装领域的常见问题：

| 文件 | 内容 |
|------|------|
| 尺码推荐.txt | 身高体重与建议尺码对照表 |
| 颜色选择.txt | 肤色、场合、体型、季节的穿搭颜色建议 |
| 洗涤养护.txt | 不同材质服装的洗涤与保养方法 |
