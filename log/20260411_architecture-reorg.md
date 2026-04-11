# Architecture Documentation Reorg — 2026-04-11

## Summary

Consolidated all fiddle-app research documents into a single canonical `architecture.md` at the fiddle root. Reorganized the research folder, slimmed APPS.md, created research stubs for open questions, and added backlog items for all planned work.

## What Was Done

### New Files Created
- **`fiddle/architecture.md`** — Canonical architecture & implementation strategy (13 sections: platform decisions, tech stack, performance techniques, data architecture, design system, data robustness, platform adapter, Electron security, development workflow, testing, development order, Electron shared setup, packaging)
- **`research/bundling-strategy.md`** — Explainer: no-bundler vs esbuild vs Vite
- **`research/icloud-sqlite-sync-safety.md`** — Research stub for iCloud + SQLite sync risks
- **`research/electron-boilerplate-template.md`** — Research stub for shared Electron template
- **`research/spec-naming-convention.md`** — Proposed architecture-area prefixes for spec filenames
- **`research/electron-packaging.md`** — Explainer: packaging vs bundling, electron-builder vs forge

### Files Reorganized
- 7 old research files → `research/skulch/` (superseded by architecture.md)
- MM's `cross-platform-options.md` → `media-markup/research/skulch/`
- `instructions for a planning session.md` → this log entry

### Files Updated
- **APPS.md** — Heavy trim to pure registry + data flow map (detailed content moved to app folders)
- **CLAUDE.md (fiddle)** — Added links to architecture.md and APPS.md
- **CLAUDE.md (Projects)** — Added Obsidian callout conventions and Q/A pattern guidance
- **media-markup/research/Design and implementation Notes.md** — Added performance tips section for timeline
- **fiddle/backlog.md** — Added items P4–P10 (research/planning), C3–C16 (development order Groups 1–3)

### Key Decisions Captured in architecture.md
- Vanilla JS, no framework (Svelte/React/Tailwind rejected)
- Vitest + Playwright as test tools, `data-testid` convention adopted
- Three-mode development workflow: vibe coding (default), spec-driven (opt-in), adversarial test pass (escalation)
- Retro-spec rhythm: vibe code → `/retro-spec` → `/commit`
- Schema versioning with `min_read_compatible` for cross-app db consumers
- Three-group development order (P1 foundations, P2 core apps, P3 mobile)
- MM desktop first, iPad later (platform adapter designed from day one)

### Research Topics with Gemini
Earlier in this session, reviewed two documents from a Gemini conversation (`electron-research.md` and `testing-strategy.md`). Evaluated them against established plans, added critique sections, then extracted the useful ideas (Canvas rendering, rAF, Pointer Events, passive listeners, data-testid, Vitest/Playwright, spec-driven workflow) and discarded the rest (Svelte, Tailwind, always-on multi-agent process).

The testing strategy discussion evolved into the spec-driven mode compromise and retro-spec rhythm through iterative conversation.

## Open Items (Backlog)
All captured in `fiddle/backlog.md` with links to research stubs where applicable. Key open questions:
- Bundling strategy (P4)
- iCloud + SQLite sync safety (P5)
- Electron boilerplate template (P6)
- Spec file naming convention (P7)
- `/retro-spec` skill (P8)
- Electron packaging (P9)
- Per-Tune Markdown format move to spec/ (P10)
