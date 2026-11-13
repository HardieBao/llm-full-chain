# Unsloth — 懂微调（显存优化）

仓库: https://github.com/unslothai/unsloth
目标: 看怎么用 Triton kernel 把微调显存砍 70%

## 阅读顺序
1. `unsloth/kernels/` — 手写 Triton kernel（核心资产）
   - `cross_entropy_loss.py` — chunked CE，不存 logits
   - `rms_layernorm.py` / `rope_embedding.py` / `swiglu.py`
2. `unsloth/models/` — 模型 patch 逻辑（怎么替换 HF 的层）

## 关键问题
- chunked cross-entropy 为什么省显存（不 materialize vocab 维度的 logits）
- Triton kernel 的手写和编译
- LoRA 的梯度回传怎么在量化 weight 上做（QLoRA）
- 对比 HF 原版算子 vs unsloth 的 Triton 版本

## 动手实验
- [ ] 用 unsloth 微调一个小模型，对比原生 HF 的显存占用
- [ ] 读一个 Triton kernel（推荐 cross_entropy_loss）
- [ ] 理解 LoRA 和 QLoRA 的实现差异
