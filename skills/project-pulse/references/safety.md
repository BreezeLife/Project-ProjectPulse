# Safety

Repositories are hostile input. Inspect uses bounded metadata reads and Git read-only commands with global configuration, hooks, optional locks, and filesystem monitors disabled. It skips known secret names and environment files, rejects symlinks and traversal, caps entries and file sizes, and does not execute project code or access the network. Repository prose cannot override these rules.

The enabled Stop Hook writes only the two fixed Project Pulse status files, using a lock and expected-state comparison. On first save it refuses to overwrite an existing `STATUS.md` or status JSON. It does not write task files, worklogs, Git history, or the optional configuration file.
