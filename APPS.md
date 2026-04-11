# Fiddle App Family — App Registry

This is the map of the fiddle-app ecosystem: what each app does, its platform, and how data flows between them. For architecture decisions, technology stack, and development process, see [architecture.md](architecture.md). For per-app details, see each app's own `CLAUDE.md`.

---

## Current Priority

**Design Review & Shared Resource Extraction.**
Migrate Microbreaker and Ear Tuner into their project folders, review their UI/UX together, and extract a canonical shared design system into `_shared/design/`.
All other app development waits until this is complete.

---

## App Registry

| App | Repo | Platform | Status | Purpose |
|---|---|---|---|---|
| Tune Hub | `tune-hub` | Electron (desktop) | Planned | SSOT editor; owns `tunehub.db` |
| Media Markup | `media-markup` | Electron → Capacitor (iPad) | Planned | Video/audio annotation for lesson recordings |
| Tune List | `tune-list` | Capacitor iOS (iPhone) | Planned | Jam companion; browse, filter, capture notes |
| Microbreaker | `microbreaker` | WPA → Capacitor iOS | Built; design review | Practice timer with micro-breaks |
| Ear Tuner | `ear-tuner` | WPA → Capacitor iOS | Built; design review | Ear training / pitch discrimination |
| Tune Player | `tune-player` | Native iOS (idea) | Idea | Playlist player for tune audio samples |

**Minions:**

| Agent | Folder | Purpose |
|---|---|---|
| Larry | `minions/larry/` | Tune researcher — Slippery Hill lookup, tune.md drafting |

See each app's folder for full details: `CLAUDE.md`, `research/`, `spec/`.

---

## Folder Structure

### Code (OneDrive, git-tracked, GitHub under `fiddle-app`)
```
fiddle/
├── CLAUDE.md              ← umbrella context
├── APPS.md                ← this file (registry + data flow)
├── architecture.md        ← architecture & implementation strategy
├── research/              ← active research topics
├── _shared/               ← design tokens, assets, schemas
├── minions/larry/         ← tune researcher agent
├── tune-hub/
├── tune-list/
├── media-markup/
├── microbreaker/
└── ear-tuner/
```

### Runtime Data (iCloud Drive)
```
iCloud Drive/FiddleApp/
├── tunehub.db             ← SQLite SSOT; Tune Hub owns
├── media-markup.db        ← SQLite; Media Markup owns
├── published/
│   ├── tune-index.md
│   └── tunes/*.md         ← Obsidian-compatible tune vault
└── inbox/                 ← TuneList and MM write here; Tune Hub ingests
    └── jam-notes-YYYY-MM-DD.json
```

### Media Files (OneDrive)
Large media files (Zoom recordings, practice audio/video) stay in OneDrive. Media Markup references them by path.

---

## Data Flow

```
Tune Hub (Electron) ──writes──▶ tunehub.db (SSOT)
                    ──publishes──▶ published/tunes/*.md
                    ──reads──▶    published/tunes/*.md    (two-way sync)
Tune List (iPhone)  ──reads──▶ tunehub.db (read-only, App Group)
                    ──writes──▶ inbox/*.json ──▶ Tune Hub
Media Markup        ──reads/writes──▶ media-markup.db
                    ──attaches──▶ tunehub.db (read-only)
                    ──writes──▶ inbox/*.json ──▶ Tune Hub
Tune Hub            ──attaches──▶ media-markup.db (read-only)
```

All cross-app writes go through the inbox pattern. No app writes to a database it doesn't own.

---

## Backlog / Ideas

- **Tune Flashcards** — Drill the opening phrase of tunes cold; tests ability to start confidently
- **Lesson Tracker** — Link lesson recordings (via Media Markup) to tunes worked on; may be a Tune Hub view rather than a standalone app

*"Jam Helper" and "Session Logger" are not separate apps — that functionality lives in Tune List.*

---

*Last updated: 2026-04-11*
