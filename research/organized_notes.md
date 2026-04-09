# Fiddle Apps — Organized Notes

*Sources: FiddleAppsNotes.md (2026-03-30), MM and TuneHub notes.md (2026-04-02)*

---

## Unsure


---

## Fiddle Apps Family

### App Priority (2026-03-30)

Most useful:
1. MM
2. TuneList
3. TuneHub

### Common UI/UX

- ~~Use play buttons from YouTube? Or just skip and back? They already are. Maybe just make play triangle larger? Consider shading in background of back and skip.~~

### App Inventory (2026-04-02)

| App | Status | Purpose |
|-----|--------|---------|
| Practice Timer | Built | Structured practice sessions with timed work/break intervals |
| Ear Tuner | Built | Pitch discrimination game; two violin tones, identify higher/lower; difficulty adapts |
| Intonio (Intonation Monitor) | Built/In Progress | Real-time polyphonic pitch detection via microphone; scrolling pitch history |
| TuneHub | Planned | Core tune knowledge repository; central DB used by other apps |
| Media Markup (MM) | Planned | Video annotation for Rhys lesson recordings; segments, speed, volume, skip |
| TuneList | Planned | Jam session companion; reads TuneHub DB, filters by key, voice input, audio capture |

### Architecture — SQLite + iCloud

#### Database Strategy
- SQLite as source of truth, human-readable flat files as shadows
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
- The two dbs attach each other.
- ~~Q: could the cloud file system be abstracted (could be used with OneDrive or Google Drive or iCloud). Are they similar enough?~~
  - A: See [cloud-storage-abstraction.md](cloud-storage-abstraction.md).

#### iCloud Sync
- Both DB files live in iCloud Drive, sync independently
- Single user = no simultaneous edit risk; discipline of closing app on one device before opening on another is sufficient
- ~~**Companion file pattern** for sync confidence: app writes a lightweight `mm_sync.json` after every save containing timestamp + version/checksum; iPad app reads this on launch and warns if it doesn't match local DB~~
- Shadow WebVTT/MD files provide additional recovery option if DB is corrupted in a sync mishap
- ~~Can two parties edit different copies of the db via iCloud? If so, which one wins? Have Claude think it through. Use case of editing on airplane. Then edit on desktop before the iPad syncs.~~

#### Locking
- Desktop WPA can open SQLite directly. iPad could also open SQLite, once it gets the file, but locking for conflicts seems problematic.
- ~~Check for lock data. Have ability to break another app's lock. Lock will include App-person-date-time-device.~~

#### Cross-App Read Pattern
- TuneList reads TuneHub DB read-only (attaches it)
- TuneList never writes to TuneHub DB directly
- New tune data and comments from TuneList submitted as JSON files to a TuneHub inbox folder; TuneHub processes inbox to update its DB

### Data Robustness / Longevity Principles
- SQLite = source of truth (queryable, portable, widely supported)
- WebVTT shadows = interoperable, plain text, readable in Notepad
- MD shadows = human narrative, readable without any software
- No proprietary binary formats; everything has a plain-text projection
- Aim: data remains useful even if none of the apps can be maintained
- Always generate a Md view of everything with enough data to rebuild the TuneHub.db. We can bootstrap the project by building out all of the information in md.

### Video Annotation Format Research

#### Standard Caption Formats
- **SRT** — simplest, plain text, just sequence number + timestamp + text
- **WebVTT (.vtt)** — web standard, HTML5 native, supports named cue IDs, overlapping cues, and non-standard key-value metadata; best choice for shadow format
- **TTML/DFXP** — XML-based, broadcast/streaming use, too verbose for our purposes
- **YTT** — YouTube's proprietary XML format; YouTube *accepts* WebVTT on upload and converts it, so WebVTT shadow files would work for unlisted YouTube videos with chapter navigation

#### No Music-Specific Standard Exists
- Score-based tools (Flat for Education, etc.) are notation-focused, not video annotation
- **ELAN (.eaf)** — XML-based linguistics research tool with multi-tier time-aligned annotation; closest to what MM needs conceptually, but wrong audience and UI
- No existing format targets "fiddle teacher reviewing a recorded Zoom lesson"

---

## TuneHub

### Data / Fields

- Tune meta-data:
  - Checked against Slippery Hill yet?
  - ~~IsTopic — not really a tune~~

- ~~The key of T is a topic, like intonation or rhythm.~~

- What about images in tune pages?

- Q: Certain portions of tune data should be persisted and displayed as Md even in TuneHub?

- TH cleans up display and editing of discrete fields, but "notes on how-to-play" are mostly Md?

- ~~TH has 3 categories of notes:~~
  - ~~Original/integrated/own~~
  - ~~Media-linked (maybe copied from caption, maybe tweaked. Remembers a start/end time and segmentID)~~
  - ~~Live comments from media. MM may mark some as private/hidden. Really this is just a view of segments. The tune only persists the mediaID.~~

- ~~Media-linked notes: Click a media-segment and "copy to notes". Have a "copied" checkmark to remember which have been copied.~~

- ~~Q: Should tuneID and mediaID be a friendly guid? 2026-03-23\_13-59-326. Ask advice. Want human readability with no collisions and no central management. 260323-1359-326. Or just search for a new integer? SQLite can manage integers. Lesson extraction cannot figure out a tune id. It just sends new tune requests and new media requests to the TuneHub inbox. TuneHub reconciles and generates the SSOT ids and Md.~~

- TH needs to be SSOT for media, because most media will not have markup.

### People / Sources

- ~~TH will have a table of sources and their aliases, e.g. Clyde, Snake, Tommy, Nokosee.~~
- ~~Have a People table with aliases. Maddie, Christy, Rhys, Ryck~~
- Maybe have a whole section that is about people. Notes about people gathered through the tune list app.

### Status / Confidence

- "Can start/lead"
- ~~Need a status for "can lead but not start" or maybe that is just "Learn to start"~~

### Research Feature

- ~~Have a "research" button that will proactively find information about a tune, including YouTube videos and sheet music and ABC. Can a WPA call Claude? Maybe it just generates a prompt and user must paste it. The prompt can cause the AI to send results to the inbox.~~

### Workflows

~~Workflow — Add a lesson recording:~~
~~1. Save zoom~~
~~2. Drag it to TuneHub~~
~~3. TuneHub suggests tune associations based on the zoom filename~~
~~4. User may need to disambiguate tune names or add new tune or topic~~

~~Workflow — Add downloaded audio/video:~~
~~1. Download video or find a mp3~~
~~2. Drag it to a tune. Adds it to Media table and makes the association~~

~~Maybe from TH you can "add YouTube video" and it will call command line to download it.~~

---

## Media Markup (MM)

### Tune Structure Markup

- ~~MM can detect BPM and suggest snap boundaries at beat and half-beat intervals~~
- ~~Allow user to "tap along" to establish beats~~

- ~~Have a separate "structure" layer, or "tune" segments. A group of hierarchical segments that span:~~
  ~~1. Whole tune~~
  ~~2. Reps~~
  ~~3. Section~~
  ~~4. Part~~
  ~~5. Phrase~~

- ~~Can export a tune… just audio or also video~~

- We may know how many parts are in a tune and how many times they repeat.

- ~~User say: map a tune. User taps along to the beat for the entire tune. Hits enter at end. Tap different keys to indicate the end of a part. Trims "beats" off the end. Fine-tweaks ends. Identifies a part, labels it. Auto-guess phrases. Manually correct them. Start with positional names in curly brackets until given real names. Auto-Find next part… based on the first. Tweak the selection of beats. Fine-tune boundaries. Select two parts and create a section. Auto detect next section. … Pick two or 3 sections and create a Rep. Auto-detect the rest of the tune. When we name phrases, auto propagate to like-named parts.~~

- In playback, you can select at any granularity in the hierarchy to play. A special mode to compare a phrase to other phrases in the same relative position.

- Exports tune structure markup.

- ~~Support chords in the markup:~~
  ```
  D… G.A. Bm… D.GA
  ```

- Alternative structure format:
  ```
  A x 2
  …. ….. …. ….. (or) 4 5 4 5
  C1 R1 C1 R2

  A1:
  ```
  You can then just replace beats with chords.

- Tune structure diagram: https://claude.ai/public/artifacts/1974dc00-74ef-4e66-a575-2009bdf2367c

### Shadow Format Strategy
- **Primary format**: JSON (rich, typed, linked to TuneHub)
- **Shadow format**: WebVTT (.vtt) — human-readable, player-compatible, plain text, survives without any software
- App writes both on every save; app never *reads* WebVTT back

### WebVTT Design Choices
- Gaps between cues = implicitly skipped (no need to mark skip segments explicitly in shadow file)
- Speed and volume metadata go *inside* the cue text, not after the arrow, for maximum readability and longevity:
  ```
  segment-001
  00:04:30.000 --> 00:12:00.000
  [speed:0.75] Blackberry Blossom - first pass
  ```
- High-level tune spans (e.g. "Rose in the Mountain" covering 0–40 min) stored as short TOC cues in the first few seconds of the file, avoiding overlapping cue complications with generic players:
  ```
  toc-01
  00:00:00.000 --> 00:00:01.000
  [tune:Rose in the Mountain] [span:00:00:00-00:40:00]
  ```
- TOC cues are metadata only; app suppresses them during playback

### Segment Model
- Segments are **sparse**, not contiguous — only "keep" segments are listed; gaps are skipped
- Overlapping cues are valid WebVTT but confuse most players; use TOC header block pattern instead
- WebVTT supports named cue IDs — use descriptive IDs for human readability
- ~~Also have the ability to create a singular "mark" like "start of example phrase"… this will avoid having to really segment everything… only segment when you need a new "caption". Marks within the time of a top-level segment will appear as children of that segment.~~

### Media Metadata Storage
- How will MM store/edit media metadata?
- MM creates local json with segment data. It could send it to inbox, but merge could be complex. Maybe start with live db connections, but MM holds lock for minimal time. It periodically checks to see if it is no longer the last editor. If so, it looks for changes to its in-memory data.
- Segment SSOT would be MediaMarkup.db
- Search in MM covers tune name and file name.

### iOS / Cross-Device
- MM on iOS may just wake up and suggest a list of recent media and new media (only show a small window of new media, top 3 is probably enough).
- It would probably be nice to do initial markup on the desktop or laptop, or at least have Claude or TuneHub create the initial media metadata and add tune associations. On the iPad, MM would list new media first, and when creating segment groups, would suggest ones for the pre-associated tunes.
- Typical workflow: Save zoom. Initiate markup from iPad. It should allow picking the file from OneDrive or iCloud. There's a chance it is already in the media index, but not if we are selecting a raw file directly.
- iOS app can share the db? Or it looks at json view?
- Ask Claude if it could handle simultaneous editing of segments by both MM WPA and MM iPad. That would be great.

### Intonio Integration
- ~~For audio, generate video that is the frequency profile from Intonio, showing the named peaks. Also for regular video. Or can it show that display on-the-fly without generating video?~~

---

## TuneList

### Core Design Notes
- Must work **fully offline** (jam venues have unreliable signal)
- Key switching is infrequent (jams stay in one key for an hour+); but switching should be easy
- Primary friction point is **adding new tunes and notes quickly**
- All UI must be operable **one-handed** (bow in the other hand); large tap targets, minimal typing
- ~~Can have playlists. Acts as a media player.~~
- ~~Can play tunes slow or with adjusted pitch.~~
- ~~Skips dead air.~~

### Key / Tuning State
- ~~Voice input via Web Speech API for notes (tap to activate, speak, review, submit)~~
- Primary state is the current key, but secondary state is current tuning.
- Tuning on displays tunes that match the current key, but not the current tuning.
- There will be a toggle to filter by the current tuning, or show all tunings.

### Audio Recording Workflow
- ~~Hear unknown tune → record → tune ends → add title → submit audio + metadata JSON to TuneHub inbox.~~
- Assume the tune is in the currently active key. Use key-to-tuning rules to suggest tuning.

### Main Working Screen Layout
- Shows the key prominently at the top, with the tuning just to the side of it, and a filter toggle just to the right of that. Click the key or the tuning in order to change it.
- To the right of that, filter buttons for different tune status (e.g. can start, etc.).
- Shows a list of tunes.
  - Clicking on a tune brings up detailed information about that tune from TuneHub; you can also add notes. There is also a record button to record audio related to that tune. It might just be voice notes or it might be a recording of playing the tune.
  - Hold-tap on the tune to enter note-taking directly.
  - There is a plus button somewhere to the right of the tune that adds it to the list of tunes played in the current jam. When you hit that button, it opens a dialogue for adding notes such as who led the tune. There's a handy button for closing that dialogue even if you don't add notes about the tune.
- At the bottom are controls, including a big + to add a new tune, as well as a record button to record some audio immediately without first asking questions about tune name, etc.
- There is also a button to end the jam, which will take you back to the starting screen.
- There will be a button to display the in-progress list of tunes played at the jam. From this display, you can rearrange the tunes in the list in case you added them out of order.

### Jam Setup
~~When you start the app, the first thing to do is to establish the current jam. You see a list of recent jams. If you click one of them, then you are making that jam active and any changes in notes will be in the context of that jam. There will also be a prominent button to create a new jam that will be pre-populated with the time and location data from GPS displaying a town name. Users can add a more specific name, or select from a list of recurring jams. One of the jams is called "not a jam" or "just looking". You can click that one to view the tune list and add to tune lists in the context of a "jam" that is not really a jam.~~

~~One workflow is to click on an old jam, and then at the bottom click the button that brings up the "tunes played" list from the jam. We will just call this the "played list".~~

~~The played list has a button at the top to copy to the clipboard, which will copy the list to the clipboard in a format that will work well when pasted into an email.~~

### People / Jam Notes
- ~~In the jam notes, have a section that's explicitly about people. People that were there, people that I met, notes about them.~~

### Data / Offline
- JSON inbox files accumulate locally offline, sync to iCloud when signal returns.
- **Writes (PWA phase):** Jam notes stored in browser localStorage as discrete jam records. Each jam has a date and optional name; multiple jams per day supported. Notes accumulate indefinitely — no pressure to share immediately. When ready, user manually triggers share: Web Share API → iOS Share Sheet → "Save to Files" → `FiddleApp/inbox/`. Each exported file marked "shared" in localStorage. Tune List will not re-export already-shared notes. Tune Hub deduplicates on ingest. Once confirmed shared, local history can be cleared.
- **Writes (native phase):** App writes directly to iCloud container — no user action required; share tracking still applies for deduplication.

---

## Ear Tuner

- ~~Be able to copy a report that you can email others. As html or md?~~

---

## Intonio

- ~~Intonio should be able to detect tonality by displaying the top 3 candidate chords that work with the current frequencies. Chords score higher if there are peaks in their notes. They lose points if there are notes that are small, dissonant intervals away from the chord notes.~~

---

## Larry (Minion)

~~Import rules:~~
- ~~`L:` for lyrics~~
- ~~`!` anywhere means "want to learn"~~
- ~~Square brackets for tunings~~
- ~~`W:` with a person. First heard it from them or otherwise associated with them.~~
