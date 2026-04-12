# 2026-04-12-11-49 Dev Process Refinement

**2026-04-12**

Casey had a conversation with Gemini about token-efficient multi-agent development workflows. The output was a "Distributed Architect-Coder Framework" proposing inbox-driven communication, ctags-based skeleton context, and formalized system prompts for Architect/Coder/Tester roles. Casey asked me to evaluate it against what we already have in `architecture.md` Section 9.

## Evaluation of Gemini's Framework

Wrote a detailed assessment appended to `research/More Dev Process from Gemini.md` (Section 7). Key conclusions:

- **Skeleton context (ctags):** Worth stealing partially. Generate on demand during spec writing, not as a persistent file. Raw ctags misses JSDoc — a custom `tags-to-skeleton.js` script that pulls JSDoc from source is the right approach.
- **Inbox folders:** Over-engineered for a solo developer who manually starts each session. Existing specs + handoff manifests serve the same purpose.
- **Manual Coder terminal (Casey's idea, not Gemini's):** The most pragmatic suggestion. Casey drives a second Claude Code terminal for implementation, then hands results back to the Architect session. Better than automated subagents for interactive/exploratory work.
- **Spec-driven mode more often:** Yes, selectively — any time work crosses module or app boundaries.

## Architecture.md Updates

Several substantial additions based on the evaluation and follow-up discussion:

### JSDoc Convention (Section 2)
Added a formal JSDoc requirement for all exported functions and public class methods. Serves triple duty: IDE intellisense, skeleton generation, and subagent context. Internal helpers exempt. This wasn't previously documented anywhere.

### Spec vs. Brief Separation (Section 9)
Casey identified a real problem: specs were serving as both durable design documentation and disposable coder work orders. These have different lifespans and audiences. The fix:

- `specs/` — permanent design records (what and why). Never deleted after implementation.
- `handoffs/` — all ephemeral workflow artifacts, distinguished by suffix:
  - `*.brief.md` — architect-to-coder work orders (references the spec, adds implementation instructions)
  - `*.done.md` — coder-to-architect delta reports
  - `*.test.md` — coder-to-tester test artifacts

This was the most important design decision of the session. The original architecture.md had specs doing double duty, which would have led to either specs being deleted (losing design history) or specs accumulating coder-specific cruft.

### Manual Coder Terminal (Section 9)
Documented the workflow: Architect writes spec + brief, Casey opens a second terminal and drives implementation interactively, then runs `/handover` to generate the done artifact.

### Other Additions
- Concrete trigger table for when to use spec-driven mode (cross-module, schema migrations, platform adapter, cross-app data flow, new stores, contracts)
- `/handover` skill concept (git-diff-based extraction, writes handoffs/*.done.md)
- Codebase skeleton generation section (ctags workflow, when to use, Markdown output format)
- Coder subagent prompt updated for spec+brief separation and JSDoc requirement
- Retro-spec section clarified as durable (no brief needed)

### Spec Format and Brief Format
Added the Brief format template alongside the existing Spec format, with clear labels: spec is "Durable — specs/", brief is "Ephemeral — handoffs/*.brief.md".

## Backlog Items Added
- **P11:** Build the `/handover` skill
- **C17:** Build `tags-to-skeleton.js` script
