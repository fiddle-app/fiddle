# Implementation Plan: GitHub & Submodule Setup (20260405-2025)

## Objective
Establish a structured GitHub ecosystem for the "Fiddle App Family" using separate repositories for each app and a parent "family" repository to manage the overall backlog and shared context via Git submodules.

## Key Files & Context
- **Root Directory:** `C:\Users\CaseyM\OneDrive\Projects\fiddle`
- **Log Filename:** `log\20260405-2025-github-submodule-setup.md`
- **SSH Alias:** `github.com-fiddle` (mapped to `fiddle-app` account)
- **Email Identity:** `microbreaktimer@gmail.com` (configured via `gitdir` in `~/.gitconfig`)
- **App Folders (to be submodules):**
  - `_shared`
  - `ear-tuner`
  - `microbreaker`
  - `media-markup`
  - `tune-hub`
  - `tune-list`

## Phase 0: Renaming & Prep
1.  **Rename Folder:** Rename `music-markup` to `media-markup`.
2.  **Update References:** Replace "music-markup" with "media-markup" in:
    - `APPS.md`
    - `CLAUDE.md`
    - `media-markup/CLAUDE.md`
    - `github_repo_plan.md`

## Phase 1: Initialize and Push Child Repositories
For each child directory (`_shared`, `ear-tuner`, `microbreaker`, `media-markup`, `tune-hub`, `tune-list`):

1.  **Initialize Git:** `git init`
2.  **Initial Commit:** `git add .`, `git commit -m "initial commit"`
3.  **GitHub Creation:** Create a new repository on GitHub under the `fiddle-app` account with the same name as the folder. (Using `gh repo create fiddle-app/<repo-name> --public --source=. --remote=origin --push` if available, otherwise manual creation).
4.  **Set Remote and Push:** If not done by `gh`, then `git remote add origin git@github.com-fiddle:fiddle-app/<repo-name>.git` and `git push -u origin main`.

## Phase 2: Initialize and Push Parent Repository
In the root `fiddle` directory:

1.  **Prepare .gitignore:** Create a `.gitignore` to exclude local environment files and temporary logs.
    ```text
    # Note: Child folders will be managed as submodules
    ```
2.  **Initialize Git:** `git init`
3.  **Initial Commit (Umbrella files + Minions):** `git add .` (ensuring child folders are NOT staged yet if they were already git-initialized), `git commit -m "initial commit (parent backlog and minions)"`
4.  **GitHub Creation:** Create a new repository `fiddle-app/fiddle` on GitHub.
5.  **Set Remote and Push:** `git remote add origin git@github.com-fiddle:fiddle-app/fiddle.git`, `git push -u origin main`.

## Phase 3: Wire Submodules
In the root `fiddle` directory:

1.  **Add Submodules:** For each child repository, add it as a submodule.
    *Recommended approach for existing folders:*
    1. Move `folder` to `folder_tmp`.
    2. `git submodule add git@github.com-fiddle:fiddle-app/<repo-name>.git <folder>`
    3. If there were uncommitted local changes, merge from `folder_tmp` and remove it.
2.  **Commit Submodule Registration:** `git add .gitmodules`, `git commit -m "wire app submodules"`, `git push`.

## Verification & Testing
- Run `git remote -v` in each folder to ensure the correct SSH alias is used.
- Verify `git config user.email` returns `microbreaktimer@gmail.com` in all repos.
- Confirm submodules are correctly listed on GitHub in the `fiddle` repository.
- Verify relative links in `backlog.md` resolve correctly in VS Code.

## Results & Completion

**Completed:** 2026-04-05
**Executed by:** Claude (claude-sonnet-4-6) in Claude Code Desktop

---

### Pre-flight Issues Resolved

**`gh` CLI not in Git Bash PATH**
`gh` was installed via `winget install GitHub.cli` but the Git Bash shell (used by Claude Code Desktop) did not inherit the Windows PATH entry. Fixed by creating `~/.bashrc` with:
```bash
export PATH="$PATH:/c/Program Files/GitHub CLI"
```
This file did not previously exist. It will be sourced automatically in future bash sessions.

**UTF-8 BOM in `~/.ssh/config`**
The SSH config file had a UTF-8 BOM (byte order mark), causing SSH to reject it with `Bad configuration option: \357\273\277host`. Removed the BOM using PowerShell `[System.IO.File]::ReadAllBytes` / `WriteAllBytes`. SSH key routing then worked correctly for all operations.

---

### Phase 1: Child Repositories

All 6 child repos initialized, committed, and pushed to `fiddle-app` on GitHub.

| Repo | GitHub URL | Initial Commit |
|------|-----------|----------------|
| `_shared` | https://github.com/fiddle-app/_shared | a5da99b |
| `ear-tuner` | https://github.com/fiddle-app/ear-tuner | fe766eb |
| `microbreaker` | https://github.com/fiddle-app/microbreaker | cb63cae |
| `media-markup` | https://github.com/fiddle-app/media-markup | 9500614 |
| `tune-hub` | https://github.com/fiddle-app/tune-hub | a7583be |
| `tune-list` | https://github.com/fiddle-app/tune-list | efe442f |

**Deviation:** The first push to `_shared` failed on first attempt due to the SSH BOM issue (fixed above). The second push to `ear-tuner` failed on the first attempt due to a brief GitHub propagation delay after repo creation; a retry succeeded. All subsequent repos used a 3-second sleep before push to avoid this.

---

### Phase 2: Parent Repository (`fiddle`)

- Created `~/.gitignore` at the fiddle root to exclude child app folders (before submodule registration) and `.claude/settings.local.json`.
- Staged and committed: `.claudeignore`, `.gitignore`, `APPS.md`, `CLAUDE.md`, `GEMINI.md`, `MM and TuneHub notes.md`, `backlog-readme.md`, `backlog.md`, `log/` (all files), `minions/` (all files).
- GitHub repo created and pushed: https://github.com/fiddle-app/fiddle (commit e69d93c).

**Deviation:** `.claude/settings.local.json` was initially staged by `git add .` and removed before committing. Added to `.gitignore`.

---

### Phase 3: Submodule Wiring

- Removed child folder exclusions from `.gitignore`.
- Ran `git submodule add git@github.com-fiddle:fiddle-app/<name>.git <folder>` for each of the 6 repos.

**Deviation from plan:** The `mv folder folder_tmp` step failed for all folders with "Permission denied" — OneDrive appears to lock directories while syncing. Git handled this gracefully: it detected that each path was already a git repo and printed "Adding existing repo at '<folder>' to the index", registering the submodule without needing to clone. All 6 submodule entries were correctly written to `.gitmodules`.

**OneDrive index.lock conflict:** After committing, a stale `index.lock` file repeatedly appeared in the parent `.git` directory (OneDrive syncing the `.git` folder). Resolved by deleting the lock file with PowerShell `[System.IO.File]::Delete()` and immediately running the commit in the same pipeline to minimize the race window. Push succeeded.

Commit: d1b04f0 — "wire app submodules"

---

### Final State

| Repo | Remote | Identity |
|------|--------|----------|
| `fiddle` (parent) | `git@github.com-fiddle:fiddle-app/fiddle.git` | fiddle-app \<microbreaktimer@gmail.com\> |
| `_shared` | `git@github.com-fiddle:fiddle-app/_shared.git` | fiddle-app \<microbreaktimer@gmail.com\> |
| `ear-tuner` | `git@github.com-fiddle:fiddle-app/ear-tuner.git` | fiddle-app \<microbreaktimer@gmail.com\> |
| `microbreaker` | `git@github.com-fiddle:fiddle-app/microbreaker.git` | fiddle-app \<microbreaktimer@gmail.com\> |
| `media-markup` | `git@github.com-fiddle:fiddle-app/media-markup.git` | fiddle-app \<microbreaktimer@gmail.com\> |
| `tune-hub` | `git@github.com-fiddle:fiddle-app/tune-hub.git` | fiddle-app \<microbreaktimer@gmail.com\> |
| `tune-list` | `git@github.com-fiddle:fiddle-app/tune-list.git` | fiddle-app \<microbreaktimer@gmail.com\> |

All submodules appear as gitlinks (mode `160000`) in the `fiddle` repo on GitHub.
Git identity is `fiddle-app <microbreaktimer@gmail.com>` across all repos (via `~/.gitconfig-fiddle` `includeIf` directive).

**Note on OneDrive + Git:** The `.git` folder is being synced by OneDrive, which causes intermittent lock file conflicts. Consider adding `.git` folders to OneDrive's exclusion list (via "Files On-Demand" or selective sync) to prevent future interference.
