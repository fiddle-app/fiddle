# Spec File Naming Convention

> [!todo] When resolved, update [architecture.md Section 9](../architecture.md#9-development-workflow) and remove the open question callout.

## The Question

Specs are looked up by *what they describe*, not *when they were written*. A date-prefix (`YYYY-MM-DD_feature.md`) doesn't help you find the spec for the timeline segment model. We need an architecture-area prefix convention.

## Proposed Architecture Areas and Prefixes

These are the major areas that specs would cover across the fiddle-app family. Each area gets a short prefix used in spec filenames.

| Prefix | Area | Examples |
|---|---|---|
| `schema-` | Database schema, tables, migrations | `schema-tunes-table.md`, `schema-version-strategy.md` |
| `ui-` | UI components, layouts, interactions | `ui-timeline-scrubbing.md`, `ui-tune-detail-view.md` |
| `data-` | Data flow, inbox pattern, sync | `data-inbox-format.md`, `data-icloud-sync.md` |
| `platform-` | Platform adapter, Electron/Capacitor specifics | `platform-adapter-interface.md`, `platform-folder-watching.md` |
| `store-` | State management, stores, observers | `store-annotation-state.md`, `store-tune-filter.md` |
| `workflow-` | User workflows, multi-step processes | `workflow-annotate-recording.md`, `workflow-jam-session.md` |
| `format-` | File formats, markdown structure, WebVTT | `format-tune-markdown.md`, `format-webvtt-shadow.md` |
| `ipc-` | IPC channels, main/renderer communication | `ipc-file-access.md`, `ipc-db-operations.md` |

### Filename Pattern

```
{prefix}-{descriptive-name}.md
```

All lowercase, hyphens between words, no dates. Examples:
- `schema-tunes-table.md`
- `ui-timeline-splitting.md`
- `platform-adapter-interface.md`
- `format-tune-markdown.md`

### What About Versioning?

Specs evolve. Rather than versioning filenames (`ui-timeline-v2.md`), update the spec in place and let git track the history. The spec always describes the *current* intended behavior.

If a spec is superseded by a fundamentally different approach (not just an update), move the old one to `specs/skulch/` and create a new one.

> [!question] Are these the right area prefixes?
> Review the list above. Are there areas missing? Are any too granular or too broad? Should `ipc-` be folded into `platform-`? Should `store-` be folded into `data-`?

A: 

> [!question] Should retro-specs use the same convention?
> A retro-spec describes the same kind of thing as a pre-spec — just written afterward. Using the same naming convention keeps them indistinguishable in the folder (which is the point — a spec is a spec regardless of when it was written).

A: 

## Per-App vs. Family-Level Specs

Each app has its own `specs/` folder for app-specific specs. The fiddle root could have a `specs/` folder for cross-app specs (schema contracts, shared design tokens, the inbox JSON format). The prefix convention applies to all levels.
