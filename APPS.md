1# Fiddle App Family — Master App List

This document tracks all planned and possible apps in the fiddle-app ecosystem.
It is a living document — update it as ideas evolve.

---

## Current Priority

**Next up: Design Review & Shared Resource Extraction**
Migrate Microbreaker and Ear Tuner into their project folders, review their UI/UX design
together, and extract a canonical shared design system into `_shared/design/`.
Plan: `_shared/design/DESIGN-REVIEW-PROJECT.md`

All other app development (Tune Hub, Tune List, etc.) waits until this is complete.

---

## Folder Structure

### Code (OneDrive, git-tracked, GitHub under `fiddle-app`)
```
C:\Users\CaseyM\OneDrive\Projects\
├── fiddle\
│   ├── CLAUDE.md                  ← umbrella Claude Code context
│   ├── APPS.md                    ← this file
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
├── tunehub.db                     ← SQLite SSOT; Tune Hub only
├── published\
│   ├── tune-index.md              ← all tunes by key, alphabetical, with links
│   ├── tunes\                     ← one .md per tune; browse in VSCode, query with Claude
│   │   ├── sally-goodin.md
│   │   └── ...
│   └── data\                      ← JSON for apps; no need to open by hand
│       ├── all-tunes.json
│       ├── tunes\
│       │   └── sally-goodin.json
│       └── lists\
├── inbox\                         ← TuneList writes; Tune Hub ingests
│   └── jam-notes-YYYY-MM-DD.json
└── media-annotations\             ← Music Markup writes; Tune Hub reads
    └── <media-filename>.json
```

### Media Files (OneDrive — large files, stay where they are)
```
C:\Users\CaseyM\OneDrive\[existing Zoom recordings location]\
```
Music Markup opens these via file picker. No reorganization needed.

---

## Data Architecture

### Source of Truth (SSOT)
All canonical tune data lives in a single **SQLite database** (`tunehub.db`), owned and edited exclusively by **Tune Hub**. No other app writes directly to this file.

### Data Flow Pattern
```
Tune Hub (desktop) ──writes──▶ tunehub.db (SSOT)
                   ──publishes──▶ published/tunes/*.md     ← human editing, Claude queries, agent augmentation
                   ──publishes──▶ published/tune-index.md  ← index by key with links
                   ──publishes──▶ published/data/*.json    ← app consumption
                   ──reads──▶    published/tunes/*.md      ← two-way sync: ingests edits back to SSOT
Tune List (mobile) ──writes──▶  inbox/*.json              ──ingests──▶ Tune Hub (Inbox view)
Music Markup       ──writes──▶  media-annotations/*.json  ──reads──▶ Tune Hub
```

### Per-Tune Markdown Format
Each tune gets a `.md` file with YAML frontmatter (machine-parseable) and consistent section headers (human-editable). Tune Hub reads diffs and promotes changes to SQLite after review.

```markdown
---
id: 12345
name: Sally Goodin
key: A
mode: mixolydian
style: breakdown
confidence: high
priority: false
last-updated: 2026-03-27
---

## Notes
Free-form prose. Fully editable in VSCode or by Claude agents.

## Start Hints
...

## Variants
...
```

### Two-Way Sync
Tune Hub publishes `.md` files. Casey (or a Claude agent) edits them — e.g. augmenting with data from slippery-hill.com. Tune Hub detects diffs and surfaces changes in a review UI before writing back to SQLite. No edits go to the SSOT without Casey's approval.

### SQLite WASM
SQLite WASM (WebAssembly build of SQLite, runs in the browser) is used only in Tune Hub. Tune List and other lightweight apps consume published JSON snapshots — no WASM needed.

---

## App Registry

---

### Tune Hub
- **URL/repo name:** `tune-hub`
- **Status:** Planned — highest priority
- **Platform:** WPA (desktop-first) → native iOS/iPadOS
- **Purpose:** The primary editing interface for all tune data. Owns and manages the SQLite SSOT. Publishes snapshot JSON and per-tune markdown for other apps and humans to consume. Has an Inbox view for reviewing and ingesting notes from Tune List and other apps.
- **Data access:**
  - **Reads/writes:** `tunehub.db` via SQLite WASM + File System Access API (desktop browser) or native SQLite (iOS)
  - **Writes (publish):** `published/tune-index.md`, `published/tunes/*.md`, `published/data/**` — triggered manually or on save
  - **Reads (two-way sync):** `published/tunes/*.md` — diffs surfaced for review before SSOT update
  - **Reads (inbox):** `inbox/*.json` — queued notes from Tune List; Casey decides what to promote
  - **Reads:** `media-annotations/*.json` — links annotations to tune records
- **Ecosystem entry point:** Tune Hub is the first app a new user runs. On first launch it detects whether the `FiddleApp/` iCloud container exists and creates it if not, using `_shared/schema/icloud-structure.json` as the canonical folder definition. Once the container exists, Tune List and Music Markup can function. The PowerShell setup script (`_shared/setup/Create-iCloudFolders.ps1`) is a developer convenience that does the same thing manually.
- **Key features:**
  - First-run onboarding: detects and creates iCloud folder structure
  - Full CRUD for tune records (name, key, mode, style, structure, origin, notes, confidence, start hints)
  - Define and save custom tune lists (consumed by Tune List)
  - Inbox view: review and act on Jam Notes from Tune List
  - Link tunes to media files and annotations
  - Publish snapshots and markdown
  - Two-way sync: review markdown edits and promote to SSOT

---

### Tune List
- **URL/repo name:** `tune-list`
- **Status:** Planned
- **Platform:** WPA (mobile-first) → native iOS/iPadOS
- **Purpose:** The digital equivalent of the paper tune list Old Time fiddlers bring to jams — but on steroids. One-stop-shopping for every way Casey needs to interact with his tune list at a jam: browsing, filtering, finding common tunes with other players, capturing in-the-moment notes. Lists are defined in Tune Hub and consumed here as read-only snapshots. Includes all session/jam logging functionality (no separate Session Logger or Jam Helper app needed).
- **Data access:**
  - **Reads:** `published/data/all-tunes.json` and `published/data/lists/*` — never touches `tunehub.db` directly
  - **Writes (PWA phase):** Jam notes stored in browser localStorage as discrete jam records. Each jam has a date and optional name; multiple jams per day supported. Notes accumulate indefinitely — no pressure to share immediately. When ready, user manually triggers share: Web Share API → iOS Share Sheet → "Save to Files" → `FiddleApp/inbox/`. Each exported file marked "shared" in localStorage. Tune List will not re-export already-shared notes. Tune Hub deduplicates on ingest. Once confirmed shared, local history can be cleared.
  - **Writes (native phase):** App writes directly to iCloud container — no user action required; share tracking still applies for deduplication
  - **Processed by:** Tune Hub Inbox view; Casey reviews and promotes notes to SSOT
- **Key features:**
  - Browse tunes sorted by key, confidence, playability
  - "Can I start this?" hints for each tune
  - Find tunes by key to match what others are playing at a jam
  - Note tunes heard at a jam (not yet on your list)
  - Mark tunes to prioritize for learning, or add quick observations
  - All write-back goes through the inbox pattern — no direct SSOT editing

---

### Media Markup *(working title)*
- **URL/repo name:** `media-markup`
- **Status:** Planned
- **Platform:** WPA (desktop-first prototype) → WPA (iOS) → native iOS/iPadOS
- **Purpose:** Replaces iMovie for annotating lesson and practice recordings. Load a video or audio file, define time segments, attach text annotations to each segment. Primary use case: reviewing Zoom lesson recordings.
- **Data access:**
  - **Reads (desktop WPA):** Media files opened via File System Access API file picker — user selects from any local folder, including OneDrive and iCloud for Windows sync folders
  - **Reads/writes (desktop WPA):** Annotation JSON saved via File System Access API to `FiddleApp/media-annotations/`
  - **Reads (iOS native):** Media files referenced by path in OneDrive; annotation JSON read/written from iCloud container
  - **Read by:** Tune Hub (links annotations to tune records)
- **Key features:**
  - Time-segment marking on video and audio
  - Per-segment text annotations
  - Annotations linked to tune records in Tune Hub
  - Possibly: export annotated summary as text or PDF

---

### Microbreaker
- **URL/repo name:** `microbreaker`
- **Status:** Built (WPA, informal — needs migration)
- **Platform:** WPA → native iOS/iPadOS
- **Purpose:** Practice timer that encourages structured micro-breaks and good practice habits.
- **Data access:** Minimal. Session settings may sync; no tune data dependency.
- **Notes:** Currently lives informally in `OneDrive\Code`. Needs migration into proper project structure and possible refactoring to fit shared design system.

---

### Ear Tuner
- **URL/repo name:** `ear-tuner`
- **Status:** Built (WPA, informal — needs migration)
- **Platform:** WPA → native iOS/iPadOS
- **Purpose:** Ear training — helps develop the ability to hear and distinguish pitch differences.
- **Data access:** Minimal. No tune data dependency.
- **Notes:** Same migration situation as Microbreaker.

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
  - **Reads:** `published/data/all-tunes.json` for tune metadata and filtering
  - **Reads (media — two sources):**
    - `FiddleApp/media/` (iCloud) — audio samples downloaded by Larry from Slippery Hill
    - OneDrive iTunes library — existing recordings; referenced by path in Music Markup
      annotation JSON, which links media files to tune records
- **Key features:**
  - Play playlist sequentially or shuffled
  - Filter tunes by attributes: confidence level, priority flag, or other tune fields
    (e.g. "only tunes marked priority=true", "only tunes with confidence=low")
  - Potentially: display tune name, key, start hints, or structure diagram while playing
- **Notes:**
  - iCloud media (`FiddleApp/media/`) is accessible natively via FileManager on iOS — seamless
  - OneDrive media on iOS has no direct path access; will require OneDrive SDK or iOS document
    picker to grant access. Treat as a known design challenge for the Swift phase.
  - On desktop (WPA or Windows), both iCloud-synced and OneDrive paths are directly accessible
  - Filter criteria will likely drive new fields or flags in the tune data schema —
    coordinate with Tune Hub when designing

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
| `_shared/schema/icloud-structure.json` | Canonical definition of the iCloud folder structure. Tune Hub reads this on first run to bootstrap the container. The PowerShell setup script also reads it. One source of truth. |
| **iCloud container** | Runtime home for `tunehub.db`, published snapshots, inbox notes, media annotations |
| **OneDrive** | Large media files (video/audio recordings); referenced by path in annotation JSON |

---

*Last updated: 2026-03-28*
