# 2026-04-12-20-25 PWA Deploy Pipeline — GitHub Repo Split & Deploy Script

**2026-04-12**

## Source

Planning and decision-making for this session was captured in real time in `research/skulch/github-repo-split-strategy.md`, with Casey answering inline questions as the document evolved. That file is marked resolved and points to architecture.md §14 as the canonical destination. The log below synthesizes the narrative from that document and the session.

## Context

The session started from a planning discussion (previous night) about how to separate source code from hosted PWA output in GitHub. The original idea — rename repos with a `-src` suffix — was rejected as ugly. A second idea — split by GitHub account (source on `caseymullen`, hosted on `fiddle-app`) — was also rejected because it would require constant `gh auth switch` churn during development.

## Final Repo Strategy

The settled plan: keep everything on `fiddle-app`, but split by repo name and visibility.

- **Source repos** (private): `ear-tuner`, `microbreaker`, `tune-hub`, `tune-list`, `media-markup`, `_shared`
- **Hosting repos** (public, GitHub Pages): `ear` → `fiddle-app.github.io/ear`, `practice` → `fiddle-app.github.io/practice`

Short names were chosen deliberately for clean public URLs. Future possibilities noted: `hub` (static Tune Hub browse), `list` (Tune List PWA).

## Folder Structure Decision

Build output lives at `C:\Builds\fiddle\` — intentionally outside OneDrive. Reasoning: generated files don't need cloud sync and OneDrive can cause file-lock conflicts during git operations.

```
C:\Builds\fiddle\
├── ear\        ← clone of fiddle-app/ear
└── practice\   ← clone of fiddle-app/practice

C:\Users\CaseyM\OneDrive\Projects\fiddle\
├── scripts\
│   └── deploy.sh   ← shared deploy script
├── ear-tuner\
│   ├── package.json
│   └── .npmrc
└── ...
```

## Documentation

- Added **Section 14** to `architecture.md`: repo layout table, folder structure, deploy pipeline description, one-time setup commands.
- Updated **APPS.md**: added "Hosted URL" column to app registry; split folder structure into source and builds sections.
- Added backlog item **P13**: consider esbuild minification in deploy pipeline (currently a direct file copy).
- Marked `research/github-repo-split-strategy.md` resolved with pointer to §14.

## One-Time GitHub Setup

- Created `fiddle-app/ear` and `fiddle-app/practice` as public repos.
- Set all source repos to private using `gh repo edit --visibility private --accept-visibility-change-consequences` (the `--accept-visibility-change-consequences` flag is required by newer `gh` versions — not documented in older examples).
- Enabled GitHub Pages via `gh api repos/fiddle-app/<repo>/pages` — requires at least one commit on `main` to exist first.

## SSH Issue

Initial clone used `git@github.com:fiddle-app/ear.git` which routed through the wrong SSH key (`caseymullen`). Fixed by updating remotes to use the `github.com-fiddle` host alias defined in `~/.ssh/config`:
```
git remote set-url origin git@github.com-fiddle:fiddle-app/ear.git
```

## Deploy Script

`scripts/deploy.sh` is parameterized by app name (`ear-tuner` or `microbreaker`). It:
1. Stashes the builds repo's `.git` directory
2. Clears and re-copies source files
3. Restores the builds repo's `.git`
4. Removes dev-only files (backlog, research, spec, handoffs, `*.md`, `*.svg`, package files)
5. Writes `.gitattributes` enforcing LF line endings
6. Commits and pushes if anything changed

Entry point per app: `npm run deploy` in `ear-tuner/package.json`.

### Key bugs hit and fixed

**`.git` clobber**: `cp -r "$SRC/." "$DEST/"` copies the source repo's `.git` into the builds directory, overwriting the builds repo's remote config. First deploy pushed to `ear-tuner` instead of `ear`. Fixed by stashing/restoring `.git` around the copy.

**Wrong git history after clobber**: After the bad push, the builds repo had ear-tuner's full git history. Fixed with:
```powershell
git -C C:\Builds\fiddle\ear fetch origin
git -C C:\Builds\fiddle\ear reset --hard origin/main
```

## Shell / Scripting Decisions

- **Standardizing on bash** for deploy scripts — available natively on Mac, available on Windows via Git Bash. `#!/usr/bin/env bash` shebang used for Mac compatibility (Apple ships an ancient `/bin/bash`).
- **npm runs scripts via cmd.exe on Windows**, so `bash` wasn't found. Fixed by adding `.npmrc` with `script-shell=C:\\Program Files\\Git\\bin\\bash.exe` in the app directory.
- **Casey added `C:\Program Files\Git\bin` to Windows PATH** — this makes bash available globally to cmd.exe, npm, and any other tool. The `.npmrc` approach remains as a fallback but PATH is the cleaner long-term solution.
- `rsync` was attempted for the copy step but is not included with Git Bash on Windows and the winget package (`cwrsync.cwrsync`) no longer exists. Reverted to `cp`/`rm` approach, which works fine for this use case. Scoop (`scoop install rsync`) is the recommended path if rsync is wanted later.
- **PowerShell vs bash for scripting**: For simple build/deploy tasks, bash is the right choice (cross-platform with Mac). For complex logic or structured data, Python is preferred over bash. Node is preferred when already in a JS project context. PowerShell scripts Casey has accumulated will work on Mac via `pwsh` (installable via Homebrew) if needed.

## Final Deploy Output

Successful deploy of ear-tuner to `fiddle-app/ear`:
- `index.html`, `sounds/*.js`, `.gitattributes`
- No SVGs (dev-only UI assets), no markdown, no backlog, no package files
- Live at `https://fiddle-app.github.io/ear/`
