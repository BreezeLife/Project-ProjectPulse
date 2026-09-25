# Project Pulse

> Install once. Use across every project.

[中文文档](README.zh-CN.md)

Project Pulse is an open-source, evidence-based project status skill for coding agents and humans. It answers: **Where is this project right now?** It separates implementation, verification, readiness, evidence, inference, and unknown.

## Highlights

- Universal installation for every Git, non-Git, monorepo, worktree, or prototype.
- Zero-configuration, read-only inspection before initialization.
- Portable `.project-pulse/status.json` state and generated `STATUS.md` handoff dashboard.
- Stale snapshot detection across machines, branches, and agents.
- Deterministic `implemented`, `verified`, `active`, `blocked`, and `unknown` states.
- Readiness view for manual testing, integration, review, and release.
- No network, telemetry, project execution, dependency installation, Git writes, or known secret reads.

## Install once

```sh
git clone https://github.com/BreezeLife/Project-ProjectPulse.git
cd Project-ProjectPulse
python3 -m pip install --user .
```

The Codex Skill is the global directory `~/.codex/skills/project-pulse`. Install it once there; target projects do not need a Skill copy:

```sh
mkdir -p "$HOME/.codex/skills/project-pulse/references"
cp skills/project-pulse/SKILL.md "$HOME/.codex/skills/project-pulse/"
cp skills/project-pulse/references/*.md "$HOME/.codex/skills/project-pulse/references/"
```

## Use from any project

```sh
cd /path/to/any-project
project-pulse inspect       # read-only default
project-pulse init          # explicit, optional persistence
project-pulse update        # explicit refresh
project-pulse inspect --json
```

In Codex, use one primary manual entrypoint:

```text
project pulse
project pulse init
project pulse update
```

`project pulse` is the normal manual command. Use `$project-pulse` when you want explicit Skill invocation. A successful response starts with `PROJECT PULSE` and includes `VCS`, `Workspace`, `Status`, `WORK`, `CHECKS`, `READINESS`, and `NEXT`. An optional Codex Stop Hook can also perform a read-only inspection automatically. Prefer these commands over ambiguous phrases such as `refresh status`, which another project-specific Skill may claim.

### Optional Codex Stop Hook

Add this user-level hook to `~/.codex/config.toml` to inspect the current project when Codex stops a turn:

```toml
[[hooks.Stop]]
[[hooks.Stop.hooks]]
type = "command"
command = "project-pulse-hook"
timeout = 10
statusMessage = "Checking Project Pulse"
```

The hook reads Codex's Stop event from stdin and returns a compact Project Pulse message. It never runs tests/builds, writes project state, or blocks the turn. Manual `project pulse` remains available. Restart Codex after changing the configuration.

If the command is not on PATH, use `python3 -m project_pulse inspect` or add `$HOME/Library/Python/3.9/bin` to PATH on a typical macOS Python 3.9 install.

## What it reports

```text
PROJECT PULSE
Project: MyAgent
VCS: GIT
Workspace: DIRTY
Status: FRESH

VERIFIED
- Login

IMPLEMENTED / UNVERIFIED
- Conversation streaming

BLOCKED
- Payments

READINESS
Manual test: READY
Integration: UNKNOWN
Review: UNKNOWN
Release: UNKNOWN

NEXT
1. Verify conversation streaming
2. Configure payment test credentials
```

Task checkboxes and agent statements can support implementation claims, but do not prove that a feature works. Missing evidence stays `UNKNOWN`; no subjective completion percentage is generated.

## Core operations

| Operation | Meaning | Writes? |
| --- | --- | --- |
| `inspect` | Discover and report current state | No |
| `init` | Create project-local configuration, canonical state, and dashboard | Yes, explicit |
| `update` | Refresh initialized state and dashboard | Yes, explicit |
| `verify` | Future approved verification commands | Not in v0.1 |

Project-local files are optional:

```text
project-pulse.json
.project-pulse/status.json   # canonical machine state
STATUS.md                    # generated human dashboard
```

The stored snapshot becomes `STALE` when the workspace changes. Status files belong to the project; the Skill and core remain globally installed.

## Scenarios

Use Project Pulse for new sessions, machine or agent switching, human or agent handoff, multi-agent branches, Git worktrees, unfamiliar repositories, prototypes without task files, “what can I test now?”, review readiness, release readiness, and long-running projects. See [docs/scenarios.md](docs/scenarios.md).

## Safety

Inspect treats repository content as untrusted data. It does not execute code or instructions, run builds or tests, install dependencies, access the network, read known secret files, follow symlinks out of the project, or perform Git writes. Init and Update write only fixed project-local paths after explicit intent. See [SECURITY.md](SECURITY.md) and [THREAT_MODEL.md](THREAT_MODEL.md).

## Documentation

- [中文 README](README.zh-CN.md)
- [Skill entrypoint](skills/project-pulse/SKILL.md)
- [Protocol](skills/project-pulse/references/protocol.md)
- [Evidence model](skills/project-pulse/references/evidence.md)
- [Security contract](SECURITY.md)
- [Scenarios](docs/scenarios.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Development

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q project_pulse
python3 -m project_pulse inspect
```

## Roadmap

v0.1 provides the universal Skill, safe discovery, Inspect, Init, Update, fingerprints, portable state, renderer, CLI, security tests, and scenarios. The optional Codex Stop Hook is an adapter; future releases may add stronger platform hardening, other agent adapters, and an explicit Verify mode.

## License

MIT. See [LICENSE](LICENSE).
