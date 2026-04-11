# Fiddle App Family — Umbrella Claude Context

This file is read by Claude Code in every project session under this folder.
It provides shared context that all apps inherit. Do not duplicate this in project-level CLAUDE.md files.

**Key documents:**
- [APPS.md](APPS.md) — app registry, folder structure, data flow
- [architecture.md](architecture.md) — architecture, technology stack, development workflow, testing strategy

---

## About the Developer

Casey Mullen — retired software engineer (C#, C++), experienced with VSCode, command line (PowerShell),
Git/GitHub, XML/JSON. Also an Old Time fiddler of 12 years. These apps are built for Casey's personal
fiddle practice workflow and eventually for public release. Casey wants brief explanations of new
technologies when relevant, but not verbose walkthroughs.

---

## Project Overview

A family of web apps (WPAs, Progressive Web Apps) supporting fiddle learning and practice.
All apps share a consistent look, feel, and data architecture.
GitHub organization: `fiddle-app`
Primary development machine: Windows desktop PC
Primary languages: JavaScript (WPA phase), Swift (future native iOS/iPadOS phase)

See `APPS.md` in this folder for the full app registry, data flow, and folder structure.

---

## Folder Structure

```
Projects/fiddle/
├── _shared/       → shared design tokens, assets, schemas (repo: fiddle-app/_shared)
├── minions/       → Claude agents ("minions") that perform specialized tasks
│   └── larry/     → tune researcher agent (Slippery Hill lookup, tune.md drafting)
├── tune-hub/      → repo: fiddle-app/tune-hub
├── tune-list/     → repo: fiddle-app/tune-list
├── media-markup/  → repo: fiddle-app/media-markup
├── microbreaker/  → repo: fiddle-app/microbreaker
└── ear-tuner/     → repo: fiddle-app/ear-tuner
```

---

## Shared Data Architecture

### Source of Truth
- SQLite database: `tunehub.db` in iCloud Drive (see below)
- Owned exclusively by Tune Hub. No other app writes to it directly.

### iCloud Container: `iCloud Drive\FiddleApp\`
```
FiddleApp/
├── tunehub.db                      ← SQLite SSOT; Tune Hub only
├── published/
│   ├── tune-index.md               ← all tunes by key, alphabetical, with links
│   ├── tunes/                      ← one .md per tune (human-editable, Claude-queryable)
│   │   └── <tune-name>.md
│   └── data/                       ← JSON snapshots for app consumption
│       ├── all-tunes.json
│       ├── tunes/
│       └── lists/
├── inbox/                          ← Tune List writes here; Tune Hub ingests
│   └── jam-notes-YYYY-MM-DD.json
├── media-annotations/              ← Music Markup writes here; Tune Hub reads
│   └── <media-filename>.json
└── media/                          ← audio/video samples; Larry downloads here
```

### OneDrive
Large media files (Zoom lesson recordings, practice audio/video) stay in OneDrive.
Music Markup opens them via the browser File System Access API file picker.
Media file paths are stored as references in annotation JSON — never embedded.

### Data Flow Summary
- Tune Hub → writes tunehub.db, publishes tunes/*.md and data/*.json
- Tune List → reads published/data/**, writes inbox/jam-notes-*.json
- Music Markup → reads/writes media-annotations/*.json
- Tune Hub → reads inbox/ and media-annotations/ to update SSOT
- Claude / agents → read/write published/tunes/*.md (two-way sync back to SSOT via Tune Hub review)

---

## Per-Tune Markdown Format

Each tune in `published/tunes/` follows this structure.
YAML frontmatter = machine-parseable. Sections = human-editable.
Tune Hub diffs edits and promotes changes to SQLite after Casey's review.

```markdown
---
id: <integer>
name: <string>
key: <A | D | E | G | ...>
mode: <major | mixolydian | dorian | minor | modal | ...>  # "modal" is valid OT catch-all
style: <breakdown | reel | waltz | jig | ...>
tuning: <GDAE | GDAD | AEAE | ADAE | ...>   # omit if default for this key (see below)
status: <canLead | learningToLead | learnSoon | learnSomeday | aware>
slipperyHill: <URL>                              # canonical Slippery Hill page
alternateNames:                                  # other names for this tune
  - name: <string>
    slipperyHill: <URL | null>                   # SH page for this alternate name, if one exists
last-updated: <YYYY-MM-DD>
---

## Notes

## Start Hints

## Structure

## Variants

## Media
```

### Tonality (key + mode combined)

`key` and `mode` are stored as separate fields for filtering, but displayed together
as **"Tonality"** in the UI. This is the right term for the combination of tonal center
and modal character (e.g., "A Mixolydian", "D Dorian", "G Major").

OT-friendly display rules:
- `key: A, mode: major` → display as **"A"** (major is implied for A tunes in OT)
- `key: A, mode: mixolydian` → display as **"A Mixolydian"**
- `key: A, mode: modal` → display as **"A Modal"** (catch-all; use when mode is unclear)
- `key: D, mode: dorian` → display as **"D Dorian"**
- All other cases → `"${key} ${mode}"` with mode capitalized

`modal` is a valid mode value in OT context — it means "not major, and the specific mode
is ambiguous or unconfirmed, but likely mixolydian, dorian, or aeolian."
More precise values are preferred when known; `modal` is the right choice when you know
the tune isn't major but aren't sure (or don't care) which modal flavor it is.

### Default Tunings by Key

Only store `tuning` in the frontmatter when it differs from the key's default.
Larry should omit the field when the tune uses its key's standard tuning.

| Key | Default tuning |
|-----|---------------|
| G   | GDAE |
| C   | GDAE |
| A   | AEAE |
| D   | ADAE |
| Other | confirm from Slippery Hill |

---

## Shared Design System

All apps use the same design tokens, fonts, icons, and sounds defined in `_shared/`.
Before writing any UI code, check `_shared/design/` for:
- Color palette and CSS variables
- Typography scale
- Icon set
- Sound files (if applicable)

When adding new design elements, add them to `_shared/` first, don't define them inline in an app.

---

## Coding Conventions

- JavaScript (ES modules) for WPA phase; no frameworks unless justified
- Prefer vanilla JS + Web APIs over libraries where feasible, to keep apps lightweight
- SQLite WASM is used only in Tune Hub — do not add it to other apps
- Other apps read from published JSON snapshots, never from tunehub.db directly
- File System Access API for any local file reading/writing on desktop
- Web Share API for iOS export from Tune List (PWA phase)
- Each app is its own GitHub repo under the `fiddle-app` account
- Commit messages should be descriptive; no --no-verify bypasses

---

## WPA → Swift Portability

All apps (except Tune Hub) start as WPAs but are planned for native iOS/iPadOS ports.
The goal is translation at porting time, not a rewrite. Code accordingly.

### Platform Adapter Layer
Web-only APIs — File System Access, Web Share, localStorage, IndexedDB — must never appear
in business logic. Wrap them in a thin adapter (e.g. `StorageAdapter`) with methods like
`readTuneList()` or `writeJamNotes()`. The WPA version implements those with browser APIs;
the Swift version implements the same interface with iCloud/FileManager calls. Core logic
never touches the platform directly.

### JSON Schema Design
Design all schemas with Swift's `Codable` in mind:
- Every field has a single, consistent type — no field that's sometimes a string, sometimes an array
- Nullable/optional fields are consistently marked and always present (even if null)
- Use camelCase keys (maps directly to Swift property names with `Codable`)
- If schemas are clean, Swift `Codable` conformance is nearly automatic

### State and Event Patterns
Avoid scattered `addEventListener` calls in business logic — they don't map to Swift.
Use an explicit observer/callback pattern instead: a store notifies registered listeners when
state changes. This maps cleanly to SwiftUI's `ObservableObject` / `@Published`.

### Module Structure
One module = one clear responsibility. Each JS file should be portable as a unit —
a `TuneStore`, a `JamNoteBuilder`, etc. If logic is tangled or mixed with DOM code,
porting becomes a rewrite instead of a translation.

### Style
- Use camelCase throughout (matches Swift)
- Use ES module classes with constructor + methods — maps directly to Swift structs/classes
- Avoid JS-specific idioms in business logic: no prototypal inheritance tricks, no `arguments`
  object, no `this`-binding gymnastics

### What Doesn't Port (and That's Fine)
The UI layer (HTML, CSS, DOM manipulation) gets thrown away at porting time — that's expected.
Design tokens in `_shared/design/` will be re-implemented as Swift Color extensions.
No need to make the CSS layer portable; just keep it well-organized so you know what to rebuild.

---

## Backlog System

Backlogs are managed by the **backlog-manager skill** (also called "Barry"). The system is documented in `backlog-readme.md` at this folder's root.

Current backlog locations:
- `fiddle/backlog.md` — parent (family-level) backlog
- `fiddle/ear-tuner/backlog.md` — Ear Tuner child backlog
- TuneHub, Media Markup, TuneList, Intonio, MicroBreaker do not have child backlogs yet

To add a loose item, just append a plain line to the relevant `backlog.md`. The skill will assign IDs, sort, and format on the next cleanup. Item type prefix: B=Bug, C=Coding, D=Design, H=Human, P=Planning, T=Testing, X=Cross-project.

The "cleanup backlog" skill is the backlog-manager skill (Barry).

---

## Licensing & Attribution

Apps will be publicly released, free, with a request for donations (Venmo).
License: requires attribution for derivative works (e.g. CC BY or similar open source license — TBD).
Always include Casey's attribution in generated code headers where appropriate.
