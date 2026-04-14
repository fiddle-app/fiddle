# 2026-04-14-00-02 Context Cleanup

Audited and restructured the entire CLAUDE.md hierarchy across `Projects/` and `fiddle/` to eliminate redundancy, fix stale contradictions, and reduce auto-loaded context to within budget.

## Plan

See [ear-tuner/research/context-cleanup-plan.md](../ear-tuner/research/context-cleanup-plan.md) for the full plan with phase-by-phase details.

**Goals:**
1. Single source of truth — every piece of information documented in exactly one place; other files link to it
2. Minimal auto-loaded context — CLAUDE.md files stay lean (pointers + behavioral instructions); detailed reference docs are read on-demand via links
3. Correct information — fix stale contradictions between files
4. Cross-project conventions at the right level — dev process and folder conventions live at `Projects/` level, not buried in fiddle-specific files

---

## Execution Log

**2026-04-13 → 2026-04-14**

### What triggered this

Ran the new `/audit` skill against the ear-tuner working directory. The audit scored the CLAUDE.md hierarchy at **13/100 (CRITICAL)**, driven primarily by `fiddle/CLAUDE.md` being 181 lines (auto-loaded in every fiddle session) and `media-markup/CLAUDE.md` at 167 lines. Every fiddle working context exceeded the 250-line budget. The audit also found two data-flow contradictions and a broken file reference.

Casey had already been thinking about this — the `context-cleanup.md` notes document in the fiddle folder outlined goals and questions. The audit gave concrete numbers to prioritize against.

### Key decisions made during planning

1. **Dev process is cross-project, not fiddle-specific.** Casey pointed out that architecture.md shouldn't own "dev workflow" and "testing" because those are development process conventions that will apply to future non-fiddle projects too. This led to splitting into two new Projects-level files instead of stuffing everything into architecture.md.

2. **Two files, not one, for process docs.** `folder-conventions.md` (lightweight, frequently needed — what does `specs/` mean?) vs. `dev-process.md` (heavier, only needed when really building — spec-driven mode, handoff formats, testing strategy). The split reflects different access patterns.

3. **"About the Developer" removed from fiddle/CLAUDE.md.** Casey's global Claude profile already covers this. No need to burn context lines repeating it.

4. **No per-app architecture.md files.** App-specific design details belong in `{app}/specs/{app}-spec.md`. A per-app architecture.md would create a confusing three-way split.

5. **Plans go in `research/` as .md files.** Casey prefers reviewing plans in Obsidian/VSCode, not in the terminal. This was added to both `folder-conventions.md` and `Projects/CLAUDE.md`.

6. **Intonio is a real app.** It listens to fiddle playing, visualizes frequency spectrum, and identifies notes on a musical staff with sharp/flat color indication. Added to APPS.md registry.

### What was done

**Phase 1 — New Projects-level files:**
- Created `Projects/folder-conventions.md` (16 lines) — standard folder meanings
- Created `Projects/dev-process.md` (455 lines) — migrated from architecture.md Sections 9-10 plus JSDoc convention from Section 2. Generalized subagent prompts to be less fiddle-specific. Added Section 11 (Planning Process).
- Updated `Projects/CLAUDE.md` — added Key References section, Planning Process section, and fixed the `backlog.readme.md` ignore rule to handle naming variations

**Phase 4 — Trimmed architecture.md (815 → 408 lines):**
- Removed Sections 9 (Development Workflow) and 10 (Testing) entirely — content migrated to dev-process.md
- Replaced JSDoc Convention subsection with a 2-line pointer
- Added pointer to dev-process.md and folder-conventions.md at the top
- Renumbered remaining sections (old 11-14 → 10-13)
- Updated cross-reference in Section 7 (platform adapter) to point to media-markup spec instead of CLAUDE.md

**Phase 2 — Slimmed fiddle/CLAUDE.md (181 → 45 lines):**
- Removed: About the Developer, Folder Structure diagram, entire Shared Data Architecture section (stale — still documented old media-annotations/ approach and wrong Tune List data source), Coding Conventions, WPA→Swift Portability (39 lines duplicating architecture.md), verbose Backlog System section
- Kept: Project Overview (trimmed), Key References (new), Shared Design System (behavioral rule only), Per-Tune Markdown Format pointer, Backlog (2 lines), Licensing & Attribution

**Phase 3 — Slimmed media-markup/CLAUDE.md (167 → 35 lines):**
- Created `media-markup/specs/media-markup-spec.md` (157 lines) with all the detailed content: workflow, keyboard shortcuts, platform adapter interface, data architecture with SQL examples
- CLAUDE.md now has purpose, status, platform, data architecture summary, and links to spec

**Phase 5 — Created ear-tuner/CLAUDE.md (29 lines):**
- Purpose, status, target platform, key files, known issues (iOS silent switch, bell volume)

**Phase 6 — Fixed contradictions:**
- Data flow contradictions eliminated by removing the stale version from fiddle/CLAUDE.md (APPS.md already had the correct version)
- Broken `backlog-readme.md` reference eliminated by trimming the backlog section
- Intonio added to APPS.md registry and folder structure diagram
- Updated APPS.md header to point to dev-process.md for development process (no longer in architecture.md)

**Phase 7 — Trimmed stubs:**
- `_shared/CLAUDE.md` and `microbreaker/CLAUDE.md` reduced from 15 lines each to 3 lines

### Deviations from plan

- `fiddle/CLAUDE.md` came out at 45 lines instead of the planned ~80. The plan overestimated how much "keep" content there would be — turns out most of it was redundant with APPS.md and architecture.md once the SSOT principle was applied strictly.
- `dev-process.md` came out at 455 lines instead of the planned ~280. The architecture.md dev workflow content was larger than estimated, and a new Section 11 (Planning Process) was added per Casey's feedback.
- The plan was written in `ear-tuner/research/` because the session started in ear-tuner. Casey noted mid-session that the work should have been done from the fiddle directory. The shell wouldn't change cwd (anchored to launch directory), so all work used absolute paths.

### Final metrics

| File | Before | After |
|---|---|---|
| `Projects/CLAUDE.md` | 76 | 90 |
| `Projects/folder-conventions.md` | — | 16 (new) |
| `Projects/dev-process.md` | — | 455 (new) |
| `fiddle/CLAUDE.md` | 181 | 45 |
| `fiddle/architecture.md` | 815 | 408 |
| `fiddle/APPS.md` | 100 | 101 |
| `media-markup/CLAUDE.md` | 167 | 35 |
| `media-markup/specs/media-markup-spec.md` | — | 157 (new) |
| `ear-tuner/CLAUDE.md` | — | 29 (new) |
| `_shared/CLAUDE.md` | 15 | 3 |
| `microbreaker/CLAUDE.md` | 15 | 3 |

**Context load (auto-loaded lines when working in a directory):**

| Working in... | Before | After |
|---|---|---|
| ear-tuner/ | 257 | 164 |
| media-markup/ | 424 | 170 |
| tune-list/ | 193 | 193 |
| minions/larry/ | 349 | 227 |

All contexts now well under the 250-line budget.

### Open items

- The `/audit` skill itself was also debugged this session — it wasn't recognized because the skill file was `audit-SKILL.md` (flat) instead of `audit/SKILL.md` (subdirectory pattern matching the existing `log` skill). Fixed by moving it.
- `dev-process.md` subagent prompts still reference fiddle-specific conventions. Acceptable for now but will need parameterization when non-fiddle projects start.
- The plan file question in `context-cleanup-plan.md` about fiddle-specific content in dev-process.md remains unanswered by Casey.
