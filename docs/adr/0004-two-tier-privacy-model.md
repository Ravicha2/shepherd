# Two-tier privacy model

CLAUDE.md shape data is split into local-only and shareable tiers. Local-only: raw section headings, individual skill names, full skill references. Shareable: derived booleans (has_stack_section, has_patterns_section), counts (section_count, total_length_chars), and category tags (skill_category_tags grouped, not individual names). We chose this because section headings like "## Stripe Payment Integration" or "## HIPAA Compliance Rules" reveal proprietary capabilities, and combinations of individual skill names can uniquely identify small organizations.

**Considered options:**
- Share everything (simplest, maximum data for pattern comparison) — rejected because CLAUDE.md headings can contain business-sensitive information and the design promises privacy-first
- Share nothing (maximum privacy, no hub value) — rejected because it eliminates the community pattern comparison that makes Shepherd valuable

**Consequences:** The hub receives coarser-grained data than the local dashboard. Pattern comparisons on the hub will work on category tags and booleans, not on individual skill names. If hub users need finer granularity, they must explicitly opt in per session — the two-tier model makes this a conscious choice, not a default.