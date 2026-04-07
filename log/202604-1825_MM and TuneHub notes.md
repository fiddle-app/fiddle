# Media Markup & Fiddle App Architecture Notes
## Session Summary — April 2, 2026

## Video Annotation Format Research

### Standard Caption Formats
- **SRT** — simplest, plain text, just sequence number + timestamp + text
- **WebVTT (.vtt)** — web standard, HTML5 native, supports named cue IDs,
  overlapping cues, and non-standard key-value metadata; best choice for
  shadow format
- **TTML/DFXP** — XML-based, broadcast/streaming use, too verbose for our
  purposes
- **YTT** — YouTube's proprietary XML format; YouTube *accepts* WebVTT on
  upload and converts it, so WebVTT shadow files would work for unlisted
  YouTube videos with chapter navigation

### No Music-Specific Standard Exists
- Score-based tools (Flat for Education, etc.) are notation-focused, not
  video annotation
- **ELAN (.eaf)** — XML-based linguistics research tool with multi-tier
  time-aligned annotation; closest to what MM needs conceptually, but wrong
  audience and UI
- No existing format targets "fiddle teacher reviewing a recorded Zoom lesson"

---

## Media Markup (MM) — Design Decisions

### Shadow Format Strategy
- **Primary format**: JSON (rich, typed, linked to TuneHub)
- **Shadow format**: WebVTT (.vtt) — human-readable, player-compatible,
  plain text, survives without any software
- App writes both on every save; app never *reads* WebVTT back

### WebVTT Design Choices
- Gaps between cues = implicitly skipped (no need to mark skip segments
  explicitly in shadow file)
- Speed and volume metadata go *inside* the cue text, not after the arrow,
  for maximum readability and longevity:
  ```
  segment-001
  00:04:30.000 --> 00:12:00.000
  [speed:0.75] Blackberry Blossom - first pass
  ```
- High-level tune spans (e.g. "Rose in the Mountain" covering 0–40 min)
  stored as short TOC cues in the first few seconds of the file, avoiding
  overlapping cue complications with generic players:
  ```
  toc-01
  00:00:00.000 --> 00:00:01.000
  [tune:Rose in the Mountain] [span:00:00:00-00:40:00]
  ```
- TOC cues are metadata only; app suppresses them during playback

### Segment Model
- Segments are **sparse**, not contiguous — only "keep" segments are
  listed; gaps are skipped
- Overlapping cues are valid WebVTT but confuse most players; use TOC
  header block pattern instead
- WebVTT supports named cue IDs — use descriptive IDs for human readability

---

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

---

## Fiddle App Family — Full Inventory

| App | Status | Purpose |
|-----|--------|---------|
| **Practice Timer** | Built | Structured practice sessions with timed work/break intervals |
| **Ear Tuner** | Built | Pitch discrimination game; two violin tones, identify higher/lower; difficulty adapts |
| **Intonio** (Intonation Monitor) | Built/In Progress | Real-time polyphonic pitch detection via microphone; scrolling pitch history |
| **TuneHub** | Planned | Core tune knowledge repository; central DB used by other apps |
| **Media Markup (MM)** | Planned | Video annotation for Rhys lesson recordings; segments, speed, volume, skip |
| **TuneList** | Planned | Jam session companion; reads TuneHub DB, filters by key, voice input, audio capture |

---

## TuneList — Key Design Notes
- Must work **fully offline** (jam venues have unreliable signal)
- Key switching is infrequent (jams stay in one key for an hour+); but
  switching should be easy
- Primary friction point is **adding new tunes and notes quickly**
- Voice input via Web Speech API for notes (tap to activate, speak, review,
  submit)
- **Audio recording workflow**: hear unknown tune → record → tune ends →
  add title → submit audio + metadata JSON to TuneHub inbox. Assume the tune is in the currently active key.  use key-to-tuning rules to suggest tuning
- primary state is the current key, but secondary state is current tuning.  
- tuning on displays fortunes that match the current key, but not the current tuning.
– there will be a toggle to filter by the current tuning, or show all tunings
- All UI must be operable **one-handed** (bow in the other hand); large
  tap targets, minimal typing
- the main working screen
   - shows the key prominently at the top, with the tuning just to the side of it, and a filter toggle just to the right of that. click the key or the tuning in order to change it.
   - to the right of that a filter buttons for different tunes status, for example, can start, etc.
   - then show a list of tunes.
     - clicking on a tune brings up detailed information about that tune from TuneHub, you can also add notes. there is also a record button to record audio related to that tune. It might just be voice notes or it might be a recording of playing the tune.
     - hold tap on the tune to enter note-taking directly
     - there is a plus button somewhere to the right of the tune that adds it to the list of tunes that were played in the current jam. When you hit that button, it opens a dialogue for adding notes such as who led the tune. There's a handy button for closing that dialogue even if you don't add notes about the tune.
   - At the bottom are controls, including a big + to add a new tune, as well as a record button to record some audio immediately without First asking questions about tune name, etc.
   - there is also a button to end the jam, which will take you back to the starting screen.
   - there will be a button to display the in progress. List of tunes played at the jam. From this display, you can rearrange the tunes in the list in case you added them out of order.
- JSON inbox files accumulate locally offline, sync to iCloud when signal
  returns

when you start the app, the first thing to do is to establish the current jam. You see a list of recent jams. If you click one of them, then you are making that jam be active. In any changes in notes will be in the context of that jam.
There will also be a prominent button to create a new jam that will be pre-populated with the time in location data from GPS displaying a town name. These are can add a more specific name, or select from a list of recurring jams.  One of the jams is called "not a jam "or "just looking ". You can click that one to view the tune list and added to turn lists in the context of a "jam quote that is not really a jam.

One workflow is to click on an old jam, and then at the bottom click the button that brings up the "tunes played" list from the jam. We will just call this the "played list"".

The plate list has a button at the top to copy to the clipboard, which will copy the list to the clipboard in a format that will work well when pasted into an email.


---

## Longevity / Data Robustness Principles
- SQLite = source of truth (queryable, portable, widely supported)
- WebVTT shadows = interoperable, plain text, readable in Notepad
- MD shadows = human narrative, readable without any software
- No proprietary binary formats; everything has a plain-text projection
- Aim: data remains useful even if none of the apps can be maintained
