# Project Pulse

> Install once. Use across every project.

[中文文档](README.zh-CN.md)

Project Pulse is an open-source, evidence-based project status skill for coding agents and humans. It answers: **Where is this project right now?** It separates implementation, verification, readiness, evidence, inference, and unknown.

## Visual guide

![Project Pulse infographic: install once, open any project, ask Codex, read the dashboard, and optionally enable automatic saving](docs/project-pulse-guide.en.svg)

[Open the full-size infographic](docs/project-pulse-guide.en.svg). The commands and Stop Hook setup below provide the copyable steps.

## Highlights

- Universal installation for every Git, non-Git, monorepo, worktree, or prototype.
- Zero-configuration, read-only inspection before initialization.
- Portable `.project-pulse/status.json` state and generated `STATUS.md` handoff dashboard.
- Aligned, count-accurate task charts in the CLI and a compact Markdown dashboard in `STATUS.md`.
- A ranked Focus section surfaces up to five actionable task details before the full task list.
- Human-readable output follows the process or macOS preferred language (English and Simplified Chinese); JSON state remains language neutral.
- Stale snapshot detection across machines, branches, and agents.
- Deterministic `implemented`, `verified`, `active`, `blocked`, and `unknown` states.
- Readiness view for manual testing, integration, review, and release.
- No network, telemetry, project execution, dependency installation, Git writes, or known secret reads.

## Install once

Run these commands from the repository root on each machine. There is no per-project installation.

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

`project pulse` is the normal manual command. Use `$project-pulse` when you want explicit Skill invocation. The full report separates the workspace snapshot, task states, evidence checks, readiness, and next action. An optional Codex Stop Hook shows a shorter summary with task counts and at most two items needing attention. Prefer these commands over ambiguous phrases such as `refresh status`, which another project-specific Skill may claim.

### Optional Codex Stop Hook

Add a `Stop` group to the user-level `~/.codex/hooks.json` (merge it with existing hooks). Use the absolute path printed by `command -v project-pulse-hook` for `command`:

```json
{
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "/absolute/path/to/project-pulse-hook", "timeout": 30, "statusMessage": "Saving Project Pulse progress"}]}]
  }
}
```

Codex desktop supports hooks and has an in-app trust review. In the desktop app, open **Settings → Hooks**, review the exact Project Pulse command, and trust it. If the new hook does not appear, restart the app. In the CLI, use `/hooks` or its startup review screen. On every Stop in a recognized project, it saves only `.project-pulse/status.json` and `STATUS.md`, verifies the saved snapshot, then displays `SAVE: SAVED` and the compact status. It skips empty directories and reports a non-blocking `SAVE: FAILED` if guarded writing fails. It does not create `project-pulse.json`, run tests/builds, write task/worklog files, or commit to Git. Manual `project pulse` remains available.

If `command -v project-pulse-hook` returns nothing, add your Python user script directory to PATH before configuring the hook. On a typical macOS Python 3.9 install it is `$HOME/Library/Python/3.9/bin`.

## What it reports

```text
PROJECT PULSE · MyAgent
Snapshot: FRESH · DIRTY · GIT main @ abc123

TASKS (3)
! Blocked                1  █
◐ Needs verification     1  █
✓ Verified               1  █
▶ Active                 0  —
○ Remaining              0  —
↷ Deferred               0  —
? Unknown                0  —
Each █ = 1 task; chart stops at 20. Counts are exact.

FOCUS (2)
—   ! Blocked              Payments
—   ◐ Needs verification   Conversation streaming
[P0]–[P3] sort first (P0 highest); — means unmarked, sorted by state and source order.

TASK DETAILS (3)
! Blocked (1)
- Payments
◐ Needs verification (1)
- Conversation streaming
✓ Verified (1)
- Login

EVIDENCE                       READINESS
Build        UNKNOWN           Manual test  NOT READY
Tests        PRESENT           Integration  UNKNOWN
Manual test  UNKNOWN           Review       UNKNOWN
                               Release      UNKNOWN

NEXT ACTION  Resolve blocked work (1 task).
```

### Dashboard preview

The generated `STATUS.md` puts the chart above a short, ranked list of actionable details (example data):

| Priority | State | Item |
| --- | --- | --- |
| P0 | ○ Remaining | Fix checkout |
| P1 | ◐ Needs verification | Verify API integration |
| — | ! Blocked | Obtain test credentials |

The five highest-ranked actionable items appear here; the complete task list remains below it. `P0` is highest. `—` means no explicit priority was assigned.

The Stop Hook saves progress before showing a compact overview. `init`, `update`, and the enabled Stop Hook generate `STATUS.md` with active states above zero-count states and evidence beside readiness. Each bar stops at 20 tasks; counts remain exact. Set `PROJECT_PULSE_LANG=zh_CN` to request Chinese output explicitly, or `PROJECT_PULSE_LANG=en` for English. Otherwise the process locale, then the macOS preferred language, selects the display language. Task titles and JSON codes are unchanged.

Add `[P0]` through `[P3]` at the start of a checkbox task title to set an explicit priority (`P0` highest), for example `- [ ] [P0] Fix checkout`. The Focus section sorts these tags first, then unmarked actionable tasks by state and file order. It never infers importance from task wording. The full task list remains below the Focus section; the Stop Hook shows the top two items.

Adding or changing a priority marker keeps the task's identity and historical evidence; as with any task-file edit, current verification must match the new project fingerprint.

Task checkboxes and agent statements can support implementation claims, but do not prove that a feature works. Missing evidence stays `UNKNOWN`; no subjective completion percentage is generated.

An evidence check reads `PRESENT` when at least one verified task has matching current build, test, or human evidence. It does not assert that the whole project passed that check. A stale snapshot makes evidence checks and readiness `UNKNOWN` until current evidence is recorded.

## Core operations

| Operation | Meaning | Writes? |
| --- | --- | --- |
| `inspect` | Discover and report current state | No |
| `init` | Create project-local configuration, canonical state, and dashboard | Yes, explicit |
| `update` | Refresh initialized state and dashboard | Yes, explicit |
| Enabled Stop Hook | Save current status and dashboard before showing a compact report | Yes, two fixed files |
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

Inspect treats repository content as untrusted data. It does not execute code or instructions, run builds or tests, install dependencies, access the network, read known secret files, follow symlinks out of the project, or perform Git writes. Init and Update write only fixed project-local paths after explicit intent; the enabled Stop Hook writes only the two status files. See [SECURITY.md](SECURITY.md) and [THREAT_MODEL.md](THREAT_MODEL.md).

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
