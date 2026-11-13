<div align="center">

# ⚡ LLM-Full-Chain：大模型全链路硬核实战路径

**从 600 行底层源码、GRPO 后训练科学消融、企业级 RAG/Agent 生产落地，到大模型红队攻防与权重层破甲（Abliteration）**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./STUDY-PLAN.md)
[![2025 Stack](https://img.shields.io/badge/Tech_Stack-2025_R1%20%7C%20GRPO%20%7C%20DAPO%20%7C%20vLLM%20%7C%20LangGraph-blue.svg)](#)
[![Hardware Friendly](https://img.shields.io/badge/GPU-单卡_12G~24G_可跑全流程-orange.svg)](#-算力门槛与本地复现指南)

**[📖 12 周闯关打卡表](./STUDY-PLAN.md)** · **[🧪 GRPO 后训练消融实验套件](./07.5-后训练配方/demos/README.md)** · **[🏢 四大企业级交付实战](#第三阶段应用架构与企业级交付实战-0910-1215)** · **[🛡️ LLM 红队与破甲](#第四阶段安全攻防与模型逆向手术-11)**

</div>

---

## 🎯 为什么要做这个仓库？（拒绝收藏夹吃灰与调包玩具）

GitHub 上的大模型教程大多走向两个极端：要么是塞满 500 篇论文链接的 Awesome 清单（新手点进去不知道先看哪一行代码），要么是 10 行代码调个 OpenAI API 的玩具 Demo（一进企业面对真实脏数据、高并发、幻觉和越狱攻击立刻崩盘）。

**`LLM-Full-Chain` 的设计哲学只有三条：**
1. **源码级祛魅**：每个核心环节只挑 **1 个最干净的工业级标杆仓库**，明确标出**“先读哪 3 个文件、带着哪 4 个问题去读、改哪几行代码做实验”**。
2. **紧跟 2025 最新范式**：全面覆盖 **DeepSeek-R1 / GRPO / ByteDance DAPO 消融实验**、**MinerU + CoT 合成数据管线**、**RAGFlow 深度表格解析 + BGE-M3 混合检索**、**LangGraph 强可控状态机 + 安全沙箱**、**Outlines 有限状态机结构化锁死**。
3. **造模型 × 落生产 × 破模型 三位一体**：不仅教你把模型训出来、放到生产环境省 70% 成本，还从网络安全红队视角教你**怎么用间接注入劫持 Agent、怎么在激活空间擦除拒答向量（Abliteration）**。

---

## 🗺️ 全景演进路线图

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 第一阶段：扒光黑盒 —— 摸透模型原理与高性能推理底座 (Week 1 ~ 3)                           │
│                                                                                         │
│  [00 入门准备] ──► [01 nanoGPT] ──► [02 llama2.c] ──► [02.5 Tokenizer/BPE]              │
│                      (600行训练)     (纯C手写KV Cache)   (minbpe/中文Token税)            │
│                                            │                                            │
│                                            ▼                                            │
│                    [05 vLLM 并发] ◄── [04 llama.cpp] ◄── [03 Transformers]              │
│                    (PagedAttention)   (GGUF/Q4量化算子)   (GQA/RoPE/SwiGLU工业实现)      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 第二阶段：掌握训练与对齐 —— 预训练、后训练配方与科学消融 (Week 4 ~ 6)                     │
│                                                                                         │
│  [05.5 预训练工程] ──► [08 评估体系 Eval] ──► [06 TRL 微调库] ──► [07 Unsloth 省显存]    │
│  (nanotron 3D并行)     (先立尺子再训练)       (SFT/DPO源码)       (手写Triton Kernel)    │
│                                                                          │              │
│                                                                          ▼              │
│                                           [12 垂直领域模型实战] ◄── [07.5 后训练与消融]  │
│                                           (脏数据清洗→合成CoT→防遗忘) (R1/GRPO/DAPO 7组) │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 第三阶段：企业级落地工程 —— 生产级 RAG、强可控 Agent 与 LLMOps (Week 7 ~ 10)              │
│                                                                                         │
│  [09 Dify 平台架构] + [10 LlamaIndex 组件]                                              │
│            │                                                                            │
│            ├──► [13 企业级 RAG 实战] (RAGFlow表格解析 + BGE-M3多路召回 + ACL + RAGAS)    │
│            ├──► [14 企业级 Agent 实战] (LangGraph审批断点 + OpenHands沙箱 + Text2SQL)   │
│            └──► [15 LLMOps 与上线工程] (Outlines 100% JSON + Langfuse监控 + RouteLLM)   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 第四阶段：王牌融合 —— 大模型红队攻防与权重层逆向手术 (Week 11 ~ 12)                       │
│                                                                                         │
│  [11 LLM安全：破甲与破限] (直接/间接注入 ──► PoisonedRAG投毒 ──► 护栏绕过 ──► Abliteration)│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 章节导览与核心产出

### 第一阶段：扒光黑盒 —— 摸透原理与推理底座 (`00` ~ `05`)

| 章节 | 导航与笔记 | 对标源码仓库 | 先读哪个核心文件 | 本章必交动手产出 |
|---|---|---|---|---|
| **00** | [入门准备与环境](./00-入门准备/NOTES.md) | — | `NOTES.md` | 配通 CUDA + PyTorch 最小训练四步与 `einsum` |
| **01** | [nanoGPT 懂原理](./01-nanoGPT-懂原理/NOTES.md) | [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) | `model.py` → `train.py` | 给 `sample.py` 手写加上 KV Cache，实测提速比 |
| **02** | [llama2.c 懂推理](./02-llama2.c-懂推理/NOTES.md) | [karpathy/llama2.c](https://github.com/karpathy/llama2.c) | `run.c`（单文件 700 行） | 搞懂 RMSNorm、RoPE 旋转位置编码与 Int8 量化推理 |
| **02.5** | [Tokenizer 与 BPE](./02.5-tokenizer-BPE/NOTES.md) | [karpathy/minbpe](https://github.com/karpathy/minbpe) | `minbpe/basic.py` | 训练自定义 BPE，实测中文在 GPT-4 vs Qwen 下的 Token 税 |
| **03** | [Transformers 工业实现](./03-transformers-Llama-工业实现/NOTES.md) | [huggingface/transformers](https://github.com/huggingface/transformers) | `models/llama/modeling_llama.py` | 禁用 `generate()`，基于 `forward()` 手写流式 Top-p 采样器 |
| **04** | [llama.cpp 端侧性能](./04-llama.cpp-性能工程/NOTES.md) | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | `src/llama.cpp` → `ggml/` | 对比 `FP16 / Q8_0 / Q4_K_M` 内存占用与吐字速度 |
| **05** | [vLLM 高并发服务](./05-vllm-性能工程/NOTES.md) | [vllm-project/vllm](https://github.com/vllm-project/vllm) | `vllm/attention/` → `vllm/core/` | 理解 PagedAttention 与 Continuous Batching 并完成并发压测 |

### 第二阶段：掌握训练与对齐 —— 预训练、后训练配方与科学消融 (`05.5` ~ `08`)

| 章节 | 导航与笔记 | 对标源码仓库 | 核心攻克点 | 本章必交动手产出 |
|---|---|---|---|---|
| **05.5** | [预训练工程与 3D 并行](./05.5-预训练工程/NOTES.md) | [huggingface/nanotron](https://github.com/huggingface/nanotron) + `TinyLlama` + `datatrove` | TP/PP/DP/ZeRO 切分原理、MinHash 去重、Chinchilla 定律 | 分析真实 3T tokens 预训练 Loss Spike 排障日志 |
| **06** | [TRL 微调标准库](./06-trl-微调/NOTES.md) | [huggingface/trl](https://github.com/huggingface/trl) | `SFTTrainer` / `DPOTrainer` / `PPO` / `GRPO` 源码 | 跑通 0.5B 模型 SFT 与 DPO 偏好对齐 |
| **07** | [Unsloth 显存优化](./07-unsloth-微调/NOTES.md) | [unslothai/unsloth](https://github.com/unslothai/unsloth) | `unsloth/kernels/cross_entropy_loss.py` | 实测手写 Triton Kernel 相比原生 HF 节省的显存峰值 |
| **07.5** | [后训练配方与 GRPO 消融](./07.5-后训练配方/NOTES.md) | [huggingface/open-r1](https://github.com/huggingface/open-r1) + `DAPO` + `Dr.GRPO` | **内置完整可运行消融套件 (`demos/train_grpo.py`)** | 跑完 **A~G 七组科学消融矩阵**（3 seeds 均值、长度偏差与 KL 曲线） |
| **08** | [评估体系 Eval](./08-评估-eval/NOTES.md) | [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | `pass@k` vs `maj@k`、数据污染检测、LLM-as-Judge 偏见校准 | 搭建 50 题私有领域黄金评测集 |

### 第三阶段：应用架构与企业级交付实战 (`09` ~ `10`, `12` ~ `15`)

| 章节 | 导航与笔记 | 核心技术栈 | 解决的企业级真实痛点 | 简历级交付作品 |
|---|---|---|---|---|
| **09** | [Dify 应用平台源码](./09-dify-应用层/NOTES.md) | `Dify` | DAG 工作流编排引擎 + 100+ 模型统一 `model_runtime` 抽象 | 200 行纯 Python 手写最小 DAG 工作流引擎 |
| **10** | [LlamaIndex RAG 组件](./10-llama_index-应用层/NOTES.md) | `LlamaIndex` | 索引构建、检索器与重排后处理的解耦设计 | 实现自定义混合 Retriever |
| **12** | **[【实战 1】垂直领域模型](./12-垂直领域模型实战/NOTES.md)** | `MinerU` + `easy-dataset` + `Distilabel` + `LLaMA-Factory` | **脏 PDF 解析 → CoT 思维链蒸馏 → 8:2 混训防灾难性遗忘 → 防误报强化** | **《SecAudit-7B 代码漏洞审计垂直模型》**（含 Recall 与误报率 FPR 评测报告） |
| **13** | **[【实战 2】企业级生产 RAG](./13-企业级RAG实战/NOTES.md)** | `RAGFlow` + `Qdrant` + `BGE-M3` + `LightRAG` + `RAGAS` | **跨页复杂表格解析 + 稠密/稀疏/BM25 三路召回 + 元数据 ACL 权限隔离 + 精排** | **RAGAS 量化提分报告**（准确率从 40% 提至 90% 的完整消融记录） |
| **14** | **[【实战 3】企业级强可控 Agent](./14-企业级Agent实战/NOTES.md)** | `LangGraph` + `OpenHands` + `SWE-agent` + `Vanna` | **状态机锁死边界 + 高危操作人工审批断点 (HITL) + Docker 沙箱自愈 + 语义层 Text2SQL** | **带审批断点与容器沙箱的自动化渗透/数据分析 Agent** |
| **15** | **[【实战 4】LLMOps 与上线工程](./15-LLMOps与上线工程/NOTES.md)** | `Outlines` + `Langfuse` + `RouteLLM` + `vLLM` | **FSM 锁死 100% 合法 JSON + 全链路 Tracing + 坏例回流飞轮 + 大小模型路由省 70% 成本** | **生产级监控大盘 + TTFT/TPOT 压测报告 + 成本路由网关** |

### 第四阶段：安全攻防与模型逆向手术 (`11`)

| 章节 | 导航与笔记 | 核心工具与项目 | 攻防覆盖面 | 毕业级硬核产出 |
|---|---|---|---|---|
| **11** | **[LLM 安全：破甲与破限](./11-LLM安全-破甲破限/NOTES.md)** | `garak` + `PyRIT` + `HarmBench` + `NeMo Guardrails` + `TransformerLens` | 六级直接越狱、PoisonedRAG 知识库投毒、Agent 工具链劫持、护栏绕过、**残差流拒答向量擦除 (Abliteration)** | **自动化红队 ASR 评估报告 + 权重层 Abliteration 破甲手术脚本** |

---

## 💻 算力门槛与本地复现指南

本路径专门针对个人开发者与学生做了**小模型对齐优化**——除 `05.5 预训练工程` 以读代码为主外，**其余 15 个章节全部可在单张消费级显卡（甚至免费云端 T4）上跑通**：

| 硬件档位 | 可完整跑通的章节 | 推荐模型尺寸 |
|---|---|---|
| **纯 CPU / Mac M 系列** | `00`, `02`, `02.5`, `03`, `04`, `08`, `09`, `10`, `14` | `Llama2.c-15M`, `Qwen2.5-0.5B/1.5B (GGUF Q4)` |
| **单卡 12GB (如 RTX 3060/4070)** | 上述全部 + `01 (nanoGPT)`, `06`, `07 (Unsloth QLoRA)`, `11`, `13` | `Qwen2.5-0.5B / 1.5B`, `BGE-M3` |
| **单卡 24GB (如 RTX 3090/4090 或租用 ¥1.5/h)** | **全套 `00 ~ 15` 通杀**（含 `05 vLLM`、`07.5 GRPO 7组消融`、`12 7B垂直模型微调`、`11 权重Abliteration`） | `Qwen2.5-7B-Instruct`, `DeepSeek-R1-Distill-Qwen-7B` |

---

## 🚀 3 分钟快速开始

### 1. 克隆本学习路径仓库

```bash
git clone https://github.com/HardieBao/llm-full-chain.git
cd llm-full-chain
```

### 2. 按需一键拉取各章节配套的经典源码

无需一次性下载几十 GB，使用内置脚本按你当前学到的章节浅克隆（`--depth 1`）：

```bash
# 查看所有章节配套的源码仓库清单
python scripts/clone_repos.py --list

# 只拉取第一周要读的轻量级仓库 (nanoGPT + llama2.c + minbpe)
python scripts/clone_repos.py --stage 01 02 02.5

# 或者一键拉取所有轻量必读仓库
python scripts/clone_repos.py --light
```

### 3. 本地启动交互式在线阅读网站（基于 VitePress）

本仓库已内置 VitePress 文档站配置，支持暗黑模式、左侧章节树、全文搜索：

```bash
npm install
npm run docs:dev
```

---

## 📅 怎么学不半途而废？

请直接打开 **[《STUDY-PLAN.md：12 周大模型全栈与安全工程师实战打卡表》](./STUDY-PLAN.md)**，严格遵守**“每周必须产出一个脚本或一张实验对比表落入 `demos/` 目录”**的纪律，按周推进。

---

## 🌟 站在巨人肩膀上：全球顶级大模型大师路线与神课索引

本仓库并非闭门造车，而是将全球 5 大顶尖门派的精华熔铸为一条连贯的实战链路。在学习对应章节时，强烈建议配合以下大师的原版教材与神课食用：

| 大师 / 机构 | 代表作 / 神课 | 核心门派与专长 | 对应本仓库章节 |
|---|---|---|---|
| **Andrej Karpathy**<br>*(前 Tesla AI 总监 / OpenAI 联创)* | • [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html)<br>• [Eureka Labs / LLM101n](https://github.com/karpathy/LLM101n) | **【从零手搓派鼻祖】**<br>`micrograd → makemore → nanoGPT → minbpe → llama2.c → llm.c`，把底层张量与反向传播剥得干干净净。 | `00` · `01` · `02` · `02.5` |
| **Maxime Labonne**<br>*(Liquid AI 后训练负责人)* | • [mlabonne/llm-course](https://github.com/mlabonne/llm-course) *(45k+ ⭐)*<br>• [Uncensor any LLM with Abliteration](https://huggingface.co/blog/mlabonne/abliteration) | **【开源微调与破甲实战派】**<br>分为 LLM Scientist / Engineer 两条线，也是激活空间擦除拒答向量（Abliteration）破甲技术的核心推广者。 | `06` · `07` · `11` · `12` |
| **Sebastian Raschka**<br>*(Lightning AI 首席教育官)* | • [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) *(35k+ ⭐)* | **【立体图解学院派】**<br>为每一行注意力矩阵乘法和架构演进（GPT-2 → Llama 3 → Qwen2.5）绘制了极其直观的彩色张量流向图。 | `01` · `03` |
| **Stanford CS336**<br>*(Percy Liang & T. Hashimoto)* | • [CS336: Language Modeling from Scratch](https://stanford-cs336.github.io/spring2024/) | **【工业级预训练系统神课】**<br>手写 BPE、手写 FlashAttention Triton Kernel、手写 3D 分布式并行、MinHash 数据清洗与 Scaling Law 拟合。 | `04` · `05` · `05.5` · `07` |
| **Nathan Lambert**<br>*(AllenAI OLMo / Tülu 负责人)* | • [RLHF Book](https://rlhfbook.com/)<br>• [allenai/open-instruct](https://github.com/allenai/open-instruct) | **【现代后训练与 RL 理论圣经】**<br>从 SFT、Reward Model、PPO、DPO 一路讲透到 2025 最新的 **DeepSeek-R1 / GRPO** 强化学习配方。 | `06` · `07.5` · `08` |
| **Datawhale 中文社区** | • [self-llm (开源大模型食用指南)](https://github.com/datawhalechina/self-llm)<br>• [happy-llm](https://github.com/datawhalechina/happy-llm) | **【中文生态与国产模型保姆级实战】**<br>针对国内算力与镜像环境，提供 Qwen / DeepSeek / InternLM 等国产模型的部署与微调脚本。 | `03` · `06` · `12` |

### 📊 横向对比：`LLM-Full-Chain` 补齐了哪些空白？

| 覆盖维度 | Karpathy `Zero to Hero` | Raschka `From Scratch` | Labonne `llm-course` | Stanford `CS336` | **本仓库 `LLM-Full-Chain`** |
|---|:---:|:---:|:---:|:---:|:---:|
| **底层源码手搓 (`01~03`)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **端侧量化与高并发推理 (`04~05`)** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **2025 GRPO/DAPO 科学消融 (`07.5`)** | ❌ | ❌ | ⭐⭐ | ❌ | **⭐⭐⭐⭐⭐ (内置7组消融)** |
| **企业脏数据/生产RAG/可控Agent/LLMOps (`12~15`)** | ❌ | ❌ | ⭐⭐⭐ | ❌ | **⭐⭐⭐⭐⭐ (四大企业实战)** |
| **红队注入/RAG投毒/权重破甲 (`11`)** | ❌ | ❌ | ⭐⭐⭐ | ❌ | **⭐⭐⭐⭐⭐ (攻防全链路)** |

---

## 🤝 贡献与开源协议

欢迎提交 Issue 或 PR 补充你的源码批注、`demos/` 实验脚本或消融实验结果。本项目采用 [MIT License](./LICENSE) 开源。
