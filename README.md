# my-mini-swe-agent

一个从零手写的 AI 软件工程 Agent（SWE Agent），用来学习「让大模型自己写命令、改代码、解决编程问题」背后的工作原理。

灵感来自 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)，但代码是我自己一点点搭起来的，目标是**用最少、最可读的代码跑通一个完整闭环**。

> ⚠️ 这是一个学习项目，不是生产工具。代码刻意保持简单，不少能力（轨迹保存、错误兜底、步数限制接入等）仍在逐步补全中。

## 它能做什么

给定一个任务描述（比如"打印当前系统时间"），Agent 会进入这样一个循环：

```
任务描述
   │
   ▼
┌─────────────────────────────────────┐
│  model  让大模型生成一个 bash 命令      │  ◄──────┐
│          (tool call)                 │         │
└─────────────────────────────────────┘         │
   │                                            │
   ▼                                            │
┌─────────────────────────────────────┐         │
│  parse  校验并解析 tool call          │         │
└─────────────────────────────────────┘         │
   │                                            │
   ▼                                            │
┌─────────────────────────────────────┐         │
│  env    在 Docker 容器里执行命令      │         │
└─────────────────────────────────────┘         │
   │                                            │
   ▼                                            │
   把命令输出反馈给大模型 ────────────────────────┘
   （若输出首行是 COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT 则提交并结束）
```

一句话：**大模型负责"想"，Docker 负责"做"，命令输出负责"喂回去"**。

## 项目结构

```
my-mini-swe-agent/
├── agents/            # Agent 控制流（主循环）
│   └── default.py
├── environment/       # 执行环境（Docker 容器）
│   ├── docker.py
│   └── test/
├── model/             # 大模型接口（litellm 封装）
│   └── litellm_base_model.py
├── run/               # 入口脚本
│   └── hello_world.py
├── utils/             # 工具函数（tool call 解析、异常定义）
│   ├── action_toolcall.py
│   └── exceptions.py
└── tests/             # 单元测试
```

### 各模块职责

| 模块 | 职责 | 关键类/函数 |
|------|------|------------|
| `agents` | 主循环：query → 执行 → 观察，直到退出 | `DefaultAgent.run()` |
| `environment` | 在 Docker 容器里执行 bash 命令 | `DockerEnv.execute()` |
| `model` | 调用大模型、解析 tool call、算成本 | `LitellmModel.query()` |
| `utils` | tool call 的解析与校验、异常类型 | `parse_actions()` |
| `run` | 组装 Agent 并启动的入口 | `hello_world.py` |

## 技术栈

- **Python 3.10+**（类型注解 + `pydantic` 管理配置）
- **DeepSeek** 作为大模型，通过 **litellm** 统一调用
- **Docker** 作为隔离执行环境
- **typer** 做命令行入口、**jinja2** 做模板、**python-dotenv** 读环境变量

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/DuckDuckDaphnia/my-mini-swe-agent.git
cd my-mini-swe-agent

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate
pip install litellm typer pydantic jinja2 python-dotenv

# 3. 配置 .env（放入你的 API key，该文件已被 gitignore）
echo "DEEPSEEK_API_KEY=sk-xxxx" > .env
echo "MODEL_NAME=deepseek/deepseek-chat" >> .env

# 4. 运行（需要本地 Docker 已启动；用 -m 方式运行，项目内导入以仓库根目录为锚）
python -m run.hello_world --task "打印当前系统时间"
```

## 学习记录：已实现 vs 待办

### ✅ 已跑通

- [x] litellm 调用 DeepSeek，通过 tool call 强制模型输出 bash 命令
- [x] tool call 的解析与格式校验（缺参数 / 未知工具 / 无 tool call 时抛出 `FormatError` 并反馈给模型）
- [x] Docker 容器执行 bash 命令，回传输出与退出码
- [x] `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` 提交机制
- [x] 成本 / 步数上限的检查逻辑（`LimitsExceeded`）

### 🚧 待完善

- [ ] 步数限制（`step_limit`）还没接到命令行入口，目前默认不限
- [ ] Docker 容器还没挂载宿主代码目录，暂时只能做"执行命令"类任务
- [ ] 轨迹（trajectory）保存与序列化
- [ ] 主循环的通用异常兜底（如命令执行超时）

## 免责声明

这是个人的学习项目，代码质量和健壮性都不以生产为标准。如果你也在学习 SWE Agent，欢迎参考、提 issue 或一起交流。
