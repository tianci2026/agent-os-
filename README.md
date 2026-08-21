# Agent OS

> 零依赖的 agent 记忆与工具治理插件包。纯 Python stdlib，`pip install` 即用。
> 给任意 LLM agent 装上四档记忆召回 + 工具审批沙箱 + 时间旅行，长程任务省 60%+ token。

## 为什么需要 Agent OS

传统 agent 每轮对话把全部历史重新注入 prompt，token 消耗是 **O(N²)**——20 轮 4.2 万 token，100 轮 120 万。

Agent OS 通过 `recall(top_k=5)` 精准召回，把历史注入降到 **O(N)**——每轮只注入 5 条相关记忆，轮数越多省得越多。配合蒸馏压缩（25:1）、工具仲裁（试错 3→1 次）、ReAct 轮次上限，长程任务实际计费省 60-70%。

## 核心特性

- **记忆四档检索**：BM25（词频）/ 语义（余弦）/ 混合（加权融合）/ 图联想（突触遍历扩展）
- **时间旅行**：`as_of(ts)` 回溯任意时刻的完整记忆状态
- **遗忘有尊严**：墓碑标记而非硬删除，可恢复，审计可回放
- **工具全生命周期治理**：注册 → 审批（PENDING_REVIEW）→ 版本 → 仲裁 → 沙箱隔离 → 审计
- **进程级沙箱**：subprocess 隔离 + 资源限制（CPU/内存/文件数）+ 孙进程树清理
- **工作流 DAG 引擎**：并行执行 + 条件分支 + 递归子流 + 环检测
- **多租户隔离**：每租户独立记忆/工具/会话/工作流，token 配额治理
- **可选 SQLite 后端**：`AGENT_OS_MEMORY_BACKEND=sqlite`，neurons 不驻留内存 + 索引检查点启动加速
- **MCP 标准协议**：内置 MCP Server，Claude / Cursor / 任意 MCP 客户端可直接接入
- **零依赖**：纯 Python stdlib，无 pip 依赖，无依赖冲突

## 安装

```bash
pip install agent-os
```

或直接从源码：

```bash
git clone https://gitcode.com/tianci2026/agent-os.git
cd agent-os
python -m unittest discover -s tests  # 180 tests, 0 deps
```

## 快速开始

### 1. 记忆召回（3 行代码）

```python
from agent_os import MemoryCore, Source

mem = MemoryCore("./my_store")
nid = mem.record("KV cache 加速推理", layer=1, subject="project:x",
                 source=Source(type="user", ref="u1"))

hits = mem.recall("KV cache", subject="project:x", top_k=5)
for h in hits:
    print(h.neuron.content, h.score)
```

### 2. 四档检索

```python
# BM25（默认，纯文本）
hits = mem.recall("缓存优化", mode="bm25")

# 语义（需宿主注入 embedding）
hits = mem.recall("cache", mode="semantic", query_embedding=[0.1, 0.2, ...])

# 混合（BM25 + 语义加权）
hits = mem.recall("cache", mode="hybrid", query_embedding=[0.1, 0.2, ...])

# 图联想（种子 + 突触扩展）
hits = mem.recall("cache", mode="graph")
```

### 3. 工具治理 + 沙箱

```python
from agent_os import ToolRegistry

reg = ToolRegistry("./my_store")
reg.register_tool({
    "tool_id": "tool:calc", "name": "计算器", "version": "1.0",
    "description": "执行数学表达式计算", "parameters": {"expr": "string"},
    "permission_level": "PROJECT_WRITE", "sandbox": True})

# LLM 生成的工具默认 PENDING_REVIEW，需 admin 显式批准
reg.approve_tool("tool:calc")

# 执行
result = reg.execute("tool:calc", {"expr": "1+1"})
```

### 4. 时间旅行

```python
import time
mem.record("早期记忆", layer=1, subject="x", source=Source(type="user", ref="u1"))
t1 = time.time()
time.sleep(0.02)
mem.record("晚期记忆", layer=1, subject="x", source=Source(type="user", ref="u1"))

view = mem.as_of(t1)  # 只看到"早期记忆"，"晚期记忆"尚未发生
```

### 5. 启动 Web UI

```bash
python serve_ui.py ./data/webui 8787
# 打开 http://127.0.0.1:8787
```

### 6. 启动 MCP Server

```python
from agent_os.mcp_server import MCPServer
server = MCPServer("./my_store")
server.serve()  # Claude / Cursor 可通过 MCP 协议接入
```

### 6.5 DeepSeek Harness 插件（一行安装）

```sh
dsh plugin --profile web add agent-os-dsh
```

安装后自动挂载 MCP 接入：`mcp__agentos__agent_os_chat` / `recall` / `distill` /
`trigger_workflow` 等工具直接可用（本地 Ollama 免费通道，详见 `dsh-plugin/README.md`）。

### 7. SQLite 后端（规模化）

```bash
AGENT_OS_MEMORY_BACKEND=sqlite python serve_ui.py
# neurons 不驻留内存，索引检查点持久化，启动直接加载
```

## 架构

```
┌─────────────────────────────────────────────────────┐
│                   Agent OS                          │
├───────────┬───────────┬───────────┬───────────────┤
│  Memory   │  Tools    │  Workflow │   Runtime     │
│  Core     │  Registry │  DAG      │   ReAct       │
├───────────┼───────────┼───────────┼───────────────┤
│ recall    │ register  │ parallel  │ run_react     │
│  bm25     │ approve   │ branch    │ chat_once     │
│  semantic │ arbitrate │ recurse   │ max_steps=6   │
│  hybrid   │ sandbox   │ cycle chk │               │
│  graph    │ audit     │           │               │
├───────────┴───────────┴───────────┴───────────────┤
│          Persistence (JSONL / SQLite)              │
│     oplog + snapshot + as_of + compaction          │
├─────────────────────────────────────────────────────┤
│    MCP Server  │  Web API  │  Multi-tenant Auth    │
└─────────────────────────────────────────────────────┘
         零依赖 · 纯 Python stdlib · 180 tests
```

## 模块

| 模块 | 职责 |
|---|---|
| `memory` | MemoryCore：记录/链接/召回/遗忘/恢复/时间旅行/子 agent 协议 |
| `retrieval` | BM25 / 语义余弦(LSH) / 混合 / 图联想 |
| `persistence` | JSONL oplog + snapshot + compaction + SQLite 可选后端 |
| `tools` | 工具注册/意图路由/仲裁/生命周期/版本/审计/权限 |
| `sandbox` | 进程级隔离（subprocess + 资源限制 + 孙进程清理） |
| `workflow` | DAG 工作流引擎（并行/条件/递归/环检测） |
| `runtime` | ReAct 循环 + 多轮会话 |
| `distillation` | 记忆蒸馏（L1→L2→L3 巩固循环） |
| `scheduler` | 定时调度 + 并发上限 |
| `auth` | 多租户鉴权 + token 摘要存储 |
| `metrics` | 用量追踪 + 配额治理 + LLM 成本核算 |
| `mcp_server` | MCP 标准协议服务端 |
| `web_api` | HTTP REST API + Web UI |

## LLM 兼容

通过 OpenAI 兼容协议接入任意 LLM：

| LLM | base_url | 状态 |
|---|---|---|
| Ollama（本地） | `http://localhost:11434` | ✅ 原生支持 |
| DeepSeek | `https://api.deepseek.com/v1` | ✅ OpenAI 兼容 |
| OpenAI | `https://api.openai.com/v1` | ✅ OpenAI 兼容 |
| Kimi / GLM / 豆包 | 各自 API 端点 | ✅ OpenAI 兼容 |

## 测试

```bash
python -m unittest discover -s tests -p "test_*.py"
# Ran 180 tests in ~50s — OK
```

## 安全

22 项安全加固全部完成（1 严重 / 4 高危 / 8 中危 / 9 低危），详见 `deliverables/security-audit-report-2026-08-21.md`。

规模化加固：沙箱孙进程清理（C1）、as_of 早停（D5）、SQLite 后端 + 索引检查点（D1）。

## 项目结构

```
agent-os/
├── agent_os/           # 源码（~7000 行）
├── tests/              # 180 测试
├── frontend/           # Web UI（单 HTML）
├── docs/               # 设计规范
├── deliverables/       # 审计报告
├── examples/           # 示例代码
├── serve_ui.py         # Web UI 启动脚本
└── pyproject.toml      # 打包配置
```

## License

[AGPL-3.0](LICENSE) — GNU Affero General Public License v3.0。网络服务使用也必须开源修改后的源码。

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。提交前请确保 `python -m unittest discover -s tests` 通过。
