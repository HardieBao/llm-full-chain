# TRL — 懂微调（RLHF 标准流程）

仓库: https://github.com/huggingface/trl
目标: 看 SFT/DPO/PPO/GRPO 的工业实现

## 阅读顺序
1. `trl/trainer/sft_trainer.py` — 监督微调（最简单）
2. `trl/trainer/dpo_trainer.py` — DPO（不用训练奖励模型的对齐）
3. `trl/trainer/ppo_trainer.py` — PPO（经典 RLHF）
4. `trl/trainer/grpo_trainer.py` — GRPO（DeepSeek-R1 用的）

## 关键问题
- DPO 的 loss 长什么样？（对比两个 policy 的 log-ratio）
- PPO 的 reward model 和 value model 怎么协同
- GRPO 为什么不需要 value model（组内相对排名）
- `peft` 集成：LoRA adapter 怎么挂进 trainer

## 动手实验
- [ ] 用 SFT 微调 Qwen2.5-0.5B 在一个小数据集上
- [ ] 构造偏好对数据跑一遍 DPO
- [ ] 读 GRPO 的 reward function 接口
