# llama.cpp — 懂性能工程

仓库: https://github.com/ggml-org/llama.cpp
目标: 看怎么把模型跑到 CPU/手机上

## 阅读顺序
1. `ggml/` 目录 — 张量计算库（核心）
   - `ggml-cpu/` CPU 算子（SIMD / AVX / NEON）
   - `ggml-cuda/` GPU 算子
2. `src/llama.cpp` — 模型加载 + 图构建 + 推理
3. `include/gguf.h` — 自定义模型文件格式

## 关键问题
- GGUF 格式设计（为什么 mmap 友好）
- 量化：Q4_K / Q6_K / Q8_0 的内存布局和反量化
- 算子融合和内存复用怎么做
- KV cache 在 llama.cpp 里怎么管（context 滑动窗口）

## 动手实验
- [ ] `llama-cli` 跑一个 0.5B 模型，`-ngl 99` 看 GPU offload
- [ ] 读一个具体算子（比如 matmul 的 Q4 实现）
- [ ] 用 `ggml` 单独写一个小计算图
