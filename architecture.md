# Fiddle App Family — Architecture & Implementation Strategy

This is the canonical reference for how the fiddle-app family is built and why. It consolidates finalized decisions from research conducted in March–April 2026. For the app registry and data flow overview, see [APPS.md](APPS.md). For per-app details, see each app's own `CLAUDE.md`.

Historical research documents (including analysis that led to these decisions) are archived in [`research/skulch/`](research/skulch/).

---

## 1. Platform Decisions

| App | Platform | Status |
|---|---|---|
| Tune Hub | Electron (desktop-only) | Planned |
| Media Markup | Electron (desktop) → Capacitor iOS (iPad, future) | Planned |
| Tune List | Capacitor iOS (iPhone-only) | Planned |
| Microbreaker | WPA → Capacitor iOS wrap | Built (WPA); design review |
| Ear Tuner | WPA → Capacitor iOS wrap | Built (WPA); design review |

**Rationale by app:**

- **Tune Hub:** SSOT editor used at a desk. Needs direct file system access (folder watching, OneDrive paths), keyboard shortcuts, and `better-sqlite3` (Node.js native SQLite). No iOS port planned.
- **Media Markup:** Desktop-first for large video files and keyboard-driven annotation. iPad is a real future use case (annotating Zoom lessons on the couch), but desktop development comes first for easier debugging. The platform adapter pattern (see [Section 7](#7-platform-adapter-pattern)) makes the iPad port a wrap, not a rewrite.
- **Tune List:** Jam companion, used in-hand on a phone. Direct `tunehub.db` access via shared iCloud App Group. Future recording feature needs persistent mic permissions (Capacitor fixes the iOS re-ask problem).
- **Microbreaker / Ear Tuner:** Working WPAs. The Capacitor wrap fixes iOS permission persistence (microphone, motion sensors) and enables App Store distribution. The port is scaffolding + App Store logistics, not a code rewrite.

> [!tip] All apps in the family run HTML/CSS in a browser engine (Chromium for Electron, WKWebView for Capacitor). The shared design system (`_shared/design/`) applies identically across all of them with zero porting cost.

For full deliberation, see [skulch/2026-04-07_rethinking-dev-plans.md](research/skulch/2026-04-07_rethinking-dev-plans.md).

---

## 2. Technology Stack

### Core Stack

- **JavaScript** — ES modules, vanilla JS, no framework
- **CSS** — Custom properties (variables) via `_shared/design/`, no utility framework
- **SQLite** — `better-sqlite3` for Electron apps; `@capacitor-community/sqlite` for Capacitor apps
- **Electron** — Desktop apps (Tune Hub, Media Markup)
- **Capacitor** — iOS apps (Tune List, Microbreaker, Ear Tuner, future MM iPad)

### Frameworks: Evaluated and Rejected

We seriously considered frameworks including React, Svelte 5, and Tailwind CSS, but rejected them for this project:

- **React / Svelte:** Adds a build step, a dependency, and cognitive overhead switching between framework code and the vanilla JS used across the family. For a solo developer maintaining multiple apps, consistency across the family outweighs marginal per-app gains. Capacitor works with vanilla JS — a framework is not required. See [skulch/2026-04-11_electron-research.md](research/skulch/2026-04-11_electron-research.md) for the full Gemini analysis and evaluation.
- **Tailwind CSS:** Replaces the `_shared/design/` CSS variable system with a different philosophy. The existing approach is lighter, framework-free, shared across all apps without a build step, and portable to Swift Color extensions at future porting time.

### Bundling
We will probably eventually add a bundler for smaller iPhone apps, but probably not before then. See [research/bundling-strategy.md](research/bundling-strategy.md) for a full explainer.

### Why Vanilla JS

The coding conventions (see [CLAUDE.md](CLAUDE.md)) are designed for eventual Swift portability:
- ES module classes with constructor + methods map to Swift structs/classes
- Explicit observer/callback patterns map to SwiftUI's `ObservableObject` / `@Published`
- camelCase throughout matches Swift conventions
- No JS-specific idioms (prototypal inheritance, `arguments` object, `this`-binding gymnastics) in business logic

A framework's abstractions (virtual DOM, compiled reactivity, JSX) don't translate to Swift and would make porting a rewrite instead of a translation. We may never actually port to Swift if Capacitor proves good enough, but we want to keep our options open.

### JSDoc Convention

All exported functions, classes, and methods must have JSDoc annotations. This is the project's lightweight type system — no TypeScript, but the same benefits where it matters.

**Scope:** Public API surface only. If a function or method is exported (or is a public method on an exported class), it gets JSDoc. Internal helpers within a module don't need it unless the logic is non-obvious.

**What to document:**
- `@param` with type and description for each parameter
- `@returns` with type and description
- `@throws` if the function can throw
- A one-line summary of what the function does

```javascript
/**
 * Filter tunes by tonality (key + mode combination).
 * @param {Tune[]} tunes - Array of tune objects to filter
 * @param {string} key - Tonal center (e.g., 'A', 'D', 'G')
 * @param {string} [mode] - Optional mode filter (e.g., 'mixolydian', 'dorian')
 * @returns {Tune[]} Filtered array of matching tunes
 */
export function filterByTonality(tunes, key, mode) { ... }
```

**Why this matters (beyond documentation):**
1. **IDE support:** VSCode uses JSDoc for autocomplete, hover info, and inline type checking (even without TypeScript) when `// @ts-check` is enabled
2. **Skeleton generation:** JSDoc is what makes ctags-based codebase skeletons useful — signatures alone are ambiguous without type and purpose annotations
3. **Subagent context:** When a Coder or Tester subagent receives a skeleton of a module it needs to interact with, JSDoc tells it what the contract is without reading the implementation
4. **Swift portability:** JSDoc types map directly to Swift type annotations at porting time

> [!tip] Adding JSDoc is not busywork to apply retroactively to existing code. Add it as you write new exports and when you touch existing ones. It accumulates naturally.

---

## 3. Performance Techniques

These techniques are adopted from the Gemini architecture research. They apply across the family but are especially relevant to Media Markup's annotation timeline.

### Canvas Rendering
For complex visual elements (waveforms, annotation markers, playhead visualization), render on an HTML5 Canvas rather than managing thousands of DOM nodes. DOM-heavy timelines cause lag during fast scrolling and scrubbing.

### requestAnimationFrame
Sync video frame seeking and playhead rendering using `requestAnimationFrame` to match the screen's refresh rate. Never use `setInterval` or `setTimeout` for frame-synced rendering.

### Pointer Events
Use the Pointer Events API (unified mouse/touch) for all interactive elements that must work on both desktop and iPad. This avoids separate mouse and touch handler code paths and maps cleanly to the Capacitor WKWebView environment.

### Passive Event Listeners
Use `{ passive: true }` on scroll and touch listeners to prevent the JS thread from blocking the browser's compositor thread. Critical for smooth scrolling on iOS.

### GPU-Composited Animations
Use CSS `will-change` and `transform` properties for animations that should be GPU-composited. Avoid triggering layout recalculations during animations.

### Web Workers
For heavy computation (if needed — e.g., waveform generation, large dataset processing), offload to a Web Worker to keep the main thread responsive.

> [!tip] These techniques work identically in vanilla JS, Electron (Chromium), and Capacitor (WKWebView). No framework needed.

---

## 4. Data Architecture

### Source of Truth

All canonical data lives in SQLite databases. Each database has exactly one owner:

| Database | Owner | Location |
|---|---|---|
| `tunehub.db` | Tune Hub | iCloud Drive / FiddleApp/ |
| `media-markup.db` | Media Markup | iCloud Drive / FiddleApp/ |

No other app writes to a database it doesn't own.

### Cross-App Access: ATTACH Pattern

Apps that need data from another app's database use SQLite's `ATTACH DATABASE` in read-only mode:

```sql
-- MM attaching TuneHub's db to look up tunes
ATTACH DATABASE '/path/to/tunehub.db' AS tunehub;
SELECT * FROM tunehub.tunes WHERE id IN (
  SELECT tune_id FROM media_files WHERE path = ?
);
```

| App | tunehub.db | media-markup.db |
|---|---|---|
| Tune Hub (Electron, desktop) | Read/write (owns it) | Attaches read-only |
| MM (Electron, desktop) | Attaches read-only | Read/write (owns it) |
| MM (Capacitor, iPad — future) | Read-only via App Group | Read/write via App Group |
| Tune List (Capacitor, iPhone) | Read-only via App Group | — |

SQLite WAL mode supports multiple concurrent readers safely.

### Shared iCloud App Group (iOS)

All iOS apps share `tunehub.db` and `media-markup.db` via an Apple **App Group** — a shared iCloud container accessible to apps from the same developer account. Setup is an Xcode entitlements step (e.g., `group.com.fiddle-app.shared`), not code.

### Inbox Pattern

Apps that don't own a database communicate changes through the inbox:
- **Tune List** → writes `inbox/jam-notes-YYYY-MM-DD.json`
- **Media Markup** → writes inbox JSON for newly discovered tunes
- **Tune Hub** → reads inbox on demand, reviews changes, updates SSOT

No app modifies another app's database directly. All cross-app writes go through the inbox.

### Schema Versioning

Each database has a `schema_version` table tracking the current schema version and a read-compatible version floor:

```sql
CREATE TABLE schema_version (
  version INTEGER NOT NULL,          -- current schema version
  min_read_compatible INTEGER NOT NULL  -- oldest version that can still read this db
);
```

- The owning app checks `version` on startup and runs sequential migration scripts if needed.
- Read-only consumers (Tune List, MM reading tunehub.db) check `min_read_compatible`. If the db version is newer than the consumer understands but `min_read_compatible` is within range, the consumer proceeds safely. If not, it warns the user.
- Adding a new table or column is a new `version` but typically doesn't change `min_read_compatible` — old readers simply ignore what they don't know about.
- A breaking change (renamed column, removed table) bumps `min_read_compatible` to force consumer updates.

> [!question] iCloud + SQLite sync safety
> SQLite + iCloud sync is a known pain point. Apple's own documentation warns about it. Key risks: concurrent writes from different devices could corrupt the database; WAL mode helps concurrent reads but doesn't solve cross-device write conflicts. At minimum, each app should detect whether the database has been modified since it was last opened (check mtime or a checkpoint counter) and warn before writing. A possible approach: each writer records its session in the database so other instances can detect a competing writer and stay read-only. **This needs deeper research before committing to multi-device write workflows.**

A: See [research/icloud-sqlite-sync-safety.md](research/icloud-sqlite-sync-safety.md) for the research stub. Backlog item P5.

### Per-Tune Markdown

Tune Hub publishes human-readable markdown files that are optimized for Obsidian compatibility to a known location (probably the "Obsidian" folder that Obsidian creates at the root of the iCloud storage). A fallback location can be in `published/tunes/`. These serve as:
- Human-editable tune documentation (Obsidian vault)
- Claude/Larry-queryable reference
- Source material for a future public website
- Two-way sync: Tune Hub detects edits and surfaces changes for review before updating the SSOT
- We might also push the files to NotebookLM

Format details are in [tune-md-format](tune-hub/spec/tune-md-format.md)

### JSON Publishing — Dropped

The original plan for `published/data/` JSON snapshots has been dropped. All consuming apps access `tunehub.db` directly via the iCloud App Group. The inbox pattern still uses JSON for write-back.

For full data architecture deliberation, see [skulch/2026-04-06_cloud-storage-abstraction.md](research/skulch/2026-04-06_cloud-storage-abstraction.md) and [skulch/2026-04-07_rethinking-dev-plans.md](research/skulch/2026-04-07_rethinking-dev-plans.md).

---

## 5. Shared Design System

All apps use the same design tokens, fonts, icons, and sounds defined in `_shared/design/`. This is the single source of truth for visual consistency across the family.

- **CSS variables** define the color palette, typography scale, spacing, etc.
- All apps import these variables — no app defines its own colors or fonts inline
- New design elements are added to `_shared/` first, never defined ad-hoc in an app
- The design system works identically across Electron (Chromium) and Capacitor (WKWebView)

If any app is ever ported to native Swift, CSS variables translate to Swift `Color` extensions and `Font` definitions. The UI layer (HTML/CSS/DOM) is thrown away at porting time — that's expected. Design tokens survive as the bridge.

> [!todo] Design Review & Shared Resource Extraction
> The current priority is to migrate Microbreaker and Ear Tuner into their project folders, review their UI/UX together, and extract a canonical shared design system into `_shared/design/`. All other app development waits until this is complete. See [APPS.md](APPS.md) for status.

---

## 6. Data Robustness & Longevity

Design principle: data must remain useful even if none of the apps can be maintained.

- **SQLite** = source of truth (queryable, portable, universally supported)
- **Markdown** = human-readable tune documentation (readable in any text editor)
- **WebVTT** = shadow format for media annotations (player-compatible, plain text)
- **JSON** = inbox files and structured data exchange

No proprietary binary formats. Everything has a plain-text projection. The markdown files contain enough data to rebuild `tunehub.db` from scratch if needed.

---

## 7. Platform Adapter Pattern

Business logic must never call platform APIs directly. All file system access, database access, folder watching, and preference reads/writes go through a **platform adapter** — instantiated once at startup and injected into every module that needs it.

### The Rule

> Grep `src/app/` — there must be zero occurrences of `require('fs')`, `window.showOpenFilePicker`, `electron`, `localStorage`. Those words only appear in `src/platform/`.

### Structure

```
src/
  app/            ← 100% shared business logic and UI
  platform/
    electron.js   ← fs, fs.watch, electron-store, better-sqlite3
    capacitor.js  ← (future) Capacitor Filesystem, SQLite plugin
```

### Module Construction

```javascript
// Correct — adapter injected at construction
export class AnnotationStore {
  constructor(platform) {
    this.platform = platform;
  }
  async save(annotation) {
    const db = await this.platform.openDB('media-markup');
    // ...
  }
}

// Wrong — platform API called directly
import fs from 'fs';  // never in app/ modules
```

This pattern applies to all Electron/Capacitor apps: Media Markup, Tune Hub (if it ever gains a second platform), and any future app with cross-platform ambitions. It's what makes "add Capacitor later" a wrap rather than a rewrite.

The full adapter interface for MM is defined in [media-markup/CLAUDE.md](media-markup/CLAUDE.md).

---

## 8. Electron Security

All Electron apps (Tune Hub, Media Markup) must enforce these security measures from day one:

### contextIsolation

Always `true`. The renderer process runs in an isolated context; it cannot access Node.js APIs directly. All communication between renderer and main process goes through `contextBridge`.

### Content Security Policy (CSP)

Set a strict CSP that prevents inline scripts and restricts resource loading. This prevents XSS in the renderer.

### contextBridge

Expose only the specific IPC methods the renderer needs. Never expose broad APIs like `fs` or `child_process` to the renderer.

```javascript
// preload.js — expose only what's needed
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('api', {
  openDB: (name) => ipcRenderer.invoke('open-db', name),
  watchFolder: (path) => ipcRenderer.invoke('watch-folder', path),
  getPreference: (key) => ipcRenderer.invoke('get-preference', key),
});
```

> [!question] Shared Electron boilerplate
> Tune Hub and Media Markup share security setup (contextBridge, CSP, IPC patterns). Should there be a shared template in `_shared/`, or extract common patterns after the first app is built? The Gemini research suggested a security-aware template. Current plan: build MM first, get the Electron setup right, then extract reusable parts before starting Tune Hub.

A: See [research/electron-boilerplate-template.md](research/electron-boilerplate-template.md) for research stub. Backlog item P6. The question of using Ear Tuner as the template donor (simple app, easy to learn Electron on) is explored there.

---

## 9. Development Workflow

### Three Modes

Development follows one of three modes, chosen per-feature based on complexity:

#### Default: Vibe Coding

Normal interactive development with Claude Code. No spec required, no process overhead. Just build the thing, iterate, ship. This is how most work gets done.

#### Opt-In: Spec-Driven Mode

For features complex enough to benefit from thinking-it-through-first. Casey explicitly requests this mode.

1. **Casey + Claude (Architect role):** Discuss the feature, explore options, make decisions. Claude captures the design as a **spec** in the app's `specs/` folder. The spec is a durable design document — it records what the feature does and why, independent of who implements it or when.
2. **Architect writes a brief:** A work order referencing the spec, with implementation-specific instructions for the Coder. Written to `handoffs/` (see [Handoff Artifact Locations](#handoff-artifact-locations)). The brief is ephemeral — it's consumed and discarded.
3. **Coder** (subagent or manual terminal — see below)**:** Reads the spec (for design intent) and the brief (for instructions), then implements. If the coder has to guess, either the spec or the brief had gaps.
4. **Coder produces a handoff:** Files changed, functions added, `data-testid` values, IPC channels, state changes. Written to the app's `handoffs/` folder.
5. **Casey reviews.**

**How to invoke:** Just ask. Say something like "let's spec this out first" or "spec-driven mode for this feature." Claude will switch to the Architect role: discussing requirements, capturing the spec, then writing the brief and handing off to a Coder. There's no formal state to enter or exit — the mode ends naturally when the feature is implemented and reviewed. If you want to drop back to vibe coding mid-feature, just say so.

**When to use spec-driven mode:** Use it any time the work crosses a boundary where one person's assumptions could silently break another part of the system. Concrete triggers:

| Trigger | Example | Why it needs a spec |
|---|---|---|
| Cross-module changes | Adding a new IPC channel (preload + main + renderer) | Three files must agree on the channel name, payload shape, and error handling |
| Schema migrations | Adding a column to `tunehub.db` | Must consider `min_read_compatible`, downstream consumers, migration order |
| Platform adapter additions | New method on the Electron adapter | The contract must be defined before implementation so both platforms can conform |
| Cross-app data flow | Tune List writing a new inbox format that Tune Hub ingests | Producer and consumer must agree on schema without sharing a codebase |
| New store or state machine | Adding `AnnotationStore` with multiple states | States, transitions, and observer contracts need to be explicit |
| Anything with a "contract" | A new event/callback that multiple modules subscribe to | If the contract is implicit, consumers will each guess differently |

Single-file changes, CSS tweaks, and self-contained bug fixes don't need specs. If you're only touching one module and the change is obvious, vibe code it.

#### Optional Escalation: Adversarial Test Pass

For the highest-risk work (schema migrations, platform adapter contracts, cross-app data flow). A separate tester subagent reads the spec + manifest and writes tests without having seen the implementation conversation.

#### Manual Coder Terminal

An alternative to the automated subagent: Casey opens a second Claude Code terminal and drives the implementation personally, then hands the results back to the Architect session.

**When to use this instead of a subagent:**
- UI/UX work where real-time visual feedback matters ("move this 5px left")
- Exploratory implementation where the approach isn't clear yet and you want to iterate
- Learning a new API or library where you want to see what happens interactively
- Any task where you'd spend more time writing the spec than doing the work, but still want the Architect to stay clean

**Workflow:**

```
Architect terminal                    Coder terminal (Casey drives)
─────────────────                    ────────────────────────────
1. Write spec → specs/                
   Write brief → handoffs/           
                                     2. Read spec + brief, implement,
                                        iterate with Casey's guidance
                                     3. /handover → generates handoff
                                        artifact in handoffs/
4. Read handoff, update mental       
   model, continue planning          
                                     (optional) 5. Tester subagent reads
                                        spec + handoff, writes tests
```

The key difference from a subagent: Casey provides the judgment loop. The coder gets real-time "no, not that way" feedback that no spec can fully convey. The `/handover` skill (see below) ensures the results are captured in a structured format the Architect can consume.

### Specs vs. Workflow Artifacts

Design documentation and work orders serve different purposes and have different lifespans. They live in separate folders:

```
<app>/
  specs/       ← Durable design documents (what and why)
  handoffs/    ← Ephemeral workflow artifacts (briefs, deltas, test artifacts)
```

#### `specs/` — Permanent Design Records

Specs document the design intent of a feature: what it does, why it exists, what constraints it operates under. They are useful long after implementation — for onboarding, testing, documentation, and future modifications. A spec never contains coder-specific instructions like "implement this method" or "use the existing helper in utils.js."

A spec answers: *"If I come back to this feature in six months, what do I need to know?"*

Contents:
- Feature specs (the standard format below)
- Retro-specs (same format, written after vibe-coded work)

Specs are **not deleted** after implementation. They accumulate as the design record of the app.

#### `handoffs/` — Ephemeral Workflow Artifacts

Handoffs are consumed and discarded. They exist only to move information between roles during active development. Everything in `handoffs/` can be deleted after the feature is committed and reviewed.

Contents, distinguished by suffix:

| Suffix | Direction | Purpose |
|---|---|---|
| `*.brief.md` | Architect → Coder | Work order: what to implement, which files to touch, coder-specific instructions. References the spec for design intent. Also used for bug briefs. |
| `*.done.md` | Coder → Architect | Delta report: files changed, exports added/modified, deviations from spec |
| `*.test.md` | Coder → Tester | Test artifact: test cases, inputs, expected outputs, state setup |

**Linking:** All artifacts for a feature share a base name. Example:
- `specs/schema-sources-table.md` — the durable design spec
- `handoffs/schema-sources-table.brief.md` — "implement the sources table per the spec; here's the migration file to modify"
- `handoffs/schema-sources-table.done.md` — "done; added 2 exports, modified migration 003"
- `handoffs/schema-sources-table.test.md` — "test the NOT NULL constraint, test the default value"

**Lifecycle:** Clean out `handoffs/` regularly. Once work is committed and reviewed, the briefs and deltas have no further value. The spec in `specs/` stays.

### The `/handover` Skill

A Claude Code skill invoked at the end of a Coder session (manual terminal or subagent) to generate a structured handoff artifact. Invoke with `/handover`.

**What it does:**
1. Runs `git diff` against the base (pre-implementation state) to identify all changed files
2. Extracts new/modified exports and function signatures from the diff
3. Collects any new `data-testid` attributes added
4. Notes any new IPC channels or platform adapter methods
5. Checks for deviations from the spec (if a spec file is referenced)
6. Writes the handoff artifact to the app's `handoffs/` folder
7. Outputs a summary to the terminal

**What Casey does next:** Copy/paste or reference the handoff file path in the Architect terminal. The Architect reads it to update its understanding of the codebase state.

> [!todo] The `/handover` skill needs to be implemented as a Claude Code custom skill. See backlog. The git integration (diffing against a baseline commit) is the key automation — everything else could be done manually, but the diff-based extraction is where the skill saves real time.

### The Retro-Spec Rhythm

When vibe coding produces work worth documenting, a **retro-spec** closes the gap. It's the same durable design document as a pre-spec — same format, same `specs/` folder — just written after the code. No brief is needed (there's no coder to hand off to — the work is already done).

```
vibe code → /retro-spec → /commit → repeat
```

The retro-spec:
1. Forces a "wait, is this actually right?" pause before committing
2. Creates a permanent design record that explains what the feature does and why
3. Seeds future user documentation
4. Gives the commit message substance (commit references the spec)

> [!question] Spec file naming convention
> Date-prefix doesn't fit specs — they're looked up by what they describe, not when they were written. Architecture-feature naming (e.g., `ui-timeline-splitting.md`, `schema-sources-table.md`) may work better. Needs a dedicated conversation before `specs/` folders accumulate files.

A: See [research/spec-naming-convention.md](research/spec-naming-convention.md) for proposed area prefixes (schema-, ui-, data-, platform-, store-, workflow-, format-, ipc-). Backlog item P7.

### Spec Format (Durable — `specs/`)

The spec is a design document, not a work order. It should make sense to someone who has never seen the implementation conversation.

```markdown
# Feature: [Name]

## Purpose
Why this feature exists. What problem it solves.

## Requirements
- Functional requirements (what it must do)
- Data requirements (what it reads/writes, schemas)
- Platform requirements (Electron-specific, Capacitor-specific)

## States and Transitions
Major states the feature can be in, and what causes transitions.

## Constraints
- Security (CSP, contextIsolation)
- Performance (if relevant)
- Portability (platform adapter boundaries)

## Out of Scope
What this feature explicitly does NOT do.
```

### Brief Format (Ephemeral — `handoffs/*.brief.md`)

The brief is a work order for the Coder. It references the spec and adds implementation-specific instructions. It can also be a bug brief (no spec needed — just describe the bug).

```markdown
# Brief: [Feature or Bug Name]
**Spec:** [path to spec, if one exists]

## Task
What the Coder should do (implementation instructions, not design rationale).

## Files to Touch
- path/to/file.js — what to add or modify

## Context (Skeleton)
<!-- Paste relevant skeleton excerpts for modules the Coder needs to
     interact with but shouldn't modify -->

## Acceptance Criteria
How to know the work is done.
```

### Handoff Format (Ephemeral — `handoffs/*.done.md`)

```markdown
# Handoff: [Feature Name]

## Files Modified
- path/to/file.js — what changed

## Key Functions / Exports
- functionName(params) — what it does

## UI Selectors (data-testid)
- testid-name — what element

## State Changes
- storeName — what's new or changed

## IPC / Platform Adapter
- channel or method — what it does

## Deviations from Spec
- What was different from the spec/brief and why

## How to Verify
- Steps to manually confirm the feature works
```

### Coder Subagent System Prompt

```
You are a Coder subagent for the Fiddle App family. You will receive:
- A **spec** (design document — what the feature does and why)
- A **brief** (work order — what to implement and where)

Read both. The spec is the source of truth for design intent. The brief tells
you what to do. If they conflict, flag it — don't guess.

Implement using vanilla JavaScript (ES modules, classes with constructor + methods,
camelCase). Do NOT use any framework (React, Svelte, etc.) or utility CSS library
(Tailwind).

Constraints:
- All platform access (file system, SQLite, preferences) must go through the platform
  adapter — never call fs, electron, localStorage, or window.showOpenFilePicker
  directly from src/app/.
- Every interactive UI element must have a data-testid attribute.
- Use the observer/callback pattern for state management (no framework stores).
  Include a .reset() method on any store for test isolation.
- Follow the project's CSS variable system from _shared/design/ — no inline
  color/font definitions.
- All exported functions and public class methods must have JSDoc annotations
  (@param with types, @returns, @throws).
- After implementation, produce a Handoff (handoffs/*.done.md) summarizing: files
  modified, key functions/exports, data-testid values added, state changes,
  IPC/platform adapter methods used, deviations from spec, and manual verification
  steps.

Read the app's CLAUDE.md for app-specific context before starting.
```

### Tester Subagent System Prompt

```
You are a QA Tester subagent for the Fiddle App family. You will receive a spec
document and a handoff manifest from the Coder.

Your job:
1. Read the spec to understand the intended behavior.
2. Read the handoff manifest to understand what was built and where.
3. Write Vitest tests for business logic, stores, and data transformations.
4. Write Playwright tests for critical UI workflows (Electron apps).
5. Use data-testid selectors for all UI element references.
6. Flag anything where you had to guess at intended behavior. List these as
   "Ambiguities" at the end of your test file or in a separate note. These are
   edge cases the spec didn't cover — Casey will resolve them.

Do NOT fix implementation bugs yourself. Report failures to the Coder with the
error log and the test that triggered it.

If working without a spec (post-hoc testing of vibe-coded work), read the code
and the app's CLAUDE.md to infer intent, but always flag guesses.
```

### Codebase Skeleton Generation

A **skeleton** is a compressed view of a codebase: just the exports, class definitions, method signatures, and JSDoc — no implementation bodies. It gives the Architect (or a subagent) enough context to reason about module boundaries and contracts without reading every file.

#### When to Generate a Skeleton

Don't maintain a persistent skeleton file — it goes stale the moment anyone edits code. Generate one on demand in these situations:

| Situation | Why a skeleton helps |
|---|---|
| Writing a spec that touches modules you haven't read in this session | Shows the shape of what exists without polluting context with implementation details |
| Spinning up a Coder subagent that needs to interact with existing modules | The skeleton goes into the spec as "here's what you're working alongside" |
| Starting a new Architect session after a long break | Quick orientation: what's the public API surface right now? |
| Before a cross-app change | See the contracts between apps without reading both codebases fully |

Don't bother for single-file edits, bug fixes in a file you're already reading, or vibe coding sessions where you're exploring interactively.

#### How to Generate

Use [Universal Ctags](https://ctags.io/) to extract symbols, then format as Markdown for readability.

**Step 1 — Generate tags:**

```bash
# From the app root (e.g., ear-tuner/)
ctags -R --fields=+S+l --languages=JavaScript --extras=+q -f tags src/
```

Key flags:
- `-R` — recurse into subdirectories
- `--fields=+S+l` — include function signatures (`S`) and language (`l`)
- `--languages=JavaScript` — JS only (skip node_modules noise)
- `--extras=+q` — include qualified names (e.g., `ClassName.methodName`)

**Step 2 — Convert to Markdown skeleton:**

A script (to be built — see backlog) reads the `tags` file and the corresponding source files to produce a Markdown skeleton:

```markdown
# Skeleton: ear-tuner/src

## audio/AudioEngine.js
- `export class AudioEngine`
  - `constructor(platform)` — Initialize audio context via platform adapter
  - `calibrate(baseFrequency: number): Promise<boolean>` — Set reference pitch
  - `getFrequency(): number` — Current detected frequency
  - `start(): void` — Begin listening
  - `stop(): void` — Stop listening and release resources

## stores/TunerStore.js
- `export class TunerStore`
  - `constructor(audioEngine)` — Wraps AudioEngine with observable state
  - `subscribe(listener): void` — Register state change callback
  - `reset(): void` — Reset to initial state (test isolation)
```

The skeleton includes JSDoc summaries and parameter types (this is why the JSDoc convention matters — without it, the skeleton is just bare function names). Implementation bodies, private helpers, and comments are stripped.

**Step 3 — Include in spec (when relevant):**

When writing a spec for a Coder, attach the skeleton of any modules the Coder needs to interact with but shouldn't modify:

```markdown
## Context: Existing Modules (Skeleton Only — Do Not Modify)
<!-- paste or link the skeleton here -->
```

This gives the Coder the contract without the temptation (or context cost) of reading the full implementation.

> [!todo] Build the `tags-to-skeleton.js` script. It should read a ctags `tags` file, pull JSDoc from the corresponding source files, and output a grouped Markdown skeleton. This is a small utility — maybe 50–100 lines. See backlog.

---

## 10. Testing

### Tools

- **Vitest** — unit and integration tests. Works with vanilla JS and ES modules natively, fast, good watch mode. Both Claude and the Gemini research independently recommended this choice.
- **Playwright** — E2E tests. Handles Electron's multi-process architecture. Also usable for Capacitor webview testing. Again, independently recommended by both Claude and Gemini.

### Convention: `data-testid`

All interactive UI elements get a `data-testid` attribute. This decouples tests from CSS classes and DOM structure, making tests stable through UI refactors. Adopt this now, even before writing tests.

### Tiered Testing Strategy

**Tier 1 — Always test (Vitest):**
- SQLite schema migrations and queries (data corruption is the worst bug)
- Platform adapter interface contracts
- JSON schema validation (inbox files, tune markdown frontmatter parsing)
- Any pure-function business logic (tune filtering, key/mode display rules, status sorting)

> [!tip] Tier 1 items are natural candidates for spec-driven mode — write the spec, implement, test.

**Tier 2 — Test when stable (Playwright):**
- Critical user workflows in Electron apps (Tune Hub CRUD, MM segment creation)
- Cross-app data flow (Tune List reads what Tune Hub writes)
- Add these once the UI is settled, not during initial prototyping

**Tier 3 — Don't bother testing:**
- CSS styling and layout (verify visually)
- One-off UI interactions during rapid iteration
- Anything that changes faster than the test can be maintained

### Post-Hoc Testing (Vibe-Coded Work)

When testing features that were vibe-coded without a spec, the tester (Claude in-session or a subagent) reads the code and writes tests. The key instruction: **"flag what you had to guess."** Flagged items are exactly the edge cases a spec would have covered. Resolving them retroactively doubles as a design-intent audit.

---

## 11. Development Order

Development proceeds in three groups. Items within a group can be worked in parallel.

### Group 1 — Foundations (P1)

- **TuneHub data:** Define the backend schema (`tunehub.db` tables, columns, types, constraints, schema_version). This unblocks all other apps.
- **Larry & TuneHub:** Define the canonical `.md` formatting for tune files (ingestion and publishing).
- **Larry:** Define ingestion formats (may vary by source).
- **Larry:** Figure out how to effectively gather data from Slippery Hill and other sources. These may eventually be incorporated into TuneHub if implementable in JavaScript.
- **Ear Tuner & Microbreaker:** Initial porting of existing code into project folders. Finalize and extract design standards into `_shared/design/`.

### Group 2 — Core Apps (P2)

- **Ear Tuner & Microbreaker:** Port to standard Electron architecture in prep for eventual iPhone/iPad apps.
- **Media Markup:** Desktop (Electron) version.
- **Tune Hub:** App with UI.
- **Tune List:** Desktop development version (Capacitor iPhone target).

### Group 3 — Mobile (P3)

- **Media Markup:** iPad (Capacitor).
- **Ear Tuner:** iPhone/iPad (Capacitor wrap).
- **Microbreaker:** iPhone/iPad (Capacitor wrap).

> [!warning] Group 2 and 3 apps depend on the tunehub.db schema being defined in Group 1. The schema doesn't need a UI — just the DDL and migration scripts.

---

## 12. Electron Shared Setup

> [!question] Shared Electron template vs. extract-after-first-app
> Tune Hub and Media Markup share Electron setup patterns: `contextBridge`, `contextIsolation`, CSP, IPC, window management. Options: (a) build a shared template in `_shared/` upfront, or (b) build MM first, get the setup right, then extract reusable parts. The Gemini research recommended a security-aware template. Current plan: option (b) — extract after MM proves the patterns.

A: Covered in Section 8 above. Research stub and backlog item P6 created.

---

## 13. Electron Packaging & Distribution

> [!question] Electron packaging and distribution
> Electron apps need to be packaged (electron-builder, electron-forge, etc.) for distribution. Even for personal use: how to build a runnable `.exe`, auto-update capability, code signing. Not urgent but a known future task. Packaging is distinct from bundling — bundling optimizes your JS source files, packaging wraps them + the Electron runtime into a native executable. See [research/electron-packaging.md](research/electron-packaging.md) for full details. Backlog item P9.

A: 

---

## 14. GitHub Repo Structure & Deploy Pipeline

### Repo Layout

All repos live under `fiddle-app`. Source repos are private; hosting repos are public with GitHub Pages enabled.

| Repo | Visibility | Role | Hosted URL |
|---|---|---|---|
| `ear-tuner` | Private | Source — Ear Tuner | — |
| `microbreaker` | Private | Source — Microbreaker | — |
| `tune-hub` | Private | Source — Tune Hub | — |
| `tune-list` | Private | Source — Tune List | — |
| `media-markup` | Private | Source — Media Markup | — |
| `_shared` | Private | Shared design tokens, assets | — |
| `ear` | Public | Hosted PWA — Ear Tuner | `fiddle-app.github.io/ear` |
| `practice` | Public | Hosted PWA — Microbreaker | `fiddle-app.github.io/practice` |

Source repos hold all dev work: code, specs, tests, research, backlog, CLAUDE.md.
Hosting repos (`ear`, `practice`) hold only built output for GitHub Pages to serve.

Future hosting repos if needed: `hub` (static Tune Hub browse site), `list` (Tune List PWA).

### Folder Structure

```
C:\
├── Builds\fiddle\                       ← generated output; NOT OneDrive-synced
│   ├── ear\                             ← clone of fiddle-app/ear  (GitHub Pages)
│   └── practice\                        ← clone of fiddle-app/practice (GitHub Pages)
│
└── Users\CaseyM\OneDrive\Projects\fiddle\   ← source; OneDrive-synced, git-tracked
    ├── ear-tuner\
    ├── microbreaker\
    ├── scripts\
    │   └── deploy.sh                    ← shared deploy script (parameterized)
    └── ...
```

`C:\Builds\` is intentionally outside OneDrive. Build output is regenerated on demand — syncing it wastes bandwidth and risks file-lock conflicts during git operations.

### Deploy Pipeline

Each PWA app has `build` and `deploy` scripts in its `package.json`:

```json
{
  "scripts": {
    "build": "echo 'No bundler — static files copied directly (see backlog P13)'",
    "deploy": "bash ../../scripts/deploy.sh ear-tuner"
  }
}
```

The shared script `scripts/deploy.sh`:
1. Copies app source files to `C:\Builds\fiddle\<repo>\`, excluding dev-only files (`.md`, `backlog/`, `research/`, `spec/`, `handoffs/`, `node_modules/`)
2. Commits with a datestamp message and pushes to the hosting repo
3. GitHub Pages serves the result automatically

Run from PowerShell:
```powershell
cd $env:USERPROFILE\OneDrive\Projects\fiddle\ear-tuner
npm run deploy
```

> [!note] The build step is currently a direct file copy — no bundler. Minification via esbuild is a future consideration (backlog P13).

---

*Consolidated from research conducted March–April 2026. Last updated: 2026-04-12.*
