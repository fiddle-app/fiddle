# Cloud Storage Abstraction: iCloud vs. OneDrive vs. Google Drive

## TL;DR

| | Swift + iCloud | Swift + OneDrive/GDrive (File Provider) | Swift + OneDrive/GDrive (REST API) | Desktop Web | Mobile Web |
|---|---|---|---|---|---|
| SQLite DB | Easy | Easy (user picks once) | Medium (download→use→upload) | Easy (FSAA) | Not feasible |
| JSON files | Easy | Easy | Medium | Easy | Not feasible |
| Media files | Easy | Easy | Medium | Easy | Not feasible |
| Provider swap | — | Near-identical to iCloud | Medium friction | Free (sync app does it) | — |

FSAA = File System Access API

---

## The Core Tension

iCloud integrates at the **OS file system level** — files appear as local URLs the system syncs transparently. OneDrive and Google Drive (without desktop sync apps or File Provider extensions) are **remote REST APIs** — you download a file, use it, upload it back.

This gap creates the main abstraction challenge, especially for SQLite. However, two mechanisms close it significantly: **iOS File Provider extensions** (Swift/mobile) and **desktop sync apps + File System Access API** (desktop web).

---

## Swift App (iOS/macOS)

### iCloud (baseline)

Files live at a local URL under the iCloud ubiquity container:

```swift
let base = FileManager.default.url(forUbiquityContainerIdentifier: nil)!
let dbURL = base.appendingPathComponent("db/app.sqlite")
// Pass dbURL directly to SQLite — works transparently
```

iCloud syncs in the background. No API calls needed. SQLite, JSON, and media all "just work."

### OneDrive / Google Drive via iOS File Provider Extension

OneDrive and Google Drive iOS apps register as **File Provider extensions**, which means their files appear natively in the iOS Files app — and are accessible to Swift apps via the same document picker / security-scoped URL APIs as iCloud.

Key APIs:
- `UIDocumentPickerViewController` — user browses any provider in the Files app and picks a file; you get back a security-scoped URL
- `url.startAccessingSecurityScopedResource()` / `stopAccessingSecurityScopedResource()` — how you use the URL
- `NSFileCoordinator` — coordinated reads/writes, same as iCloud
- `url.bookmarkData()` — persist the URL so you don't need the picker on every launch

```swift
// First launch: user picks file from any provider (iCloud, OneDrive, GDrive, etc.)
// Subsequent launches: restore from bookmark
let bookmarkData = try url.bookmarkData(options: .minimalBookmark, ...)
UserDefaults.standard.set(bookmarkData, forKey: "dbBookmark")
```

**Caveat:** access is user-initiated. The user must pick the file at least once. Background, silent, programmatic access to a specific path (without user picking) still requires the REST API. For an app where the user opens a file, this is fine.

| | iCloud | OneDrive/GDrive (File Provider) | OneDrive/GDrive (REST API) |
|---|---|---|---|
| Access model | Programmatic, background | User-initiated picker, then bookmarked URL | Programmatic, background |
| SQLite | Local URL, transparent sync | Local security-scoped URL, provider syncs | Download→use→upload |
| Provider swap | — | Near-identical to iCloud once URL is in hand | Different code path |

### OneDrive / Google Drive via REST API (no desktop sync app, no File Provider)

When you need silent background access, you need their SDKs:

- **OneDrive:** [Microsoft Graph SDK for Swift](https://github.com/microsoftgraph/msgraph-sdk-swift)
- **Google Drive:** Google APIs Client Library for Swift (or raw REST calls)

Both require OAuth2 + explicit download/upload:

```swift
let data = try await driveProvider.download(remotePath: "db/app.sqlite")
let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent("app.sqlite")
try data.write(to: tempURL)
defer { try? driveProvider.upload(localURL: tempURL, to: "db/app.sqlite") }
```

### Abstraction Protocol (Swift)

```swift
protocol CloudFileProvider {
    func read(remotePath: String) async throws -> Data
    func write(_ data: Data, to remotePath: String) async throws
    func delete(remotePath: String) async throws
    func list(directory: String) async throws -> [String]

    /// Returns a local URL for providers that support it (iCloud, File Provider).
    /// nil means caller must use read/write API instead.
    func localURL(for remotePath: String) -> URL?
}
```

**The SQLite problem:** you cannot pass a `nil` URL to SQLite. You must branch:

```swift
if let url = provider.localURL(for: "db/app.sqlite") {
    db = try Connection(url.path)           // iCloud or File Provider URL
} else {
    let tmp = try await provider.downloadToTemp("db/app.sqlite")
    db = try Connection(tmp.path)           // REST API providers
    // coordinate upload on close/checkpoint
}
```

This branching is unavoidable unless you always use the download→use→upload pattern (which works for iCloud too but loses the transparent sync benefit).

---

## Desktop HTML/Web App

### File System Access API

Modern desktop browsers (Chrome, Edge) expose the **File System Access API**, allowing a web app to read and write files on the local file system with user permission:

```javascript
// First run: user picks the file
const handle = await window.showOpenFilePicker({
  types: [{ accept: { 'application/octet-stream': ['.sqlite'] } }]
});

// Persist the handle in IndexedDB — no picker needed on subsequent runs
await idb.put('handles', handle, 'tunehub.db');

// Read
const file = await handle.getFile();
const bytes = await file.arrayBuffer();
const db = new SQL.Database(new Uint8Array(bytes));

// Write back
const data = db.export();
const writable = await handle.createWritable();
await writable.write(data);
await writable.close();
```

### Cloud Providers on Desktop: The Abstraction is Free

On desktop, all three cloud providers install sync apps that create local folders:

| Provider | Local path (example) |
|---|---|
| iCloud Drive | `~/Library/Mobile Documents/` (macOS) |
| OneDrive | `~/OneDrive/` or `C:\Users\...\OneDrive\` |
| Google Drive | `/Volumes/Google Drive/` or a drive letter on Windows |

A web app using the File System Access API **doesn't know or care** which cloud backs the file. It reads/writes a local path; the sync daemon handles the rest. The abstraction is essentially free across all three providers.

### File Picker UX: Setup Once, Not Every Run

Users pick files once during initial setup. Handles are persisted in IndexedDB. On subsequent runs:

| Moment | What happens |
|---|---|
| First launch | User picks each `.db` / `.json` / media file via picker |
| Same browser session, reopen tab | No prompt — files open automatically |
| After browser restart | Small one-click permission confirmation per file (not full picker) |
| After clearing site data | Back to full file picker |

The post-restart prompt looks like: *"tunehub.db — Allow site to edit this file? [Allow] [Don't allow]"* — a single click, not a browse-and-pick dialog.

### Browser Support

| Browser | File System Access API |
|---|---|
| Chrome / Edge | Full support |
| Firefox | **Not supported** (intentional privacy stance) |
| Safari (desktop) | Partial, inconsistent |

If Firefox or Safari support is required, the FSAA approach doesn't work. Fallback options are limited to `<input type="file">` (read-only, no persistence) or restructuring to avoid local file access entirely.

### SQLite in the Browser

SQLite runs in-memory via [sql.js](https://github.com/sql-js/sql-js) or [wa-sqlite](https://github.com/rhashimoto/wa-sqlite). The whole DB file is loaded, used, and saved explicitly — there's no transparent sync. This pattern is the same regardless of which cloud provider backs the file:

```typescript
async function loadDB(handle: FileSystemFileHandle) {
  const bytes = await handle.getFile().then(f => f.arrayBuffer());
  return new SQL.Database(new Uint8Array(bytes));
}

async function saveDB(db: SQL.Database, handle: FileSystemFileHandle) {
  const data = db.export();
  const writable = await handle.createWritable();
  await writable.write(data);
  await writable.close();
  // Cloud sync daemon picks up the change automatically
}
```

---

## Mobile Web (Browser on iPhone/iPad)

**Not a viable platform for this architecture.** The File System Access API is not supported in Mobile Safari or WKWebView. iCloud has no public web API for file contents. The only feasible cloud access from mobile web is via OneDrive/Google Drive REST APIs, which requires OAuth and explicit upload/download — not transparent sync.

For iPad access, see the Electron vs. Capacitor section below.

---

## Electron vs. Capacitor for iPad

### Electron on iPad: Not Feasible

Electron does not run on iOS/iPadOS. Apple prohibits embedded browser engines (other than WebKit) and Node.js runtimes. An Electron app cannot be distributed on the App Store or run on an iPhone/iPad.

### Capacitor: The Correct Path

**Capacitor** (by Ionic) wraps a standard HTML/JS/CSS app in a native iOS container (WKWebView), with native plugins bridging to device APIs. This gives you:

- **Same core codebase** for desktop web and iPad native app
- **Native plugins** replace browser APIs at the platform layer

| Layer | Desktop Web (Chrome/Edge) | iPad (Capacitor) |
|---|---|---|
| SQLite | sql.js + File System Access API | `@capacitor-community/sqlite` |
| File system | File System Access API | Capacitor Filesystem plugin |
| File picker | `showOpenFilePicker()` | Native iOS document picker |
| iCloud sync | OS sync daemon handles it | Plugin supports iCloud container |
| Media files | File System Access API | Capacitor Filesystem or asset URL |

### Code Structure

The platform layer is the only thing that diverges:

```
src/
  app/            ← ~85-90% shared (UI, business logic, routing)
  platform/
    web.ts        ← File System Access API implementation
    capacitor.ts  ← Capacitor plugin implementation
```

At build time, you bundle with the appropriate platform file. Everything above the platform interface is shared.

### What This Means for the File Picker UX

On iPad, the Capacitor document picker is the equivalent of the desktop FSAA picker. The user picks files once; the app stores references. Capacitor's SQLite plugin handles iCloud sync natively on iOS, so the transparent sync behavior that iCloud provides in a pure Swift app is preserved.

---

## Verdict

| Scenario | Feasibility | Notes |
|---|---|---|
| Desktop web, swap cloud providers | **Free** | Sync apps make all providers look identical to FSAA |
| Swift iOS, iCloud | **Easy** | Transparent sync, local URL, no user interaction |
| Swift iOS, OneDrive/GDrive (File Provider) | **Easy-Medium** | User picks file once; security-scoped URL from then on |
| Swift iOS, OneDrive/GDrive (REST API) | **Medium** | Download→use→upload; needed only for background access |
| Swap iCloud ↔ OneDrive/GDrive in Swift (SQLite) | **Medium-Hard** | Local URL vs. download→use→upload gap; mitigated if File Provider extension is available |
| iPad app via Capacitor | **Medium** | ~85-90% code shared with desktop web; platform layer diverges |
| Electron on iPad | **Not feasible** | iOS prohibits it |
| iCloud from web app | **Not feasible** | No public iCloud Drive web API |

### Recommendation

- **Design the platform adapter layer up front.** Web-only APIs (FSAA, IndexedDB, sql.js) must never appear in business logic — wrap them in a `StorageAdapter` with methods like `loadDB()` and `saveDB()`. The desktop web version implements these with FSAA; a Capacitor iPad build implements them with Capacitor plugins. Core logic never touches the platform directly.
- **iCloud first, swap later.** If iCloud is the only target for now, build the iCloud implementation behind the protocol. Swapping to another provider is then localized to a new adapter implementation.
- **SQLite lowest common denominator.** If you want iCloud, OneDrive, and GDrive to behave identically in Swift, use download→use→upload for all providers (forgoing transparent sync). Accepts the tradeoff in exchange for a clean, branchless abstraction.
- **Auth stays in the factory.** Keep OAuth token management and provider selection behind a single factory — that's the only place that knows which provider is active.
