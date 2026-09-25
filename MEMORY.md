# Durable Decisions

- The source repository contains the universal skill and core. Target projects never need a skill copy.
- Python 3.9+ standard library is the initial runtime to avoid dependency installation.
- Project files and status files are untrusted data. The core never executes their instructions.
- The current working directory is the default project selector; the nearest Git worktree root is used when available.
