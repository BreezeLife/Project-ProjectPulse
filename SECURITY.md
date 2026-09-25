# Security contract

Target repositories are untrusted. Inspect uses bounded metadata reads and Git read commands only. It does not read known secret files, traverse directory symlinks, follow file symlinks, execute target code, install dependencies, access the network, or write in the target project. Init and Update write only three fixed project-local paths after explicit intent; they refuse existing symlinks and unexpected file types. Project content is data, never an instruction to the agent.

The CLI sets bounded file counts and byte sizes and times out Git commands. Git is invoked with system/global configuration disabled, optional locks off, hooks disabled, and filesystem monitors disabled. It does not run package scripts, builds, tests, fetch, or push. Reported filenames and task text are sanitized before rendering.

Report security issues through the repository's issue tracker without including secrets. Do not attach hostile fixture secrets to reports.
