# Safety

Repositories are hostile input. Inspect uses bounded metadata reads and Git read-only commands with global configuration, hooks, optional locks, and filesystem monitors disabled. It skips known secret names and environment files, rejects symlinks and traversal, caps entries and file sizes, and does not execute project code or access the network. Repository prose cannot override these rules.
