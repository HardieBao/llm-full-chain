# 14 · 企业级 Agent 系统实战（强可控状态机 + 沙箱 + Text2SQL）

目标：跳出“写个 while 循环调 Tool”的玩具 Agent，掌握企业真正敢上线的高可靠 Agent 架构。

---

## 一、企业为什么不敢用“纯自主 Agent”（如早期 AutoGPT）？

1. **死循环烧钱**：一步调错工具，自己在那重试 50 轮，把 Token 额度烧穿。
2. **不可控越权**：在生产数据库上拼错一条 `DELETE` 或乱发一封外部邮件。
3. **格式脆弱**：模型少吐一个引号，下游解析崩溃。
4. **不可复现**：同一个问题跑两次，走的分支完全不一样，线上出 Bug 没法修。

> **企业级准则**：**能用确定性工作流（DAG）解决的，绝不交给 LLM 自由发挥；必须用 Agent 的地方，用状态机（StateGraph）锁死转移边界，用沙箱（Sandbox）隔离执行，用人在回路（HITL）卡住高危写操作。**

---

## 二、三大最高商业价值的 Agent 实战场景

### 场景 1：代码 / 渗透 / 运维 Agent（带安全沙箱闭环）

这是你最占优势的赛道：**LLM 规划 → 生成代码/脚本/Payload → 丢进隔离容器执行 → 捕获 stdout/stderr → 根據报错自我修正**。

- **标杆开源项目**：
  - **[All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)**（原 OpenDevin）— 工业级代码与终端操作 Agent 架构典范，必读它的 `EventStream`、Docker 沙箱通信机制、上下文压缩策略。
  - **[SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)** — 提出了极其重要的 **ACI（Agent-Computer Interface，专门为大模型设计的精简工具接口）** 理念：为什么直接给模型 bash 不如给它封装好的专用查看/编辑命令？
  - **[e2b-dev/E2B](https://github.com/e2b-dev/E2B)** — 毫秒级启动的云端/本地安全沙箱基础设施。

### 场景 2：Text2SQL / 企业数据商业分析 Agent

所有企业都有海量业务表（ERP、物流、托盘、财务），老板想直接问：“上个月哪个仓库的胶盒滞留率最高？同比涨了多少？”

- **为什么直接把建表语句塞给 LLM 会挂？**
  1. 企业有 500 张表，塞不进 Context。
  2. 字段名缩写含糊（比如 `wd_sts = 3` 代表什么状态？模型根本不知道）。
  3. 复杂多表 Join 极易写错 SQL 语法或写出慢查询拖垮数据库。
- **工业级 Text2SQL 架构（Vanna / WrenAI 范式）**：
  1. **语义层（Semantic Layer / MDL）**：先定义表关系、枚举值字典、业务指标口径（如“滞留率”的标准计算公式）。
  2. **Few-shot 动态召回**：用向量库检索“与当前问题最像的 5 条历史正确 SQL（Golden SQL）”塞进 Prompt。
  3. **执行校验与自愈环**：`生成 SQL → EXPLAIN 语法与开销检查 → 只读账号执行 → 若报错把 Error 喂回给模型重写（最多 3 次） → 用 ECharts 渲染图表`。
- **标杆开源项目**：
  - **[vanna-ai/vanna](https://github.com/vanna-ai/vanna)** — RAG + Text2SQL 最简洁优雅的工业实现（训练 DDL + 文档 + 历史 SQL）。
  - **[Canner/WrenAI](https://github.com/Canner/WrenAI)** — 引入语义建模层（MDL）的企业级 Text2BI 标杆。

### 场景 3：强可控多智能体状态机（LangGraph + PydanticAI）

- **[langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)**：把 Agent 写成带环图（Graph）：
  - **显式状态（TypedDict / Pydantic State）**：所有节点共享一个强类型状态对象。
  - **Checkpointer（持久化断点）**：执行到高危操作（如“确认发货”、“执行漏洞利用脚本”）自动挂起（`interrupt`），存盘等待人工审批通过后，从断点恢复继续跑。
- **[pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)**：Pydantic 官方出品，主打类型安全、依赖注入与结构化校验。

---

## 三、Agent 工具设计黄金法则（ACI 原则）

你给 Agent 写 Tool（或 MCP Server）时，遵守这 5 条能让成功率翻倍：

1. **防呆报错提示**：工具报错时不要抛 500 行 Python 堆栈，要返回**指导模型下一步怎么改的自然语言提示**（例如：`"Error: palletId 必须是整数，你传了字符串 'P1001'，请先调用 search_pallet 获取数字 ID"`）。
2. **输出截断与分页**：严禁一个工具一次性返回 5MB JSON 把上下文撑爆，强制默认 `limit=20` 并提示总条数。
3. **幂等与只读分离**：把查询类工具和写操作工具彻底分开，写操作工具强制要求 `dry_run: bool = True` 参数。
4. **扁平化参数**：尽量用一层的简单类型（`str, int, Enum`），少用三层嵌套字典。
5. **契约先行**：所有工具的 docstring 必须写清“什么时候用我、什么时候别用我、返回什么字段”。

---

## 动手实战清单

- [ ] 用 **LangGraph** 写一个带 **Human-in-the-loop（人工审批断点）** 的三节点渗透/运维 Agent：`侦察节点(自动) → 审批断点(暂停等确认) → 执行节点`
- [ ] 用 **Vanna** 连接一个本地 SQLite/MySQL 业务库（比如模拟 e-HUB 的托盘库存表），灌入 10 条业务口径说明和 10 条标准 SQL，测复杂聚合查询的准确率
- [ ] 读 **SWE-agent** 的论文或代码，理解它是怎么设计文件浏览和修改工具（ACI）来降低模型犯错率的
