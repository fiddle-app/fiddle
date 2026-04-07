# Rethinking the Dev Plans

> Status: thinking-out-loud, no decisions made

---

## What Prompted This

The original plan (CLAUDE.md) calls for all apps except Tune Hub to start as WPAs and be ported to native Swift for iOS/iPadOS. That was written as a forward-looking commitment, not a sunk cost. Re-examining it is healthy.

The key pressures pushing back on the plan:
- Microbreaker and Ear Tuner are nearly done as WPAs — porting them is significant work for uncertain gain
- MM needs iPad someday, but also needs a real desktop version (not just for prototyping)
- The cross-platform-options.md research recommends Capacitor + React for MM — which would fragment the codebase from the vanilla JS convention
- Maintaining two paradigms (vanilla JS WPA + React/Capacitor) as a solo developer is real cognitive overhead
- Conversely, native Swift for iPad would give the best feel but means writing core logic twice

---

## App-by-App Assessment

### Microbreaker and Ear Tuner — Capacitor Wrap Is Worth It

Initially assessed as "leave them alone," but there's a compelling counter-argument: iOS Safari deliberately does not persist microphone or motion sensor permissions between PWA sessions. Every time the user opens the app, it re-asks. Native apps (including Capacitor-wrapped apps) ask once; the OS remembers. That's a real UX failure, not a polish issue.

App Store distribution adds: no browser required to launch, proper home screen presence, automatic updates.

**The port is very straightforward for these two apps specifically.** WKWebView (what Capacitor uses) natively supports both APIs they need:
- Web Audio API / getUserMedia (microphone) — works in WKWebView on iOS 14.5+
- DeviceMotionEvent / DeviceOrientationEvent (gyroscope) — works in WKWebView

There's no API replacement needed. The port is scaffolding + App Store logistics, not a code rewrite:
1. `npx cap init && npx cap add ios`
2. Add `NSMicrophoneUsageDescription` / `NSMotionUsageDescription` to `Info.plist` — this is what makes permissions stick
3. App icons, splash screen assets
4. Mac (or cloud build) for Xcode compile
5. App Store submission and review

Business logic: zero changes. The effort-to-benefit ratio is much better than for a typical port.

**The real cost:** Apple Developer account ($99/year, shared across all apps), App Store review overhead per update, Mac access for builds.

**Recommendation:** Wrap both with Capacitor. The permission UX fix alone justifies it. The $99/year developer account is shared with MM anyway once that goes to App Store.

### Tune Hub — Desktop-Only, No Change

Complex data management. Likely a power tool you use at a desk. The SQLite WASM dependency and the "writes the SSOT" responsibility both push toward desktop. No iOS port makes sense.

**Recommendation:** Stay the course. Desktop WPA only.

### Tune List — iPhone App via Capacitor

Initially assessed as a light PWA that could stay web-only. This underestimated what TuneList actually needs:

- **Direct tunehub.db access.** TuneList's tune detail view would surface everything TuneHub knows. Making TuneHub publish all of that as JSON just to serve TuneList is significant infrastructure with staleness tradeoff. Since TuneList is going Capacitor anyway, it reads the db directly via a shared iCloud App Group container.
- **Recording feature.** A future feature to record a quick take at a jam and associate it with a tune requires microphone access — which has the same permission re-ask problem in Mobile Safari as Microbreaker/Ear Tuner. Capacitor fixes it.
- **iPhone-only.** TuneList is a jam companion, used in hand. Desktop is not a target. This simplifies the build story — one Capacitor iOS build.

App Groups (shared iCloud container) is how TuneList and MM access tunehub.db and media-markup.db without each app copying data into its own sandbox. Setup is an Xcode entitlements step, not code.

**Recommendation:** Capacitor iOS, iPhone-only. Direct db access via shared iCloud App Group container.

### Media Markup — The Hard One

MM is the only app where "I need this on iPad" is a real, concrete use case: sitting with your iPad, watching a Zoom lesson recording, annotating it in real time. That's a genuinely iPad-native workflow.

But MM also has a strong desktop use case: large video files (Zoom recordings) live in OneDrive; you want to work with them at your desk on a big screen with a full keyboard. Desktop isn't just a prototyping phase — it may be the primary use case for some sessions.

So MM is the only app in the family that genuinely needs both, and needs both well.

---

## The Core Question for MM: One Codebase or Two?

### Option A: WPA (desktop) + Native Swift (iPad)

Two separate implementations of the annotation logic.

**Pros:**
- Native iPad experience: best video playback integration, Files app, Apple Pencil potential
- Desktop version is a clean, lightweight WPA with no mobile concerns
- Each codebase is optimized for its target

**Cons:**
- Core annotation logic written twice (JSON structure, time segment model, tune linking)
- Any schema change must be made in two places
- Swift development requires a Mac at some point (Xcode, TestFlight)
- Significantly more total work

**Verdict:** Hard to justify for a solo developer unless the native iPad experience is a hard requirement.

### Option B: Capacitor — One Codebase, Two Builds *(tentative plan)*

Same HTML/JS/CSS core, wrapped by Electron for desktop and Capacitor iOS for iPad.

**Pros:**
- ~85-90% code shared (UI, annotation logic, JSON schema, tune linking)
- Desktop gets full file system access via Node.js (Electron) or FSAA (browser)
- iPad gets native iOS wrapper with Capacitor SQLite and Filesystem plugins
- Cloud builds (Capawesome, Ionic Appflow) remove the Mac requirement for most of the dev cycle
- Design tokens from `_shared/design/` apply equally to both targets

**Cons:**
- Two build pipelines (Electron + Capacitor iOS) to maintain
- Platform adapter layer requires discipline — file access APIs diverge between Electron and Capacitor
- If using React (as the cross-platform-options.md recommends), adds framework overhead and fragments from the vanilla JS convention used by other apps
- Capacitor's web view is WKWebView on iOS — not quite a full browser, edge cases exist

**Verdict:** Most pragmatic path if you commit to the platform adapter pattern. The Electron + Capacitor split is the main complexity; the code itself stays clean if the adapter is well-designed.

**Status:** Tentative plan, based on the analysis in this document.

### Option C: Desktop WPA Now, Defer iPad

Build MM for desktop first as a standard WPA (File System Access API, no framework). Leave iPad as a future concern.

**Pros:**
- Gets you a working tool faster
- No premature architecture decisions
- Consistent with vanilla JS convention
- If Capacitor is the eventual iPad answer, wrapping a vanilla JS WPA is straightforward

**Cons:**
- iPad users wait (possibly a long time)
- If you later decide on Capacitor, you may need to refactor the platform layer retroactively (manageable if the adapter discipline was there from the start)

**Verdict:** Reasonable if the desktop use case is more urgent and iPad is genuinely future. The risk is that "future" becomes "never." Mitigate by designing the platform adapter from day one even if only the web implementation exists.

---

## The React Question

The cross-platform-options.md recommends React for MM. This deserves scrutiny.

**Arguments for React:**
- Component model maps better to a complex UI with dynamic segment timelines
- Capacitor community has good React examples and tooling
- Easier to find help/resources

**Arguments against React:**
- Every other app in the family uses vanilla JS — React fragments the codebase
- Adds a build pipeline (JSX, bundler) that other apps don't need
- For a solo developer, switching mental models between React and vanilla JS across apps is friction
- Capacitor works perfectly fine with vanilla JS — React is not a requirement

**Verdict:** Avoid React unless the UI complexity genuinely demands it. A well-organized vanilla JS app with a component-like module structure (as already called out in CLAUDE.md) serves MM fine and keeps the family coherent. If complexity grows, Web Components are a middle ground that stays framework-free.

---

## Look-and-Feel Sharing Across Technologies

This is the question that cuts across all the above decisions.

### Within the web family (WPA, Electron, Capacitor)

**Easy.** All run HTML/CSS in a browser engine. The `_shared/design/` system — CSS variables, typography scale, icon set — applies identically. Capacitor on iOS runs WKWebView, which renders the same CSS. Electron uses Chromium. A component styled for Microbreaker looks the same in MM.

The shared design system is already the right call. Keep investing in it as the single source of truth.

### Web family → Native Swift

**Hard.** Colors and type scales can be ported (CSS variables → Swift Color extensions). But:
- Hover states don't exist on touch
- Custom web components need to be rebuilt as SwiftUI views
- Animations and transitions are expressed differently
- Layout systems differ (CSS Flexbox/Grid vs. SwiftUI stacks)

You can make a Swift app *feel consistent* with the web apps through shared color palette and typography — but it's a deliberate rebuild, not a translation. Expect 30-40% of the UI work to be redone even with a clean design system.

### Practical implication

If Microbreaker and Ear Tuner stay as WPAs and MM goes Capacitor, the entire family is HTML/CSS-based. The `_shared/design/` system works seamlessly across all of them with zero porting cost. This is actually an argument **for** the Capacitor path over native Swift — it keeps the look-and-feel story simple.

If any app goes native Swift, that app's UI is a manual re-implementation. Manageable, but real work.

---

## Suggested Revised Plan

This is not a decision — it's a proposed direction to evaluate:

| App | Platform | Rationale |
|---|---|---|
| Microbreaker | WPA → Capacitor iOS wrap | Permission persistence + App Store; port is scaffolding, not a rewrite |
| Ear Tuner | WPA → Capacitor iOS wrap | Same |
| Tune List | Capacitor iOS (iPhone-only) | Direct db access via shared iCloud container; recording feature needs native mic permissions |
| Tune Hub | Desktop WPA | SSOT editor; desktop-only is fine |
| Media Markup | Electron (desktop) now → Capacitor iOS later | Folder watching, keyboard shortcuts, and direct OneDrive access require Electron; platform adapter makes iPad port a wrap |

**The key commitment this requires:**

MM's platform adapter layer must be designed from day one, even if only the web implementation exists at launch. File access, SQLite operations, and the document picker must go through the adapter — never called directly from business logic. That's what makes "add Capacitor later" a wrap rather than a rewrite.

---

## JSON Publishing — Scope Reduced

The original architecture required TuneHub to publish all tune data as JSON snapshots for other apps to consume. With all consuming apps going Capacitor and accessing `tunehub.db` directly via a shared iCloud container, the in-app JSON publishing pipeline is no longer needed.

**What stays:**
- `published/tunes/*.md` — human-readable, Claude/Larry-queryable, source material for a future public website
- The inbox pattern — TuneList and MM still write inbox JSON; TuneHub ingests it

**What goes:**
- `published/data/all-tunes.json`, `published/data/tunes/`, `published/data/lists/` — no longer needed as an app-to-app transport layer

**Public tune data:** If tune data is ever published for external consumption, it would be a website generated from the markdown files — not a structured data format for ingestion into other systems. There is no known standard interchange format for fiddle tune libraries. (Slippery Hill stores structured tune data but its internal format is unknown — a research question if interoperability ever becomes a goal.)

## Shared iCloud Container (App Groups)

All iOS apps in the fiddle family share `tunehub.db` and `media-markup.db` via an Apple **App Group** — a shared iCloud container accessible to apps from the same developer account. All fiddle apps are under the same account, so this works cleanly.

Setup: each app gets an App Groups entitlement in Xcode pointing to the same group identifier (e.g., `group.com.fiddle-app.shared`). This is configuration, not code — not complicated, but requires Xcode.

| App | tunehub.db | media-markup.db |
|---|---|---|
| TuneHub (desktop) | Read/write (owns it) | Attaches read-only |
| MM (Electron, desktop) | Attaches read-only via local iCloud path | Read/write (owns it) |
| MM (Capacitor, iPad) | Read-only via App Group | Read/write via App Group |
| TuneList (Capacitor, iPhone) | Read-only via App Group | — |

SQLite WAL mode supports multiple concurrent readers safely. TuneHub is the only writer to tunehub.db; MM is the only writer to media-markup.db.

## Xcode

Getting any app to a real iPhone or the App Store requires Xcode — for signing, provisioning profiles, App Groups entitlements, TestFlight, and App Store submission. Capacitor's iOS docs walk through the Xcode-specific steps. The learning curve is real but bounded; the entitlements work is configuration, not programming.

Cloud build services (Capawesome, Ionic Appflow) can handle the compile step without a Mac for most of the dev cycle, but Xcode is still needed for the initial setup and App Store submission.

---

## Open Questions

- Is the iPad use case for MM urgent, or can it wait until the desktop version is proven?
- Is there a Mac available for Xcode/Capacitor builds, or is cloud-build the only path?
- Does the annotation timeline UI complexity actually justify React, or is vanilla JS with a clean module structure sufficient? (Default: vanilla JS, consistent with the family.)
- ~~Should MM's desktop version target the browser or Electron?~~ **Decided: Electron.** Folder watching, keyboard shortcuts, and direct OneDrive path access are blockers for the browser approach.
