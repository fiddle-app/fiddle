# Fiddle App Family — Umbrella Claude Context

This file is read by Claude Code in every project session under this folder.
It provides shared context that all apps inherit. Do not duplicate this in project-level CLAUDE.md files.

---

## Key References

- [APPS.md](APPS.md) — app registry, folder structure, data flow
- [architecture.md](architecture.md) — platform decisions, tech stack, data architecture, platform adapter, Electron security, deploy pipeline
- [Per-tune markdown format](tune-hub/spec/tune-md-format.md) — frontmatter schema, tonality display rules, default tunings by key

For development process, testing, and folder conventions, see [dev-process.md](../dev-process.md) and [folder-conventions.md](../folder-conventions.md) at the Projects level.

---

## Project Overview

A family of web apps and native apps supporting fiddle learning and practice.
All apps share a consistent look, feel, and data architecture.
GitHub organization: `fiddle-app`. Each app is its own repo.
See [APPS.md](APPS.md) for the full registry, folder structure, and data flow diagrams.

---

## Shared Design System

All apps use the same design tokens, fonts, icons, and sounds defined in `_shared/design/`.
Before writing any UI code, check `_shared/design/` for existing palette, typography, icons, and sounds.
When adding new design elements, add them to `_shared/` first — never define them inline in an app.

---

## Backlog

Managed by the backlog-manager skill ("Barry"). See `backlog.md` in this folder or any app folder.

---

## Licensing & Attribution

Apps will be publicly released, free, with a request for donations (Venmo).
License: requires attribution for derivative works (e.g. CC BY or similar open source license — TBD).
Always include Casey's attribution in generated code headers where appropriate.
