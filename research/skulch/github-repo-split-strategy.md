# GitHub Repo Split Strategy — Source vs. Hosted

> [!tip] Resolved — see [architecture.md §14](../architecture.md) for the canonical documentation.

## The Problem

Each PWA app has two distinct concerns that don't belong in the same repo:

1. **Source code** — JS modules, build tooling, specs, tests, dev history
2. **Hosted output** — the static files GitHub Pages (or similar) serves to end users

Mixing them in the same repo creates noise: build artifacts in source history, deployment
files alongside dev files, unclear separation of what's "for developers" vs. "for the web."

## Previous Idea (Rejected)

Rename repos with a `-src` suffix (e.g. `fiddle-app/ear-tuner-src`). Rejected because:
- Ugly in directory listings and terminal
- Doesn't match the folder names under `Projects/fiddle/`
- Awkward to type repeatedly during development

## New Idea

**Split by GitHub account, keep names the same.**

| Account | Role | Example |
|---|---|---|
| `caseymullen` | Source repo (dev work) | `caseymullen/ear-tuner` |
| `fiddle-app` | Hosted repo (deployed output) | `fiddle-app/ear-tuner` |

- `caseymullen/ear-tuner` holds all source: JS modules, specs, tests, build config, CLAUDE.md, backlog, etc.
- `fiddle-app/ear-tuner` holds only what GitHub Pages (or similar) needs to serve the app.
- Tune Hub is probably not a PWA, so it may not need this split — evaluate per app.

## Benefits

- Local folder names (`Projects/fiddle/ear-tuner/`) match both repo names cleanly.
- The `caseymullen` account accumulates dev history and tooling; `fiddle-app` stays clean as a delivery vehicle.
- Clear mental model: if you're coding, you're on `caseymullen`; if you're deploying, you're pushing to `fiddle-app`.

## Open Questions

> [!question] Build and deploy workflow
> How does output get from `caseymullen/ear-tuner` to `fiddle-app/ear-tuner`?
> Options: CI/CD pipeline, manual copy, git subtree, submodule, deploy script.

A: What are my options for CO/CD pipeline? Can this just be a simple script? Python? Powershell? Some official tool? Can a submodule be in a separate account? Answer at the bottom of this document.

> [!question] Which apps need the split?
> PWAs only? Or does Electron also benefit from separating source from distributables?

A: Hmmm... I guess the only apps that need "hosting" on github may be ear-tuner and microbreaker. So this is not an issue for all of the apps.

> [!question] Existing repos
> The current `fiddle-app/ear-tuner` repo has source in it. Migrate it to `caseymullen`,
> or start fresh and archive the old one?

A: Actually, I've got a new and perhaps better idea. Short URLs are good, if I create a new public repo named "ear" then I can host at "fiddle-apps.github.io/ear" microbreaker might be "fiddle-apps.github.io/practice".   This also avoids the headache of switching my active account back and forth all the time. So I think the new plan is to just create new "ear" and "practice" public repos with open pages turned on for hosting. Turn off open-pages for ear-tuner. Make all of the existing fiddle apps repos private.   Given this new plan, what would be a recommended location on my disk for storing the published artifacts from my build process  ("CI/CD pipeline"). Should I have a "Builds" folder sitting next to my "Projects" folder in OneDrive, or would it be better to keep "Builds" outside the scope of OneDrive?

> [!todo] Decide and document the deploy pipeline before implementing

---

## Revised Plan: Short-Named Public Repos for Hosting

Based on Casey's answers above, the plan has evolved from "split by account" to something simpler:

### GitHub Repo Layout

| Repo | Visibility | Purpose | GitHub Pages |
|---|---|---|---|
| `fiddle-app/ear` | Public | Hosted PWA for Ear Tuner | `fiddle-app.github.io/ear` |
| `fiddle-app/practice` | Public | Hosted PWA for Microbreaker | `fiddle-app.github.io/practice` |
| `fiddle-app/ear-tuner` | **Private** | Source code, specs, backlog | Pages OFF |
| `fiddle-app/microbreaker` | **Private** | Source code, specs, backlog | Pages OFF |
| `fiddle-app/tune-hub` | **Private** | Source (not a PWA) | Pages OFF |
| `fiddle-app/tune-list` | **Private** | Source | Pages OFF |
| `fiddle-app/media-markup` | **Private** | Source | Pages OFF |
| `fiddle-app/_shared` | **Private** | Design tokens, shared assets | Pages OFF |

Benefits:
- Short, clean public URLs (`fiddle-app.github.io/ear`)
- No account-switching headache — everything stays on `fiddle-app`
- Source repos go private — dev history isn't public
- Hosting repos contain only built artifacts, no source noise

### CI/CD Pipeline Options

For a personal project with two PWA targets, here are the realistic options from simplest to most involved:

**1. Simple shell script (recommended)**
A bash or PowerShell script that runs the build, copies output to the Pages repo clone, commits, and pushes. Something like:
```bash
# deploy.sh ear
APP=$1
npm run build
cp -r dist/* ../builds/fiddle/$APP/
cd ../builds/fiddle/$APP
git add -A && git commit -m "Deploy $(date +%Y-%m-%d-%H%M)" && git push
```
Pros: Dead simple, no dependencies, easy to debug. Cons: Manual trigger only.

**2. npm script wrapper**
Same as above but wired into `package.json` as `npm run deploy`. Still a script under the hood, just a conventional entry point.

**3. GitHub Actions**
A workflow in the source repo that builds on push and deploys to the Pages repo. This is the "official" CI/CD tool, but it adds complexity: you'd need a deploy key or personal access token for the cross-repo push, and the source repo would need Actions enabled. Overkill for now but worth considering later if you want automated deploys on every push.

**4. Python / Node deploy script**
More portable than bash, good if you want to add features (like cache-busting filenames, manifest generation, or build validation). But unnecessary at this stage.

**Recommendation:** Start with option 2 — an `npm run deploy` script that calls a shared bash script. Upgrade to GitHub Actions only if you find yourself wanting automated deploys on push.

### Submodules Across Accounts

Yes, a submodule can reference any repo regardless of account or org, as long as the repo is accessible (public, or private with appropriate SSH key). Since `fiddle-app/ear` would be public, any repo could reference it as a submodule. But you probably don't need submodules here — the deploy script handles the connection between source and hosting repos.

### Build Artifacts: Where on Disk?

**Keep builds outside OneDrive.** Reasons:

- Build output is generated, not source — syncing it to OneDrive wastes bandwidth and storage for files that can be recreated in seconds
- OneDrive sync can interfere with git operations (file locks, partial syncs)
- OneDrive might try to sync mid-build, creating inconsistent state

Recommended location:

```
C:\Users\CaseyM\
├── OneDrive\Projects\fiddle\     ← source (synced)
│   ├── ear-tuner\                   dev work happens here
│   ├── microbreaker\                dev work happens here
│   └── ...
│
└── Builds\fiddle\                ← build output (NOT synced)
    ├── ear\                         local clone of fiddle-app/ear
    └── practice\                    local clone of fiddle-app/practice
```

Each folder under `Builds/fiddle/` is a plain git clone of the corresponding Pages repo. The deploy script builds from source, copies into the clone, commits, and pushes.

Alternatively, `C:\Builds\fiddle\` works too — shorter path, further from user profile clutter. Pick whichever feels natural.

> [!claude]  Use C:\builds\

> [!question] Final directory location preference
> `C:\Users\CaseyM\Builds\fiddle\` or `C:\Builds\fiddle\` or somewhere else?

A: C:\Builds\fiddle\

> [!question] App-specific short names
> `ear` and `practice` — are these the final names? Any other apps that might need hosting later?

A: These are final for now. I could use "list" for a WPA TuneList, but that may never happen. "could put a static website for browsing the tunehub at "hub".

> [!todo] Create the `fiddle-app/ear` and `fiddle-app/practice` repos on GitHub

> [!todo] Set existing source repos to private

> [!todo] Write the shared deploy script

> [!todo] Update APPS.md and architecture.md to reflect the new repo layout
