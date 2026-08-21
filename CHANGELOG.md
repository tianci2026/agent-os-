# Changelog

All notable changes to Agent OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.0] - 2026-08-21

### Added
- MCP 内建工具 `agent_os_distill`：L1→L2→L3 自动提炼（subject / to_layer / max_group）
- 环境变量注入真实 LLM：`AGENT_OS_OLLAMA=1`（本地免费）/ `AGENT_OS_OPENAI_BASE_URL`
  （OpenAI 兼容 API），chat 与蒸馏共用；未注入走确定性桩（行为不变）

### Fixed
- 蒸馏真实 LLM 模式幂等：摘要/结论非确定时按「支撑集合锚点」识别重复，重跑不膨胀
- 蒸馏回调输出净化：LLM 输出前导空白 strip，空/纯空白回退模板凝练（不留空内容神经元）

## [0.10.0] - 2026-08-21

### Added
- 记忆四档检索：BM25 / 语义余弦(LSH) / 混合加权 / 图联想
- 时间旅行 `as_of(ts)`：回溯任意时刻完整记忆状态
- 遗忘有尊严：墓碑标记 + 可恢复 + 审计可回放
- 工具全生命周期治理：注册 → 审批(PENDING_REVIEW) → 版本 → 仲裁 → 沙箱 → 审计
- 进程级沙箱：subprocess 隔离 + 资源限制 + 孙进程树清理(Linux killpg / Windows Job Object)
- 工作流 DAG 引擎：并行执行 + 条件分支 + 递归子流 + 环检测
- ReAct 循环 + 多轮会话（max_steps=6）
- 多租户隔离 + token 配额治理
- MCP 标准协议服务端
- HTTP REST API + Web UI
- LLM 适配器：Ollama / OpenAI 兼容(DeepSeek/Kimi/GLM/豆包)
- 记忆蒸馏：L1→L2→L3 巩固循环
- 定时调度器 + 并发上限
- 可选 SQLite 后端（`AGENT_OS_MEMORY_BACKEND=sqlite`）：neurons 不驻留内存
- 索引检查点持久化：启动时直接加载 BM25/语义/去重/邻接索引，跳过全量重建
- as_of 段首 ts 早停：避免遍历全量 archive 段

### Security
- 22 项安全加固全部完成（1 严重 / 4 高危 / 8 中危 / 9 低危）
  - C1: 沙箱进程树清理
  - H1: baseUrl 协议白名单 + 内网/元数据黑名单
  - H2: 关鉴权时默认绑 127.0.0.1 + 醒目告警
  - H3: CORS Origin 白名单
  - H4: innerHTML 全用 esc() 转义
  - M1: token SHA-256 摘要存储
  - M2: 请求体上限 10MB
  - M3: 异常脱敏，详情只记服务端日志
  - M4: 条件求值改 AST 白名单解释器
  - M5: admin token 改 sessionStorage
  - M6: 所有 urlopen 加 timeout
  - M7: agents.json 损坏容错
  - M8: 去除硬编码路径
  - L1-L9: 转义统一/常量时间比较/邻接表/BM25增量/as_of上限/锁告警/并发上限/显式from_dict/400解析

### Tests
- 180 tests passed, 零回归（含 10 项 SQLite 后端验收）

## [0.9.0] - 2026-08-20

### Added
- 阶段 C：联邦跨项目 recall / 工具自设计实验 / 系统门面编排
- MCP Server 初版
- 结构化日志 + metrics + LLM 成本核算
- ReAct 循环 + 多轮会话

## [0.8.0] - 2026-08-19

### Added
- 阶段 B：宿主注入 embedding / 四档检索 / 图联想 / 事件总线 / 记忆图导出
- 工具仲裁（确定性多工具选优）
- 工具生命周期状态机

## [0.7.0] - 2026-08-19

### Added
- 阶段 A：记忆内核 / 持久层 / 工具注册 / 意图路由
- JSONL oplog + snapshot + compaction
- 跨进程文件锁 + 原子写
