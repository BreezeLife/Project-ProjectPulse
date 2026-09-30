# Changelog

## 0.1.0

- Initial universal skill, read-only inspection, optional persistent status, and deterministic state model.

## Unreleased

- Add optional Codex Stop Hook adapter that saves two status files before showing a compact report.
- Show current verification evidence in detailed and compact reports; clarify that evidence presence is not a project-wide pass.
- Add icon-labeled task bars to CLI output and a Markdown `STATUS.md` dashboard with safe task-title escaping.
- Make repeated Stop saves idempotent for task evidence and exclude generated status files from Git workspace dirtiness, including tracked files.
- Align and condense CLI and Markdown dashboards; localize human-facing output to English or Simplified Chinese from the environment.
- Surface prioritized actionable task details in CLI, Markdown, and Stop Hook summaries; support explicit `[P0]`–`[P3]` task markers without guessing priority.
