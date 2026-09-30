# Project Pulse

**为 Coding Agent 提供基于证据的项目状态。** 看清哪些工作已经实现、哪些有当前验证证据，以及下一步该关注什么。

[English README](README.md)

Project Pulse 由可复用的 Agent Skill 和确定性的 Python 命令行工具组成。它读取当前项目，按状态整理任务，突出优先事项，并区分证据与就绪度，不猜测完成百分比。**无需初始化即可只读查看。**

## 快速开始

### 1. 每台机器安装一次

需要 Python 3.9+。以下命令使用 POSIX Shell（macOS、Linux 或 Git Bash）。先克隆仓库，再从仓库根目录安装：

```sh
git clone https://github.com/BreezeLife/Project-ProjectPulse.git
cd Project-ProjectPulse
python3 -m pip install --user .
project-pulse --help
```

命令行工具没有第三方运行时依赖。如果安装后找不到 `project-pulse`，请将 Python 用户脚本目录加入 `PATH`（在 macOS/Linux 上通常是 `python3 -m site --user-base` 输出目录下的 `bin`）。

### 2. 将 Skill 安装到 Agent 的全局目录

仍在本仓库根目录，复制 Skill 到 Codex 和 Claude Code 的用户级目录。若只使用其中一个 Agent，可从循环中删去另一个名称。

```sh
for agent in codex claude; do
  target="$HOME/.$agent/skills/project-pulse"
  mkdir -p "$target/references"
  cp skills/project-pulse/SKILL.md "$target/"
  cp skills/project-pulse/references/*.md "$target/references/"
done
```

这是**每台机器一次**的安装，目标项目不需要复制 Skill。以后更新时，拉取本仓库并重新执行安装和复制命令即可。

### 3. 打开任意项目并查看状态

```sh
cd /path/to/your-project
project-pulse inspect
```

| 使用环境 | 只读查看 | 首次保存快照 | 刷新已保存的快照 |
| --- | --- | --- | --- |
| Codex 桌面版或 CLI | `project pulse` 或 `$project-pulse` | `project pulse init` | `project pulse update` |
| Claude Code | `/project-pulse` | `/project-pulse init` | `/project-pulse update` |
| 终端或其他 Agent | `project-pulse inspect` | `project-pulse init` | `project-pulse update` |

`init` 是可选操作，会创建项目本地状态；先执行一次 `init`，之后才能 `update`。还可以用 `project-pulse inspect --project /path/to/project` 指定目录，或用 `project-pulse inspect --json` 获取机器可读结果。Claude Code 的 Skill 按其个人 Skill 目录规则安装；此版本尚未完成 Claude Code 交互会话的实机验收。

## 图解指南

![Project Pulse 中文指南：安装、在 Codex 中使用、解读仪表板和可选自动保存](docs/project-pulse-guide.zh-CN.svg)

[查看原尺寸信息图](docs/project-pulse-guide.zh-CN.svg)。图中演示 Codex 流程；上表列出了 Claude Code 与命令行的对应调用方式。

## 能得到什么

Project Pulse 读取 `TASKS.md`、`TODO.md` 和 `ROADMAP.md` 中的复选任务，以及有读取上限的文件和 Git 元数据。它结合已保存状态计算报告；只有执行保存操作才会重新生成 `STATUS.md`。

- **当前快照**：项目名称、分支、提交、工作区改动，以及已保存状态是 `FRESH` 还是 `STALE`。
- **任务仪表板**：准确数量、最多 20 格的条形图、完整任务明细，以及最多五项需关注的重点事项。
- **区分证据**：构建、测试和人工证据与“已实现”的任务声明分开呈现。
- **就绪信号**：人工测试根据任务状态保守推导；没有项目专属规则时，集成、审查和发布始终为 `UNKNOWN`。
- **可移植交接**：可选的 `.project-pulse/status.json` 保存规范状态；`STATUS.md` 是生成的人类可读面板。

### 示例：重点事项表

以下是生成的 `STATUS.md` 的示例数据：

| 优先级 | 状态 | 事项 |
| --- | --- | --- |
| P0 | ○ 待完成 | 修复结账流程 |
| P1 | ◐ 已实现·待验证 | 验证 API 集成 |
| — | ! 阻塞 | 获取测试凭据 |

在复选任务标题开头写 `[P0]` 至 `[P3]` 可明确排序，例如 `- [ ] [P0] 修复结账流程`，其中 P0 最高。未标注的任务按状态及原文件顺序排列；Project Pulse 不根据措辞猜测优先级。重点事项最多显示五项，完整任务明细仍保留。修改优先级标记不会改变任务身份，但工作区变化后仍需要匹配当前快照的验证证据。

### 保守解读状态

| 信号 | 含义 |
| --- | --- |
| `◐ 已实现·待验证` | 勾选任务表示有实现声明，不代表功能已经通过测试。 |
| `PRESENT` 证据 | 至少一项已验证任务有匹配当前快照的构建、测试或人工证据；不代表全项目通过。 |
| `UNKNOWN` | 缺少当前证据或项目自己的就绪规则，不推断为通过。 |
| `STALE` | 已保存状态不再匹配当前工作区；证据检查和就绪度回到 `UNKNOWN`。 |

人类可读标签默认跟随进程语言或 macOS 首选语言。可用 `PROJECT_PULSE_LANG=zh_CN` 或 `PROJECT_PULSE_LANG=en` 指定。任务标题和 JSON 状态码不会被翻译。

Project Pulse 不运行构建或测试，也不创建新的验证记录。只有规范状态里已有“已验证”任务且附有匹配当前快照的证据，才会显示 `PRESENT`；目前尚未实现 `verify` 操作。

## 可选：Codex 每回合自动保存

Codex Stop Hook 仅保存 `.project-pulse/status.json` 和 `STATUS.md`，重新检查保存的快照后显示最多两项重点事项的简短状态；它不运行项目测试。在用户级 `~/.codex/hooks.json` 中**追加 Stop 组**并保留其他 Hook。将 `command` 替换为 `command -v project-pulse-hook` 输出的绝对路径：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/absolute/path/to/project-pulse-hook",
            "timeout": 30,
            "statusMessage": "Saving Project Pulse progress"
          }
        ]
      }
    ]
  }
}
```

在 Codex 桌面版打开**设置 → Hooks**，核对该命令后选择信任；如果新 Hook 未显示，再重启应用。Codex CLI 可使用 `/hooks` 或启动时的审核界面。Hook 会跳过空目录；受保护写入失败时会给出不阻断回合的提示。本仓库尚未配置 Claude Code 的自动保存；上面的 Skill 和命令行仍可手动使用。

## 数据与安全边界

| 操作 | 对项目的写入 |
| --- | --- |
| `inspect` | 无 |
| `init` | `project-pulse.json`、`.project-pulse/status.json`、`STATUS.md` |
| `update` | 更新已初始化的状态和面板 |
| 已启用的 Codex Stop Hook | 仅 `.project-pulse/status.json` 和 `STATUS.md` |

目标仓库会被视为不可信数据。只读查看不会执行目标代码或其中的指令，不运行构建或测试，不安装依赖，不访问网络，不读取已知秘密文件，也不写入 Git。写入器只处理固定路径，并拒绝不安全的覆盖。详见[安全契约](SECURITY.md)与[威胁模型](THREAT_MODEL.md)。

Project Pulse 可用于 Git 仓库、worktree、monorepo 和普通目录。没有任务记录时，它会报告未知任务状态，不会编造进度。

## 常见问题

| 现象 | 检查方法 |
| --- | --- |
| 找不到 `project-pulse` 命令 | 将 Python 用户脚本目录加入 `PATH`，然后重新打开终端。 |
| Codex 或 Claude Code 没有显示 Skill | 确认该 Agent 的用户级 Skill 目录内有 `SKILL.md` 和 `references/`，再开启新会话。 |
| `update` 提示项目尚未初始化 | 先在该项目运行一次 `project-pulse init`。 |
| Codex Hook 提示需要审核 | 打开**设置 → Hooks**，核对命令并选择信任。 |
| 快照显示 `STALE` | 先检查工作区变化；确定要保存当前状态时再运行 `update`。 |

## 项目资料

- [Skill 指令](skills/project-pulse/SKILL.md) · [状态协议](skills/project-pulse/references/protocol.md) · [证据规则](skills/project-pulse/references/evidence.md)
- [使用场景](docs/scenarios.md) · [安全契约](SECURITY.md) · [威胁模型](THREAT_MODEL.md)
- [贡献指南](CONTRIBUTING.md) · [变更记录](CHANGELOG.md) · [许可证](LICENSE)

检查源码可运行 `python3 -m unittest discover -s tests -v`。
