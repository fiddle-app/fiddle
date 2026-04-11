## Architecture & Framework Research: Electron + Capacitor Video Annotator## Executive Summary
For a cross-platform application (Windows/macOS/Linux via Electron and iOS via Capacitor) requiring high-performance UI components like a responsive video timeline, the recommended stack is Svelte 5 or SolidJS over React.
------------------------------
## 1. Core Technical Recommendations## Framework: Svelte 5 (Primary Recommendation)

* Reason: High-frequency UI updates (60fps+ scrubbing) require minimal overhead. Svelte eliminates the Virtual DOM, compiling to direct DOM manipulations.
* Impact: Lower CPU/RAM usage—critical for video-heavy apps—and superior responsiveness on mobile (iPhone) where hardware resources are more constrained than desktop.

## Build Tooling: Vite + Electron-Vite

* Reason: Provides the fastest Hot Module Replacement (HMR). Essential for fine-tuning UI animations and gesture responsiveness without constant app restarts.

## State Management: Signals / Svelte Stores

* Reason: Use fine-grained reactivity. When dragging the timeline, only the specific time-code and playhead elements should update, rather than re-rendering large component trees.

------------------------------
## 2. Platform Strategy: Electron to Capacitor## Process Isolation

* Strategy: Maintain a strict "Bridge" pattern.
* Electron: Use contextBridge for filesystem/Node.js access.
* Capacitor: Use standard Capacitor Plugins for iOS native features.
* Code Structure: Abstract these calls into a single service layer (e.g., api.saveFile()) that detects the platform at runtime.

## UI Consistency

* Library: Use Tailwind CSS for styling. It ensures a consistent layout engine across the Electron Chromium window and the iOS WKWebView.
* Touch Targets: Design the timeline for "Pointer Events" (unified mouse/touch API) to ensure the dragging logic works identically on a trackpad and a touchscreen.

------------------------------
## 3. High-Performance Timeline (Video Scrubbing)## The "Glued-to-Finger" Requirement

* Canvas Rendering: For complex annotations or waveforms, render the timeline on an HTML5 Canvas. Managing thousands of DOM nodes for annotation markers will cause lag during fast scrolls.
* RequestAnimationFrame (rAF): Sync the video frame seeking and timeline playhead updates using rAF to match the screen's refresh rate (especially 120Hz ProMotion displays on iPhone).
* Passive Listeners: Use { passive: true } on scroll/touch listeners to prevent the JS thread from blocking the browser's compositor thread.

------------------------------
## 4. Testing & Quality Assurance

* E2E Testing: Use Playwright. It is the only modern framework that effectively handles Electron’s multi-process architecture and can also be used for mobile webview testing.
* Unit Testing: Use Vitest. It shares the Vite pipeline, ensuring your tests run in an environment identical to your development build.
* Security: Enforce contextIsolation: true and a strict Content Security Policy (CSP) from day one to prevent XSS in the Electron renderer.

------------------------------
## 5. Pros/Cons Summary for Project Stakeholders

| Feature | React (Standard) | Svelte (Recommended) |
|---|---|---|
| Performance | Good (Virtual DOM overhead) | Excellent (Compiled, No VDOM) |
| Mobile Port | Heavy bundle size | Lightweight (Better for iOS) |
| Development | Massive ecosystem | Highly intuitive, less boilerplate |
| Timeline Feel | Risk of micro-stutter | Maximum fluidity |

Would you like a sample directory structure to organize this shared code across Electron and Capacitor?

