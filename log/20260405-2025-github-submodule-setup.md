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

## Results & Completion (APPENDED LATER)
(Section for appending completion logs)
