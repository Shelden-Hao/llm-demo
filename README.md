# llm-demo

大模型应用开发的两个最小可运行示例，用来把「Agent」和「RAG」两条主线各跑通一遍。

## 目录

| 目录 | 内容 |
| :--- | :--- |
| `agent-demo/` | Agent 示例：让模型自主决定调用工具完成任务的循环 |
| `rag-demo/` | RAG 示例：文档切分、向量化、检索后交给模型回答 |

## 快速开始

```bash
cd agent-demo   # 或 cd rag-demo
pip install -r requirements.txt   # 若目录内提供
python main.py
```

各示例目录内如需模型 API Key，请通过环境变量或本地 `.env` 注入，不要写进代码（仓库已忽略 `.env`）。

## 说明

- 示例优先保证「可读、可直接跑」，不做过度的工程封装。
- 两个目录互相独立，可以单独打开阅读。
