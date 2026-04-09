# Fiddle App Family â€” Backlog

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
| D1 | P2 | . | Revisit play/transport button styling — larger play triangle; consider shaded background on back/skip buttons |  |
| P2 | P2 | . | Research cloud file storage abstraction — can the storage layer be abstracted to work with iCloud, OneDrive, and Google Drive interchangeably? |  |
| P3 | P2 | . | Think through SQLite conflict resolution: offline edits on device A before device B syncs (e.g., edit on airplane, then desktop opens before iPad sync catches up) |  |
| C1 | P2 | . | Implement cross-device sync confidence file — lightweight JSON (timestamp + checksum) written on every save; peer app warns on launch if local file doesn't match |  |
| C2 | P2 | . | Implement SQLite locking — lock record contains app/person/date-time/device; UI to view and break another app's lock |  |
| H3 | P2 | . | [Larry] Implement import parsing rules: L: (lyrics), ! (want-to-learn), [tuning], W: (person association) |  |

