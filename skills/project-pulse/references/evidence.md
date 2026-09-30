# Evidence

Evidence types are `filesystem`, `vcs`, `task`, `build`, `test`, `human`, and `agent_inference`. Task checkboxes and agent statements support implementation claims only. A `passed` verification requires current fingerprint-matched `build`, `test`, or `human` evidence. Missing evidence stays `UNKNOWN`; no confidence score or percentage is converted into proof.

The report shows `PRESENT` for a build, test, or human check when at least one verified task has that type of current evidence. `PRESENT` describes available evidence, not a project-wide pass. A stale snapshot resets these checks to `UNKNOWN`.
