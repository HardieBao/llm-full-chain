# LlamaIndex — 懂应用层（RAG 数据结构）

仓库: https://github.com/run-llama/llama_index
目标: 看 RAG 的索引/检索/重排怎么做成可组合的组件

## 阅读顺序
1. `llama_index/core/indices/` — 各种索引实现（VectorStore / Summary / Tree / KnowledgeGraph）
2. `llama_index/core/retrievers/` — 检索器
3. `llama_index/core/postprocessor/` — 后处理（rerank / filter）
4. `llama_index/core/query_engine/` — 查询引擎（把上面串起来）

## 关键问题
- 索引和检索为什么解耦？（建索引 vs 查索引是两件事）
- NodeParser 分块策略有哪些（sentence / semantic / hierarchical）
- 混合检索（BM25 + vector）怎么融合
- agentic RAG 和 naive RAG 的架构差异

## 动手实验
- [ ] 用 llama_index 给一份文档建索引 + 查询
- [ ] 实现一个自定义 retriever
- [ ] 对比 llama_index 的 RAG 和你手写一个简单向量检索的差异
