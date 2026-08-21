# Contributing to Agent OS

感谢你对 Agent OS 的兴趣！本文档描述如何参与贡献。

## 开发环境

Agent OS 是**零依赖**项目，只需 Python 3.9+：

```bash
git clone https://gitcode.com/tianci2026/agent-os.git
cd agent-os
python -m unittest discover -s tests  # 确认 180 tests 通过
```

可选安装开发工具：

```bash
pip install mypy pytest  # 类型检查 + 测试运行器
mypy agent_os --config-file mypy.ini  # 类型检查
```

## 提交前检查清单

每次提交前必须通过以下检查：

```bash
# 1. 全量测试
python -m unittest discover -s tests -p "test_*.py"
# 期望: Ran 180 tests -- OK

# 2. 类型检查（可选但推荐）
mypy agent_os --config-file mypy.ini
```

## 零依赖红线

**不引入任何第三方运行时依赖。** Agent OS 的核心卖点是 `pip install agent-os` 零摩擦安装。

- ✅ `sqlite3`, `json`, `os`, `pathlib`, `threading`, `urllib` — stdlib 可用
- ❌ `numpy`, `requests`, `pydantic` — 禁止加入 dependencies
- 如果需要新功能必须用第三方库，放在 `[project.optional-dependencies]` 下作为可选依赖

## 代码规范

- Python 3.9+ 语法（`from __future__ import annotations` 已在各模块启用）
- 类型标注：公共 API 必须有类型标注（`mypy.ini` 中 `disallow_untyped_defs = True` 的模块）
- 不加注释除非逻辑非显而易见（代码应自解释）
- 每个新功能必须有对应测试

## 测试规范

- 测试文件放 `tests/test_*.py`
- 用 `unittest`（不引入 pytest 作为运行时依赖）
- 测试不依赖网络 / 外部服务
- SQLite 后端测试用 `tempfile.mkdtemp` + `AGENT_OS_MEMORY_BACKEND=sqlite`

## 提交流程

1. Fork 仓库
2. 创建分支：`git checkout -b feat/your-feature`
3. 写代码 + 测试
4. 确保全量测试通过
5. 提交 PR，描述清楚改了什么、为什么

## 安全相关贡献

安全修复优先处理。请勿在 PR 中引入：

- 硬编码密钥 / token
- 不带 timeout 的网络请求
- 未转义的用户输入拼入 HTML
- `eval()` / `exec()` 用于处理不可信输入

如发现安全漏洞，请**不要**公开提 issue，直接邮件联系维护者。

## 项目结构

```
agent_os/           # 源码（零依赖）
├── models.py       # 数据结构
├── persistence.py  # 持久层（JSONL / SQLite）
├── memory.py       # 记忆内核
├── retrieval.py    # BM25 / 语义 / 混合
├── tools.py        # 工具注册 / 审批 / 仲裁
├── sandbox.py      # 进程级沙箱
├── workflow.py     # DAG 工作流
├── runtime.py      # ReAct 循环
├── ...
tests/              # 测试
examples/           # 示例代码
docs/               # 设计规范
deliverables/       # 审计报告
```
