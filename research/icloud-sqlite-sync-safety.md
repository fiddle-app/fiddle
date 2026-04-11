# iCloud + SQLite Sync Safety

> [!todo] When resolved, update [architecture.md Section 4](../architecture.md#4-data-architecture) and remove the open question callout.

## The Problem

SQLite databases stored in iCloud Drive are synced as opaque files. iCloud doesn't understand SQLite's internal structure — it just sees a file that changed. This creates risks:

### Known Risks
- **Concurrent writes from different devices** could produce conflicting versions of the database file. iCloud resolves file conflicts by keeping both copies (appending a suffix), but SQLite can't merge two divergent databases automatically.
- **WAL mode complication:** SQLite WAL mode uses separate `-wal` and `-shm` files. iCloud may sync the main `.db` file but not the WAL file (or sync them out of order), potentially corrupting the database on the receiving device.
- **Partial sync:** If iCloud syncs a partially-written database file, the result is corruption.

### Our Situation
- Single user (Casey), multiple devices (Windows desktop, iPad)
- Each database has exactly one owning app (TuneHub owns tunehub.db, MM owns media-markup.db)
- Multiple apps may *read* a database simultaneously, but only the owner *writes*
- The same owning app may be open on two devices (e.g., MM on desktop and MM on iPad)

### Current Mitigation (Discipline-Based)
Close the app on one device before opening it on another. This avoids concurrent writes. Relies on human discipline.

## Research Questions

> [!question] Can we detect a competing writer?
> Possible approach: when an app opens a database for writing, it records a "session" row (device ID, timestamp, PID). Before writing, it checks whether another session is active. If so, it stays read-only and warns the user. Need to research: does this work reliably across iCloud sync latency?

A: 

> [!question] WAL mode + iCloud: safe or not?
> Apple's documentation has historically warned against SQLite over iCloud. Has this improved? Are there recommended patterns (e.g., checkpoint before close, disable WAL for synced databases)? Need to check current Apple developer documentation and community experience.

A: 

> [!question] Should we use Apple's recommended alternatives?
> Apple recommends CloudKit or Core Data with CloudKit sync for structured data. These are Swift/iOS-only and don't work on Windows/Electron. But for the iOS-only apps (TuneList), is there a better pattern than raw SQLite over iCloud?

A: 

> [!question] Companion file pattern
> An earlier idea (struck through in organized-notes.md) proposed a lightweight `sync.json` written after every save, containing a timestamp and checksum. The receiving app checks this on launch and warns if it doesn't match the local database. Is this worth reviving as a safety net?

A: 

## Next Steps

- Research current Apple documentation on SQLite + iCloud Drive
- Look at community experience (Stack Overflow, Apple Developer Forums) for recent reports
- Evaluate the "session row" competing-writer detection approach
- Decide whether WAL mode should be disabled for synced databases
- Prototype the detection approach in a test database
