Based on your good advice, I'm going to ask you to build a new "architecture-and-implementation-strategy.md" that will be an organized version of all of the relevant stuff from the existing research\ files. Then put the old files in a "skulch" folder so that we can mostly ignore them... and probably eventually delete them. The new md should capture all of the relevant stuff from the old files.

I agree with your advice in "electron-research" to avoid Svelte and Tailwind and similar frameworks. I'll stick with our early decision about vanilla js until it is proven that we need more.

You closed "electron-research" with advice: Extract the performance techniques (Canvas, rAF, Pointer Events, passive listeners, CSP). Discard the framework and tooling recommendations. 
Follow that advice. Incorporate the suggested performance techniques into the overall fiddle-apps development plan. Add a section to "media-markup" research\Design and implementation notes.md with tips that are particularly relevant for it, or just refer back to the overall tips in the new .md.

In your comments on "testing-strategy", for "handoff manifest", you suggest that "no new artifact type is needed". You mention that the "log" already exists. Just to be clear, I intend the "log" for higher-level activities (like reorganizing folders or defining development process). Remember that that is its purpose, not tracking spec-development.

In architecture-and-implementation-strategy.md, in the section on spec-driven dev mode, include proposed system prompts for a Coder and Tester, for the cases where I want to use them.

This new document should not include the discarded ideas, but it could mention them, e.g. "We seriously considered using frameworks like React, Sveldt, or Tailwind, but rejected them for {reason} See {link to the old .md in skulch\}"

Regarding your research document:
- 1a: I agree
- 1b: I agree
- 1c: we have worked this out already, in conversation
- 1d: correct. Ignore the strikethrough stuff
- 2a: Yes, use those tools. Maybe note that you and gemini agree on the choice.
- 2b: I agree, with some added subtlety about spec-driven dev when it is called for (tier 1) as per our conversation.
- 2c: Include this. The question remains open. Gemini recommend a security-aware template that we might evaluate.
- 2d: Include. mark as an open question. 
- 2e: Adopt The `data-testid` Convention now
- 2f: MM first on desktop, for easier debugging. Eventually, I will use it primary on the iPad, but from a dev perspective it makes sense to work out the kinks on desktop, first.
- 3a. Note as an open question and a topic for future research
- 3b. Adopt your suggested strategy, with one addition. Add a place (the same schema_version table or a new schema_read-compatible table? or something else) that captures some notion of a read-compatible generation.  If we just add a new table or a new column to an existing table, it is a new db version, but old apps that are read-only with respect to the db can still read the newer db. Really, TuneHub is the only app that has to be completely up-to-date with the schema version, because it is the only app that write to the db.
- 3c: Yes, note the research topic. This is an open question. Maybe each MM instance writes into the db when it has it open for writing, so that other instances know that there is a competing writer... and so they stay in read-only mode.
- 3d: There are some groups of apps that can go forward in parallel
	- Group 1
		- TuneHub data: The backend schema work.
		- Larry & TuneHub: defining the canonical .md formatting (for ingestion and publishing)
		- Larry: Defining one or more ingestion formats... may depend on source
		- Larry: Figure out how to effectively gather data from slippery-hill and other locations. These may eventually be incorporated into TuneHub if they can be implemented in javascript.
		- Initial porting of existing EarTuner and Microbreaker for finalization and extraction of design standards.
	- Group 2
		- Port EarTuner and Microbreaker to our "standard" Electron architecture... in prep for eventual production of iPhone/iPad apps.
		- MM Desktop
		- TuneHub App with UI
		- TuneList Desktop
	- Group 3
		- MM iPad
		- EarTuner iPhone/iPad
		- Microbreaker iPhone/iPad
	
- 3e: Yes, if backlog for fiddle does not already reflect it, it should reflect the plans mentioned in 3d, above.

Section 4 Recommendations:
1. OK
2. Yes. Covered elsewhere
3. Agreed
4. Yes. To be recorded as open question and added as a backlog item with a link to details.
5. OK. Note that plan, perhaps where it fits into the dev order mapped out in 3d, above.
6. Yes. Ensure we have backlog items for this work.
7. Yes, as agreed in conversation.
8. Yes
9. Yes. Good idea.

Section 5: Open Questions
- Turn the first two bullets into backlog items in fiddle\
- Ignore the 3rd bullet. If it is a pain point, I will feel it and know what to do


Some of the information in app.md should probably be broken out into separate .md files in the app-specific folders. In their "spec folders?"

There are also next actions and questions that should really be included on backlogs. Would it be feasible to add backlog items for them that link to the appropriate section in this new md or other relevant docs?

In general, please always remember to use "> [!question]" Obsidian callouts to highlight "open questions". And in general use obsidian callouts where appropriate. I typically view specs, research documents, etc. using Obsidian.

Before embarking on this major reorg of research into architecture-and-implementation-strategy.md and breakup of apps.md, we should plan it. Ask me any questions that you have about preferred organization, or decision about the folder file organization that remain unanswered.   Just add your proposed plan in a new section in this document. Include questions for me at the end. Eventually, we'll turn this into a log\ entry.

---

## Claude's Proposed Plan

### What We're Building

One canonical **`architecture-and-implementation-strategy.md`** at the fiddle root that consolidates all finalized decisions from the research files. It replaces the scattered research documents as the go-to reference for "how are we building these apps and why." The old research files move to `research/skulch/` for historical reference.

Separately, app-specific content that currently lives in `APPS.md` gets broken out into the relevant app folders — primarily into each app's `CLAUDE.md` or `research/` folder, since those are what Claude Code actually reads when working in an app context.

### Proposed Structure of `architecture-and-implementation-strategy.md`

1. **Overview** — What this document is, how it relates to CLAUDE.md and per-app docs.

2. **Platform Decisions** — The finalized platform table (TuneHub=Electron, MM=Electron→Capacitor, TuneList=Capacitor iPhone, Microbreaker/EarTuner=WPA→Capacitor wrap). Brief rationale for each. Link to skulch/ for the full deliberation.

3. **Technology Stack** — Vanilla JS, ES modules, no framework. Why we rejected Svelte/React/Tailwind (brief, with link to skulch/electron-research.md for the full Gemini analysis). CSS variables via `_shared/design/`. No bundler initially; esbuild if needed (open question).

4. **Performance Techniques** — Canvas rendering for complex visual elements, requestAnimationFrame, Pointer Events, passive listeners, CSS `will-change`/`transform`, Web Workers if needed. These are the extracted good ideas from the Gemini research. Note that MM's timeline is the primary consumer.

5. **Data Architecture** — SQLite SSOT, database ownership, ATTACH pattern, inbox pattern, iCloud App Group, WAL mode. Schema versioning strategy (schema_version table + read-compatibility generation). Consolidates from cloud-storage-abstraction.md, rethinking-dev-plans.md, and organized-notes.md.

6. **Shared Design System** — `_shared/design/` role, CSS variables, design token strategy. Reference to the design review project.

7. **Platform Adapter Pattern** — The interface contract, the rule ("grep src/app/ — zero platform imports"), module construction pattern. Currently in MM's CLAUDE.md but applies to all Electron/Capacitor apps.

8. **Security** — contextIsolation, CSP, contextBridge patterns for Electron. Adopted from Gemini research.

9. **Development Workflow** — The three modes: vibe coding (default), retro-spec, spec-driven mode. Spec and handoff manifest formats. Coder and Tester subagent system prompts. The `/retro-spec` skill concept. Tiered testing strategy (Tier 1/2/3). Post-hoc testing with "flag what you had to guess."

10. **Testing Tools** — Vitest (unit) + Playwright (E2E). `data-testid` convention. When to start writing tests for each tier.

11. **Development Order** — The three groups you defined in 3d, with parallel tracks noted.

12. **Electron Shared Setup** — Open question: shared boilerplate or extract-after-first-app. Note Gemini's security template suggestion.

13. **Open Questions** — Collected from across all research, formatted with `> [!question]` callouts. Each linked to a backlog item where applicable.

> [!warning] Scope of this reorg
> This touches many files across the repo. The execution order (below) is sequenced to avoid dangling references — e.g., the strategy doc is written before APPS.md is trimmed, so nothing is lost in transit. But it's a lot of moves. Consider reviewing after each major step rather than all at once.

### What Happens to APPS.md

APPS.md currently serves two purposes: (a) app registry with status and descriptions, and (b) detailed per-app design notes. I propose:

- **Keep APPS.md** as a lightweight registry and data-flow overview — the "map" of the family. Strip it down to: app table, folder structure, data flow diagram, and brief per-app summaries that point to each app's own docs.
- **Move detailed per-app content** into each app's folder. Specifically:
  - MM design notes (segment model, WebVTT shadow format, keyboard shortcuts, workflow) → already partially in `media-markup/CLAUDE.md` and `media-markup/research/`. Consolidate there.
  - TuneList design notes (main screen layout, jam setup, offline strategy, key/tuning state) → `tune-list/CLAUDE.md` or a new `tune-list/research/` doc.
  - TuneHub design notes (data fields, people/sources, status/confidence) → `tune-hub/CLAUDE.md` or spec/ folder.
  - Larry design notes → already in `minions/larry/CLAUDE.md`.
  - Ear Tuner and Microbreaker have minimal design notes; what exists can stay in APPS.md summaries or their CLAUDE.md files.

### What Happens to the Research Files

All current `research/*.md` files move to `research/skulch/`. The new `architecture-and-implementation-strategy.md` replaces them as the canonical reference. The skulch files are kept for historical context and are linked from the new doc where relevant (e.g., "We rejected Svelte — see [skulch/2026-04-11_electron-research.md] for the full analysis").

The `research/` folder remains available for future research documents that haven't been resolved into decisions yet.

### Backlog Items to Create

From your instructions and the research review:

> [!todo] fiddle/ (parent) backlog — items to add
> - Spec file naming convention — decide on architecture-feature naming for `specs/` folders
> - Build the `/retro-spec` skill
> - Research iCloud + SQLite sync safety (expand on 3c — concurrent writers, corruption risk, detection strategy)
> - Electron packaging and distribution strategy (3a)
> - Build tooling decision for vanilla JS + Electron (esbuild vs. none) — open question
> - Electron shared security template — evaluate Gemini's recommendation

> [!todo] Per-app backlogs
> Should reflect the Group 1/2/3 development order. I'll check existing backlogs and add items that aren't already there.

### Execution Order

I'd do this work in this sequence:

> [!tip] Review cadence
> Consider reviewing after each major step (especially steps 1, 3, and 4) rather than waiting for the full reorg to complete.

1. **Write `architecture-and-implementation-strategy.md`** — the big new doc.
2. **Move research files to skulch/** — simple renames.
3. **Slim down APPS.md** — remove content that's moving to app folders.
4. **Update per-app CLAUDE.md and research/ files** — move the detailed design notes from APPS.md into the right homes. Add the MM performance tips section.
5. **Update per-app backlogs** — add items reflecting the development order groups and open questions.
6. **Update fiddle/backlog.md** — add the cross-cutting items listed above.
7. **Update fiddle/CLAUDE.md** — add a reference to the new strategy doc and the development workflow section.

### Questions for Casey

> [!question] 1. Where should `architecture-and-implementation-strategy.md` live?
> I assumed `fiddle/` root (next to CLAUDE.md and APPS.md). Alternatively it could go in `research/`. My preference is the root — it's a living canonical document, not historical research.

OK. root is good

> [!question] 2. Filename
> `architecture-and-implementation-strategy.md` is descriptive but long. Alternatives: `dev-strategy.md`, `architecture.md`, `strategy.md`. Or keep it as-is? Since you view these in Obsidian, shorter names are easier to link. But clarity matters more if the name is self-documenting.

architecture.md is good

> [!question] 3. APPS.md scope after slimming
> You said "some of the information in APPS.md should probably be broken out." How aggressively should I strip it? Options:
> - **Light trim:** Remove struck-through and obsolete content, keep the detailed per-app sections but mark them as "canonical copy is in the app's folder."
> - **Heavy trim:** Reduce each app to a 3-4 line summary with a link to its folder. APPS.md becomes a pure registry + data flow map.
>
> My recommendation: heavy trim. The detailed content is more useful in the app's own folder where Claude Code will actually see it during development.

Heavy

> [!question] 4. The `organized-notes.md` file
> Much of its non-struck-through content will be absorbed into either the strategy doc or per-app docs. After that, it's mostly struck-through historical ideas. Move to skulch with the others, or is there anything in it you want to preserve separately?

Move to skulch after you have extracted what you need

> [!question] 5. The `other-thoughts-on-icloud-and-sqlite.md` file
> Its content overlaps heavily with `cloud-storage-abstraction.md` and `rethinking-dev-plans.md`. I'll extract anything unique into the strategy doc and move it to skulch. Any objection?

No objection.

> [!question] 6. MM's `cross-platform-options.md`
> Already has an addendum correcting its React/Capacitor conflations. Move to `media-markup/research/skulch/` (its own skulch), or to `fiddle/research/skulch/` with the others? My instinct: MM's own skulch, since it's app-specific research.

Yes, its own skulch. "skulch" means "junk". It is a pattern I use... a place to put stuff that is probably junk, but I'm keeping it alive for a while "just in case".

> [!tip] 7. Obsidian callout usage
> I'm now using these callout types throughout this document:
> - `> [!question]` — open questions needing a decision
> - `> [!warning]` — known risks or things that could go wrong
> - `> [!tip]` — best practices or recommendations
> - `> [!todo]` — action items that need to happen
>
> Are you happy with this set of callouts and how they're used here? I'll apply the same conventions in the strategy doc and other files.

Yes, except the questions are a little awkward because there is no easy place to answer... In obsidian my answer starts looking part of the question or I have to hit enter a few times. After every question add a  separate "A: " line, where I can provide an answer. I want this style of generating .md for things that I am expected to read to be applied in all projects, so put the Projects/Claude.md guidance.
  will provide answers

> [!question] 8. Backlog item granularity for the Group 1/2/3 development order
> Should each bullet under your groups become its own backlog item? Or should the groups themselves be backlog items with the bullets as sub-tasks/notes? The backlog system supports notes fields — I could create one item per group with the bullets in the notes.

Each bullet should be its own item. In the notes section, note "Group 1" "Group 2" as appropriate. Give each item P1, P2, P3 priority based on its group number.

You are doing a great job! You are amazing!