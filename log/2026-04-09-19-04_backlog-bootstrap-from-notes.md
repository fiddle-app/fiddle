# 202604-1904 Backlog Bootstrap from Research Notes

**2026-04-09**

## What was done

Bootstrapped the full backlog system for the fiddle app family by mining `research/organized_notes.md` for actionable items and distributing them to the appropriate child backlogs.

### Source material

`research/organized_notes.md` — compiled from two earlier note-taking sessions:
- `FiddleAppsNotes.md` (2026-03-30)
- `MM and TuneHub notes.md` (2026-04-02)

The file contained a mix of architecture decisions (already settled), background context, open questions, and discrete feature ideas. The task was to extract the latter two categories into the backlog system and mark them as processed in the source file.

---

### Backlog system documentation

Added a **Backlog System** section to `fiddle/CLAUDE.md` covering:
- Barry (backlog-manager skill) as the tool for cleanup and management
- Current backlog locations across all apps
- How to add loose items (just append plain lines; Barry cleans up)
- Note that TuneHub, MM, TuneList, Intonio, and MicroBreaker didn't have child backlogs yet at that point

---

### Item extraction

Walked the organized notes section by section and identified items that were clearly "to-do" rather than settled architecture. Added 27 loose items to `fiddle/backlog.md`, tagged by app in brackets: `[TuneHub]`, `[MM]`, `[TuneList]`, `[Intonio]`, `[Larry]`. Family-level items (no tag) covered cross-cutting concerns:
- Play button / transport control styling
- Cloud file storage abstraction research (can the storage layer work across iCloud, OneDrive, Google Drive?)
- SQLite conflict resolution for offline-edit scenarios
- Cross-device sync confidence file pattern
- SQLite locking mechanism

All captured items were struck through in `organized_notes.md` using `~~...~~`. Architectural context and already-settled decisions were left intact — the file remains a useful reference, just with the action items visibly extracted.

Notable judgment calls:
- The ear-tuner copy-report item was already in that backlog as D1; no duplicate added.
- Larry items stayed in the parent backlog since there's no minion backlog.
- Long descriptive blocks (e.g. the MM hierarchical structure section) were struck through at the feature level, not the entire section, so the design narrative remains readable.

---

### Child backlog initialization

Used Barry to initialize child backlogs for all apps that didn't have them: **tune-hub, tune-list, media-markup, microbreaker**. ear-tuner already had one.

Then moved the app-tagged items out of the parent and into their respective child backlogs:
- 9 items → `tune-hub/backlog.md`
- 5 items → `media-markup/backlog.md`
- 6 items → `tune-list/backlog.md`
- 1 item → `intonio/backlog.md`

Family-level items and the Larry item stayed in the parent.

---

### Intonio folder

The `intonio/` app folder didn't exist yet. Created it manually and wrote the three backlog files (`backlog.md`, `backlog-done.md`, `backlog-meta.json`) by hand to match the pattern of the other child apps (prefix `I`, full sibling table).

One wrinkle: Barry's first pass (before the folder existed) had dropped an empty backlog into `minions/intonio/` — confusing it with the minion context. That was removed before the parent commit.

---

### Barry cleanup

Ran Barry cleanup across all 7 backlogs at once. He assigned IDs, defaulted unspecified items to P2, and sorted by priority/status. Result:

| Backlog | New items | IDs assigned |
|---------|-----------|--------------|
| fiddle (parent) | 6 loose | D1, P2–P3, C1–C2, H3 |
| tune-hub | 9 loose | P1–P3, C1–C6 |
| media-markup | 5 loose | C1–C4, X1 |
| tune-list | 6 loose | C1–C6 |
| intonio | 1 loose | C1 |
| ear-tuner | 0 | (already clean) |
| microbreaker | 0 | (empty) |

---

### Commits and pushes

Committed and pushed all repos. Commit order: child repos first, then parent (so submodule SHAs update correctly).

- **tune-hub, tune-list, media-markup, microbreaker**: new backlog files
- **_shared**: line ending normalization only (LF→CRLF, pre-existing divergence)
- **intonio**: new GitHub repo created (`fiddle-app/intonio`, private), git initialized, pushed; then registered as submodule in parent via `git submodule add --force`
- **fiddle (parent)**: `.gitmodules` updated, submodule SHAs updated, backlog and CLAUDE.md committed, research notes committed
