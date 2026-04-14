# Fiddle App Family — Architecture & Implementation Strategy

This is the canonical reference for how the fiddle-app family is built and why. It consolidates finalized decisions from research conducted in March–April 2026. For the app registry and data flow overview, see [APPS.md](APPS.md). For per-app details, see each app's own `CLAUDE.md`.

For development process, testing strategy, and folder conventions, see [dev-process.md](../dev-process.md) and [folder-conventions.md](../folder-conventions.md) at the Projects level.

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

See [dev-process.md](../dev-process.md) Section 8 for the full JSDoc convention. In brief: all exported functions, classes, and public methods get JSDoc annotations (`@param`, `@returns`, `@throws`). This is the project's lightweight type system — no TypeScript, but the same benefits for IDE support, skeleton generation, subagent context, and Swift portability.

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

The full adapter interface for MM is defined in [media-markup/specs/media-markup-spec.md](media-markup/specs/media-markup-spec.md).

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

## 9. Development Workflow & Testing

Development workflow, testing strategy, spec/handoff formats, subagent prompts, and skeleton generation are documented in [dev-process.md](../dev-process.md) at the Projects level. These are cross-project conventions, not fiddle-specific architecture.

---

## 10. Development Order

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

## 11. Electron Shared Setup

> [!question] Shared Electron template vs. extract-after-first-app
> Tune Hub and Media Markup share Electron setup patterns: `contextBridge`, `contextIsolation`, CSP, IPC, window management. Options: (a) build a shared template in `_shared/` upfront, or (b) build MM first, get the setup right, then extract reusable parts. The Gemini research recommended a security-aware template. Current plan: option (b) — extract after MM proves the patterns.

A: Covered in Section 8 above. Research stub and backlog item P6 created.

---

## 12. Electron Packaging & Distribution

> [!question] Electron packaging and distribution
> Electron apps need to be packaged (electron-builder, electron-forge, etc.) for distribution. Even for personal use: how to build a runnable `.exe`, auto-update capability, code signing. Not urgent but a known future task. Packaging is distinct from bundling — bundling optimizes your JS source files, packaging wraps them + the Electron runtime into a native executable. See [research/electron-packaging.md](research/electron-packaging.md) for full details. Backlog item P9.

A: 

---

## 13. GitHub Repo Structure & Deploy Pipeline

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
