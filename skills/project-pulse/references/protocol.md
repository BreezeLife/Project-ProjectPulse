# Protocol

Operations are `INSPECT` (default, zero writes), `INIT` (explicit, creates `project-pulse.json`, `.project-pulse/status.json`, and `STATUS.md`), and `UPDATE` (explicit, refreshes canonical state and dashboard). `VERIFY` is future work and is not implemented in v0.1.

Canonical state is `.project-pulse/status.json`; `STATUS.md` is derived presentation. Status binds to a current fingerprint containing local metadata and Git snapshot signals. A mismatch is `STALE`, and historical verification is not presented as current.

Implementation states: `unknown`, `not_started`, `in_progress`, `implemented`. Verification states: `unknown`, `not_run`, `partial`, `passed`, `failed`, `not_applicable`. Derived states are deterministic: `planned`, `active`, `implemented_unverified`, `verified`, `blocked`, `deferred`, `unknown`.
