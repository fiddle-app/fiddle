# Research Review — 2026-04-11

Reviewed by Claude (Opus 4.6) at Casey's request. This review evaluates the two Gemini-sourced documents (`electron-research.md` and `testing-strategy.md`) against the established project plans, and identifies broader questions and decisions that need attention.

---

## 1. Conflicts and Contradictions

### 1a. Framework Choice: Gemini vs. Established Plan

**The conflict:** Both Gemini documents assume Svelte 5 as the framework. The electron-research file recommends it explicitly; the testing-strategy file builds its entire workflow around Svelte stores, Svelte Testing Library, and Svelte compilation.

**The established position:** Vanilla JavaScript with ES module classes. `rethinking-dev-plans.md` explicitly evaluated frameworks (including React) and rejected them. CLAUDE.md codifies vanilla JS as a convention and designs the module structure for Swift portability.

**My assessment:** The established position is correct for this project. The arguments for Svelte (compiled reactivity, no virtual DOM) are real but solve problems this project doesn't have at scale. The family currently has two working WPA apps in vanilla JS. Adding a framework to new apps fragments the codebase, adds build tooling, and creates a skills gap between "framework apps" and "vanilla apps." The portability argument in CLAUDE.md (ES module classes map to Swift structs/classes) is also a strong reason to stay vanilla.

**Exception to watch:** If MM's annotation timeline genuinely requires complex component-level reactivity (deeply nested, frequently-updating UI state), a framework *might* earn its keep for that one app. But try vanilla JS + Canvas first. The timeline's visual complexity is better served by Canvas rendering than by component reactivity.

### 1b. Tailwind CSS vs. Shared Design System

**The conflict:** Gemini recommends Tailwind for cross-platform consistency. The project uses `_shared/design/` with CSS variables.

**My assessment:** CSS variables are the right choice. They're framework-free, work in Electron and Capacitor's WKWebView identically, require no build step, and can be ported to Swift Color extensions at translation time. Tailwind would require a build pipeline, add a dependency, and create a different styling paradigm from the existing apps.

### 1c. Testing Strategy vs. Development Reality

**The conflict:** The testing-strategy file proposes a formal multi-agent workflow (Architect/Coder/Tester) with spec documents, handoff manifests, and adversarial verification. The existing project uses Claude Code as a single assistant in conversational sessions with session logging.

**My assessment:** The multi-agent approach is designed for a team, or for an AI-assisted workflow with multiple concurrent agents and formal handoff points. Casey is a solo developer using Claude Code interactively. The overhead of maintaining `/specs`, `handoff.md`, and `vibe_log.md` artifacts would slow development without proportional quality gains. The "Vibe Code Mode" escape hatch in the document is itself evidence that the process is too heavy — if you need a formal exception for minor changes, the baseline is wrong.

### 1d. The `organized-notes.md` Strikethrough Items

The organized-notes file contains many struck-through items (ideas that were considered and rejected or deferred). Some of these conflict with current plans if read without noticing the strikethroughs:
- ~~Voice input via Web Speech API~~ — dropped
- ~~BPM detection and tap-along beats~~ — dropped
- ~~Intonio integration with MM~~ — dropped
- ~~Playlists in TuneList~~ — dropped (TuneList is not a media player)

These are fine as historical record, but anyone (human or AI) reading the file should be aware that struck-through items are **not** part of the plan.

---

## 2. Decisions You Need to Make

### 2a. Testing Tools: Vitest + Playwright?

Both Gemini documents recommend Vitest (unit) and Playwright (E2E). These are actually good recommendations that are independent of the Svelte assumption:

- **Vitest** works with vanilla JS and ES modules natively. It's fast, has a good watch mode, and doesn't need a framework.
- **Playwright** handles Electron's multi-process architecture and can also test Capacitor webviews.

**Decision needed:** Do you want to adopt Vitest + Playwright as the standard test tools across the family? If yes, this should go into CLAUDE.md's coding conventions. My recommendation: yes, adopt both, but defer writing tests until each app has stabilized past initial prototyping. (See the tiered strategy in my evaluation appended to `testing-strategy.md`.)

### 2b. When Does Testing Start?

The Gemini documents assume testing is part of the development process from day one. For personal-use apps in active design iteration, that's premature — you'd rewrite tests as fast as you write them.

**Decision needed:** At what point in each app's lifecycle do you want tests? My recommendation:
- **Immediately:** SQLite schema definitions and migration scripts (data integrity is non-negotiable)
- **Once the data model stabilizes:** Business logic (filtering, sorting, display rules, JSON parsing)
- **Once the UI settles:** E2E workflows via Playwright
- **Never:** CSS layout, visual styling (verify by looking at it)

### 2c. Electron Boilerplate: How Much Shared Setup?

Both Tune Hub and Media Markup are Electron apps. They'll share:
- `contextBridge` / `contextIsolation` security setup
- IPC patterns for file system access
- Platform adapter interface design
- CSP configuration
- Window management basics

**Decision needed:** Should there be a shared Electron template or boilerplate in `_shared/`, or should each app set up Electron independently? A shared template reduces duplication but adds coupling. My recommendation: start with one app (whichever you build first — probably MM based on the priority list in organized-notes), get the Electron setup right, then extract the reusable parts into `_shared/` before starting the second app.

### 2d. Build Tooling for Vanilla JS + Electron

Without a framework, you don't need Vite or Webpack for development. But Electron apps still need:
- A way to bundle the renderer process code for production
- Source maps for debugging
- Possibly minification (though for personal use, this is low priority)

**Decision needed:** What's the build story for Electron apps? Options:
1. **No bundler** — use ES modules directly in Electron's renderer (Chromium supports them natively). Simplest approach; works until you have performance or dependency reasons to bundle.
2. **esbuild** — extremely fast, zero-config for JS bundling. Add it when/if needed.
3. **Vite** — more features (HMR, plugin ecosystem) but heavier. Only justified if you adopt a framework.

My recommendation: start with option 1 (no bundler). Add esbuild if you hit a specific need.

### 2e. The `data-testid` Convention

The testing-strategy document recommends `data-testid` attributes on all interactive elements. This is a genuinely good practice even before you write any tests — it makes elements addressable by purpose rather than by CSS class or DOM position.

**Decision needed:** Adopt `data-testid` as a convention now, or defer until testing starts? My recommendation: adopt it now. It's zero cost to add during development and saves refactoring later.

### 2f. MM Desktop Priority vs. iPad

`rethinking-dev-plans.md` lists this as an open question: "Is the iPad use case for MM urgent, or can it wait?"

The organized-notes describe the iPad workflow (annotating Zoom recordings on iPad), and the rethinking document recommends Electron desktop first with the platform adapter designed for future Capacitor. But the priority list in organized-notes puts MM as #1.

**Decision needed (reaffirm or revise):** Is the plan still "Electron desktop first, iPad later"? The platform adapter design is the key enabler either way — the question is just sequencing.

---

## 3. Questions About Development Plans and Procedures

### 3a. How Will You Manage Electron App Packaging and Distribution?

Electron apps need to be packaged (electron-builder, electron-forge, etc.) for distribution. Even for personal use, you'll want:
- A way to build a runnable `.exe` (Windows)
- Auto-update capability (or manual update process)
- Code signing (optional for personal use, required for distribution)

This isn't addressed in any research document. It's not urgent, but it's a known future task.

### 3b. How Will You Handle SQLite Schema Migrations?

Tune Hub owns `tunehub.db`. Media Markup owns `media-markup.db`. As these apps evolve, schemas will change. Questions:
- Who runs migrations — the owning app on startup?
- What happens if TuneList (read-only consumer) encounters a schema version it doesn't understand?
- Is there a version table in each database?
- What's the migration format — raw SQL scripts? A migration tool?

My recommendation: each database should have a `schema_version` table with a single integer. The owning app checks version on startup and runs sequential migration scripts. Consuming apps check the version and warn if it's newer than they understand.

### 3c. How Will iCloud Sync Conflicts Be Handled in Practice?

The organized-notes mention the "discipline of closing app on one device before opening on another." The rethinking document accepts this as sufficient for a single user. But in practice:
- What if you forget to close MM on the desktop and open it on iPad?
- SQLite + iCloud sync is a known pain point (Apple's own documentation warns about it)
- WAL mode helps with concurrent reads, but concurrent writes from different devices could corrupt the database

**This deserves more research.** The companion-file pattern (sync timestamp/checksum) was struck through in organized-notes but the underlying concern is valid. At minimum, each app should detect whether the database file has been modified since it was last opened (check mtime or a checkpoint counter) and warn before writing.

### 3d. What's the App Development Order?

The organized-notes say: MM first, then TuneList, then TuneHub. But the current priority in APPS.md says: "Design Review & Shared Resource Extraction" first, all other development waits. And TuneHub is the SSOT — TuneList and MM both depend on data structures that TuneHub defines.

**Tension:** You can't fully build TuneList or MM without at least defining the tunehub.db schema. But you don't need a working TuneHub UI to define the schema.

**Possible resolution:** Define the tunehub.db schema (tables, columns, types, constraints) as part of the design review phase, before any app development starts. This gives MM and TuneList a stable contract to build against, even if TuneHub's UI comes later.

### 3e. What Happens to the Existing WPA Code for Microbreaker and Ear Tuner?

Both apps are "Built (WPA) — in design review." The plan says they'll get Capacitor wraps. But:
- Where does the current code live? Is it already in the `microbreaker/` and `ear-tuner/` folders, or does it need to be migrated from old Claude chat artifacts?
- APPS.md says: "Migrate Microbreaker and Ear Tuner into their project folders" — so migration hasn't happened yet.
- The design review is supposed to extract a shared design system from these apps.

**Decision needed:** Is migrating existing code into the repo folders part of the current design review phase? If so, that's the first concrete step.

---

## 4. Recommendations

1. **Don't adopt Svelte, Tailwind, or the always-on multi-agent workflow.** The Gemini documents were generated without project context and their core tech stack recommendations conflict with established, well-reasoned decisions. However, the *mechanisms* (specs, coder subagents, handoff manifests) have value when used selectively — see item 7.

2. **Do extract the good ideas:** `data-testid` convention, Vitest + Playwright as future test tools, Canvas rendering for MM's timeline, security hardening (CSP, contextIsolation) for Electron apps, Pointer Events for cross-platform input.

3. **Define the tunehub.db schema early** — even before building TuneHub's UI. This unblocks MM and TuneList development.

4. **Research iCloud + SQLite sync safety** more deeply before committing to the multi-device workflow. This is the riskiest technical assumption in the architecture.

5. **Start with no bundler** for Electron apps. Add build tooling only when a specific need arises.

6. **Get the existing WPA code into the repo** as the first concrete step of the design review. You can't review what isn't checked in.

7. **Adopt the "Spec-Driven Mode" compromise for development workflow.** (Added after discussion with Casey.) The Gemini document's mistake was making ceremony the default. The revised approach:

   - **Vibe coding is the default.** Most work happens interactively with Claude Code, no spec required, no process overhead.
   - **Spec-driven mode is an opt-in escalation** for features complex enough to benefit from a written plan. Casey asks Claude to capture the design as a spec; a coder subagent implements from the spec (validating its completeness); the coder produces a handoff manifest summarizing what was built.
   - **Adversarial testing is a further optional escalation** for high-risk work (schema migrations, platform adapter contracts). A separate tester subagent writes tests from the spec + manifest without having seen the implementation conversation.
   - **Specs double as documentation source material.** After an app stabilizes, its `specs/` folder seeds user documentation. This gives specs lasting value beyond the coding session — they capture what the app does, major states and transitions, data contracts, and platform-specific behavior.

   This is experimental. Casey may abandon it if the overhead doesn't pay off. The key is that it's opt-in, so abandoning it costs nothing. Full details are in the revised evaluation appended to `testing-strategy.md`.

8. **Adopt the retro-spec rhythm for vibe-coded work.** The natural development loop is: vibe code → `/retro-spec` → `/commit`. The retro-spec captures what was built in the same format as a pre-spec, gives the commit message substance, and accumulates documentation. Two separate skills (`/retro-spec` and `/commit`) kept composable — sometimes you want one without the other.

9. **For post-hoc testing of vibe-coded features, use the "flag what you had to guess" pattern.** A tester (Claude in-session or a tester subagent) reads the code and writes tests, but explicitly flags any test where it had to infer design intent. The flagged items are exactly the edge cases a spec would have addressed — resolving them retroactively is still valuable and doubles as a design-intent audit.

---

## 5. Open Questions (Deferred)

- **Spec file naming convention.** Date-prefix doesn't fit specs well — they're looked up by what they describe, not when they were written. Architecture-feature naming (e.g., `ui-timeline-splitting.md`, `schema-sources-table.md`) may be better. Needs a dedicated conversation before `specs/` folders accumulate files.
- **`/retro-spec` skill implementation.** Needs to be built. Core behavior: diff against HEAD, read changed files, generate a spec in the agreed format, present for review, save to `specs/`.
- **Whether a combined `/checkpoint` skill is worth adding** (retro-spec + commit in one pass). Defer until the two-skill rhythm has been tried.
