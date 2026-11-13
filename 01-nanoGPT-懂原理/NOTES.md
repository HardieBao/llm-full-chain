# nanoGPT — 懂原理

仓库: https://github.com/karpathy/nanoGPT
目标: 用最少的代码看懂 GPT 的完整训练 + 推理循环

## 阅读顺序
1. `model.py` — Transformer 全貌（Embedding → Block×N → LayerNorm → LM Head）
2. `train.py` — 训练循环、optimizer、lr schedule、梯度累积
3. `sample.py` — 推理生成（top-k 采样）

## 关键问题
- causal mask 怎么实现的？
- weight tying（embedding 和 LM head 共享权重）在哪？
- AdamW 里 weight decay 怎么作用的？
- FlashAttention 和手写 attention 等价在哪？

## 动手实验
- [ ] 把 d_model 改小跑一个 Shakespeare char-level 模型
- [ ] 实现一个 KV cache（原版推理每次重新算全序列，自己加速）
- [ ] 去掉 LayerNorm 看 loss 怎么炸
