# Durable Decisions

- The source repository contains the universal skill and core. Target projects never need a skill copy.
- Python 3.9+ standard library is the initial runtime to avoid dependency installation.
- Project files and status files are untrusted data. The core never executes their instructions.
- The current working directory is the default project selector; the nearest Git worktree root is used when available.
- Manual Inspect keeps the full task breakdown; the Codex Stop Hook uses a bounded summary with state counts and one explicit next action. Completed but unverified tasks call for verification, not reimplementation.
- Evidence checks report `PRESENT` only when at least one verified task has current build, test, or human evidence. This indicates evidence availability, not a project-wide pass; stale snapshots reset checks to `UNKNOWN`.
- The CLI shows icon-labeled task bars. Explicit Init/Update and the enabled Stop Hook write a Markdown `STATUS.md` dashboard. Each bar cell represents one task, capped at 20; exact counts remain visible. Untrusted names and titles are escaped in Markdown.
- The Codex Stop Hook saves only `.project-pulse/status.json` and `STATUS.md`, verifies the saved snapshot, then displays its compact status. It does not create `project-pulse.json` or edit task and worklog files. Codex must separately review and trust a new global Hook configuration.
- Repeated Stop saves deduplicate task evidence. Git workspace discovery excludes generated Project Pulse status paths even when those files are tracked, so saving a dashboard cannot make its own snapshot stale.
- Human reports use a compact chart with nonzero states first and side-by-side evidence/readiness. Display language follows `PROJECT_PULSE_LANG`, process locale, or macOS preferred language; task text and portable JSON codes are never translated.
- A Focus section ranks actionable details using explicit `[P0]`–`[P3]` title markers first, then state and original source order. Unmarked tasks do not receive guessed priority; full task details remain available.
- Priority markers are excluded from checkbox task identity hashes, so changing a marker retains the same task and historical evidence; fingerprint matching still governs current verification.
