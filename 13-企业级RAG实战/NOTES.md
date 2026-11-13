# 13 · 企业级生产 RAG 实战（从 40% 准确率到 90%）

目标：跨越“跑通 10 行代码的向量检索 Demo”到“能扛住企业上万份复杂文档、带权限隔离与量化评估的生产级系统”之间的鸿沟。

---

## 一、为什么玩具 RAG 一进企业就死？

| 真实企业痛点 | Naive RAG（玩具做法）怎么挂的 | 生产级解法 |
|---|---|---|
| **复杂版面与表格** | 按固定 500 字符硬切，把跨页表格切碎，表头和数值分离 | 视觉版面分析（Layout Analysis）+ 表格转 Markdown/HTML 整块保留 + 父子文档索引 |
| **专有名词/型号搜不到** | 纯稠密向量（Embedding）对 `CVE-2024-3094`、`GB50016-2014`、设备编号不敏感 | **多路混合检索**：`BM25 全文检索 + 稠密向量 + 稀疏向量 (BGE-M3)` |
| **排第一的不是最相关的** | 余弦相似度只看大概语义，前 5 名里混进似是而非的段落 | 必加 **Cross-Encoder Reranker**（如 `bge-reranker-v2-m3`）做精排 |
| **跨文档全局问题答不出** | 问“今年所有安全事故的共性原因是什么？”，Top-K 只召回 5 个碎片 | **GraphRAG / LightRAG**（实体关系图谱 + 社区摘要） |
| **越权泄密** | 员工搜“年终奖”，把高管薪资表召回出来了 | **向量库元数据 ACL 过滤**：检索时强制带 `WHERE dept_id IN (...) AND role_level <= user_level` |

---

## 二、生产级 RAG 标准架构图

```
[入库链路 Ingestion Pipeline]
  PDF / Word / Excel / 扫描件
     ↓ 1. 深度文档解析 (RAGFlow DeepDoc / MinerU / Unstructured)
  结构化块 (保留章节标题树、完整表格、图片 Caption)
     ↓ 2. 层次化切分 (Parent-Child Chunking: 小块检索，大块送给 LLM)
     ↓ 3. 多模态/多路编码 (BGE-M3: Dense + Sparse + ColBERT) + 绑定 ACL 权限标签
  落库: Milvus / Qdrant / Elasticsearch (向量 + 倒排索引合一)

[查询链路 Query Pipeline]
  用户提问: "A型号设备在零下20度怎么排障？"
     ↓ 1. 查询改写 (Query Rewrite / HyDE / 子问题拆解) + 注入用户权限 Token
     ↓ 2. 多路召回 (Vector Top-50 + BM25 Top-50 + 图谱关联实体) [全部带 ACL 过滤]
     ↓ 3. RRF 融合 + Reranker 精排 → 截取 Top-5 高置信度父文档块
     ↓ 4. 严格引用生成 (要求模型每句话后标注 [Doc_ID, Page_X]，无依据必须拒答)
  最终回答 + 原文高亮溯源卡片
```

---

## 三、必读的核心开源项目

| 项目 | 定位 | 重点学什么 |
|---|---|---|
| **[infiniflow/ragflow](https://github.com/infiniflow/ragflow)** | 企业级 RAG 标杆 | 必读它的 `deepdoc/` 目录（版面识别、表格结构识别 TSR、OCR 管线）和混合检索设计 |
| **[HKUDS/LightRAG](https://github.com/HKUDS/LightRAG)** | 轻量级 GraphRAG | 比微软原版 GraphRAG 省 90% Token，看它怎么抽实体边、怎么把图检索和向量检索融合 |
| **[FlagOpen/FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding)** | BGE 模型全家桶 | `BGE-M3`（同时输出稠密+稀疏+多向量）和 `bge-reranker` 的工业用法 |
| **[explodinggradients/ragas](https://github.com/explodinggradients/ragas)** | RAG 自动化评估 | 四大核心指标：`Context Precision`、`Context Recall`、`Faithfulness（忠实度/防幻觉）`、`Answer Relevancy` |
| **[qdrant/qdrant](https://github.com/qdrant/qdrant)** | 高性能向量库 | 学习 Payload Indexing（带复杂权限过滤的混合检索） |

---

## 四、企业调优纪律：用 RAGAS 说话，不凭感觉调参

每次改动（换 Embedding、改 chunk_size、加 Reranker），跑同一套 100 题测试集，填这张表：

| 诊断现象 | 哪个指标低？ | 根因定位 | 针对性手术 |
|---|---|---|---|
| 该找的文档没找出来 | `Context Recall` 低 | 切块太碎 / Embedding 不懂行话 / 缺关键词匹配 | 上 `BGE-M3` 混合检索 + Parent-Child 索引 + Query 扩展 |
| 找出来的排在后面被截断了 | `Context Precision` 低 | 粗召回噪音多 | 加 `bge-reranker-v2-m3`（Top-50 压到 Top-5） |
| 文档找对了，LLM 还是胡编 | `Faithfulness` 低 | 模型脑补了自身预训练知识 | 压低 `temperature=0.1` + System Prompt 强约束引用 `[1]` |
| 答得对但答非所问/啰嗦 | `Answer Relevancy` 低 | 提示词模板或 Query 拆解有问题 | 优化生成 Prompt，加 Few-shot 示例 |

---

## 动手实战清单

- [ ] 部署或源码跑通 **RAGFlow**，丢入一份带复杂合并单元格表格的真实 PDF，对比它和普通 LangChain `PyPDFLoader` 切出来的块有什么天壤之别
- [ ] 用 `Qdrant` + `BGE-M3` + `bge-reranker` 手写一个不到 150 行的**混合检索 + 重排 + 权限过滤（ACL）**脚本
- [ ] 引入 **RAGAS**，为你上面的脚本跑出量化对比报告（纯向量 vs 混合检索+重排）
