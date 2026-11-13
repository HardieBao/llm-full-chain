#!/usr/bin/env python3
"""
一键按需拉取各章节对应的经典开源源码仓库（默认 --depth 1 浅克隆省空间）。

用法：
    python scripts/clone_repos.py --list          # 查看所有章节与对应仓库
    python scripts/clone_repos.py --stage 01 02   # 只拉取第 01、02 章的源码
    python scripts/clone_repos.py --light         # 拉取所有轻量级必读仓库 (<100MB)
    python scripts/clone_repos.py --all           # 拉取全部章节参考仓库
"""

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPOS = [
    {
        "id": "01",
        "dir": "01-nanoGPT-懂原理/nanoGPT",
        "url": "https://github.com/karpathy/nanoGPT.git",
        "light": True,
        "desc": "600行PyTorch最小GPT训练与推理闭环",
    },
    {
        "id": "02",
        "dir": "02-llama2.c-懂推理/llama2.c",
        "url": "https://github.com/karpathy/llama2.c.git",
        "light": True,
        "desc": "700行单文件纯C推理 Llama 2 (KV Cache / RoPE / RMSNorm)",
    },
    {
        "id": "02.5",
        "dir": "02.5-tokenizer-BPE/minbpe",
        "url": "https://github.com/karpathy/minbpe.git",
        "light": True,
        "desc": "100行最小BPE Tokenizer实现",
    },
    {
        "id": "03",
        "dir": "03-transformers-Llama-工业实现/transformers",
        "url": "https://github.com/huggingface/transformers.git",
        "light": False,
        "desc": "HuggingFace 工业级模型实现标准 (精读 modeling_llama.py)",
    },
    {
        "id": "04",
        "dir": "04-llama.cpp-性能工程/llama.cpp",
        "url": "https://github.com/ggml-org/llama.cpp.git",
        "light": False,
        "desc": "C++量化与全平台高性能推理引擎",
    },
    {
        "id": "05",
        "dir": "05-vllm-性能工程/vllm",
        "url": "https://github.com/vllm-project/vllm.git",
        "light": False,
        "desc": "PagedAttention 与高并发推理服务框架",
    },
    {
        "id": "05.5",
        "dir": "05.5-预训练工程/nanotron",
        "url": "https://github.com/huggingface/nanotron.git",
        "light": True,
        "desc": "HuggingFace 精简 3D 并行预训练框架 (TP/PP/DP)",
    },
    {
        "id": "06",
        "dir": "06-trl-微调/trl",
        "url": "https://github.com/huggingface/trl.git",
        "light": True,
        "desc": "SFT / DPO / PPO / GRPO 后训练标准库",
    },
    {
        "id": "07",
        "dir": "07-unsloth-微调/unsloth",
        "url": "https://github.com/unslothai/unsloth.git",
        "light": True,
        "desc": "手写 Triton Kernel 显存减半的高效微调库",
    },
    {
        "id": "07.5",
        "dir": "07.5-后训练配方/open-r1",
        "url": "https://github.com/huggingface/open-r1.git",
        "light": True,
        "desc": "DeepSeek-R1 开源复现全流程管线",
    },
    {
        "id": "08",
        "dir": "08-评估-eval/lm-evaluation-harness",
        "url": "https://github.com/EleutherAI/lm-evaluation-harness.git",
        "light": False,
        "desc": "业界标准的 LLM 权威基准评测框架",
    },
    {
        "id": "09",
        "dir": "09-dify-应用层/dify",
        "url": "https://github.com/langgenius/dify.git",
        "light": False,
        "desc": "生产级 LLM 应用与 Agent 工作流平台",
    },
    {
        "id": "10",
        "dir": "10-llama_index-应用层/llama_index",
        "url": "https://github.com/run-llama/llama_index.git",
        "light": False,
        "desc": "RAG 数据索引、检索与重排组件库",
    },
    {
        "id": "11",
        "dir": "11-LLM安全-破甲破限/HarmBench",
        "url": "https://github.com/centerforaisafety/HarmBench.git",
        "light": True,
        "desc": "LLM 红队越狱攻击与防御标准评测集",
    },
    {
        "id": "12",
        "dir": "12-垂直领域模型实战/LLaMA-Factory",
        "url": "https://github.com/hiyouga/LLaMA-Factory.git",
        "light": True,
        "desc": "企业级垂直模型微调瑞士军刀",
    },
    {
        "id": "13",
        "dir": "13-企业级RAG实战/ragflow",
        "url": "https://github.com/infiniflow/ragflow.git",
        "light": False,
        "desc": "深度文档解析 (DeepDoc) 与企业级生产 RAG 引擎",
    },
    {
        "id": "14",
        "dir": "14-企业级Agent实战/OpenHands",
        "url": "https://github.com/All-Hands-AI/OpenHands.git",
        "light": False,
        "desc": "带安全容器沙箱的工业级代码与终端操作 Agent",
    },
    {
        "id": "15",
        "dir": "15-LLMOps与上线工程/langfuse",
        "url": "https://github.com/langfuse/langfuse.git",
        "light": False,
        "desc": "开源 LLMOps 可观测性、Tracing 与数据飞轮平台",
    },
]


def clone_one(item: dict):
    target = ROOT / item["dir"]
    if target.exists() and any(target.iterdir()):
        print(f"[skip] {item['id']} 已存在: {item['dir']}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"[clone] {item['id']} -> {item['dir']} ({item['url']})")
    subprocess.run(
        ["git", "clone", "--depth", "1", item["url"], str(target)],
        check=False,
    )


def main():
    p = argparse.ArgumentParser(description="按需克隆 llm-full-chain 配套源码仓库")
    p.add_argument("--list", action="store_true", help="列出所有章节配套仓库")
    p.add_argument("--stage", nargs="+", help="指定章节编号，如 --stage 01 02 02.5")
    p.add_argument("--light", action="store_true", help="克隆所有轻量级必读仓库")
    p.add_argument("--all", action="store_true", help="克隆全部仓库")
    args = p.parse_args()

    if args.list or not (args.stage or args.light or args.all):
        print(f"{'编号':<6} {'轻量':<5} {'目标路径':<38} {'说明'}")
        print("-" * 88)
        for r in REPOS:
            tag = "Yes" if r["light"] else "No"
            print(f"{r['id']:<6} {tag:<5} {r['dir']:<38} {r['desc']}")
        print("\n示例: python scripts/clone_repos.py --stage 01 02 02.5")
        return

    selected = []
    if args.all:
        selected = REPOS
    elif args.light:
        selected = [r for r in REPOS if r["light"]]
    elif args.stage:
        wanted = set(args.stage)
        selected = [r for r in REPOS if r["id"] in wanted]

    for r in selected:
        clone_one(r)


if __name__ == "__main__":
    main()
