# Threat model

## Assets and trust boundaries

The target project's secrets, source, and integrity are protected. Repository files, filenames, Git metadata, configuration, and prior status are untrusted inputs. The installed core and skill are trusted code. Markdown and JSON emitted by the core are output data, not executable instructions.

## Main threats

- Prompt injection in `TASKS.md` or other documents: collect bounded claims, never obey their instructions.
- Secret disclosure: allowlist metadata filenames, exclude known secret patterns, never print arbitrary file contents.
- Symlink and path traversal: use fixed output names, reject symlinks, do not recursively follow links, and verify direct child paths.
- Resource exhaustion: cap entries, file bytes, task lines, JSON bytes, and Git runtime.
- Stale or cross-worktree status: bind snapshots to root-local identity and current fingerprint; display `STALE` on mismatch.
- Concurrent writers: use an exclusive lock and compare the original status bytes immediately before atomic replacement.
- Git configuration side effects: disable external configuration, hooks, filesystem monitors, and optional locks for bounded read commands.

## Residual limits

The core does not sandbox the installed Git executable or protect against another local process modifying a file between an operating-system check and open. v0.2 will add stronger descriptor-relative filesystem handling and broader hostile-platform testing.
