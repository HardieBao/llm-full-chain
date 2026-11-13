# vLLM — 懂性能工程（高并发 serving）

仓库: https://github.com/vllm-project/vllm
目标: 看怎么把模型跑成生产级 API 服务

## 阅读顺序
1. `vllm/attention/` — PagedAttention（论文核心：KV cache 分页管理）
2. `vllm/core/` — 调度器（continuous batching）
3. `vllm/engine/` — 引擎主循环
4. `vllm/executor/` — 分布式执行

## 关键问题
- PagedAttention 为什么省显存？（类比 OS 虚拟内存分页）
- continuous batching 怎么调度（不等 batch 内全部完成）
- CUDA graph 怎么 capture 推理计算
- 前缀缓存（prefix caching）怎么命中

## 动手实验
- [ ] 起 vLLM 服务，`benchmark_serving.py` 压测
- [ ] 读 KV block manager 的分配/释放逻辑
- [ ] 对比 llama.cpp 的 KV cache 管理思路
