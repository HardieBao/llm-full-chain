# 预训练工程 — 从代码到真实训练

目标：读工业级预训练代码，理解数据工程、分布式训练、scaling law。

> 这个阶段大部分**只能读不能跑**——真预训练要几十卡到几千卡。重点是把概念读懂。

## 阅读顺序

### 1. [huggingface/nanotron](https://github.com/huggingface/nanotron) — 最精简的分布式训练框架

为什么选它而不是 Megatron-LM：**代码量少一个量级**，3D 并行的核心都在。

读这些文件：
- `nanotron/parallel/tensor_parallel.py` — TP 怎么切权重矩阵
- `nanotron/parallel/pipeline_parallel.py` — PP 怎么切层
- `nanotron/parallel/data_parallel.py` — DP + ZeRO
- `nanotron/trainer.py` — 主训练循环怎么把三种并行串起来

关键问题：
- TP 切的是矩阵的哪个维度？（列切还是行切，效果不同）
- PP 的 bubble 是什么？为什么 1F1B 调度能减少它？
- DP 为什么要 gradient all-reduce？ZeRO-1/2/3 区别在哪？
- activation checkpointing 省显存的原理

### 2. [jzhang38/TinyLlama](https://github.com/jzhang38/TinyLlama) — 真实的预训练全程公开

1.1B 模型、3T tokens 的**完整**训练日志和中间 checkpoint 全公开：
- `TRAINING.md` 里有完整的 loss 曲线和调参记录
- 看真实的 loss spike 什么时候出现、怎么恢复
- 数据配比：他们怎么混合代码/文本/数学数据

### 3. [huggingface/datatrove](https://github.com/huggingface/datatrove) — 数据工程

预训练一半工作量在数据处理。读：
- `datatrove/pipeline/` — 去重（MinHash）、过滤、质量打分、去 PII
- FineWeb 数据集的构造流程（论文 + 代码配套看）

关键问题：
- MinHash 去重的原理？
- 质量分类器怎么训的？（FastText 二分类，好的语料 vs C4 尾部）
- 为什么要去重？（防止记忆 + 提升泛化）

### 4. [NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM) — 概念大全

不用全读，看这几个：
- `megatron/core/tensor_parallel/` — 最经典的 TP 实现（ColumnParallel / RowParallel）
- `megatron/core/pipeline_parallel/` — PP 调度（1F1B / interleaved）
- `megatron/core/distributed/` — ZeRO 实现

## Scaling Law（理论）

必读：
- [ ] Chinchilla 论文（DeepMind, 2022）：`N_opt ∝ D^0.5`，模型和数据要同步扩展
- [ ] [Hoffmann et al. 的 compute-optimal frontier](https://arxiv.org/abs/2203.15556)

关键结论：**模型参数量 N 和训练 token 数 D 应该等比增长**。Llama-7B 用 1T tokens 是欠训练的，Chinchilla 70B 用 1.4T 才到最优。

## 训练稳定性

真实预训练最常见的问题：

| 现象 | 原因 | 解决 |
|---|---|---|
| loss spike | lr 过大 / 数据脏 / bf16 溢出 | 降 lr、clip grad、回退 checkpoint |
| loss 不降 | 数据没 shuffle / tokenizer 错 / 学习率太小 | 排查 pipeline |
| 吞吐不达标 | TP 通信开销 / IO bottleneck | nsys profile，减 TP 或加缓存 |

## 动手实验（能做的）

- [ ] 用 nanotron 在 4 卡上跑一次 nanoGPT 级模型的 DP 训练（验证通信正常）
- [ ] 读 TinyLlama 的 loss 曲线，找出 spike 位置对照他们的 log 看怎么处理的
- [ ] 用 datatrove 跑一遍 MinHash 去重，看删掉了多少
- [ ] 计算：给你 D 个 token，Chinchilla 最优模型多大？`N ≈ D / 20`

## 读不进去的跳过

- FlashAttention 的 CUDA kernel 细节（知道它省显存就行）
- 3D 并行的具体通信原语（除非你要写框架）
- MOE 的 expert routing 细节（DeepSeek-V3 报告里看看概念就行）
