# Worklog

## 2026-09-26

- Started the v0.1 implementation in an empty workspace.
- Implemented the universal Python core, portable Skill, schemas, security contract, scenario docs, and tests.
- Ran `python3 -m unittest discover -s tests -v`: 4 tests passed.
- Initialized local Git and committed v0.1.0. No remote is configured yet.
- Created and pushed the public GitHub repository `BreezeLife/Project-ProjectPulse`, tagged `v0.1.0`, and installed the Skill and CLI globally for this user.
- Added an optional Codex Stop Hook adapter that reports current status without writing project state.

## 2026-09-27

- Separated full Inspect reporting from the compact Stop Hook summary; both now distinguish snapshot, task state, verification evidence, readiness, and next action.
- Fixed next-action wording so completed but unverified tasks prompt verification instead of appearing as unfinished implementation.
- Ran the Python unittest suite: 8 tests passed. Updated the user-level Python installation and confirmed the installed `project-pulse-hook` emits the new compact summary.
- Completed functional validation of the current working tree: 8/8 Python unit tests passed, `python3 -m compileall -q project_pulse` passed, and 16 CLI checks passed in disposable Git and non-Git projects. The checks covered read-only Inspect, task evidence boundaries, secret and symlink exclusion, Init/Update, fresh/stale snapshots, JSON output, the Stop Hook, writer lock and unsafe output rejection, nested Git-root discovery, current verification evidence, mismatched evidence rejection, and stale evidence revocation. The installed `project-pulse` command also reported this repository's current stale snapshot.
- Finished the evidence-reporting Skill update: current verified build, test, or human evidence now appears as `PRESENT` in full and compact reports; stale evidence remains `UNKNOWN`. Added two regression tests (10 total), validated the Skill format, rebuilt and installed the Python package with build isolation, synchronized the global Skill copy, and passed installed CLI/Hook smoke checks in a disposable project. This machine's old system setuptools produced an `UNKNOWN-0.0.0` package with `--no-build-isolation`; that accidental package was removed before the successful normal install.
- Added an at-a-glance dashboard: exact task counts with icon-labeled bars in CLI output, compact icon counts in the Stop Hook, and a Markdown `STATUS.md` with tables, task details, and escaped untrusted text. The 12-test suite passed, the Skill validator and Python compilation passed, and the installed CLI/Hook passed Inspect, Init, stale detection, Update, Markdown safety, and compact-summary smoke checks in a disposable project. Reinstalled the global Python package and synchronized the global Skill copy.
- Changed the optional Stop Hook to save only `.project-pulse/status.json` and `STATUS.md` before showing a verified compact status. Added safe first save, refresh, empty-directory skip, unowned-dashboard refusal, and lock-failure behavior. Repeated saves now deduplicate task evidence; generated status paths no longer make a tracked Git workspace appear dirty. All 18 Python tests, compilation, Skill validation, and `git diff --check` passed. Installed the global command and Skill, added a separate user-level Stop Hook group without replacing the existing one, and passed a direct installed-command save/refresh smoke test. Real Codex activation awaits the required `/hooks` trust review.
- Verified that Codex 0.157.1 detects exactly one new Hook and shows **Hooks need review** on startup. An accidental selection of “Trust all” during terminal inspection was immediately reverted by removing only the new Project Pulse trust entry; the pre-existing Stop Hook trust entry remains intact. Real automatic activation still awaits the user's review.
- Confirmed from the official Codex app changelog that desktop builds support in-app Hook trust review. Updated both READMEs to give desktop **Settings → Hooks** as the primary path and CLI `/hooks` as an alternative.
- The user reviewed and trusted the Project Pulse Stop Hook in Codex. A `hooks/list` request to Codex app-server confirmed `eventName: stop`, `enabled: true`, `trustStatus: trusted`, `source: user`, and a 30-second timeout. A separate CLI model turn timed out before reaching Stop, so real desktop turn execution remains to be observed; the installed hook's direct save/refresh smoke test and 18 unit tests had already passed.
- Verified the real desktop Stop boundary for the prior turn: final answer emitted at 22:11:54.978 UTC, `.project-pulse/status.json` updated at 22:11:55.383, `STATUS.md` updated at 22:11:55.963, and the turn completed at 22:11:56.964. A subsequent read-only Inspect returned `FRESH` with 12 tasks. The active trusted Hook therefore saved project progress during the turn end; direct Hook tests confirm its `SAVE: SAVED` message is composed only after the save and re-inspection.

## 2026-09-29

- Condensed the task chart and aligned Chinese/English columns; nonzero task states now appear first. Combined evidence and readiness into a paired view in CLI and Markdown, while keeping task details and exact counts.
- Added environment-based English/Simplified Chinese labels for manual reports, `STATUS.md`, and the Stop Hook. Task titles and canonical JSON status values remain unchanged. The 20-test suite passed, including Chinese layout and Hook checks.

## 2026-09-30

- Added a Focus section before full details in CLI and Markdown; Stop Hook summaries now show the two highest-ranked actionable tasks. Explicit `[P0]`–`[P3]` checkbox-title markers rank first, while unmarked tasks follow state and source order without inferred priority.
- Kept task identity stable when adding a priority marker, preserving historical evidence while requiring a fresh fingerprint for current verification. The Focus section stays at five entries, while detailed CLI and Markdown reports now show all collected tasks. Verified ordering, Markdown escaping, Chinese output, Hook saving, identity, and full detail rendering with 23 Python tests.
- Reinstalled the user-level command and synchronized the global Skill. An installed-command smoke test in a disposable project confirmed Chinese CLI/Markdown/Stop Hook output, explicit priority ordering, stable IDs after a marker change, and writes limited to the two status files.
- Reinstalled after lifting the full-detail cap; an installed-command check with 25 tasks confirmed the five-item Focus summary and all 25 task details remain visible.
- Prepared GitHub synchronization: added rendered Focus-table examples to both READMEs and clarified that each machine installs once from the repository root. Fetched the remote and confirmed its tree matches the local committed baseline despite divergent commit histories.
- Committed the dashboard, Stop Hook, localization, priority, test, and documentation changes; merged the divergent remote history while preserving the tested file tree, then pushed GitHub `master` through merge commit `74efcee`.
- Added matching English and Simplified Chinese SVG quick-start infographics to the READMEs. Each shows global installation, use in any project, dashboard signals, and the optional Stop Hook's limited write scope. The assets are generated from one dependency-free script and checked as rendered images.
- Connected `~/.claude/skills/project-pulse` to the installed global Skill and made Claude Code `/project-pulse` and its explicit `init`/`update` arguments part of the Skill contract. Validated the Skill, checked the installed CLI through read-only Inspect plus Init/Update in a disposable project, and confirmed the linked files match. A live Claude invocation remains unverified because the local Claude Code installation reports that it is not logged in.
