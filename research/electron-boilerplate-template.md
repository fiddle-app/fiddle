# Electron Boilerplate / Shared Template

> [!todo] When resolved, update [architecture.md Section 8](../architecture.md#8-electron-security) and [Section 12](../architecture.md#12-electron-shared-setup) and remove the open question callouts.

## The Question

Tune Hub and Media Markup (and potentially Ear Tuner as an early test) share Electron setup patterns. Should we build a shared template, and if so, what should it contain?

## What Would Be Shared

- `contextBridge` / `contextIsolation` security setup (preload.js)
- Content Security Policy (CSP) configuration
- IPC channel patterns (invoke/handle for platform adapter)
- Window management basics (BrowserWindow config, DevTools toggle)
- Platform adapter interface contract
- Electron-builder or electron-forge packaging config

## Approach Options

### Option A: Build template upfront in `_shared/`
Create a starter template before any Electron app is built. Risk: premature abstraction — we don't yet know what the real patterns look like in practice.

### Option B: Build first app, extract after
Build MM (or Ear Tuner as a simpler test case), get the Electron setup right through real use, then extract the reusable parts into a template. The first app becomes the template donor.

### Option C: Start with Ear Tuner as a proving ground
Ear Tuner is the simplest app (minimal data, no database, no platform adapter). Porting it to Electron first would be a low-risk way to learn the Electron patterns. The resulting setup becomes the starting template for MM and Tune Hub.

> [!question] Which app should be the template donor?
> Ear Tuner is simplest (good for learning Electron) but doesn't exercise the platform adapter or SQLite. MM exercises everything but is more complex. Starting with Ear Tuner means learning Electron on easy mode, then adding complexity for MM. Starting with MM means the template is battle-tested from the start but the learning curve is steeper.

A: 

## Gemini's Security Template Suggestion

The Gemini research ([skulch/2026-04-11_electron-research.md](skulch/2026-04-11_electron-research.md)) recommended enforcing `contextIsolation: true` and a strict CSP from day one. This aligns with our architecture (Section 8). The specific template they suggested was tied to Svelte/Vite (which we're not using), but the security principles are sound and should be part of whatever template we create.

## Next Steps

- Decide on template donor app (Ear Tuner vs MM)
- Build that app's Electron setup
- Document the patterns that emerge
- Extract reusable parts into `_shared/electron/` or a similar location
