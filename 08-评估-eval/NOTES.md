# 评估 — 不评测等于白训练

目标：学会用标准 eval 框架 + 自建 eval，把"模型效果"变成可比较的数字。

## 为什么评估比训练难

- 基准测试（benchmark）可能被污染（训练数据里见过测试题）
- 不同 decode 参数结果差很多（temp=0 vs temp=0.7 差 10+ 分）
- 单项分数高不代表能力好（MMLU 高但写代码烂很常见）
- 评估本身是个工程问题：prompt 设计、答案抽取、多 seed 稳定性

## 标准 eval 框架

### 1. [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)

**业界标准**，60+ benchmark 一次跑完：

```bash
pip install lm-eval

# 常用组合
lm_eval --model hf \
  --model_args pretrained=Qwen/Qwen2.5-0.5B-Instruct \
  --tasks mmlu,gsm8k,hellaswag,truthfulqa_mc2 \
  --num_fewshot 5 \
  --batch_size 8
```

读源码看：
- `lm_eval/tasks/` — 每个 benchmark 的实现（prompt 模板 + 评分逻辑）
- `lm_eval/models/huggingface.py` — 模型怎么接入

### 2. [huggingface/lighteval](https://github.com/huggingface/lighteval)

HF 新一代，更快更省内存，支持 vLLM 后端：
```bash
lighteval accelerate \
  "model_name=Qwen/Qwen2.5-0.5B-Instruct" \
  "lighteval|gsm8k|0|0"
```

### 3. [openai/evals](https://github.com/openai/evals)

OpenAI 自己的 eval 框架，看它的 eval 设计思路（很多 o1 的评测都用这个）。

## 必知的核心 benchmark

| Benchmark | 测什么 | 注意 |
|---|---|---|
| **MMLU** | 知识广度（57 学科 MCQ） | 已接近饱和，高分区分度低 |
| **GSM8K** | 小学数学（8.5K 题） | 7B+ 基本 80%+ |
| **MATH-500** | 竞赛数学 | OpenAI 挑的 500 题子集，难很多 |
| **HumanEval** | 代码生成 | pass@1 / pass@10 区别大 |
| **IFEval** | 指令遵循（格式/长度/关键词） | 后训练效果最直接的指标 |
| **HellaSwag** | 常识推理 | 快饱和了 |
| **TruthfulQA** | 幻觉 | MC 模式测"知道什么不知道什么" |
| **BBH** | 23 个难任务 | BIG-Bench Hard 子集，CoT 明显受益 |
| **GPQA** | 研究生级理科 | 当前最难的公开 MCQ benchmark |
| **LiveCodeBench** | 代码（滚动更新防污染） | 比 HumanEval 更能反映真实能力 |

## 关键概念

| 概念 | 说明 |
|---|---|
| **pass@k** | 生成 k 个答案，有一个对就算对。pass@1 最严格，pass@10 放水 |
| **maj@k** | k 个答案投票取多数。GSM8K 常报 maj@8 |
| **few-shot** | prompt 里给几个示例。0-shot vs 5-shot 差异可能 10-20 分 |
| **contamination** | 训练数据里有测试题 → 分数虚高。检测方法：n-gram overlap / perplexity 对比 |
| **length bias** | 长回复打分偏高（reward model 和 judge model 都有这问题） |
| **CoT vs direct** | 思维链大幅提升数学/推理，但可能降低其他能力 |

## 自建 eval

什么时候需要自建：
- 测你的垂直领域能力（法律/医疗/代码特定语言）
- 测 agent 能力（工具调用成功率、多步推理）
- 测 safety / 越狱

方法：
1. 从真实场景采样 100-500 条输入
2. 定义评分标准：精确匹配 / 关键字段 / LLM-as-judge
3. 跑 3+ seed，报均值 ± std
4. 人工抽查 10-20% 确认自动评分靠谱

LLM-as-judge 的坑：
- 用强模型评弱模型 → 长度偏差
- 换 judge 模型 → 分数不可比
- 解决：用同一 judge + 控制回复长度 + 人工校准

## 动手实验

- [ ] 用 lm-eval 跑一遍 Qwen2.5-0.5B 的 mmlu + gsm8k + ifeval，记录分数
- [ ] 对比 0-shot vs 5-shot 的 GSM8K 分数
- [ ] 对比 temp=0 vs temp=0.7 的 MMLU 分数
- [ ] 自建一个 50 题的小 eval：从你的使用场景出题，用 LLM-as-judge 打分
- [ ] 检查你训练的模型在 GSM8K 上有没有 contamination：抽 10 题看模型是否"背过"答案

## 消融实验的 eval 纪律

1. **固定 decode 参数**：所有组 temp/top_p/max_tokens 一致
2. **固定 eval 集**：同一批题，不要换
3. **报多个 benchmark**：至少 3 个不同维度（知识/推理/指令）
4. **报训练曲线**：reward/loss/KL 曲线比最终分数更能说明问题
5. **多 seed**：RL 训练方差大，单 seed 结论不可靠
