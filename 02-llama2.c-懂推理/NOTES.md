# llama2.c — 懂推理

仓库: https://github.com/karpathy/llama2.c
目标: 单文件 C 语言搞懂 LLM 推理的所有工程细节

## 阅读顺序
`run.c` 一个文件，700 行，从上往下读：
- tokenizer（vocab 加载、BPE）
- 前向：RoPE 旋转位置编码（比 nanoGPT 的 learned pos 复杂）
- KV cache 实现（核心中的核心）
- sampler（argmax / top-p / temperature）

## 关键问题
- RoPE 和 learned positional embedding 区别？
- KV cache 为什么省算力？内存换计算的本质
- 量化的 weight 怎么读（fp32 vs int8）
- 为什么推理只需要一次 forward？

## 动手实验
- [ ] 导出一个小模型跑通推理（用 llama2.c 自带的 tinystories 权重）
- [ ] 加 beam search
- [ ] 把 int8 量化改成 int4
