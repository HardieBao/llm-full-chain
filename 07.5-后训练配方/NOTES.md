# 后训练配方 — 读论文 + 跑消融

目标：搞懂 SFT → 偏好优化 → RL 的完整 pipeline，能自己设计消融实验。

## 必读论文（按顺序）

| # | 论文 | 为什么读 |
|---|---|---|
| 1 | [DeepSeek-R1](https://arxiv.org/abs/2501.12948) | GRPO + 规则奖励的全流程，蒸馏 vs 直接 RL 的对比 |
| 2 | [DAPO](https://arxiv.org/abs/2503.14476) | GRPO 的四个工程修复，§5 消融表是最好的模板 |
| 3 | [Dr. GRPO](https://arxiv.org/abs/2503.20783) | 指出 length bias，去 std 归一化 |
| 4 | [Qwen2.5 技术报告](https://arxiv.org/abs/2412.15115) | 工业级后训练配方：SFT → DPO → GRPO 多阶段 |
| 5 | [VAPO](https://arxiv.org/abs/2504.05118) | value-based 的 GRPO 替代，长 COT 更稳 |

## 开源项目

| 项目 | 干什么 |
|---|---|
| [open-r1](https://github.com/huggingface/open-r1) | HF 官方 R1 复现 pipeline，SFT→GRPO→蒸馏全流程 |
| [TinyZero](https://github.com/Jiayi-Pan/TinyZero) | $30 复现 R1-zero，最小可跑 RL |
| [cedar-grpo](https://github.com/cedar-grpo/cedar-grpo) | 专门做 GRPO 消融的参考实现 |
| [verl](https://github.com/volcengine/verl) | DAPO 背后的框架，字节开源的 RL 训练基础设施 |
| [trl](https://github.com/huggingface/trl) | `GRPOTrainer` / `DPOTrainer` / `KTOTrainer` 单文件可跑 |

## 论文索引

- [hscspring/rl-llm-nlp](https://github.com/hscspring/rl-llm-nlp) — GRPO/RLOO/CISPO/GiGPO 关系图谱，当目录用

---

## 最小消融实验（单卡可跑）

### 设计原则

> 每次只改一个变量，固定 eval 套件，跑 3 个 seed。

### 实验配置

```
基座:   Qwen2.5-0.5B-Instruct 或 Qwen3-0.6B
算法:   trl 的 GRPOTrainer（单文件依赖最少）
任务:   GSM8K 子集（500 题）或 Countdown（TinyZero 的任务）
奖励:   规则奖励 —— 答案对 +1，格式对 +0.5，长度超 2048 罚 -0.5
```

### 消融矩阵

| 组 | 配方 | 回答什么问题 |
|---|---|---|
| A | baseline（不训练） | 基座本身多少分 |
| B | SFT only（500 条正确解） | 监督数据能到多少 |
| C | GRPO only（无 SFT 冷启动） | 纯 RL 能不能自己学会 |
| D | SFT → GRPO | SFT 冷启动有没有用 |
| E | GRPO + 去 std 归一化（Dr. GRPO） | length bias 修不修 |
| F | GRPO + dynamic sampling（DAPO） | 过滤零梯度组提不提升 |
| G | GRPO + clip-higher（DAPO） | 防 entropy 塌缩有没有用 |

### 跑法

```bash
# 每个配置跑 3 个 seed，eval 固定
python train.py --algo grpo --seed 42
python train.py --algo grpo --seed 43
python train.py --algo grpo --seed 44
```

### 观测指标（比最终分数更重要）

| 指标 | 看什么 |
|---|---|
| reward 曲线 | 是否收敛、有没有塌缩 |
| KL 散度 | policy 跑偏没有（>10 一般失控） |
| response length | 是不是学会了"多说碰运气"（length hacking） |
| test acc | GSM8K / MATH-500 / IFEval |
| entropy | 是否过早塌缩（DAPO clip-higher 解决的问题） |

### 输出模板

每组一张表：

```
| seed | GSM8K | MATH-500 | IFEval | avg_len | final_reward |
| 42   |       |          |        |         |              |
| 43   |       |          |        |         |              |
| 44   |       |          |        |         |              |
| mean |       |          |        |         |              |
```

---

## 目录

```
demos/
├── README.md           ← 消融实验脚手架说明
├── configs/            ← 每组实验的 yaml
├── train_grpo.py       ← 训练入口
├── eval.py             ← 统一评测
└── results/            ← 每组 3 seed 的结果
```
