# 消融实验脚手架

最小依赖：trl + transformers + datasets + accelerate + torch

## 快速开始

```bash
# 1. 装依赖（推荐 uv，没有就 pip）
pip install trl transformers datasets accelerate peft bitsandbytes

# 2. 跑 baseline（不训练，直接评基座）
python eval.py --model Qwen/Qwen2.5-0.5B-Instruct --task gsm8k --num 200

# 3. 跑一组消融
python train_grpo.py --config configs/E_grpo_dr.yaml

# 4. 统一评测
python eval.py --model ./outputs/E_grpo_dr --task gsm8k --num 200
```

## 目录说明

```
configs/
├── A_baseline.yaml        # 不训练
├── B_sft.yaml             # SFT only
├── C_grpo.yaml            # GRPO only
├── D_sft_grpo.yaml        # SFT → GRPO
├── E_grpo_dr.yaml         # GRPO + Dr. GRPO（去 std）
├── F_grpo_dapo.yaml       # GRPO + DAPO 四个修复
└── G_grpo_clip.yaml       # GRPO + clip-higher only

results/
└── {group}_seed{42,43,44}/
    ├── metrics.json       # 各 benchmark 分数
    ├── curves/            # reward / KL / length 曲线
    └── config.yaml        # 当时的完整配置（可复现）
```

## 关键设计

1. **同 token budget**：SFT 和 GRPO 的训练步数按 token 数对齐
2. **同 eval**：固定 decode 参数（temp=0.7, top_p=0.8, max_tokens=1024）
3. **同 reward**：答案正确 +1，`<answer>` 格式 +0.5，超长 -0.5
4. **3 seed**：RL 方差大，必须多 seed

## 参考实现

- trl `GRPOTrainer`：`pip show trl` 找到安装路径，读 `trl/trainer/grpo_trainer.py`
- DAPO 的四个修复在 verl 里：`verl/trainer/ppo/ray_trainer.py` 搜 `clip_higher` / `dynamic_sampling`
- Dr. GRPO 改法：把 advantage 从 `(r - mean) / std` 改成 `(r - mean)`，再把 loss 归一化从 per-token 改成 fixed const
