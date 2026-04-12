# GitHub & Submodules Plan

## Repo Structure

Each app gets its own GitHub repo with its own top-level URL (via GitHub Pages when published). The family repo is a separate repo that serves as the parent backlog and potentially a public landing page.

## Submodules

Child app folders live inside the parent folder on disk, wired in as **git submodules**. This gives a stable relative folder hierarchy, which is required for cross-reference hyperlinks in the backlogs to resolve correctly in VS Code's markdown preview.

Setup is a one-time task — plan to use Claude Code with the GitHub connector to get the submodule wiring done correctly.

## Day-to-Day Git Workflow

- **Editing a child repo** (e.g. Ear Tuner): commit and push from VS Code as normal. Done.
- **Parent submodule pointer**: will show as a pending change in the parent repo after a child is pushed. No need to update it every time — treat it as occasional housekeeping, e.g. when doing family-level backlog work.
- **No need to push siblings** when pushing a child.