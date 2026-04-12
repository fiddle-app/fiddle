I talked to Gemini about the token efficiency of using subagents vs doing all of the work in the terminal of a single Architect agent. This is a summary of what we came up with.
# Protocol: The Distributed Architect-Coder Framework

## 1. The "Why": Token Efficiency and Logic Isolation

In large-scale coding, a monolithic context (one agent doing everything) inevitably leads to **Context Bloat**. As terminal outputs, failed attempts, and verbose implementation details accumulate, the agent’s reasoning "dilutes," leading to hallucinations and ignored instructions.

This system solves for efficiency by:

- **Separating Concern from Implementation:** The "Architect" knows _what_ the system does; the "Coder" knows _how_ a specific function works.
    
- **Stateless Subagents:** Coder agents are "ephemeral." They receive only the files they need, execute, and dissolve, preventing the accumulation of "thought tokens."
    
- **Skeleton Context:** The Architect operates on a "high-level map" (signatures and JSDoc), reducing context size by **70–90%**.
    

---

## 2. The "How": The Inbox-Driven Workflow

Communication is asynchronous and file-based. Instead of long-running chats, agents communicate via messages placed in specific folders.

### The Human-in-the-Loop "Vibe" Session

For UI Tweaking, the developer spins up a **User-Interactive Coder** (UI-Coder).

1. **Iteration:** The human and UI-Coder iterate rapidly in a dedicated terminal (e.g., "move this 5px left").
    
2. **Continuity:** The UI-Coder maintains the session context for visual consistency.
    
3. **Handoff:** Once the "vibe" is correct, the human triggers a "Close Session" command.
    
4. **Artifact Generation:** The UI-Coder generates a **Delta Report** for the Architect and a **Test Artifact** for the Tester before the session is terminated.
    

---

## 3. The Handover Message System

All inter-agent communication uses a standardized file format and naming convention:

`YYYYMMDD-HHmmss_{description}-[Target].md`

- **Targets:** `A` (Architect), `C` (Coder), `T` (Tester).
    
- **Work Chunk ID:** The filename (minus the target suffix) serves as the persistent ID across all agents to track a single feature or bug fix.
    
- **Location:** `./agents/inbox-[role]/`.
    

---

## 4. System Prompts

### Architect System Prompt

Markdown

```
## Role: Lead Software Architect
You are the primary intelligence for the "Fiddle Apps" development environment.

## Context Management
- You operate using a "Skeleton Map" (signatures, exports, and JSDoc) rather than full source code.
- Your "memory" is driven by your inbox: `./agents/inbox-architect/`.

## Operational Rules
1. Check your inbox at the start of every session for new Work Chunks.
2. When a Coder/UI-Specialist reports a "Signature Delta," update your internal representation of the Skeleton Map immediately.
3. Your primary output is a "Technical Brief" for a Coder subagent. You must define the Work Chunk ID.
4. If a task is complex, break it into multiple Work Chunks.
5. Do not write implementation code; focus on module boundaries, data flow, and interface contracts.
```

### Coder / UI-Specialist System Prompt

Markdown

```
## Role: Implementation Specialist
You are an ephemeral worker responsible for executing specific Technical Briefs.

## Context Management
- You are "stateless." Do not assume you remember previous tasks unless they are part of the current active Work Chunk ID.
- Your inputs are found in `./agents/inbox-coder/`.

## Operational Rules
1. Execute the code changes specified in the Technical Brief.
2. After completion, you MUST generate two artifacts:
   - A "Signature Delta Report" for the Architect: List any new, deleted, or modified function signatures/exports.
   - A "Test Artifact" for the Tester: Provide specific inputs, expected outputs, and state requirements for validation.
3. If this is a UI Vibe Session, maintain continuity with the human until they signal a "Session Close."
```

---

## 5. Automation: Skills and Scripts

To make this system work, the environment needs "Skills" (orchestrated by Python or PowerShell).

### Technical Brief: Dev Process Setup Agent

**Objective:** Build a suite of automation tools to manage the Architect-Coder workflow.

**Required Scripts/Functions:**

1. **`Sync-Skeleton` (Skill):** - _Input:_ Source directory (`/src`).
    
    - _Action:_ Run `ctags` or a custom parser to extract exports, class names, and JSDoc.
        
    - _Output:_ A clean Markdown Skeleton file for the Architect.
        
2. **`Compare-Signatures` (Skill):**
    
    - _Action:_ Compare the `tags` file from _before_ a coder session to the one _after_.
        
    - _Output:_ Automatically generate a "Signature Delta Report" if changes are detected.
        
3. **`Send-Message` (Skill):**
    
    - _Action:_ A CLI utility to package a Technical Brief, the relevant source files, and any dependency skeletons into the correct `inbox-coder` folder.
        

---

## 6. Example Artifacts

### Example: Technical Brief (Architect -> Coder)

Markdown

```
# Work Chunk: 20260412-1100_AddTunerCalibration
**Target:** Coder
**Status:** Priority

## Objective
Implement the `calibrate(baseFrequency)` method in `AudioEngine.js`.

## Requirements
- Reference `FiddleMath.js` (Skeleton attached) for frequency offsets.
- Update internal state `isCalibrating` to true during execution.
- Export the new method as part of the `AudioEngine` module.

## Files Attached
- `src/audio/AudioEngine.js` (Full Source)
- `docs/skeletons/FiddleMath.md` (Skeleton Only)
```

### Example: Delta Report (Coder -> Architect)

Markdown

```
# Delta Report: 20260412-1100_AddTunerCalibration
**Target:** Architect

## Signature Changes
- **Added:** `AudioEngine.calibrate(baseFrequency: number): Promise<boolean>`
- **Modified:** `AudioEngine.init()` now accepts an optional `calibrationData` object.

## Implementation Notes
Successfully integrated the calibration logic. The `isCalibrating` flag is correctly toggled via a private setter.
```

### Example: Test Artifact (Coder -> Tester)

Markdown

```
# Test Artifact: 20260412-1100_AddTunerCalibration
**Target:** Tester

## Test Case: Standard Calibration
1. Initialize `AudioEngine`.
2. Call `calibrate(440)`.
3. Verify that `AudioEngine.getFrequency()` returns 440 with 0 deviation.

## Test Case: Edge Case
- Call `calibrate(0)`.
- **Expected Result:** Method should throw an `InvalidFrequencyError`.
```

---

## 7. Claude's Take (2026-04-12)

Casey asked me to evaluate this Gemini framework against what we already have in `architecture.md` Section 9. Here's my honest assessment, question by question.

### Should You Switch to Spec-Driven Mode More Often for Token Efficiency?

**Short answer: sometimes, but not because of Gemini's framework — because of what you already have.**

The token efficiency argument is real. A monolithic session where the Architect watches 200 lines of terminal output from `npm install` or reads through implementation diffs *does* dilute context. But the fix isn't necessarily the full Gemini protocol — it's the discipline of separating "thinking about what to build" from "building it."

Your existing spec-driven mode already captures this benefit. The spec is the compressed handoff artifact. The subagent gets a clean context. The Architect never sees the implementation noise. That's the 80% win.

Where I'd nudge you: **use spec-driven mode any time you're touching more than one module or any cross-app boundary.** Not because of a formal rule, but because those are the tasks where context bloat actually hurts. Single-file UI tweaks? Vibe code them. Adding a new IPC channel that touches preload, main, and renderer? Spec it first. The token savings are a side effect of better thinking, not the other way around.

### The Manual Coder Terminal (Casey's Idea)

This is actually the most pragmatic idea in the conversation, and it's yours, not Gemini's.

Here's why it works: **you are a better orchestrator than any automation layer.** When you drive the Coder terminal yourself, you provide real-time judgment — "no, not that approach," "use the existing helper in utils.js" — that no inbox file can convey. The Coder gets your feedback loop. Then you bring the results (a commit, a diff, a summary) back to the Architect context.

This is essentially what Claude Code's subagent system already does with worktree isolation, but with you as the router instead of an automated dispatch. The advantage: you see everything. The disadvantage: you're doing the work of context-switching between terminals.

**My recommendation:** Do this when you want hands-on control of the implementation (UI work, exploratory prototyping). Use automated subagents (the existing spec-driven mode) when the spec is tight enough that you trust a subagent to execute without your real-time steering. Both are valid — they're not competing approaches, they're different tools for different situations.

### The Inbox Pattern

Over-engineered for your situation. Here's why:

The inbox pattern solves a real problem: **asynchronous coordination between agents that run on independent schedules.** Think CI bots, nightly builds, or a team of agents that wake up and check for work. That's not your workflow. You are the scheduler. You start each session manually. You know what was done because you were there (or you read the commit log).

What the inbox pattern is really doing is giving structure to handoff artifacts. You already have that — it's the spec + handoff manifest in `architecture.md` Section 9. The spec goes in `specs/`. The manifest comes back from the Coder. That's the same data flow without the `agents/inbox-architect/` folder hierarchy and the timestamped filenames.

If you ever move to a world where agents run autonomously (e.g., Larry doing overnight tune research, or a CI agent that runs tests and reports back), *then* an inbox makes sense. For now, `specs/` and commit messages are your inbox.

### The Skeleton Pattern and ctags

This is the most interesting idea in the document, and the one most worth stealing — but with caveats.

**What it gets right:** The Architect doesn't need to see implementation bodies. Function signatures, exports, class structures, and JSDoc comments are sufficient to make architectural decisions. A skeleton reduces a 500-line module to maybe 30 lines of signatures. That's a genuine context savings.

**Would ctags work for your codebase?** For vanilla JS with ES modules and classes, ctags (specifically Universal Ctags) does a reasonable job extracting:
- `export class ClassName`
- `export function functionName`
- Method definitions within classes
- `export const` / `export default`

It won't capture JSDoc, parameter types in comments, or the observer/callback patterns that are central to your architecture. A custom parser (even a simple regex-based one) that extracts exports + JSDoc would be more useful than raw ctags.

**But here's the thing:** Claude Code already has on-demand skeleton capability. When I'm in Architect mode, I can `Grep` for exports, `Read` specific files, and build a mental model on the fly. A pre-generated skeleton file is a snapshot that goes stale the moment someone edits a file. On-demand exploration is always current.

**Where a skeleton *would* help:** When spinning up a fresh subagent (Coder or Tester) that needs to understand module boundaries without reading every file. The skeleton becomes part of the spec handoff — "here's what the codebase looks like, here's what you're changing." That's a legitimate use. But I'd generate it on demand as part of the spec-writing step, not maintain it as a persistent artifact.

### Bottom Line

| Gemini Idea | Verdict | Why |
|---|---|---|
| Skeleton context for Architect | **Steal partially** — generate on demand during spec writing, don't maintain a persistent file |  |
| Inbox folders for handoff | **Skip** — your existing specs/ + handoff manifest + git commits serve the same purpose without infrastructure overhead |
| Automated delta reports | **Skip for now** — useful if you ever have agents running autonomously; overkill for manual orchestration |
| Manual Coder terminal (Casey's) | **Do this** — you're the best orchestrator; use it for hands-on work, subagents for spec-tight work |
| Switching to spec-driven more often | **Yes, selectively** — any time you cross module or app boundaries; not for single-file work |
| Ephemeral stateless Coders | **Already have this** — Claude Code subagents with worktree isolation are exactly this |

The Gemini framework describes a mature multi-agent orchestration system. It's well-designed for that problem. But your problem is smaller and more personal: one developer, a handful of apps, Claude Code as the primary tool. The architecture.md workflow (vibe coding by default, spec-driven when complexity warrants, retro-spec to close gaps) is already well-calibrated for that. Cherry-pick the skeleton idea and the manual Coder terminal pattern. Skip the infrastructure.