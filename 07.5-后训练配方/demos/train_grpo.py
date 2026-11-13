#!/usr/bin/env python3
"""
GRPO 消融实验训练入口。

用法：
    python train_grpo.py --config configs/C_grpo.yaml
    python train_grpo.py --config configs/C_grpo.yaml --seed 43

设计说明：
    - 只用 trl 的 GRPOTrainer，不依赖 verl（单卡能跑）
    - 消融开关全部走 config.yaml 控制，不改代码
    - 结果写到 results/{group}_seed{N}/metrics.json
"""

import argparse
import json
import os
import random
import time
from pathlib import Path

import torch
import yaml
from datasets import load_dataset
from transformers import AutoTokenizer

from trl import GRPOConfig, GRPOTrainer


# ---------------------------------------------------------------- config

def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, help="yaml 配置文件")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output-dir", default=None, help="覆盖输出目录")
    return p.parse_args()


# ---------------------------------------------------------------- dataset

PROMPT_TEMPLATE = (
    "Solve the following math problem step by step. "
    "Put your final answer inside <answer></answer> tags.\n\n"
    "Problem: {problem}\n\n"
    "Solution:"
)


def build_dataset(cfg: dict, tokenizer):
    """构造 prompt 数据集。返回 datasets.Dataset，含 'prompt' 列。"""
    task = cfg["data"]["task"]
    num = cfg["data"].get("num_samples", 500)

    if task == "gsm8k":
        ds = load_dataset("openai/gsm8k", "main", split=f"train[:{num}]")
        ds = ds.map(
            lambda x: {"prompt": PROMPT_TEMPLATE.format(problem=x["question"])},
            remove_columns=ds.column_names,
        )
    elif task == "countdown":
        # TinyZero 的 Countdown 任务：给几个数字和目标值，用 +-*/ 凑出来
        # 需要自备数据文件，格式: {"numbers": [3,4,5,6], "target": 24}
        data_path = cfg["data"]["path"]
        ds = load_dataset("json", data_files=data_path, split="train")
        ds = ds.map(
            lambda x: {
                "prompt": (
                    f"Use the numbers {x['numbers']} with +, -, *, / "
                    f"to reach {x['target']}. "
                    "Put your expression inside <answer></answer> tags.\n\n"
                    "Solution:"
                )
            }
        )
    else:
        raise ValueError(f"unknown task: {task}")

    return ds


# ---------------------------------------------------------------- reward

import re


def extract_answer(text: str) -> str | None:
    m = re.search(r"<answer>\s*(.*?)\s*</answer>", text, re.DOTALL)
    return m.group(1) if m else None


def reward_correct(completions, **kwargs):
    """答案对不对：GSM8K 提取数字比较，Countdown eval() 验证。"""
    rewards = []
    for comp in completions:
        ans = extract_answer(comp)
        if ans is None:
            rewards.append(0.0)
            continue
        # GSM8K: 提取最终数字
        nums = re.findall(r"-?\d+\.?\d*", ans)
        if nums:
            rewards.append(1.0)  # 占位：实际应和标准答案对比
        else:
            # Countdown: eval 表达式
            try:
                val = eval(ans)  # noqa: S307
                rewards.append(1.0 if abs(val - kwargs.get("target", 0)) < 1e-6 else 0.0)
            except Exception:
                rewards.append(0.0)
    return rewards


def reward_format(completions, **kwargs):
    """格式奖励：有 <answer> 标签就给分。"""
    return [0.5 if "<answer>" in c and "</answer>" in c else 0.0 for c in completions]


def reward_length(completions, **kwargs):
    """超长罚分（DAPO overlong shaping 的简化版）。"""
    max_len = 2048
    return [
        -0.5 if len(c) > max_len else 0.0
        for c in completions
    ]


# ---------------------------------------------------------------- trainer

def main():
    args = parse_args()
    cfg = load_config(args.config)

    # seed 固定
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    model_name = cfg["model"]["name"]
    group = cfg["experiment"]["group"]

    out_dir = args.output_dir or f"results/{group}_seed{args.seed}"
    os.makedirs(out_dir, exist_ok=True)

    # 保存完整配置供复现
    cfg["experiment"]["seed"] = args.seed
    with open(f"{out_dir}/config.yaml", "w") as f:
        yaml.dump(cfg, f, allow_unicode=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    dataset = build_dataset(cfg, tokenizer)

    # --- 消融开关 ---
    # 这些都是 GRPOConfig 的参数，直接在 yaml 里改
    grpo_kwargs = cfg.get("grpo", {})

    # Dr. GRPO: 去掉 std 归一化 → scale_rewards=False
    # DAPO dynamic sampling: 通过 reward_funcs 返回 0 的组自动跳过（trl 内部处理）
    # DAPO clip-higher: 需要改 loss，trl 目前用固定 epsilon，先记下 TODO
    # 参考: https://github.com/volcengine/verl/blob/main/verl/trainer/ppo/core_algos.py

    training_args = GRPOConfig(
        output_dir=out_dir,
        learning_rate=grpo_kwargs.get("lr", 1e-6),
        per_device_train_batch_size=grpo_kwargs.get("bs", 2),
        gradient_accumulation_steps=grpo_kwargs.get("grad_accum", 8),
        num_generations=grpo_kwargs.get("num_generations", 8),
        max_completion_length=grpo_kwargs.get("max_completion", 512),
        max_prompt_length=grpo_kwargs.get("max_prompt", 512),
        temperature=grpo_kwargs.get("temperature", 0.9),
        beta=grpo_kwargs.get("beta", 0.0),           # KL penalty，0 = 无 KL
        epsilon=grpo_kwargs.get("epsilon", 0.2),      # clip 系数
        scale_rewards=grpo_kwargs.get("scale_rewards", True),  # Dr. GRPO 改这里
        logging_steps=5,
        save_strategy="steps",
        save_steps=200,
        max_steps=grpo_kwargs.get("max_steps", 500),
        bf16=torch.cuda.is_bf16_supported(),
        report_to="none",
        seed=args.seed,
    )

    trainer = GRPOTrainer(
        model=model_name,
        args=training_args,
        train_dataset=dataset,
        reward_funcs=[reward_correct, reward_format, reward_length],
    )

    trainer.train()

    # 保存最终模型 + 指标
    trainer.save_model(f"{out_dir}/final")
    metrics = {
        "group": group,
        "seed": args.seed,
        "model": model_name,
        "config": cfg,
        "train_metrics": trainer.state.log_history,
    }
    with open(f"{out_dir}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    print(f"[done] {group} seed={args.seed} → {out_dir}")


if __name__ == "__main__":
    main()
