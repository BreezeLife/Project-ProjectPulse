# Project Pulse

**Install Project Pulse once. Use it across all your projects.** Project Pulse observes project state. It does not manage your project.

It gives coding agents and humans a compact answer to: *Where is this project right now?* It separates implementation, verification, readiness, evidence, inference, and unknown. Code present is not proof that a feature works.

**No network. No telemetry. No automatic project execution.** Inspect never writes to the project. Init and Update require explicit commands or equivalent user requests. Hooks and Verify are outside v0.1.

## Install and use

Install the CLI once from this source checkout with `python3 -m pip install --user .` (or use an isolated Python environment). Install the universal `skills/project-pulse` skill once in your agent's global skill directory, or install this repository as a supported plugin. Project Pulse does **not** require every repository to contain a Skill. The installed skill invokes the installed `project-pulse` CLI, which always resolves the current project anew.

```sh
cd any-project
project-pulse inspect
project-pulse init       # optional, explicit project-local state
project-pulse update     # refresh initialized state
```

`python3 -m project_pulse inspect` works from this source checkout. `--project PATH` selects another directory and uses the same safety checks. Ask a coding agent "project pulse", "where are we?", or "what can I test now?" for a focused report.

Project-local `project-pulse.json` configures a name and optional scope. `.project-pulse/status.json` is canonical machine state. `STATUS.md` is generated from it. These files hold project-specific state, not Project Pulse implementation. Commit them when cross-machine or cross-agent continuity is useful. A changed workspace is reported as stale until an explicit update.

## Who is Project Pulse for?

Solo developers, technical founders, coding-agent power users, multi-agent developers, engineering teams, developers switching machines or agents, and maintainers reviewing unfamiliar repositories. It is useful before manual testing, code review, release decisions, and handoffs.

## What the report means

Checked task boxes are evidence of a *claim of implementation*, not verification. Test or build results require explicit evidence with a matching current snapshot. Without a project policy, review and release readiness remain `UNKNOWN`. Project Pulse never invents progress percentages or treats an absence of failures as a pass.

See [scenarios](docs/scenarios.md), [protocol](skills/project-pulse/references/protocol.md), and [security contract](SECURITY.md).

## Development

```sh
python3 -m unittest discover -s tests -v
```
