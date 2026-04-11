# Electron Packaging & Distribution

> [!todo] When resolved, update [architecture.md Section 13](../architecture.md#13-electron-packaging--distribution) and remove the open question callout.

## Packaging vs. Bundling — What's the Difference?

These are two different steps that happen at different times and solve different problems:

### Bundling (covered in [bundling-strategy.md](bundling-strategy.md))

**When:** Build time (before the app runs)
**What it does:** Takes your many `.js` source files and combines them into one or a few files. Optionally minifies and tree-shakes.
**Why:** Performance optimization. Reduces the number of files the runtime has to load. Optional for Electron (Chromium handles ES modules natively).
**Tools:** esbuild, Vite, Webpack
**Output:** A `dist/` folder with your optimized `.js`, `.css`, and `.html` files — still just web files.

### Packaging

**When:** After development, when you want a runnable application
**What it does:** Takes your web files (bundled or not) + the Electron runtime + your `package.json` config and wraps them into a native application that users can double-click to run.
**Why:** Without packaging, users would need Node.js installed and would run `npm start` from the command line. Packaging produces a `.exe` (Windows), `.app` (macOS), or `.AppImage` (Linux) that behaves like any other installed application.
**Tools:** electron-builder, electron-forge
**Output:** An installer (`.exe`, `.dmg`) or portable executable

### The Full Pipeline

```
Source files (.js, .css, .html)
    ↓ [optional] bundling (esbuild)
Optimized web files (dist/)
    ↓ packaging (electron-builder)
Native application (.exe, installer)
    ↓ [optional] code signing
Signed application (trusted by OS)
    ↓ [optional] auto-update server
Distributed application with update capability
```

For our apps, bundling is optional (and deferred). Packaging is required whenever we want a real desktop application instead of running from the terminal.

## What Packaging Involves

### The Basics
- **electron-builder** or **electron-forge** — the two main tools. electron-builder is more mature; electron-forge is Electron's official tool (newer, more opinionated).
- Configuration goes in `package.json` or a separate config file. You specify: app name, icon, which files to include, target platforms.
- Output is a platform-specific executable. For Windows: `.exe` installer or portable `.exe`.

### Code Signing
- **Windows:** Unsigned apps trigger SmartScreen warnings ("Windows protected your PC"). Signing requires a code signing certificate ($100-300/year from a CA, or free with a self-signed cert that users must manually trust).
- **macOS:** Unsigned apps are blocked by Gatekeeper. Signing requires an Apple Developer account ($99/year — already needed for Capacitor iOS apps).
- **For personal use:** Can skip signing and accept the warnings. For public distribution: signing is effectively required.

### Auto-Update
- Electron supports auto-update via `electron-updater` (part of electron-builder) or Electron's built-in `autoUpdater`.
- Requires hosting update files somewhere (GitHub Releases is the simplest free option).
- For personal use: manual updates (re-download the .exe) are fine initially.

## Research Questions

> [!question] electron-builder vs electron-forge?
> electron-builder is more battle-tested and has more configuration options. electron-forge is the official Electron tool and integrates better with Electron's development workflow. Which fits our needs better? This can be decided when we actually build the first Electron app.

A: 

> [!question] When does packaging become necessary?
> During development, `npm start` / `electron .` is fine. Packaging is needed when: (a) you want to run the app without a terminal, (b) you want to distribute it, or (c) you want auto-update. For personal use on one machine, this is low priority. For App Store distribution of Capacitor apps, packaging is handled by Xcode/Capacitor, not Electron.

A: 

## Next Steps

- Defer until the first Electron app (MM or Ear Tuner) is functional
- At that point, evaluate electron-builder vs electron-forge
- Start with unsigned builds for personal use
- Add code signing and auto-update if/when apps are distributed publicly
