import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'LLM-Full-Chain',
  description: '大模型全链路硬核实战：从 600 行源码、GRPO 后训练消融、企业级 RAG/Agent 到红队破甲',
  lang: 'zh-CN',
  base: '/llm-full-chain/',
  ignoreDeadLinks: true,
  srcExclude: [
    '00-辅助学习工具/**',
    '辅助学习项目/**',
    '.qoder/**',
    '**/nanoGPT/**',
    '**/node_modules/**'
  ],
  themeConfig: {
    nav: [
      { text: '首页路线图', link: '/' },
      { text: '12周闯关计划', link: '/STUDY-PLAN' },
      { text: '第一阶段：原理与推理', link: '/01-nanoGPT-懂原理/NOTES' },
      { text: '第二阶段：训练与消融', link: '/07.5-后训练配方/NOTES' },
      { text: '第三阶段：企业级实战', link: '/12-垂直领域模型实战/NOTES' },
      { text: '第四阶段：红队与破甲', link: '/11-LLM安全-破甲破限/NOTES' }
    ],
    sidebar: [
      {
        text: '全局导览',
        items: [
          { text: '全景路线图 (README)', link: '/' },
          { text: '12 周实战打卡计划', link: '/STUDY-PLAN' }
        ]
      },
      {
        text: '第一阶段：原理与高性能推理 (00~05)',
        items: [
          { text: '00 · 入门准备与环境', link: '/00-入门准备/NOTES' },
          { text: '01 · nanoGPT 懂原理', link: '/01-nanoGPT-懂原理/NOTES' },
          { text: '02 · llama2.c 懂推理', link: '/02-llama2.c-懂推理/NOTES' },
          { text: '02.5 · Tokenizer 与 BPE', link: '/02.5-tokenizer-BPE/NOTES' },
          { text: '03 · Transformers 工业实现', link: '/03-transformers-Llama-工业实现/NOTES' },
          { text: '04 · llama.cpp 端侧量化', link: '/04-llama.cpp-性能工程/NOTES' },
          { text: '05 · vLLM 高并发推理', link: '/05-vllm-性能工程/NOTES' }
        ]
      },
      {
        text: '第二阶段：预训练、后训练与消融 (05.5~08)',
        items: [
          { text: '05.5 · 预训练工程与 3D 并行', link: '/05.5-预训练工程/NOTES' },
          { text: '06 · TRL 微调标准库', link: '/06-trl-微调/NOTES' },
          { text: '07 · Unsloth 显存优化', link: '/07-unsloth-微调/NOTES' },
          { text: '07.5 · 后训练配方与 GRPO 消融', link: '/07.5-后训练配方/NOTES' },
          { text: '08 · 评估体系 (Eval)', link: '/08-评估-eval/NOTES' }
        ]
      },
      {
        text: '第三阶段：应用架构与企业实战 (09~10, 12~15)',
        items: [
          { text: '09 · Dify 应用平台源码', link: '/09-dify-应用层/NOTES' },
          { text: '10 · LlamaIndex RAG 组件', link: '/10-llama_index-应用层/NOTES' },
          { text: '12 · 【实战】垂直领域模型端到端', link: '/12-垂直领域模型实战/NOTES' },
          { text: '13 · 【实战】企业级高准确度 RAG', link: '/13-企业级RAG实战/NOTES' },
          { text: '14 · 【实战】企业级强可控 Agent', link: '/14-企业级Agent实战/NOTES' },
          { text: '15 · 【实战】LLMOps 与降本上线', link: '/15-LLMOps与上线工程/NOTES' }
        ]
      },
      {
        text: '第四阶段：安全攻防与模型手术 (11)',
        items: [
          { text: '11 · LLM 红队、破甲与 Abliteration', link: '/11-LLM安全-破甲破限/NOTES' }
        ]
      }
    ],
    search: {
      provider: 'local'
    },
    outline: {
      level: [2, 3],
      label: '本页目录'
    }
  }
})
