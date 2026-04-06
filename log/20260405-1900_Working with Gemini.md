# Working with Gemini

This document outlines how Gemini CLI interacts with the established Claude-centric workflow in this project.

## Compatibility with Claude

Gemini is designed to be fully compatible with the existing `CLAUDE.md` architecture.
- **Source of Truth:** Gemini treats `CLAUDE.md` files as foundational mandates and will not create redundant `GEMINI.md` files unless specifically instructed.
- **Standards Adherence:** Gemini rigorously follows the established JavaScript (ES modules) conventions, Platform Adapter Layer patterns, and "Old Time" tonality rules documented by Casey and Claude.

## Multi-Agent Workflow Best Practices

Using both Claude and Gemini in the same project offers powerful cross-review capabilities but requires coordination:

### Potential Downsides
- **Context Desync:** Each agent only knows the current state of the files, not the conversational history of the other.
- **Conflicting Opinions:** Subtle differences in "idiomatic" implementation may arise if patterns aren't strictly defined in the context files.
- **Redundant Processing:** Both agents may perform identical research or file reads if the current status isn't clearly tracked.

### Recommendations
- **State Tracking:** Use `CLAUDE.md` or `backlog.md` to record major decisions and current status. 
- **The "Handover" Note:** When switching agents mid-task, create a temporary `HANDOVER.md` summarizing progress and the immediate next step.
- **Cross-Reviewing:** Use Gemini to review plans or code created by Claude (and vice-versa) to identify architectural flaws or portability issues regarding the Swift migration.

## Executing Skills and Minions

Gemini can emulate the "skills" and "minions" (like Larry) defined in the `minions/` folder by following their documented workflows:
- **Workflow Emulation:** Gemini can perform research tasks (e.g., Slippery Hill lookups) using its own search and web-fetching tools while adhering to the "Per-Tune Markdown Format."
- **Tool Execution:** If a skill relies on a specific script or CLI tool, Gemini can execute it via the shell.
- **Protocol Adherence:** Gemini will strictly follow the data standards and ingestion patterns defined for each minion.

*Note: Gemini cannot access Claude-specific MCP (Model Context Protocol) servers unless they are available as standard CLI tools.*
