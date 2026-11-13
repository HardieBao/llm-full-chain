# 入门准备 — 环境和基础

## 环境检查清单

- [ ] Python 3.10+（推荐 uv 管环境）
- [ ] CUDA 可用：`python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Git、VS Code / Cursor
- [ ] HuggingFace 账号 + `huggingface-cli login`

## 数学基础（够用就行）

不需要先学一遍线代，读代码时遇到再补：

| 概念 | 哪里会用到 | 快速补 |
|---|---|---|
| 矩阵乘法 | 所有 linear 层 | 知道 [m,k]×[k,n]=[m,n] |
| softmax | attention 权重 | 公式 + 数值稳定性（减 max） |
| 交叉熵 | 语言模型 loss | 就是负 log 概率 |
| 反向传播 | 训练 | 链式法则，知道梯度怎么流就行 |
| 均值/方差/标准差 | normalization、GRPO | 归一化的直觉 |

## PyTorch 最小知识

读 nanoGPT 前需要知道这些：

```python
import torch
import torch.nn as nn

# 1. 张量和设备
x = torch.randn(4, 8).cuda()

# 2. nn.Module：所有层都是它
class MyLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(8, 16)
    def forward(self, x):
        return self.linear(x)

# 3. 训练四步
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
loss.backward()      # 算梯度
optimizer.step()     # 更新权重
optimizer.zero_grad() # 清梯度

# 4. einsum（attention 里常见）
attn = torch.einsum('bthd,bshd->bths', q, k)
```

## 前置阅读

- [ ] [karpathy 的 Zero to Hero 系列](https://karpathy.ai/zero-to-hero.html) — 看完 `makemore` 前 3 集就够
- [ ] PyTorch 官方 60 分钟入门

## 硬件建议

| 预算 | 能跑什么 |
|---|---|
| 0 元 | Colab free tier（T4 15G）→ 能跑 nanoGPT + 0.5B 微调 |
| ~3000 元 | 二手 3060 12G → nanoGPT 全量 + 1B 模型微调 |
| ~8000 元 | 二手 3090 24G → 所有本地实验都够（含 7B QLoRA） |
| 云 | AutoDL 4090 ≈ ¥1.5/h → 按需租用最划算 |
