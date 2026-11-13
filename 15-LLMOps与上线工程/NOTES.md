# 15 · LLMOps、可观测性与推理成本工程（上线最后一公里）

目标：解决模型与 Agent 上线后的四大生死问题：**“怎么保证 100% 输出合法 JSON？”、“线上胡说八道怎么排查？”、“并发一高怎么不崩？”、“一个月账单怎么砍掉 70%？”**

---

## 一、四大核心工程支柱

### 1. 结构化输出强制约束（Structured Outputs / Guided Decoding）

在工程系统里，LLM 是个中间件，下游代码只认严格符合 Schema 的 JSON。靠 Prompt 写“请务必只输出 JSON”在生产环境只有 95% 成功率，剩下 5% 会导致线上崩溃。

- **原理（有限状态机 FSM / CFG 解码）**：把 JSON Schema 编译成正则表达式或上下文无关文法状态机，在模型每生成一个 Token 时，**直接把不符合语法的 Token 概率置为 $-\infty$（Mask 掉）**——从数学上保证 100% 语法合法，且还能跳过固定字段名的推理从而提速！
- **核心开源项目**：
  - **[dottxt-ai/outlines](https://github.com/dottxt-ai/outlines)** — 结构化生成鼻祖，vLLM 已原生集成。
  - **[sgl-project/sglang](https://github.com/sgl-project/sglang)** — 内置 `xgrammar` 压缩状态机（Jump-Forward Decoding），结构化输出速度最快的推理引擎。
  - **[jxnl/instructor](https://github.com/jxnl/instructor)** — 基于 Pydantic 的轻量包装器，自动校验失败重试。

### 2. 全链路可观测性与评测闭环（Tracing & Observability）

线上一个复杂 Agent 跑了 6 步，花了 15 秒，最后给用户回了一句错误答案。没有可观测性平台，你连哪一步出的错都不知道。

- **核心开源项目**：
  - **[langfuse/langfuse](https://github.com/langfuse/langfuse)**（首选，可私有化 Docker 部署）：
    - **Trace 瀑布流**：记录每次请求的完整调用树（Prompt、检索到的文档、工具入参出参、TTFT 首字延迟、Token 消耗、折合人民币成本）。
    - **Prompt 版本管理**：把 Prompt 从代码里解耦，线上热更新、A/B 测试。
    - **线上坏例回流（Dataset Flywheel）**：用户在前端点“踩”或触发报错的 Trace，一键加入评测数据集 → 攒够 500 条拿去微调小模型（**数据飞轮**）。
  - **[Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)** — 另一个优秀的开源追踪与 RAG 向量可视化工具。

### 3. 成本砍半工程：语义路由、缓存与小模型蒸馏

| 优化手段 | 原理 | 预期收益 | 代表工具 |
|---|---|---|---|
| **Prefix Caching（前缀缓存）** | System Prompt、长文档、Few-shot 示例的 KV Cache 直接在显存复用，不重复算 Prefill | 首字延迟降 60%~80%，成本降 50%+ | `vLLM --enable-prefix-caching` / `SGLang RadixAttention` |
| **模型路由（Model Router）** | 训一个极轻量分类器：80% 简单问题分给 `Qwen2.5-7B`，20% 难推理才调 `DeepSeek-R1 / Claude` | 综合成本直降 **60%~75%**，速度翻倍 | **[lm-sys/RouteLLM](https://github.com/lm-sys/RouteLLM)** / **[aurelio-labs/semantic-router](https://github.com/aurelio-labs/semantic-router)** |
| **语义缓存（Semantic Cache）** | 高频相似问题直接命中向量缓存返回，不调大模型 | 高频问答场景省 40% 算力 | **[zilliztech/GPTCache](https://github.com/zilliztech/GPTCache)** |
| **Multi-LoRA 动态服务** | 1 个 7B 底座显存常驻，同时挂载 20 个不同业务的 LoRA 权重，按请求 header 动态切换 | 省下 19 张显卡的钱 | `vLLM --enable-lora` / **[predibase/lorax](https://github.com/predibase/lorax)** |

### 4. 线上压测与性能指标（SLA）

企业上线前必须测出的 4 个硬指标（使用 `vLLM benchmark_serving.py` 或 **[genai-perf](https://github.com/triton-inference-server/perf_analyzer)**）：

1. **TTFT (Time To First Token，首字延迟)**：用户发出请求到看到第一个字的时间（聊天场景要求 `< 500ms ~ 1.5s`，主要受 Prompt 长度和 Prefill 算力影响）。
2. **TPOT / ITL (Time Per Output Token，吐字间隔)**：每个字蹦出来的间隔（`< 30~50ms` 才流畅，受显存带宽限制）。
3. **Throughput (系统总吞吐 tokens/s)**：高并发下每秒总共能吐多少 Token。
4. **Goodput**：满足上述延迟 SLA 前提下的有效吞吐量。

---

## 二、企业大模型项目完整闭环飞轮（总结全书 00~15）

```
1. 冷启动上线：用最强商业/开源大模型 (DeepSeek-V3/R1) + 生产级 RAG (13) + 可控 Agent (14) 快速把业务跑通
       ↓
2. 强约束与监控：接 Outlines 锁死 JSON 格式 + 接 Langfuse (15) 收集线上真实流量与 Bad Cases
       ↓
3. 评测基线固化：把线上真实好坏样本洗成黄金评测集 (08)
       ↓
4. 垂直蒸馏降本：用收集到的高价值数据 + CoT 合成管线 (12)，通过 Unsloth/TRL/GRPO (06/07/07.5) 微调出一个专用的 1.5B/7B 小模型
       ↓
5. 高性能替换：用 vLLM + AWQ 量化 + RouteLLM (05/15) 把 80% 流量切给自研垂直小模型，并经过红队安全扫描 (11)
       ↓
   【结果：准确率比通用大模型更高、延迟降到 200ms、成本降 90%、数据完全私有可控】
```

> **上面这 5 步，就是任何一家企业花几十万年薪招大模型工程师/架构师要干的全部事情。**

---

## 动手实战清单

- [ ] 本地用 Docker 一键拉起 **Langfuse**，在你之前的 Agent 或 RAG 脚本里加上 3 行 `@observe()` 装饰器，去面板看完整的调用树和耗时分布
- [ ] 用 **Outlines** 或 **Instructor** 强行约束一个 0.5B 小模型输出复杂的嵌套 Pydantic 对象，测试跑 100 次是否 100% 零语法错误
- [ ] 写一个压测小脚本，测一下本地推理服务在并发 `1 / 4 / 16` 下的 **TTFT** 和 **TPOT** 变化曲线
