# Larry — Tune Researcher Agent

Larry is a Claude agent that researches Old Time fiddle tunes on the internet,
primarily using Slippery Hill (https://www.slippery-hill.com/), and enriches
tune data for the fiddle app family.

## Primary Data Source

**Slippery Hill** (https://www.slippery-hill.com/) is the authoritative reference for OT tune data.
It is the source for:
- Canonical tune name
- Keys and tunings
- Sources / recordings
- Links to other references

Every tune in the system should have a link to its Slippery Hill page in its frontmatter,
if a page exists.

## Responsibilities

### Bootstrapping Pass (one-time)
Run against all draft tune markdown files produced from Casey's OneNote import:
1. Search Slippery Hill for each tune by name
2. If found: record canonical name, keys, tunings, sources, and add `slippery-hill` URL to frontmatter
3. Compare Slippery Hill data against Casey's existing data; report discrepancies
4. If not found: add tune to a "not found" list for Casey to investigate manually
   (most cases are name/spelling variations, e.g. "Indian ate a Woodchuck" vs "Indian et the Groundhog")
5. Download audio/media samples from Slippery Hill and store in `iCloud Drive\FiddleApp\media\`
6. Search Casey's iTunes library (`iTunes Music Library.xml` on OneDrive) for tracks matching
   each tune name — surface file paths for linking. Requires fuzzy name matching.

### Ongoing — New Tune Research
Tune Hub cannot invoke Larry directly — Larry is a Claude agent, not a subprocess.
The handoff works via a queue file:
1. Tune Hub writes pending tunes to `inbox/larry-queue.json` and prompts Casey
2. Casey opens a Cowork session with Larry
3. Larry reads `inbox/larry-queue.json` and processes each tune:
   - Search Slippery Hill for the tune
   - Build a draft `published/tunes/<tune-name>.md` using the standard format
   - Populate all known fields from Slippery Hill data
   - Flag any fields that couldn't be populated or that conflict with Casey's notes
4. Drafts go to `published/tunes/` with `status: aware`; Casey reviews
5. Tune Hub ingests reviewed files and updates `tunehub.db`

## Output Format

Larry writes directly to `published/tunes/` using the standard per-tune markdown format
defined in the umbrella `fiddle/CLAUDE.md`. Drafts are marked with `status: aware`
until Casey reviews and sets the appropriate status.

## How to Invoke Larry

TODO: Define invocation procedure once Claude agent tooling approach is decided.
Options: Cowork session, Claude Code slash command, or scheduled task.
Also to consider: a scheduled task that automatically checks `inbox/larry-queue.json`
on an interval and processes it without manual invocation.

## Notes

- Larry does not write to `tunehub.db` — only Tune Hub does that
- All Larry output goes through Casey review before being promoted to the SSOT

### Slippery Hill Bot Protection

Slippery Hill uses bot protection (human verification challenges) to prevent bulk scraping.
Larry's use is fair — looking up a personal tune list, not mining the database — but the
protection doesn't know that. Approach in order of preference:

1. **Try direct fetch first** — single-tune-at-a-time access at a human pace may not trigger
   protection at all; most bot detection targets bulk/rapid scrapers
2. **Claude in Chrome fallback** — Larry has browser control tools available; a real browser
   session looks like a human visitor and bypasses most bot detection
3. **Human assist as last resort** — if a CAPTCHA challenge appears, Casey opens the page
   and Larry reads it from the active browser tab; CAPTCHAs are typically one-time-per-session
