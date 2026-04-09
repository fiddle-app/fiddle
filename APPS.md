# Fiddle App Family — Master App List

This document tracks all planned and possible apps in the fiddle-app ecosystem.
It is a living document — update it as ideas evolve.

---

## Current Priority

**Next up: Design Review & Shared Resource Extraction**
Migrate Microbreaker and Ear Tuner into their project folders, review their UI/UX design
together, and extract a canonical shared design system into `_shared/design/`.
Plan: `_shared/design/DESIGN-REVIEW-PROJECT.md`

GitHub repos are set up. Waiting on Phase 1: extract code and design intent from old Claude chats.

All other app development (Tune Hub, Tune List, etc.) waits until this is complete.

---

## Platform Decisions

> See [`research/rethinking-dev-plans.md`](research/rethinking-dev-plans.md) for full rationale.

| App | Platform | Notes |
|---|---|---|
| Tune Hub | Electron (desktop-only) | SSOT editor; direct fs, keyboard shortcuts, `better-sqlite3` |
| Tune List | Capacitor iOS (iPhone-only) | Direct tunehub.db via shared iCloud App Group |
| Media Markup | Electron (desktop) → Capacitor iOS (iPad, future) | Platform adapter makes the iPad port a wrap |
| Microbreaker | WPA → Capacitor iOS wrap | Permission persistence fix; scaffolding, not a rewrite |
| Ear Tuner | WPA → Capacitor iOS wrap | Same |

The key commitment: MM and Tune Hub's platform adapters must be designed from day one, even if only
one target exists at launch. File access, SQLite, and preferences go through the adapter — never
called from business logic directly.

---

## Folder Structure

### Code (OneDrive, git-tracked, GitHub under `fiddle-app`)
```
C:\Users\CaseyM\OneDrive\Projects\
├── fiddle\
│   ├── CLAUDE.md                  ← umbrella Claude Code context
│   ├── APPS.md                    ← this file
│   ├── research\                  ← cross-app research and architecture notes
│   │   ├── rethinking-dev-plans.md
│   │   └── cloud-storage-abstraction.md
│   ├── _shared\                   ← repo: fiddle-app/_shared
│   │   ├── CLAUDE.md
│   │   ├── design\                ← color tokens, typography, style guide
│   │   ├── assets\                ← icons, sounds, fonts
│   │   └── schema\                ← JSON/data schemas for all data types
│   ├── minions\                   ← Claude agents for specialized tasks
│   │   ├── CLAUDE.md              ← minion registry
│   │   └── larry\                 ← tune researcher agent
│   │       └── CLAUDE.md
│   ├── tune-hub\                  ← repo: fiddle-app/tune-hub
│   │   └── CLAUDE.md
│   ├── tune-list\                 ← repo: fiddle-app/tune-list
│   │   └── CLAUDE.md
│   ├── media-markup\              ← repo: fiddle-app/media-markup
│   │   └── CLAUDE.md
│   ├── microbreaker\              ← repo: fiddle-app/microbreaker
│   │   └── CLAUDE.md
│   └── ear-tuner\                 ← repo: fiddle-app/ear-tuner
│       └── CLAUDE.md
└── travel\
    └── europe-2026\
```

### Runtime Data (iCloud Drive — syncs to iPhone/iPad and Windows)
```
iCloud Drive\FiddleApp\
├── tunehub.db                     ← SQLite SSOT; Tune Hub owns; others read-only
├── media-markup.db                ← SQLite; Media Markup owns; Tune Hub attaches read-only
├── published\
│   ├── tune-index.md              ← all tunes by key, alphabetical, with links
│   └── tunes\                     ← one .md per tune; browse in VSCode, query with Claude
│       ├── sally-goodin.md
│       └── ...
└── inbox\                         ← TuneList and MM write here; Tune Hub ingests
    └── jam-notes-YYYY-MM-DD.json
```

> **Note:** The `published/data/` JSON snapshot folder from the original plan has been dropped.
> Consuming apps (Tune List, Media Markup) access `tunehub.db` directly via shared iCloud App Group.
> See [`research/rethinking-dev-plans.md`](research/rethinking-dev-plans.md) for rationale.

### Media Files (OneDrive — large files, stay where they are)
```
C:\Users\CaseyM\OneDrive\[existing Zoom recordings location]\
```
Media Markup opens these via Electron `fs` (desktop) or Capacitor Filesystem plugin (iPad).
No reorganization needed.

---

## Data Architecture

### Source of Truth (SSOT)
All canonical tune data lives in a single **SQLite database** (`tunehub.db`), owned and edited
exclusively by **Tune Hub**. No other app writes directly to this file.

Annotation data lives in **`media-markup.db`**, owned by **Media Markup**. Tune Hub attaches it
read-only to surface media linked to tunes.

### Shared iCloud App Group

All iOS apps share `tunehub.db` and `media-markup.db` via an Apple **App Group** — a shared iCloud
container accessible to all apps under the same developer account. Setup is an Xcode entitlements
step (not code). See [`research/cloud-storage-abstraction.md`](research/cloud-storage-abstraction.md).

| App | tunehub.db | media-markup.db |
|---|---|---|
| Tune Hub (Electron, desktop) | Read/write (owns it) | Attaches read-only |
| MM (Electron, desktop) | Attaches read-only via local iCloud path | Read/write (owns it) |
| MM (Capacitor, iPad — future) | Read-only via App Group | Read/write via App Group |
| Tune List (Capacitor, iPhone) | Read-only via App Group | — |

SQLite WAL mode supports multiple concurrent readers safely.

### Data Flow
```
Tune Hub (Electron) ──writes──▶ tunehub.db (SSOT)
                    ──publishes──▶ published/tunes/*.md   ← human editing, Claude queries, future website
                    ──publishes──▶ published/tune-index.md
                    ──reads──▶    published/tunes/*.md    ← two-way sync: ingests edits after review
Tune List (Capacitor, iPhone) ──reads──▶ tunehub.db (read-only, App Group)
                              ──writes──▶ inbox/*.json    ──ingests──▶ Tune Hub (Inbox view)
Media Markup (Electron) ──reads/writes──▶ media-markup.db
                        ──attaches──▶ tunehub.db (read-only)
                        ──writes──▶ inbox/*.json           ──ingests──▶ Tune Hub (new tune drafts)
Tune Hub ──attaches──▶ media-markup.db (read-only, surfaces media linked to tunes)
```

### Per-Tune Markdown Format
Each tune gets a `.md` file with YAML frontmatter (machine-parseable) and consistent section headers
(human-editable). Tune Hub reads diffs and promotes changes to SQLite after review.

```markdown
---
id: 12345
name: Sally Goodin
key: A
mode: mixolydian
style: breakdown
status: canLead
last-updated: 2026-03-27
---

## Notes
## Start Hints
## Structure
## Variants
## Media
```

### Two-Way Sync
Tune Hub publishes `.md` files. Casey (or a Claude agent like Larry) edits them. Tune Hub detects
diffs and surfaces changes in a review UI before writing back to SQLite. No edits go to the SSOT
without Casey's approval.

---

## App Registry

---

### Tune Hub
- **URL/repo name:** `tune-hub`
- **Status:** Planned — high priority (after design review)
- **Platform:** Electron (desktop-only)
- **Purpose:** The primary editing interface for all tune data. Owns and manages `tunehub.db`.
  Publishes per-tune markdown for human editing and future website generation. Has an Inbox view
  for reviewing notes from Tune List and new tune drafts from MM. Attaches `media-markup.db`
  read-only to surface linked media.
- **Data access:**
  - **Reads/writes:** `tunehub.db` via `better-sqlite3` (Node.js native SQLite)
  - **Attaches (read-only):** `media-markup.db` — surfaces media linked to tunes
  - **Writes (publish):** `published/tune-index.md`, `published/tunes/*.md` — triggered manually or on save
  - **Reads (two-way sync):** `published/tunes/*.md` — diffs surfaced for review before SSOT update
  - **Reads (inbox):** `inbox/*.json` — queued notes from Tune List and MM; Casey decides what to promote
- **Ecosystem entry point:** Tune Hub is the first app a new user runs. On first launch it prompts
  for file paths (tunehub.db location, Zoom folder, etc.) and stores them in preferences.
- **Key features:**
  - First-run onboarding: set up db path and preferences
  - Full CRUD for tune records (name, key, mode, style, status, structure, notes, start hints)
  - Define and save custom tune lists (consumed by Tune List)
  - Inbox view: review and act on Jam Notes from Tune List; new tune drafts from MM
  - Link tunes to media files via media-markup.db attachment
  - Publish per-tune markdown and tune index
  - Two-way sync: review markdown edits and promote to SSOT

---

### Tune List
- **URL/repo name:** `tune-list`
- **Status:** Planned
- **Platform:** Capacitor iOS (iPhone-only)
- **Purpose:** The digital equivalent of the paper tune list Old Time fiddlers bring to jams.
  Browse, filter, find common tunes with other players, capture in-the-moment notes. Reads directly
  from `tunehub.db` via shared iCloud App Group — no JSON snapshot intermediary.
- **Research:** [`tune-list/research/platform-and-data-access.md`](tune-list/research/platform-and-data-access.md),
  [`tune-list/research/iphone-prototype-strategy.md`](tune-list/research/iphone-prototype-strategy.md)
- **Data access:**
  - **Reads:** `tunehub.db` via shared iCloud App Group (read-only); `@capacitor-community/sqlite`
  - **Writes:** `inbox/jam-notes-YYYY-MM-DD.json` — queued notes; TuneHub ingests on review
- **Prototype path:** Before a Mac is available for Capacitor builds, a read-only Mobile Safari
  prototype can validate the UI and data model using `<input type="file">` + sql.js + IndexedDB.
  See [`tune-list/research/iphone-prototype-strategy.md`](tune-list/research/iphone-prototype-strategy.md).
- **Key features:**
  - Browse tunes sorted by status (`canLead` first)
  - "Can I start this?" hints for each tune
  - Find tunes by key to match what others are playing
  - Note tunes heard at a jam (not yet on your list)
  - Mark tunes to prioritize or add quick observations
  - All write-back goes through the inbox pattern — no direct SSOT editing
  - (Future) Record a quick take at a jam; associates with the tune

---

### Media Markup *(working title)*
- **URL/repo name:** `media-markup`
- **Status:** Planned
- **Platform:** Electron (desktop) → Capacitor iOS (iPad, future)
- **Purpose:** Replaces iMovie for annotating lesson and practice recordings. Load a video or audio
  file, define time segments, attach text annotations to each segment. Primary use case: reviewing
  Zoom lesson recordings at your desk.
- **Research:** [`media-markup/research/cross-platform-options.md`](media-markup/research/cross-platform-options.md)
- **Data access:**
  - **Reads/writes:** `media-markup.db` (MM owns this database)
  - **Attaches (read-only):** `tunehub.db` — to link media to tune records
  - **Reads (media):** Zoom recordings via Electron `fs` (desktop); Capacitor Filesystem plugin (iPad)
  - **Writes (inbox):** New tunes discovered during annotation go through the inbox pattern
  - **Read by:** Tune Hub attaches `media-markup.db` read-only
- **Platform adapter:** Business logic must never call platform APIs directly. All file access,
  db access, folder watching, and preference reads go through the platform adapter.
  `src/platform/electron.js` is the desktop implementation; `src/platform/capacitor.js` is the
  future iPad implementation. See `media-markup/CLAUDE.md` for full interface spec.
- **Key features:**
  - Folder watching: MM monitors the Zoom folder and proactively suggests new recordings
  - Time-segment marking on video and audio
  - Per-segment text annotations
  - Annotations linked to tune records in Tune Hub
  - Keyboard-first design: Space, arrows, `[`/`]`, Enter, N — full shortcut coverage
  - Possibly: export annotated summary as text or PDF

---

### Microbreaker
- **URL/repo name:** `microbreaker`
- **Status:** Built (WPA) — in design review
- **Platform:** WPA → Capacitor iOS wrap
- **Purpose:** Practice timer that encourages structured micro-breaks and good practice habits.
- **Data access:** Minimal. No tune data dependency.
- **Notes:** The Capacitor wrap is scaffolding + App Store logistics, not a code rewrite.
  `WKWebView` supports Web Audio API and DeviceMotionEvent natively. The main benefit is
  persistent microphone/motion permissions (iOS re-asks every PWA session; native apps ask once).

---

### Ear Tuner
- **URL/repo name:** `ear-tuner`
- **Status:** Built (WPA) — in design review
- **Platform:** WPA → Capacitor iOS wrap
- **Purpose:** Ear training — helps develop the ability to hear and distinguish pitch differences.
- **Data access:** Minimal. No tune data dependency.
- **Notes:** Same story as Microbreaker. Capacitor wrap fixes the permission re-ask problem;
  code is unchanged.

---

### Tune Player
- **URL/repo name:** `tune-player`
- **Status:** Idea
- **Platform:** Native iOS/iPadOS (Swift-primary)
  - A desktop WPA prototype may be feasible using File System Access API + HTML5 audio,
    but iOS Safari doesn't support File System Access API — native Swift is the real target.
    Primary use case is iPad/iPhone during practice, so don't invest heavily in the WPA phase.
- **Purpose:** Plays tune audio samples in a playlist — sequentially or shuffled.
  Lets Casey drill a filtered subset of tunes (e.g. tunes actively being learned, or tunes
  where the start needs work). Useful for focused practice sessions.
- **Data access:**
  - **Reads:** `tunehub.db` via shared iCloud App Group for tune metadata and filtering
  - **Reads (media — two sources):**
    - `FiddleApp/media/` (iCloud) — audio samples downloaded by Larry from Slippery Hill
    - OneDrive — existing recordings; linked via `media-markup.db`
- **Key features:**
  - Play playlist sequentially or shuffled
  - Filter tunes by status, key, or other tune fields
  - Potentially: display tune name, key, start hints, or structure diagram while playing
- **Notes:**
  - iCloud media is accessible natively via FileManager on iOS — seamless
  - OneDrive media on iOS requires OneDrive SDK or document picker; treat as a known design challenge

---

## Minions (Claude Agents)

Agents that perform specialized, repeatable tasks in support of the apps.
All minions live in `fiddle/minions/`. They read/write via the shared iCloud container
and never write directly to `tunehub.db`.

---

### Larry — Tune Researcher
- **Folder:** `minions/larry/`
- **Status:** Planned
- **Purpose:** Looks up tune data on the internet, primarily Slippery Hill
  (https://www.slippery-hill.com/), and produces draft `published/tunes/*.md` files.
- **Primary source:** Slippery Hill — canonical name, keys, tunings, sources, recordings
- **Bootstrapping role:**
  - Process Casey's OneNote-derived tune lists
  - Match each tune to its Slippery Hill page; add URL to frontmatter
  - Report discrepancies between Casey's data and Slippery Hill
  - List unmatched tunes for manual investigation (usually a name/spelling variation)
  - (TBD) Download media samples to `iCloud Drive\FiddleApp\media-samples\`
- **Ongoing role:**
  - When Tune Hub detects a new tune name in jam notes, queue it for Larry
  - Larry builds a draft `tune.md` from Slippery Hill data
  - Casey reviews; Tune Hub ingests and updates SSOT

---

## Backlog / Ideas

- **Tune Flashcards** — Drill the opening phrase of tunes cold; tests ability to start confidently
- **Lesson Tracker** — Link lesson recordings (via Music Markup) to tunes worked on; track progress over time. May be a Tune Hub view rather than a standalone app.

*Note: "Jam Helper" and "Session Logger" are not separate apps — that functionality lives in Tune List.*

---

## Shared Infrastructure

| Layer | Description |
|---|---|
| `_shared` | Design tokens, icons, sounds, fonts, and data schemas — enforces consistent look/feel across all apps |
| **iCloud App Group** | Shared runtime container for `tunehub.db`, `media-markup.db`, inbox notes, media samples |
| **published/tunes/*.md** | Human-readable tune files; edited by Casey and Larry; source for future public website |
| **OneDrive** | Large media files (video/audio recordings); referenced by path in `media-markup.db` |

---

*Last updated: 2026-04-07*
