# Fiddle App Family — Backlog

<details>
<summary>Prefixes (for referencing items in other backlogs)</summary>

| Prefix | Project |
|--------|---------|
| P | Fiddle App Family (parent) |
| B | MicroBreaker |
| E | Ear Tuner |
| H | TuneHub |
| I | Intonio |
| L | TuneList |
| M | Media Markup |

</details>

| ID | P  | S | Description | Notes |
|----|-----|---|-------------|-------|
| H1 | P2 | . | Disambiguate OBCCCAR in lessons. Use as one source of original tune SSOT and media SSOT. |  |
| H2 | P2 | . | Clean up OneNote tune list and organize by status |  |
| P1 | P2 | . | Determine the correct list of tune status values. Clean up OneNote lists with correct status: lead, learning, want to, aware. |  |
| D1 | P2 | . | Revisit play/transport button styling � larger play triangle; consider shaded background on back/skip buttons |  |
| P2 | P2 | . | Research cloud file storage abstraction � can the storage layer be abstracted to work with iCloud, OneDrive, and Google Drive interchangeably? |  |
| P3 | P2 | . | Think through SQLite conflict resolution: offline edits on device A before device B syncs (e.g., edit on airplane, then desktop opens before iPad sync catches up) |  |
| C1 | P2 | . | Implement cross-device sync confidence file � lightweight JSON (timestamp + checksum) written on every save; peer app warns on launch if local file doesn't match |  |
| C2 | P2 | . | Implement SQLite locking � lock record contains app/person/date-time/device; UI to view and break another app's lock |  |
| H3 | P2 | . | [Larry] Implement import parsing rules: L: (lyrics), ! (want-to-learn), [tuning], W: (person association) |  |
| P4 | P1 | . | Research bundling strategy (no bundler vs esbuild) | [research/bundling-strategy.md](research/bundling-strategy.md) |
| P5 | P1 | . | Research iCloud + SQLite sync safety — concurrent writes, corruption risk, detection strategy | [research/icloud-sqlite-sync-safety.md](research/icloud-sqlite-sync-safety.md) |
| P6 | P2 | . | Research Electron boilerplate/shared template — evaluate Gemini's security template, decide template donor app | [research/electron-boilerplate-template.md](research/electron-boilerplate-template.md) |
| P7 | P2 | . | Decide spec file naming convention — architecture-area prefixes for `specs/` folders | [research/spec-naming-convention.md](research/spec-naming-convention.md) |
| P8 | P2 | . | Build the `/retro-spec` skill |  |
| P9 | P2 | . | Research Electron packaging and distribution strategy (.exe builds, auto-update, code signing) | [research/electron-packaging.md](research/electron-packaging.md) |
| P10 | P1 | . | Move Per-Tune Markdown Format from CLAUDE.md into tune-hub/spec/ | See [architecture.md §4](architecture.md#4-data-architecture) |
| C3 | P1 | . | Define tunehub.db backend schema (tables, columns, types, constraints, schema_version) | Unblocks all Group 2 apps. Group 1. |
| C4 | P1 | . | [Larry & TuneHub] Define canonical .md formatting for tune files (ingestion and publishing) | Group 1 |
| C5 | P1 | . | [Larry] Define ingestion formats (may vary by source) | Group 1 |
| C6 | P1 | . | [Larry] Research effective data gathering from Slippery Hill and other sources | Group 1 |
| C7 | P1 | . | Port existing Ear Tuner WPA code into project folder; extract design standards into _shared/design/ | Group 1. Cleanup [architecture.md §5](architecture.md#5-shared-design-system) when done. |
| C8 | P1 | . | Port existing Microbreaker WPA code into project folder; extract design standards into _shared/design/ | Group 1. Cleanup [architecture.md §5](architecture.md#5-shared-design-system) when done. |
| C9 | P2 | . | Port Ear Tuner to standard Electron architecture | Group 2 |
| C10 | P2 | . | Port Microbreaker to standard Electron architecture | Group 2 |
| C11 | P2 | . | Build Media Markup desktop (Electron) version | Group 2 |
| C12 | P2 | . | Build Tune Hub app with UI | Group 2 |
| C13 | P2 | . | Build Tune List (Capacitor iPhone target) | Group 2 |
| C14 | P3 | . | Build Media Markup iPad (Capacitor) version | Group 3 |
| C15 | P3 | . | Wrap Ear Tuner as Capacitor iPhone/iPad app | Group 3 |
| C16 | P3 | . | Wrap Microbreaker as Capacitor iPhone/iPad app | Group 3 |

