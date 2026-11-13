# Tokenizer & BPE — 模型的第一道门

目标：搞懂文本怎么变成 token ID，为什么所有 LLM 都用 BPE。

## 为什么需要学这个

- 所有模型的输入都是 token ID，不是字符串
- tokenizer 决定词表大小 → 影响模型参数量和推理速度
- 中文 token 效率低是很多坑的根源（一个汉字可能拆成 2-3 个 token）

## 阅读顺序

### 1. [karpathy/minbpe](https://github.com/karpathy/minbpe) — 100 行最小实现

一个文件 `minbpe/basic.py` 讲透 BPE 算法：
- 统计相邻 pair 频率 → 合并最频繁的 → 更新词表
- `train()` 和 `encode()`/`decode()` 加起来不到 100 行
- **必读**，读完就知道 tokenizer 没有魔法

### 2. [openai/tiktoken](https://github.com/openai/tiktoken) — 最快的生产级 BPE

- `tiktoken.get_encoding("cl100k_base")` GPT-4 用的
- 关键：`CoreBPE` 用 Rust 实现，比 Python 快 100 倍
- 看它怎么用正则预切分再 BPE

### 3. [google/sentencepiece](https://github.com/google/sentencepiece) — Llama/Qwen 用的

- 不把文本当字节流，当 Unicode 序列
- 支持 unigram（概率模型）和 BPE 两种
- Llama 系列的 tokenizer.model 都是 sentencepiece 格式

### 4. [huggingface/tokenizers](https://github.com/huggingface/tokenizers) — Rust 实现

- HF 生态的标准，支持 BPE/WordPiece/Unigram
- `tokenizers.Tokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")` 直接用

## 关键问题

| 问题 | 为什么重要 |
|---|---|
| 为什么不用 word-level？ | OOV 问题：词表有限，新词没法表示 |
| 为什么不用 char-level？ | 序列太长，每个汉字一个 token 还好，英文单词全拆字母 |
| BPE 怎么选合并哪个 pair？ | 选频率最高的，贪心策略 |
| 词表多大合适？ | GPT-2: 50257，Llama: 32000，Qwen: 152k，越大表达力越强但 embedding 参数多 |
| 中文为什么费 token？ | 英文词表为主时，一个汉字可能被拆成 2-3 个 byte-level token |

## 动手实验

- [ ] 用 minbpe 在一个小语料上训练自己的 tokenizer（几百行语料就行）
- [ ] 对比同一个句子用不同 tokenizer 编码的 token 数：
  ```python
  import tiktoken
  from transformers import AutoTokenizer

  text = "深度学习模型在自然语言处理中表现优异"
  gpt = tiktoken.get_encoding("cl100k_base").encode(text)
  qwen = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B").encode(text)
  # 对比 len(gpt) vs len(qwen)，体会中文 token 效率
  ```
- [ ] 算一下你常用的中文文本平均 token/字比

## 深入阅读

- [ ] HuggingFace 的 [tokenizers 文档](https://huggingface.co/docs/tokenizers/)
- [ ] Andrej Karpathy 的 [tokenizer 视频](https://www.youtube.com/watch?v=zduSFxRajkE)（2 小时，必看）
- [ ] Qwen2.5 的 tokenizer 配置 `tokenizer.json`，看它怎么处理中文
