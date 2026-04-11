### **The TAD (Test-After Development) Handoff Framework**

In this workflow, the **Coder** builds the feature based on a **Spec**, then generates a **Manifest** that tells the **Tester** exactly what was built. This ensures the Tester doesn't have to "guess" the implementation details while maintaining a "black-box" verification of the original requirements.

---

### **1. Architecture & `CLAUDE.md`**

In a project like your **Fiddle Apps**, `CLAUDE.md` (or a similar `.cursorrules` / `PROJECT.md` file) serves as the **Permanent Memory** for any AI agent entering the repository. You should put the **Architect's Core Rules** and the **Handoff Protocol** here.

#### **`CLAUDE.md` Content**
```markdown
# Fiddle Apps: AI Development Protocol

## 1. Development Philosophy
We follow **Spec-Driven, Test-After Development (TAD)**.
- **No code without a Spec.**
- **No PR without a Handoff Manifest.**
- **No Feature completion without Verified Tests.**

## 2. The Handoff Protocol (TAD)
1. **Architect:** Drafts/updates `/specs/feature-name.md`.
2. **Coder:** Implements logic and UI. MUST include `data-testid` on interactive elements.
3. **Coder:** Generates an **Implementation Manifest** (see template below).
4. **Tester:** Reads Spec + Manifest. Writes Vitest/Playwright tests.
5. **Verification:** Tests must pass before the task is marked "Done."

## 3. Tech Stack Requirements
- **Framework:** Svelte (Vite-native)
- **Runtime:** Electron
- **Unit Testing:** Vitest + Svelte Testing Library
- **E2E Testing:** Playwright (Electron-enabled)
- **State:** Svelte Stores (must include a `.reset()` method for testing).
```

---

### **2. Agent System Prompts**

These prompts define the "persona" and constraints for each agent.

#### **A. The Architect Agent**
*Focus: Alignment and Clarity.*
> "You are the **Lead Architect**. Your goal is to ensure the user's 'vibe' is translated into a technical contract. You are forbidden from writing implementation code. When a user asks for a feature:
> 1. Check `/specs` for a relevant file.
> 2. If it doesn't exist or is outdated, propose a Markdown update.
> 3. Ensure the spec defines: User Goal, Requirements, UI Behavior, and State changes.
> 4. Once the user approves the spec, hand it over to the Coder."

#### **B. The Coder Agent**
*Focus: Execution and Communication.*
> "You are the **Lead Developer**. You build features based on the provided Spec. 
> **Constraints:**
> - Use Svelte and Tailwind.
> - Every interactive element MUST have a `data-testid`.
> - After coding, you MUST generate an **Implementation Manifest** containing:
>   - Modified Files.
>   - Exported Functions/Signatures.
>   - Svelte Stores modified.
>   - List of `data-testid` values added.
>   - Any Electron IPC channels used."

#### **C. The Tester Agent**
*Focus: Adversarial Verification.*
> "You are the **QA Engineer**. Your job is to break the Coder's implementation.
> 1. Read the **Spec** to understand the 'Intent.'
> 2. Read the **Implementation Manifest** to understand the 'Surface Area.'
> 3. Write Vitest tests for logic/stores and Playwright tests for UI.
> 4. If a test fails, provide the error log to the Coder. Do not fix the code yourself; tell the Coder what failed."

---

### **3. The Implementation Manifest (Template)**

The Coder should append this to the chat or save it as `handoff.md` for the Tester.

```markdown
### 🚀 Handoff Manifest: [Feature Name]

**1. Surface Area**
- **Files:** `src/lib/Settings.svelte`, `src/stores/settings.ts`
- **Functions:** `updateVolume(val: number)`, `toggleMute()`

**2. UI Selectors (data-testid)**
- `settings-overlay`
- `volume-slider`
- `mute-toggle-btn`

**3. State Logic**
- Store `settingsStore` now persists to `localStorage`.
- Added `.reset()` to `settingsStore` for clean-state testing.

**4. Electron/IPC**
- `ipcRenderer.send('save-config')` called on modal close.
```

---

### **Summary of the Workflow**

1.  **You:** "Add a gear icon for settings."
2.  **Architect:** Updates `/specs/settings_ui.md`.
3.  **Coder:** Builds the gear icon and modal. Creates the **Manifest**.
4.  **Tester:** Reads the Manifest. Writes a test: `await page.getByTestId('gear-icon-btn').click()`.
5.  **Success:** Tests pass. Your project remains clean, documented, and fully tested.

---
### **Updated Strategy: The Architect-Led Hybrid Workflow**

This strategy balances high-rigidity **Test-After Development (TAD)** for core features with a flexible **"Vibe Code Mode"** for UI iterations, all while maintaining a consistent source of truth through Markdown logging.

---

## **1. Core Development: Adversarial TDD**

For major features or logic (e.g., Fiddle tuning algorithms, state management):

- **Role: Architect (Primary Session):** Operates as the brain. Responsible for research, requirement gathering, and updating `/specs`.
    
- **Role: Coder (Ephemeral Subagent):** Spun up for a single task. It is "adversarial" in that it must satisfy the Architect's spec without having been part of the planning conversation.
    
- **The Handoff:** The Coder produces an **Implementation Manifest** (`handoff.md`) detailing `data-testid` attributes, functions, and state changes for the Tester.
    

## **2. Rapid Iteration: "Vibe Code Mode"**

For minor tweaks, styling, or UI "fiddling" where strict spec-first overhead is inefficient:

- **The Switch:** You may instruct the Architect to enter **"Vibe Code Mode."** * **Direct Action:** In this mode, the Architect can bypass the ephemeral subagent and make minor implementation changes directly in the codebase.
    
- **Retroactive Documentation:** Even in Vibe Mode, the Architect is required to:
    
    1. **Log Changes:** Maintain a running log of file modifications.
        
    2. **Retro-Spec:** Be prepared to generate a formal spec _after_ the fact to document the new behavior.
        
    3. **Handoff Generation:** Produce a manifest so the **Tester** can eventually verify the changes.
        

## **3. Verification: The Gatekeeper**

- **Manual Trigger:** The **Tester** (manual terminal or ephemeral subagent) is only engaged when the feature is ready for verification or before a major commit.
    
- **Consistency:** The Tester always compares the **Handoff Manifest** against the **Spec** (whether the spec was written before or after the code).
    

---

## **4. Updated `CLAUDE.md` Instructions**

Markdown

```
# Fiddle Apps: Hybrid Development Protocol

## 1. Primary Workflow: Spec-First
- **Architect:** Primary session handles planning and specs in `/specs`.
- **Coder:** Use ephemeral subagents for implementation. 
- **Requirement:** No major implementation without a Spec and a Handoff Manifest.

## 2. "Vibe Code Mode" (Exception Rule)
- For minor UI tweaks/styling, the Architect may implement changes directly.
- **Constraint:** Architect must log changes to `docs/internal/vibe_log.md`.
- **Requirement:** Upon exiting Vibe Mode, Architect must retroactively update the relevant `/specs` and generate a Handoff Manifest for the Tester.

## 3. Implementation Standards
- **Environment:** Windows PowerShell (use valid PS commands).
- **Testing:** Vitest for logic; Playwright for UI.
- **Selectors:** Use `data-testid` for all interactive elements to facilitate adversarial testing.
- **State:** Svelte Stores must include a `.reset()` method for test isolation.

## 4. Handoff Manifest Template
Every completion of a feature (via Subagent or Vibe Mode) must provide:
- **Files Modified:** [List]
- **Key Functions/Signatures:** [List]
- **data-testid Attributes:** [List]
- **IPC Channels:** [Electron specific channels]
```

---

## **5. Sample System Prompts**

### **The Architect (Primary Terminal)**

> "You are the Lead Architect for Fiddle Apps. Your primary mode is **Spec-First**: draft a spec, then delegate to an ephemeral sub-coder. However, if the user requests **'Vibe Code Mode'**, you may perform minor implementation changes directly. While in Vibe Mode, you must track every change and be prepared to retroactively produce a Spec and a Handoff Manifest before the task is considered finished."

### **The Coder (Ephemeral Subagent)**

> "You are a specialized Coder subagent. You will receive a Spec from the Architect. Implement the logic using Svelte and Electron. You must use `data-testid` for all UI elements. Your final output must be the code and an Implementation Manifest summarizing your work for a separate Tester agent."

### **The Tester (Verification Mode)**

> "You are a QA Engineer. Your goal is to verify the code against the Spec. Read the `handoff.md` to find the `data-testid` selectors and function signatures. Run Vitest and Playwright. Report failures to the Architect; do not attempt to fix the code yourself."

---

## Claude's Evaluation (2026-04-11)

### Summary

This document proposes an elaborate multi-agent testing workflow (Architect → Coder → Tester handoff) with formal specs, implementation manifests, and adversarial verification. It was generated by Gemini and assumes a Svelte + Tailwind stack that contradicts the project's established conventions. The process design is enterprise-grade and far too heavy for a solo developer building personal-use apps. However, there are some good ideas buried in the ceremony.

### What's Useful

1. **`data-testid` on interactive elements.** This is a genuinely good practice. It decouples tests from CSS classes and DOM structure, making tests stable through UI refactors. Worth adopting as a convention even without the rest of this framework.

2. **The concept of a handoff manifest (lightweight version).** Not the full template proposed here, but the idea of the AI summarizing what it built — files changed, key functions, IPC channels used, how to test it — is valuable. This is essentially what a good commit message plus a brief PR description already provides. The project's existing `/log` skill already captures session summaries. No new artifact type is needed.

3. **Store `.reset()` for test isolation.** If the project uses observable stores (which it will, per CLAUDE.md's observer/callback pattern), having a reset method for test setup is practical.

4. **Vitest for unit testing.** Vitest is a reasonable choice. It's fast, works with ES modules natively, and doesn't require a framework. This recommendation stands independent of the Svelte assumption.

5. **Playwright for E2E testing.** Playwright handles Electron's multi-process architecture well, which matters for Tune Hub and Media Markup. Correct recommendation.

### What Conflicts with Established Plans

1. **Assumes Svelte + Tailwind.** The CLAUDE.md and entire `testing_strategy.md` are written for a Svelte project. The fiddle-app family uses vanilla JS. The proposed CLAUDE.md content would overwrite critical project conventions (platform adapter pattern, WPA→Swift portability rules, coding conventions, design system integration) with framework-specific instructions.

2. **Multi-agent orchestration is overkill.** The Architect/Coder/Tester agent separation with formal handoffs makes sense for a team. For a solo developer working with one AI assistant (Claude Code), this creates process overhead that slows development without proportional quality gains. Casey can review code directly; Claude Code can write tests in the same session that wrote the feature. The "adversarial" value comes from testing, not from agent separation.

3. **Spec-first mandate ("No code without a Spec").** For core data models and cross-app contracts (e.g., the tune markdown format, inbox JSON schema, SQLite schema), specs are valuable and already exist in CLAUDE.md and APPS.md. For UI features and iteration, requiring a formal spec document before any code is written creates friction that kills momentum — especially in a personal project where the developer is also the product owner and can change direction instantly.

4. **"Vibe Code Mode" as a workaround reveals the problem.** If the process is rigid enough that you need a formal escape hatch for minor tweaks, the process is too rigid. The right default should be lightweight, with formality added where it earns its keep (data schemas, cross-app contracts, platform adapter interfaces).

### Alternative Strategy: Right-Sized Testing for a Solo Developer

**Principle:** Test what's expensive to break manually. Don't test what's cheap to verify by using the app.

**Tier 1 — Always test (unit tests, Vitest):**
- SQLite schema migrations and queries (data corruption is the worst bug)
- Platform adapter interface contracts (if the adapter breaks, the wrong platform code runs)
- JSON schema validation (inbox files, tune markdown frontmatter parsing)
- Any pure-function business logic (tune filtering, key/mode display rules, status sorting)

**Tier 2 — Test when stable (E2E tests, Playwright):**
- Critical user workflows in Electron apps (Tune Hub CRUD, MM segment creation)
- Cross-app data flow (TuneList reads what TuneHub writes)
- Add these once the UI is settled, not during initial prototyping

**Tier 3 — Don't bother testing:**
- CSS styling and layout (verify visually)
- One-off UI interactions during rapid iteration
- Anything that changes faster than the test can be maintained

**Process:** No formal specs directory. The CLAUDE.md, APPS.md, and per-app CLAUDE.md files already serve as living specs. Claude Code writes feature code and tests in the same session. If a feature is complex enough to need a written plan, use Claude Code's plan mode — it's built for this and doesn't require a separate artifact.

### Verdict (initial)

Adopt `data-testid`, Vitest, and Playwright. Adopt the tiered testing approach above. Discard the multi-agent orchestration, formal spec directory, handoff manifests, and Svelte-specific conventions. The existing project documentation (CLAUDE.md + APPS.md) already provides the "permanent memory" this document tries to create with its proposed CLAUDE.md replacement.

---

## Revised Position: The Spec-Driven Mode Compromise (2026-04-11)

After discussion with Casey, the evaluation above is revised. The original critique was correct that the Gemini proposal's *defaults* were wrong, but too aggressive in discarding the *mechanisms*. The revised approach:

### Development Modes

**Default: Vibe Coding.** Normal interactive development with Claude Code. No spec required. No handoff manifest. Just build the thing, iterate, ship. This is how most work gets done.

**Opt-in escalation: Spec-Driven Mode.** Casey explicitly invokes this for features that are complex enough to benefit from thinking-it-through-first. The workflow:

1. **Casey + Claude (Architect role):** Discuss the feature, explore options, make decisions. Claude captures the result as a **spec** in the app's `specs/` folder. The spec must be complete enough that a coder subagent with no conversation context could implement from it.
2. **Coder subagent:** Receives the spec and implements it. The isolation is the point — it validates that the spec is actually complete. If the subagent has to guess, the spec had gaps.
3. **Coder produces a handoff manifest:** Files changed, functions added, `data-testid` values, IPC channels, state changes. This is nearly free for the agent to generate and useful for verification.
4. **Casey reviews.** If tests are warranted (Tier 1 or Tier 2 work), they can be written now against the manifest, either in the same session or by a tester subagent.

**Optional further escalation: Adversarial Test Pass.** For the highest-risk work (schema migrations, platform adapter contracts, cross-app data flow), a separate tester subagent reads the spec + manifest and writes tests without having seen the implementation conversation. This is the Gemini document's "adversarial verification" idea, reserved for where it earns its keep.

### Why Specs Have Lasting Value

The original evaluation missed an important argument: **specs survive as documentation source material.** After an app stabilizes, its `specs/` folder contains feature-level descriptions of what the app does, why, and how. This is the seed for user documentation — not a throwaway development artifact. The spec doesn't need to cover every UI detail, but it should capture:

- What the feature does and why it exists
- Major states and state transitions
- Data structures and contracts
- Platform-specific behavior differences (Electron vs. Capacitor)

This is the "Tier 1 stuff and major states and state changes" that Casey identified as worth documenting regardless.

### What Changes from the Original Gemini Proposal

| Gemini Proposal | Revised Approach |
|---|---|
| Spec-first is the default | Vibe coding is the default; spec-driven is opt-in |
| "Vibe Code Mode" is an exception requiring retroactive docs | Vibe coding requires nothing — it's just normal work |
| Architect/Coder/Tester always engaged | Only Coder subagent in spec-driven mode; Tester only for high-risk work |
| Assumes Svelte + Tailwind | Stack-agnostic; uses project's vanilla JS conventions |
| Formal `vibe_log.md` tracking | No tracking for vibe work; session logs already exist via `/log` |
| Proposed CLAUDE.md replacement | Spec-driven mode documented in CLAUDE.md as an available workflow, not a mandate |

### Spec Format (Proposed)

```markdown
# Feature: [Name]

## Purpose
Why this feature exists. What problem it solves.

## Requirements
- Functional requirements (what it must do)
- Data requirements (what it reads/writes, schemas)
- Platform requirements (Electron-specific, Capacitor-specific)

## States and Transitions
Major states the feature can be in, and what causes transitions.

## Constraints
- Security (CSP, contextIsolation)
- Performance (if relevant)
- Portability (platform adapter boundaries)

## Out of Scope
What this feature explicitly does NOT do.
```

### Handoff Manifest Format (Proposed)

```markdown
# Handoff: [Feature Name]

## Files Modified
- path/to/file.js — what changed

## Key Functions / Exports
- functionName(params) — what it does

## UI Selectors (data-testid)
- testid-name — what element

## State Changes
- storeName — what's new or changed

## IPC / Platform Adapter
- channel or method — what it does

## How to Verify
- Steps to manually confirm the feature works
```

### Writing Tests Without a Spec (Post-Hoc Testing for Vibe-Coded Work)

Not all testable work goes through spec-driven mode. When vibe-coded features reach stability and you want tests, the question is: where does the tester get its knowledge?

**What works without a spec:**
- **Pure functions, store logic, data transformations, queries.** The function signature and its callers tell you what it should do. A tester agent can read the code and write tests directly.
- **State machines and workflows.** The code shows states and transitions. Combined with the app's CLAUDE.md, this is usually enough.

**What doesn't work well without a spec:**
- **Edge cases and error handling.** The code shows what *does* happen, not what *should* happen. A tester writing from code alone will verify current behavior, which may include accidental behavior nobody thought about.

**The mitigation: "flag what you had to guess."** When a tester agent (or Claude in the main session) writes tests from code, it should flag any test where it had to infer design intent. These flags are exactly the edge cases that would have been in a spec — and resolving them retroactively is still valuable.

**Mechanics — three options, increasing formality:**

1. **Same session.** "Write tests for the segment creation workflow." Claude already has context from the session, knows what was built, writes tests. Lowest friction. Downside: in long sessions, early context may have been compressed.

2. **Later session.** "Write tests for MM's segment model." Claude reads the code, reads CLAUDE.md, reads existing test patterns, writes tests. Works well but may miss intent on edge cases.

3. **Tester subagent.** Claude spawns a subagent briefed with: "Read these files. Read the app's CLAUDE.md. Write Vitest tests covering the public API, state transitions, and error cases. Flag anything where you had to guess at intended behavior." The subagent returns tests plus a list of ambiguities for Casey to resolve.

Option 3 is the sweet spot for post-hoc Tier 2 testing. The flagged-ambiguities list turns the testing pass into a design-intent audit.

### The Retro-Spec: Bridging Vibe Coding and Documentation

When vibe coding produces work worth documenting (most Tier 1 and Tier 2 features), a **retro-spec** closes the gap. It's the same artifact as a pre-spec — same format, same `specs/` folder — just written after the code instead of before it.

**The development rhythm:**

```
vibe code → retro-spec → commit → repeat
```

The retro-spec serves three purposes:
1. **Pause to reflect.** Forces a "wait, is this actually right?" check before committing.
2. **Documentation seed.** The `specs/` folder accumulates feature-level descriptions that seed user docs later.
3. **Commit substance.** The commit message summarizes the retro-spec and references it, giving the git history real explanatory power.

**Tooling: two separate skills.**

- **`/retro-spec`** — Diffs against HEAD, reads changed files, writes a spec to `specs/` describing what was built. Presents it for Casey's review before saving.
- **`/commit`** — Already exists. When a retro-spec was just written in the same session, the commit message naturally references it. No special wiring needed.

These are kept separate because sometimes you retro-spec but aren't ready to commit (want to review/adjust), and sometimes you commit without a retro-spec (trivial changes). But the expected common case is invoking them as a pair.

A combined `/checkpoint` skill (retro-spec → stage → commit in one pass) may be added later if the paired rhythm proves consistent.

**Open question: spec file naming convention.** Date-prefix (`YYYY-MM-DD_feature-name.md`) works for chronological research notes, but specs are looked up by *what they describe*, not *when they were written*. An architecture-feature convention (e.g., `ui-timeline-splitting.md`, `schema-sources-table.md`) may fit better. This needs a dedicated discussion before the `specs/` folder accumulates files. Deferred to a future conversation.

### Next Steps

1. Document the development workflow (vibe coding default, spec-driven opt-in, retro-spec rhythm) in the fiddle-level CLAUDE.md as an available process. It's experimental — Casey may abandon it if the overhead doesn't pay off. The key is that it's opt-in, so abandoning it costs nothing.
2. Build the `/retro-spec` skill.
3. Decide on `specs/` file naming convention (separate conversation).