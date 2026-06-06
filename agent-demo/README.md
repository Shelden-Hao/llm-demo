# 智扫通智能客服 Agent Demo

基于 **LangChain + 通义千问(Qwen) + ChromaDB** 的扫地/扫拖机器人智能客服系统,支持 ReAct 风格的工具调用、RAG 知识检索和个性化使用报告生成,前端使用 Streamlit。

---

## 一、项目功能

| 功能 | 说明 |
|---|---|
| 多轮对话 | Streamlit 聊天界面,带历史消息上下文 |
| 专业知识问答 | 从 `data/` 下的 PDF/TXT 知识库做语义检索,结合 LLM 总结回答 |
| 天气查询 | 根据城市返回天气信息(模拟) |
| 用户信息获取 | 模拟获取用户 ID、所在城市、当前月份 |
| 个性化使用报告 | 查询外部 CSV 使用记录,生成 Markdown 格式的月度报告 |
| 提示词动态切换 | 通过中间件识别"报告生成"场景,自动切换到报告专用提示词 |
| 工具调用监控 | 装饰器中间件记录每次工具的入参、结果、耗时、异常 |
| 模型调用日志 | 记录模型调用前的消息数量、消息类型、内容 |

---

## 二、目录结构

```
agent-demo/
├── app.py                 # Streamlit 入口(聊天界面)
├── agent/                 # Agent 组件
│   ├── react_agent.py     # ReAct Agent 主类
│   ├── tools/
│   │   ├── agent_tools.py # 7 个 @tool 工具
│   │   └── middleware.py  # 3 个中间件
│   └── chroma_db/         # agent 模块自己的 chroma(空目录)
├── rag/                   # RAG 模块
│   ├── vector_store.py    # 向量库管理(加载/去重/入库)
│   ├── rag_service.py     # RAG 总结服务(retrieve + summarize)
│   └── chroma_db/         # Chroma 持久化目录
├── model/
│   └── factory.py         # 模型工厂(ChatModel + Embeddings)
├── utils/
│   ├── path_tool.py       # 统一绝对路径
│   ├── config_handler.py  # 读取 4 个 yaml 配置
│   ├── prompt_loader.py   # 加载 3 个 .txt 提示词
│   ├── file_handler.py    # MD5 计算 / 文件遍历 / PDF/TXT 加载
│   └── logger_handler.py  # 日志器(控制台 + 文件)
├── config/                # 4 个 yaml 配置
│   ├── agent.yml
│   ├── chroma.yml
│   ├── prompts.yml
│   └── rag.yml
├── prompts/               # 3 个提示词模板
│   ├── main_prompt.txt       # 系统主提示词(含工具说明)
│   ├── rag_summarize.txt     # RAG 总结提示词
│   └── report_prompt.txt     # 报告生成专用提示词
├── data/                  # 知识库数据
│   ├── external/records.csv # 用户使用记录(报告生成用)
│   └── *.pdf / *.txt        # 扫地机器人相关知识文档
├── chroma_db/             # 项目根的 chroma 持久化(与 rag/chroma_db 一致)
├── logs/                  # 日志目录(按天切分)
└── md5.text               # 已入库文件的 MD5 列表(去重用)
```

---

## 三、核心架构

```
┌─────────────────────────────────────────────────────────────┐
│  Streamlit UI (app.py)                                      │
│  st.chat_input() → st.session_state["agent"].execute_stream │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  ReactAgent (agent/react_agent.py)                          │
│  langchain.agents.create_agent()                            │
│  ┌──────────────────┐  ┌──────────────────────────────┐    │
│  │ chat_model       │  │ 7 个 tool                    │    │
│  │ (Qwen3-max)      │  │ • rag_summarize              │    │
│  └──────────────────┘  │ • get_weather                │    │
│                        │ • get_user_location          │    │
│  ┌──────────────────┐  │ • get_user_id                │    │
│  │ 3 个 middleware  │  │ • get_current_month          │    │
│  │ • monitor_tool   │  │ • fetch_external_data        │    │
│  │ • log_before_    │  │ • fill_context_for_report    │    │
│  │   model          │  └──────────────────────────────┘    │
│  │ • report_prompt_ │                                       │
│  │   switch(dynamic)│                                       │
│  └──────────────────┘                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│ RagSummarizeService  │    │ 外部 CSV 读取                │
│ (rag/rag_service.py) │    │ (agent_tools.fetch_external)│
│  retriever (k=3)     │    │                              │
│  prompt + LLM        │    │                              │
└──────────┬───────────┘    └──────────────────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ VectorStoreService           │
│ (rag/vector_store.py)        │
│ • 文件遍历 + MD5 去重        │
│ • RecursiveCharacterText     │
│   Splitter(chunk=200,        │
│   overlap=20)                │
│ • Chroma.add_documents()     │
│ • DashScopeEmbeddings        │
│   (text-embedding-v4)        │
└──────────────────────────────┘
```

---

## 四、关键设计点

### 1. 知识库加载与去重(`vector_store.py:33-114`)
- 遍历 `data/` 下所有 `.txt` / `.pdf`
- 计算**整文件** MD5,与 `md5.text` 里的历史 MD5 对比 → 已处理则跳过
- 没处理过:`PyPDFLoader` / `TextLoader` 读为 `Document` → `RecursiveCharacterTextSplitter` 切成 chunk → `vector_store.add_documents()` 入库 → 写 MD5

### 2. 报告场景提示词切换(`middleware.py:50-56` + `agent_tools.py:110-112`)
- `@dynamic_prompt` 装饰器在每次 LLM 调用前触发
- 初始 `runtime.context["report"] = False` → 加载主提示词
- Agent 调用 `fill_context_for_report` 工具时,`monitor_tool` 中间件把 context 置为 `True`
- 下一次模型调用时,`report_prompt_switch` 检测到 `report=True` → 加载报告专用提示词

### 3. RAG 总结(`rag_service.py:38-57`)
- `retriever.invoke(query)` 召回 top-k=3 个 chunk
- 拼成 `参考资料1: ... 参考资料2: ...` 格式
- 喂给 `rag_summarize` 提示词,要求 LLM **严格基于参考资料**回答

### 4. 路径统一(`utils/path_tool.py`)
- 所有路径都走 `get_abs_path(相对路径)`,以 `agent-demo/` 为根
- 避免在不同 cwd 下运行的路径错乱

---

## 五、环境准备

### 5.1 依赖

```
streamlit
langchain >= 1.0
langchain-chroma
langchain-community
langchain-core
langchain-text-splitters
chromadb
dashscope
pypdf
pyyaml
```

> 项目无 `requirements.txt`,按需安装即可。本机已验证 `pypdf` 需单独 `pip install pypdf`。

### 5.2 API Key

注册并开通阿里云[百炼](https://dashscope.console.aliyun.com/apiKey)服务,创建 API Key。

**Windows PowerShell:**
```powershell
$env:DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxx"
```

---

## 六、启动步骤

按顺序执行,所有命令都在 `agent-demo/` 目录下运行。

### 第 1 步:灌知识库(只跑一次即可)

```powershell
$env:DASHSCOPE_API_KEY = "sk-xxxx"
$env:PYTHONPATH = "C:\Codefield\llm-demo\agent-demo"
python rag/vector_store.py
```

输出示例:
```
[加载知识库]... 内容加载成功   (新文件)
[加载知识库]... 内容已经存在知识库内,跳过   (重复)
```

### 第 2 步:启动 Web 应用

```powershell
$env:DASHSCOPE_API_KEY = "sk-xxxx"
$env:PYTHONPATH = "C:\Codefield\llm-demo\agent-demo"
streamlit run app.py
```

浏览器打开:`http://localhost:8501`

> **为什么需要 `PYTHONPATH`?**  代码里 `from utils.xxx import ...` 依赖 `agent-demo/` 在 `sys.path` 里。直接在 `agent-demo/` 下 `python xxx.py` 默认不会把当前目录加进去。

---

## 七、使用示例

打开 `http://localhost:8501` 后,在输入框试这些:

| 输入 | 触发的能力 |
|---|---|
| `小户型适合哪些扫地机器人?` | `rag_summarize` 工具 → 检索知识库 → 总结回答 |
| `北京今天天气怎么样,适合用机器人吗?` | `get_weather` + `rag_summarize` |
| `给我生成我的6月使用报告` | `get_user_id` → `get_current_month` → `fill_context_for_report`(切换提示词)→ `fetch_external_data` → Markdown 报告 |
| `我家的机器人主刷缠了头发怎么办?` | `rag_summarize`(故障处理知识) |

---

## 八、配置说明

### `config/rag.yml` — 模型选择
```yaml
chat_model_name: qwen3-max          # 聊天模型
embedding_model_name: text-embedding-v4   # 向量模型
```

### `config/chroma.yml` — 向量库 + 切分策略
```yaml
collection_name: agent
persist_directory: chroma_db
k: 3                                # 召回 top-3
data_path: data
md5_hex_store: md5.text
allow_knowledge_file_type: ["txt", "pdf"]
chunk_size: 200                     # 每片 200 字符
chunk_overlap: 20                   # 相邻片重叠 20 字符
separators: ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
```

### `config/prompts.yml` — 提示词路径
```yaml
main_prompt_path: prompts/main_prompt.txt
rag_summarize_prompt_path: prompts/rag_summarize.txt
report_prompt_path: prompts/report_prompt.txt
```

### `config/agent.yml` — Agent 配置
```yaml
external_data_path: data/external/records.csv
```

---

## 九、日志

- 文件:`logs/agent_YYYYMMDD.log`(按天切分)
- 控制台:INFO 级;文件:DEBUG 级(包含所有工具入参、模型调用前消息详情)
- 关键日志点:
  - `[tool monitor]执行工具:xxx`  — 工具调用前
  - `[log_before_model]即将调用模型,带有 N 条消息`  — 模型调用前
  - `[加载知识库]xxx 内容加载成功`  — 知识库入库

---

## 十、常见问题

**Q1: `ModuleNotFoundError: No module named 'utils'`**
→ 缺 `PYTHONPATH`,见"第 2 步"。

**Q2: 启动后报 DashScope 鉴权失败**
→ 检查 `$env:DASHSCOPE_API_KEY` 是否设置,且 key 是否有效。

**Q3: 知识库已建过,如何强制重建?**
→ 删 `chroma_db/` 目录 + 删 `md5.text`,再跑一次 `vector_store.py`。

**Q4: 想加新的知识文档?**
→ 扔到 `data/` 下,后缀在 `chroma.yml` 的 `allow_knowledge_file_type` 里,跑 `vector_store.py`。

**Q5: 中文在 PowerShell 终端显示乱码**
→ 正常,只是终端编码问题,日志文件(`logs/*.log`)里和 Streamlit 界面里都是正常的 UTF-8。
