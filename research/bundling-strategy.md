# Bundling Strategy: No Bundler vs. esbuild

> [!todo] When resolved, update [architecture.md Section 2](../architecture.md#2-technology-stack) and remove the open question callout.

## The Question

For our vanilla JS + Electron apps, do we need a bundler at all? If so, which one?

## What Is Bundling?

A **bundler** takes your many separate `.js` files (ES modules) and combines them into one or a few output files. It can also:
- **Tree-shake:** Remove unused exports so the output is smaller
- **Minify:** Shorten variable names and strip whitespace to reduce file size
- **Resolve dependencies:** Inline or bundle `node_modules` packages so the app is self-contained
- **Generate source maps:** Map the bundled output back to your original files for debugging

## No Bundler — What That Means

Electron's renderer process uses Chromium, which natively supports ES modules (`import`/`export`). So your code can run as-is — each `.js` file is loaded individually by the browser engine at runtime.

**Pros:**
- Zero build step — what you write is what runs
- Debugging is straightforward — the files in DevTools match your source files exactly
- No configuration, no build tool dependencies, nothing to break
- Fastest possible development cycle (edit → refresh → see changes)

**Cons:**
- Each `import` triggers a separate HTTP-like request inside Electron. For a small app (dozens of modules), this is imperceptible. For hundreds of modules, startup could be noticeably slower.
- No tree-shaking — if you import a large library and use one function, the whole library loads
- No minification — files are slightly larger (irrelevant for a desktop Electron app where files are local, but matters for Capacitor iOS where bundle size affects app store download size)
- `node_modules` packages that use CommonJS (`require()`) won't work in ES module context without a bundler or adapter

**Bottom line for us:** For Electron desktop apps with vanilla JS and few dependencies, no bundler is fine. The apps are local — there's no network latency on imports, and file size doesn't matter. Startup with dozens of modules will be instant.

## esbuild — What It Adds

**esbuild** is an extremely fast bundler (written in Go, ~100x faster than Webpack). It takes your ES modules and produces a single bundled file.

**When you'd want it:**
- If you add a `node_modules` dependency that uses CommonJS and won't load as an ES module
- If you eventually have so many modules that startup feels sluggish (unlikely for our apps)
- When building the Capacitor iOS version of an app — smaller bundle = faster app launch on mobile
- If you want to minify for production builds (minor benefit for Electron, more relevant for Capacitor)

**What it doesn't add:**
- No new syntax or language features — your code stays vanilla JS
- No framework requirement — it just concatenates and optimizes your existing files
- Minimal configuration — often just `esbuild src/main.js --bundle --outfile=dist/main.js`

**Bottom line:** esbuild is the "if we need it" escape hatch. It's trivial to add later because it doesn't change how you write code — it just changes how the code is delivered to the runtime.

## Recommendation

Start with no bundler. Add esbuild when one of these triggers occurs:
1. A needed npm package uses CommonJS and won't load natively
2. Capacitor iOS build needs a smaller bundle
3. Startup feels slow (measure first — don't assume)

This is not a decision that needs to be locked in. Moving from "no bundler" to "esbuild" is a 15-minute task, not an architecture change.

> [!question] Vite — worth considering?
> Vite is a dev server + bundler that provides hot module replacement (HMR) — you edit a file and the change appears in the running app without a full reload. This is valuable when iterating on UI. However, Vite adds complexity (config, plugin system, dev server), and HMR is less important in Electron where refresh is already fast. If we adopt a framework in the future, Vite would become relevant. For now, it's unnecessary overhead.

A: 
