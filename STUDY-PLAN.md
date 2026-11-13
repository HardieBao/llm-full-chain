# 12 周大模型全栈与安全工程师实战规划表

> **核心纪律**：
> 1. **无产出不结项**：每周必须把对应的脚本、对比表或模型权重落进 `demos/` 目录，光看视频/看文章不算完成。
> 2. **四阶段螺旋上升**：先扒光黑盒底座（1~3周）→ 再搞定训练与垂直微调（4~6周）→ 再攻克企业级 RAG/Agent/LLMOps（7~10周）→ 最后用你的安全老本行打穿模型攻防与权重手术（11~12周）。

---

## 第一阶段：扒光黑盒 —— 摸透模型原理与推理底座（第 1～3 周）

### 第 1 周：最小 GPT 闭环 + Tokenizer 真相
- **关联目录**：`00-入门准备`、`01-nanoGPT-懂原理`、`02.5-tokenizer-BPE`
- **学习安排**：
  - [ ] Day 1–2：精读 `01-nanoGPT-懂原理/nanoGPT/model.py`，画图写出 `CausalSelfAttention` 中 `Q/K/V` 的张量 shape 变化 `[B, T, C] -> [B, nh, T, hs]`
  - [ ] Day 3–4：精读 `train.py` 与 `sample.py`，本地跑通莎士比亚 char-level 模型训练与采样
  - [ ] Day 5–6：读完 `karpathy/minbpe`（100行），理解 BPE 合并规则与中文 Token 效率问题
- **本周必交作业**：
  - [ ] `01-nanoGPT-懂原理/demos/kv_cache_sample.py`：给 nanoGPT 的推理加上手写 KV Cache，对比生成 500 tokens 的耗时
  - [ ] `02.5-tokenizer-BPE/demos/compare_tokenizers.py`：对比同一篇中文技术文档在 GPT-4 (`tiktoken`) 与 `Qwen2.5` 下的 token 数差距

### 第 2 周：C 语言极简推理 + 工业级 Llama 架构
- **关联目录**：`02-llama2.c-懂推理`、`03-transformers-Llama-工业实现`
- **学习安排**：
  - [ ] Day 1–3：通读 `llama2.c/run.c`，彻底搞懂现代 LLM 三大件：**RMSNorm**、**RoPE 旋转位置编码**、**SwiGLU**
  - [ ] Day 4–6：对照精读 HuggingFace `modeling_llama.py`，看懂 **GQA（分组查询注意力）** 怎么减少 KV Cache 显存
- **本周必交作业**：
  - [ ] `03-transformers-Llama-工业实现/demos/manual_generate.py`：禁用 `model.generate()`，只用 `model.forward(past_key_values=...)` 手写支持 `temperature` 和 `top_p` 的流式生成循环

### 第 3 周：推理性能工程（端侧量化 vs 服务端高并发）
- **关联目录**：`04-llama.cpp-性能工程`、`05-vllm-性能工程`
- **学习安排**：
  - [ ] Day 1–2：搞懂 `GGUF` 格式、mmap 零拷贝加载、`Q4_K_M / Q8_0` 块量化与反量化原理
  - [ ] Day 3–5：搞懂 vLLM 的 **PagedAttention**（KV Cache 分页防碎片）与 **Continuous Batching**（动态批处理调度）
- **本周必交作业**：
  - [ ] 实测 `Qwen2.5-1.5B` 在 `FP16 / Q8_0 / Q4_K_M` 下的内存占用、首字延迟与吐字速度对比表
  - [ ] 跑通 vLLM 服务并完成一次多并发请求压测

---

## 第二阶段：掌握训练与对齐 —— 后训练、消融与垂直领域模型（第 4～6 周）

### 第 4 周：评估先行 + 微调双雄（TRL & Unsloth）
- **关联目录**：`08-评估-eval`、`06-trl-微调`、`07-unsloth-微调`、`05.5-预训练工程`
- **学习安排**：
  - [ ] Day 1–2：**先立尺子再训练**，用 `lm-evaluation-harness` 或 `07.5/demos/eval.py` 跑出 `Qwen2.5-0.5B` 基线分数
  - [ ] Day 3–4：读 `trl` 的 `SFTTrainer` 与 `DPOTrainer` 核心 loss 实现；浏览 `05.5-预训练工程` 理解 TP/PP/DP/ZeRO 概念
  - [ ] Day 5–6：读 `unsloth` 的 Chunked Cross-Entropy Triton Kernel，跑通单卡 QLoRA 微调
- **本周必交作业**：
  - [ ] 记录同一模型在原生 HF vs Unsloth 下的显存峰值（VRAM）与训练吞吐对比

### 第 5 周：R1 范式实战 —— GRPO 强化学习与科学消融
- **关联目录**：`07.5-后训练配方`
- **学习安排**：
  - [ ] Day 1–2：精读 DeepSeek-R1 报告 + ByteDance DAPO 论文（掌握 clip-higher、dynamic sampling、token-level loss、超长惩罚）
  - [ ] Day 3–6：运行 `07.5-后训练配方/demos/train_grpo.py` 及 `configs/A~G` 消融配置
- **本周必交作业**：
  - [ ] 产出完整的 **A～G 七组消融实验报告**（含 GSM8K 分数、平均长度曲线、KL 散度、3 seeds 均值方差）

### 第 6 周：【实战大作业 1】从零训练《SecAudit 代码漏洞审计垂直模型》
- **关联目录**：`12-垂直领域模型实战`
- **学习安排**：
  - [ ] Day 1–2：用 `MinerU` / `easy-dataset` 清洗漏洞报告，构造 1000 条漏洞代码（正样本）+ 1000 条修复后安全代码（负样本防误报）
  - [ ] Day 3–4：用强模型蒸馏 `<think>污点追踪推理</think><conclusion>{JSON}</conclusion>` 长思维链数据，并按 8:2 混入通用代码数据防灾难性遗忘
  - [ ] Day 5–6：完成 SFT + 防误报规则奖励 GRPO 两阶段训练
- **本周必交作业（简历作品 1）**：
  - [ ] 垂直模型权重 + 评测表（对比基座 vs SFT vs SFT+GRPO 的 **漏洞检出率 Recall** 与 **误报率 FPR**）

---

## 第三阶段：企业级应用与上线工程 —— RAG、Agent 与 LLMOps（第 7～10 周）

### 第 7 周：源码拆解 —— Dify 与 LlamaIndex 的架构抽象
- **关联目录**：`09-dify-应用层`、`10-llama_index-应用层`
- **学习安排**：
  - [ ] Day 1–3：读 `LlamaIndex` 的索引、检索器、重排器解耦设计
  - [ ] Day 4–6：读 `Dify` 的 DAG 工作流引擎调度与多模型 `model_runtime` 统一抽象
- **本周必交作业**：
  - [ ] 200 行纯 Python 手写一个最小 DAG 工作流引擎 + 多模型统一调用层

### 第 8 周：【实战大作业 2】高准确度企业级生产 RAG
- **关联目录**：`13-企业级RAG实战`
- **学习安排**：
  - [ ] Day 1–2：使用 `RAGFlow DeepDoc` / `MinerU` 解析带复杂跨页表格的行业 PDF，实现父子文档分块（Parent-Child Chunking）
  - [ ] Day 3–4：基于 `Qdrant` + `BGE-M3` 实现“稠密向量 + 稀疏向量 + BM25”多路召回 + 元数据 ACL 权限过滤 + `bge-reranker-v2-m3` 精排
  - [ ] Day 5–6：体验 `LightRAG` 图谱检索，并用 `RAGAS` 跑自动化评估
- **本周必交作业（简历作品 2）**：
  - [ ] RAGAS 量化调优表：证明混合检索+重排+父子块相比 Naive RAG 在 `Context Recall` 与 `Faithfulness` 上的具体涨幅

### 第 9 周：【实战大作业 3】强可控企业级 Agent（状态机 + 沙箱 + Text2SQL）
- **关联目录**：`14-企业级Agent实战`
- **学习安排**：
  - [ ] Day 1–2：精读 `OpenHands` 与 `SWE-agent`，掌握安全容器沙箱与 **ACI 工具设计 5 法则**
  - [ ] Day 3–4：用 **LangGraph** 编写带 **Human-in-the-Loop（高危操作人工审批断点）** 的自动化渗透/运维 Agent
  - [ ] Day 5–6：用 **Vanna** 搭建带业务语义字典与 SQL 报错自愈循环的 Text2SQL 商业分析 Agent
- **本周必交作业（简历作品 3）**：
  - [ ] `14-企业级Agent实战/demos/` 下可运行的 LangGraph 渗透辅助 Agent 或 Text2SQL 完整工程

### 第 10 周：LLMOps、结构化锁死与成本砍半工程
- **关联目录**：`15-LLMOps与上线工程`
- **学习安排**：
  - [ ] Day 1–2：用 `Outlines` / `Instructor` 在解码层锁死有限状态机，实现 100% 零语法错误的 JSON 输出
  - [ ] Day 3–4：Docker 部署 **Langfuse**，给第 8、9 周系统接入全链路 Tracing、耗时监控与坏例回流数据飞轮
  - [ ] Day 5–6：配置 `RouteLLM` 大小模型成本路由 + vLLM `Prefix Caching`，压测 **TTFT（首字延迟）** 与 **TPOT**
- **本周必交作业**：
  - [ ] Langfuse 监控面板截图 + 路由前后 API 成本与延迟对比报告

---

## 第四阶段：王牌融合 —— 大模型红队、破甲与逆向手术（第 11～12 周）

### 第 11 周：应用层攻防 —— 注入、越狱、RAG 投毒与护栏绕过
- **关联目录**：`11-LLM安全-破甲破限`
- **学习安排**：
  - [ ] Day 1–2：用 `garak` / `PyRIT` 扫描自建模型与应用，测出基线 **ASR（攻击成功率）**
  - [ ] Day 3–4：实战 **PoisonedRAG（知识库投毒）** 与间接 Prompt 注入，劫持第 9 周的 Agent 工具调用链
  - [ ] Day 5–6：部署 `Llama Guard` / `NeMo Guardrails` + Canary Token，再用编码混淆与 Crescendo 多轮攻击做绕过对练

### 第 12 周：【实战大作业 4】权重层逆向手术 —— 激活分析与 Abliteration
- **关联目录**：`11-LLM安全-破甲破限`
- **学习安排**：
  - [ ] Day 1–3：采集模型在合规/拒答指令下的各层残差流激活（Residual Stream Activations），定位模型内部的“拒答方向向量（Refusal Direction）”
  - [ ] Day 4–6：对模型权重矩阵做正交投影擦除（Abliteration），产出破限模型，并用 `eval.py` 检测手术前后的推理能力损耗
- **本周必交作业（简历作品 4）**：
  - [ ] `abliteration_test.py` 权重手术脚本 + 擦除前后 ASR 与 GSM8K 准确率对比报告
