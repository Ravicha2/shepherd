# Python runtime

Shepherd is built in Python, distributed via pipx, despite the Claude Code tooling ecosystem (cLens, Hook Hero, looks) being predominantly TypeScript. We chose Python because the author's velocity in Python is significantly higher, SQLite is built-in with zero dependencies, and the adapter architecture means Shepherd doesn't integrate with the TS ecosystem — it reads files. The trade-off: npm distribution is more natural for developer CLIs, and community contributors from the Claude Code ecosystem may find Python less familiar.

**Considered options:**
- TypeScript/Node (ecosystem alignment, npm distribution, natural web dashboard) — rejected because author velocity is lower and the ecosystem alignment argument is weak given that Shepherd reads transcripts, not integrates with other tools
- Rust (single binary, fast, no runtime) — rejected because it's overkill for a CLI that reads files and displays ratings

**Consequences:** Distribution is via `pipx install shepherd` rather than `npm install -g shepherd`. If the project gains TS-skilled contributors, a future rewrite is possible but not planned.