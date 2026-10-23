# llm-demo

大模型应用开发的两个最小可运行示例，把「Agent」和「RAG」两条主线各跑通一遍。两个目录都用 Streamlit 做界面，可以本地起页面点着看效果。

## 目录

| 目录 | 内容 | 入口 |
| :--- | :--- | :--- |
| `agent-demo/` | Agent 示例：`ReactAgent` 负责推理与工具调用，配合提示词与本地工具完成任务 | `app.py` |
| `rag-demo/` | RAG 示例：知识库上传、切分、向量化到 Chroma，检索后交给模型回答 | `app_qa.py`（问答）、`app_file_uploader.py`（建库） |

两个目录各自都有更详细的 `README.md`，先看子目录那份。

## 快速开始

```bash
# Agent 示例
cd agent-demo
pip install streamlit
streamlit run app.py

# RAG 示例
cd rag-demo
pip install streamlit
streamlit run app_file_uploader.py   # 第一步：上传文档建库
streamlit run app_qa.py              # 第二步：开始问答
```

## 关键文件

- `agent-demo/agent/react_agent.py`：ReAct 循环与工具调用的核心实现
- `rag-demo/config_data.py`：切分参数、Chroma 集合名与持久化目录（`./chroma_db`）
- `rag-demo/rag.py`：检索 + 生成的串联逻辑
- `md5.text`：已处理文件的指纹，用于跳过重复入库

## 说明

- 模型 API Key 请用环境变量或本地 `.env` 注入，不要写进代码（`.env` 已在忽略列表中）。
- `chroma_db/`、`chat_history/`、`logs/` 都是运行时产物，不需要提交。
