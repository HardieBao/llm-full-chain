# 12 · 垂直领域模型端到端实战（从脏数据到领域专家）

目标：不调现成玩具数据集，走完**企业里从零训练一个垂直行业模型（网安/代码审计/工地安全/金融/法律）**的真实闭环。

> **毕业级推荐选题**：基于 `Qwen2.5-Coder-7B` 或 `Qwen2.5-1.5B`，训练一个**《SecLLM：代码漏洞审计与渗透路径推理模型》**（或者你目录下的《工地安全预警模型》）。

---

## 一、为什么大部分人训垂直模型会失败？

| 常见死法 | 真实原因 | 企业级解法 |
|---|---|---|
| 训完后模型“变傻”了，连基本指令都听不懂 | **灾难性遗忘**：全塞领域数据，把基座的通用能力冲掉了 | 领域数据 : 通用高质量数据 按 **7:3 或 8:2** 混合训练 |
| 背诵了文档原话，换个问法就不会 | 直接把文档切成 QA，没有推理过程 | 构造 **长思维链（CoT）合成数据**，教模型“怎么分析”而不是“背结论” |
| 不应该微调的场景硬上微调 | 把微调当知识库用（试图让 7B 模型记住 10 万条动态资产） | **静态规律/专业推理逻辑 → 微调**；**动态事实/具体文档 → RAG** |
| 没有基线就开训 | 不知道 Prompt 工程能做到多少分，白花几千块算力 | 先做 `Zero-shot → Few-shot → RAG` 基线，微调必须比它们高 10%+ 才算成功 |

---

## 二、企业级垂直模型五步流水线

```
[1. 原始脏文档]  (PDF报告 / 漏洞库 / 行业规范 / 历史工单)
       ↓  MinerU / Marker / Data-Juicer (解析 + 去噪 + 脱敏)
[2. 干净领域语料库]  (Markdown / JSONL)
       ↓  Distilabel / EasyDataset + 强模型(DeepSeek-V3) 蒸馏
[3. 合成指令与思维链数据集]  (SFT CoT 数据 + DPO 正负偏好对)
       ↓  LLaMA-Factory / Unsloth (LoRA 或 全量)
[4. 多阶段训练]  (可选 CPT 增量预训练 → SFT 指令微调 → DPO/GRPO 强化)
       ↓  自建领域 Eval 黄金集 (500 题)
[5. 量化导出与上线]  (AWQ/GGUF → vLLM 服务化)
```

---

## 三、分步核心工具与实操

### 阶段 1：啃下非结构化脏数据（80% 的时间花在这）

- **[opendatalab/MinerU](https://github.com/opendatalab/MinerU)**：把复杂的行业 PDF（带双栏、表格、公式、架构图）精准转成 Markdown。
- **[modelscope/data-juicer](https://github.com/modelscope/data-juicer)**：阿里的工业级数据清洗算子库（过滤乱码、去重 MinHash、去敏感信息 PII、按困惑度 PPL 过滤低质文本）。

### 阶段 2：无中生有——合成高质量 SFT / CoT 数据

没有现成问答对怎么办？用强模型（DeepSeek-V3 / R1）当“出题老师”：

- **[ConardLi/easy-dataset](https://github.com/ConardLi/easy-dataset)**：带 GUI，把清洗好的 Markdown 丢进去，自动切分章节 → 自动生成多样化问题 → 自动生成带推理过程的答案 → 导出 ShareGPT/Alpaca 格式。
- **[argilla-io/distilabel](https://github.com/argilla-io/distilabel)**：代码级合成数据管线。常用范式：
  1. **Self-Instruct / Evol-Instruct**：让强模型把简单问题改写得更复杂（加约束、加边界条件、多步推理）。
  2. **Rejection Sampling（拒绝采样）**：同一个问题让模型生成 8 个回答，用规则或裁判模型挑出最好的当 Chosen，最烂的当 Rejected → 直接拿到 **DPO 偏好数据集**。

### 阶段 3：训练配方决策（CPT vs SFT vs RL）

| 阶段 | 什么时候需要做？ | 数据格式 | 关键超参经验 |
|---|---|---|---|
| **CPT（增量预训练）** | 领域有大量底层黑话/私有协议/罕见代码语言，基座根本没见过 | 纯文本（`{"text": "..."}`），通常 >1B tokens | `lr=1e-5 ~ 5e-5`，混入 15% 通用预训练语料 |
| **SFT（监督微调）** | **必做**。教模型学会领域任务格式、分析套路、输出规范 | `[{"role":"user",...}, {"role":"assistant",...}]`（5k~50k 条高质量足矣） | LoRA `r=16~64, alpha=32~128`，全参 `lr=1e-5`，`epochs=2~3`（过拟合警告） |
| **DPO / GRPO** | 压制幻觉、对齐格式、或在代码/安全场景有**明确验证器**时 | DPO: `{prompt, chosen, rejected}`；GRPO: `{prompt, ground_truth}` | DPO `beta=0.1, lr=5e-7`；GRPO 用规则打分 |

训练底座工具：**[hiyouga/LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)**（企业里最省心的瑞士军刀，YAML 配置一键切换 CPT/SFT/DPO，内置 SwanLab/WandB 监控）。

---

## 四、实战项目蓝图：训练《SecAudit-7B 代码漏洞审计模型》

### 1. 数据源构造
- **正样本（有漏洞）**：从 CVE 补丁库（如 `Big-Vul`、`DiverseVul`、GitHub Security Advisories）提取修补前的函数代码。
- **负样本（无漏洞，极重要！）**：提取修补后的函数代码！**如果不放修补后的安全代码，训出来的模型看什么代码都报漏洞（100% 误报率）**。
- **CoT 蒸馏**：用 DeepSeek-R1 针对每一对（漏洞代码 + 修复补丁）生成固定格式的推理链：
  ```xml
  <think>
  1. 定位输入源(Source): 用户可控参数 `req.query.id` 在第 12 行进入函数。
  2. 追踪数据流(Propagation): 未经类型转换或参数化，直接拼接到 `sql` 字符串。
  3. 触发点(Sink): 第 18 行 `db.execute(sql)` 执行原始拼接语句。
  4. 对照验证: 检查上下文无白名单过滤，确认存在 SQL 注入。
  </think>
  <conclusion>
  {"vulnerable": true, "cwe": "CWE-89", "line": 18, "fix": "使用参数化查询 cursor.execute(sql, (id,))"}
  </conclusion>
  ```

### 2. 训练三部曲
1. **SFT 阶段**：10,000 条上述 `<think> + <conclusion>` 数据（5000 漏洞 + 5000 修复后安全代码）+ 2,000 条通用代码指令数据，用 Unsloth/LLaMA-Factory 训 2 个 epoch。
2. **GRPO 强化阶段**：
   - 奖励函数 1（格式奖）：输出合法 JSON + `<think>` 标签 → `+0.5`
   - 奖励函数 2（准确奖）：`vulnerable` 布尔值判断正确 → `+1.0`；CWE 编号匹配 → `+1.0`
   - 奖励函数 3（防误报重罚）：安全代码误报为漏洞（False Positive） → `-1.5`（企业最恨误报！）

### 3. 交付评测指标
不能只看 Loss！必须汇报这张表：
```
| 模型 | 漏洞检出率 (Recall) | 误报率 (FPR, 越低越好) | CWE 分类准确率 | JSON 格式合法率 |
|---|---|---|---|---|
| Qwen2.5-7B-Instruct (基座) |  |  |  |  |
| + SFT (10k CoT) |  |  |  |  |
| + SFT + GRPO (防误报奖励) |  |  |  |  |
```

---

## 动手清单

- [ ] 用 `MinerU` 或 `easy-dataset` 把你手头的一份专业 PDF（如 OWASP 指南或工地安全规范）转成 200 条带 `<think>` 的 QA 对
- [ ] 配好 `LLaMA-Factory`，跑通一次“领域数据 80% + 通用数据 20%”的混合 LoRA 微调
- [ ] 在测试集上对比微调前后在**领域专有问题**和**通用闲聊问题**上的表现，验证有没有发生灾难性遗忘
