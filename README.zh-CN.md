# Project Pulse

> 安装一次，跨所有项目使用。

[English README](README.md)

Project Pulse 是一个开源、基于证据的项目状态 Skill，服务于 Coding Agent 和开发者。它回答：**这个项目现在进行到哪里了？** 它严格区分实现、验证、就绪度、证据、推断和未知。

## 核心能力

- 一次安装，可用于任意 Git、非 Git、monorepo、worktree 或原型项目。
- 初始化前即可只读检查。
- 使用 `.project-pulse/status.json` 保存可移植状态，生成 `STATUS.md` 作为交接面板。
- 跨电脑、分支和 Agent 检测过期快照。
- 确定性计算 `implemented`、`verified`、`active`、`blocked` 和 `unknown`。
- 展示手工测试、集成测试、审查和发布就绪度。
- 无网络、无遥测、不执行项目代码、不安装依赖、不写 Git、不读取已知秘密文件。

## 一次安装

```sh
git clone https://github.com/BreezeLife/Project-ProjectPulse.git
cd Project-ProjectPulse
python3 -m pip install --user .
```

Codex Skill 安装在全局目录 `~/.codex/skills/project-pulse`。只安装一次，目标项目不需要复制 Skill：

```sh
mkdir -p "$HOME/.codex/skills/project-pulse/references"
cp skills/project-pulse/SKILL.md "$HOME/.codex/skills/project-pulse/"
cp skills/project-pulse/references/*.md "$HOME/.codex/skills/project-pulse/references/"
```

## 在任意项目中使用

```sh
cd /path/to/any-project
project-pulse inspect       # 默认只读检查
project-pulse init          # 明确初始化，可选
project-pulse update        # 明确刷新
project-pulse inspect --json
```

在 Codex 中使用以下短指令可以更稳定地触发：

```text
project pulse
project pulse init
project pulse update
```

需要显式调用 Skill 时使用 `$project-pulse`。成功的 Project Pulse 输出会以 `PROJECT PULSE` 开头，并包含 `VCS`、`Workspace`、`Status`、`WORK`、`CHECKS`、`READINESS` 和 `NEXT`。推荐使用这些固定指令，不要使用可能被项目专用 Skill 接管的模糊指令，例如 `refresh status`。

如果命令不在 PATH 中，可以使用 `python3 -m project_pulse inspect`。macOS Python 3.9 常见用户级命令目录是 `$HOME/Library/Python/3.9/bin`。

## 核心操作

| 操作 | 含义 | 是否写入 |
| --- | --- | --- |
| `inspect` | 发现并报告当前状态 | 否 |
| `init` | 创建项目配置、canonical state 和面板 | 是，需明确请求 |
| `update` | 更新已初始化的状态和面板 | 是，需明确请求 |
| `verify` | 未来的授权验证命令 | v0.1 未实现 |

项目本地文件是可选的：

```text
project-pulse.json
.project-pulse/status.json   # canonical machine state
STATUS.md                    # 生成的人类可读面板
```

工作区变化后，保存的快照会显示为 `STALE`。状态文件属于项目；Skill 和核心代码保持全局安装。

## 适用场景

适合新会话、切换电脑或 Agent、人和 Agent 交接、多 Agent 分支、Git worktree、陌生仓库、没有任务文件的原型，以及“现在能测试什么”“是否可以审查”“是否可以发布”等问题。详见 [用户场景](docs/scenarios.md)。

## 安全边界

Inspect 把仓库内容视为不可信数据。它不会执行代码或仓库指令，不运行构建和测试，不安装依赖，不访问网络，不读取已知秘密文件，不跟随 symlink 逃出项目，也不执行 Git 写操作。Init 和 Update 只有在明确请求后才写入固定项目路径。详见 [SECURITY.md](SECURITY.md) 和 [THREAT_MODEL.md](THREAT_MODEL.md)。

## 文档

- [English README](README.md)
- [Skill 入口](skills/project-pulse/SKILL.md)
- [协议](skills/project-pulse/references/protocol.md)
- [证据模型](skills/project-pulse/references/evidence.md)
- [安全契约](SECURITY.md)
- [用户场景](docs/scenarios.md)
- [贡献指南](CONTRIBUTING.md)
- [变更记录](CHANGELOG.md)

## 开发与测试

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q project_pulse
python3 -m project_pulse inspect
```

## 路线图

v0.1 提供通用 Skill、安全发现、Inspect、Init、Update、指纹、可移植状态、渲染器、CLI、安全测试和场景文档。后续版本可以增加更强的平台安全防护、Agent 适配器和显式 Verify 模式。Hooks 按设计不属于 v0.1。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
