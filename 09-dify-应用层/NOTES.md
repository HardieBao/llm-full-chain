# Dify — 懂应用层（LLM 平台）

仓库: https://github.com/langgenius/dify
目标: 看生产级 LLM 应用平台怎么抽象 Agent/RAG/工作流

## 阅读顺序
1. `api/core/agent/` — Agent 抽象（tool calling / react）
2. `api/core/rag/` — RAG 管线（datasource → index → retrieval → rerank）
3. `api/core/app/` — 应用运行时（chatflow / workflow / agent chat）
4. `api/core/model_runtime/` — 模型 provider 抽象（怎么兼容 100+ 模型）

## 关键问题
- 模型 provider 怎么统一抽象（OpenAI/Anthropic/Ollama/本地）
- RAG 的分块/索引/检索/重排怎么解耦
- Workflow 引擎怎么编排 LLM 调用 + 工具 + 条件分支
- streaming（SSE）怎么处理

## 动手实验
- [ ] 本地起 dify，配一个本地模型
- [ ] 读 workflow engine 的 DAG 执行逻辑
- [ ] 对比 dify 的 RAG 和 llama_index 的 RAG 抽象
