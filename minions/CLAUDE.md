# minions/

This folder contains Claude agents ("minions") that perform specialized, repeatable tasks
in support of the fiddle app family. Each minion has its own subfolder with a CLAUDE.md
describing its purpose, capabilities, and how to invoke it.

## Minion Registry

| Name  | Folder  | Purpose                                      | Status  |
|-------|---------|----------------------------------------------|---------|
| Larry | larry/  | Tune researcher — finds tune data on the web | Planned |

## General Notes

- Minions are invoked by Casey or by apps (e.g. Tune Hub triggering a Larry research pass)
- Each minion should be self-contained: its CLAUDE.md fully describes how to run it
- Minions read from and write to the shared iCloud container, following the same data
  architecture as the apps (no direct writes to tunehub.db)
