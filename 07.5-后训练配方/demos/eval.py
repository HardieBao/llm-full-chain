#!/usr/bin/env python3
"""
统一评测脚本。所有消融组用同一套参数跑，保证可比。

用法：
    python eval.py --model Qwen/Qwen2.5-0.5B-Instruct --task gsm8k --num 200
    python eval.py --model ./results/C_grpo_seed42/final --task gsm8k --num 200
"""

import argparse
import json
import re
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer


def extract_answer(text: str) -> str | None:
    m = re.search(r"<answer>\s*(.*?)\s*</answer>", text, re.DOTALL)
    return m.group(1) if m else None


def extract_number(text: str) -> float | None:
    nums = re.findall(r"-?\d+\.?\d*", text)
    return float(nums[-1]) if nums else None


PROMPT_TEMPLATE = (
    "Solve the following math problem step by step. "
    "Put your final answer inside <answer></answer> tags.\n\n"
    "Problem: {problem}\n\n"
    "Solution:"
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--task", default="gsm8k", choices=["gsm8k", "math500", "ifeval"])
    p.add_argument("--num", type=int, default=200)
    p.add_argument("--output", default=None)
    args = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        device_map="auto",
    )
    model.eval()

    # 加载测试集
    if args.task == "gsm8k":
        ds = load_dataset("openai/gsm8k", "main", split=f"test[:{args.num}]")
        gold_key = "answer"
        prompt_key = "question"
    elif args.task == "math500":
        ds = load_dataset("HuggingFaceH4/MATH-500", split=f"test[:{args.num}]")
        gold_key = "answer"
        prompt_key = "problem"
    else:
        raise NotImplementedError(f"{args.task} eval not implemented yet")

    results = []
    correct = 0
    total_len = 0

    for i, item in enumerate(ds):
        prompt = PROMPT_TEMPLATE.format(problem=item[prompt_key])
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                top_p=0.8,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        text = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        total_len += len(text)

        pred = extract_number(extract_answer(text) or "")
        gold = extract_number(item[gold_key])
        is_correct = pred is not None and gold is not None and abs(pred - gold) < 1e-4

        if is_correct:
            correct += 1

        results.append({
            "idx": i,
            "correct": is_correct,
            "pred": pred,
            "gold": gold,
            "len": len(text),
        })

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(ds)}] acc={correct/(i+1):.3f}")

    metrics = {
        "model": args.model,
        "task": args.task,
        "num": len(ds),
        "acc": correct / len(ds),
        "avg_len": total_len / len(ds),
        "correct": correct,
    }

    out_path = args.output or f"eval_{args.task}_{Path(args.model).name}.json"
    with open(out_path, "w") as f:
        json.dump({"metrics": metrics, "details": results}, f, indent=2)

    print(f"\n{'='*40}")
    print(f"model:  {args.model}")
    print(f"task:   {args.task} ({len(ds)} samples)")
    print(f"acc:    {metrics['acc']:.3f}")
    print(f"avg_len:{metrics['avg_len']:.0f}")
    print(f"saved → {out_path}")


if __name__ == "__main__":
    main()
