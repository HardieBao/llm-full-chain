# transformers 读 Llama — 懂工业实现

仓库: https://github.com/huggingface/transformers
目标: 看一个生产级模型实现长什么样

## 阅读顺序
1. `src/transformers/models/llama/modeling_llama.py` — 单文件读懂 Llama
   - `LlamaRMSNorm`（不是 LayerNorm）
   - `LlamaRotaryEmbedding` + `apply_rotary_pos_emb`
   - `LlamaAttention`（GQA: num_key_value_heads）
   - `LlamaMLP`（SwiGLU）
   - `LlamaDecoderLayer` → `LlamaModel` → `LlamaForCausalLM`
2. `configuration_llama.py` — 超参结构
3. `generation/utils.py` — generate() 的完整逻辑

## 关键问题
- GQA（分组查询注意力）怎么实现的？K/V 头数 < Q 头数
- RMSNorm 为什么比 LayerNorm 快？
- HuggingFace 怎么兼容几十种 attention backend（sdpa/flash/eager）
- `past_key_values` 的 cache 接口长什么样

## 动手实验
- [ ] 用 transformers 加载 Qwen2.5-0.5B，打印每层的 weight shape
- [ ] 手动跑一次 forward，不走 generate()，自己实现采样
- [ ] 对比 llama2.c 的 forward 和 modeling_llama.py 的 forward
