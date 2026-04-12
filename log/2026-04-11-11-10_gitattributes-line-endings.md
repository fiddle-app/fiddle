# Add .gitattributes to all repos — normalize line endings to LF

**Date:** 2026-04-11

## Problem

Every commit on Windows produced warnings like:
```
warning: in the working copy of 'backlog/backlog-done.md', LF will be replaced by CRLF the next time Git touches it
```

Caused by `core.autocrlf = true` set at the local repo level, which triggers Git's automatic LF↔CRLF conversion.

## Fix

- Added `.gitattributes` with `* text=auto eol=lf` to all 7 repos (fiddle parent + ear-tuner, intonio, media-markup, microbreaker, tune-hub, tune-list).
- Removed the local `core.autocrlf` setting from each repo.

This normalizes all text files to LF in both the repo and working copy. All modern Windows editors handle LF fine, so no impact on editing or viewing files.

## Repos affected

All fiddle-app repos. Committed and pushed to main on each.
