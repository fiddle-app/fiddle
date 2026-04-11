## Architecture — SQLite + iCloud

### Database Strategy
- **SQLite as source of truth**, human-readable flat files as shadows
- Each app owns its own DB file:
  - `tunehub.db` — owned by TuneHub
  - `mm.db` — owned by Media Markup
- SQLite `ATTACH DATABASE` used for cross-app read-only joins:
  ```sql
  SELECT t.tune_name, m.segment_label
  FROM tunehub.tunes t
  JOIN mm.segments m ON m.tune_id = t.id
  ```
- Read-only attachment is safe with the other app having the file open

### iCloud Sync
- Both DB files live in iCloud Drive, sync independently
- Single user = no simultaneous edit risk; discipline of closing app on
  one device before opening on another is sufficient
- **Companion file pattern** for sync confidence: app writes a lightweight
  `mm_sync.json` after every save containing timestamp + version/checksum;
  iPad app reads this on launch and warns if it doesn't match local DB
- Shadow WebVTT/MD files provide additional recovery option if DB is
  corrupted in a sync mishap

### Cross-App Read Pattern
- TuneList reads TuneHub DB read-only (attaches it)
- TuneList never writes to TuneHub DB directly
- New tune data and comments from TuneList submitted as **JSON files to a
  TuneHub inbox folder**; TuneHub processes inbox to update its DB