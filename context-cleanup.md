The context audit revealed a bunch of issues and inconsistencies and redundancies. This is largely due to my systems for working evolving over time.

I made a bunch of suggestions, but feel free to question them. You know more about how and when you will follow links to read linked .md files. We have a few goals:
- Each pieced of information should have a SSOT. Redundantly documented stuff is wasteful and gets out of sync. This includes information like architecture, specs, folder structure, etc. Some of that stuff is duplicated, now.
- Enable you to only load as much information into your context as needed. We probably don't need to load the entire architecture.md into context for routine tasks that do not involve designing, writing, or testing the software, so we don't want to put anything in architecture.md that we will need more often, e.g. see the notes about documenting the folder structure, below.

fiddle/claude.md contains stuff that should be elsewhere. Some of it should be in fiddle\architecture.md (such as swift portability prepraredness). Some of it may be out-of-date and should be removed. Ask me about conficts, if you need to, but generally architecture.md is newer and should supercede anything you find in claude.md

I want to have a SSOT for 

If multiple files need to refer to the overall source/build folder structure, then pull it out into a separate .md and have them point to it. I think it is currently documented in multiple places, like apps.md and fiddle\claude.md

I'm sure that multiple apps will need to refer to the iCloud data folder structure, which I think is documented in multiple places. I suppose that could be a section in the architecture and other files can link to that section, but it might be better if it were its own .md that various places could include "in-line".

# file/folder patterns
Somewhere, we should document the overall patterns of folders and files that are used in all of the apps, folders like specs, log, research, research\skulch, and backlog

# backlog
We don't want to redundantly describe the log skill or barry the backlog manager.  There are broken links to backlog-readme.md and backlog.readme.md that must have been broken when we moved it. Maybe fiddle\claude.md does not describe the backlog but just notes the existence of the skill?

## specs
The rule for \specs\ is that every app folder should have a main spec in {app-name}/specs/{app-name}-spec.md. Other smaller specs go in that file using a YYYY-MM-DD_{description}.md filename. This way we know which specs are newer (and may supercede stuff in the main spec). Eventually the smaller ones are used to update or merge into the main one.

## log
We have a skill to deal with this. Maybe just refer to the skill?

## research
These files tend to be short-lived and end up as part of a log entry or in skulch. There should be a clear understanding to ignore the stuff in skulch unless we are specifically looking for old research topics.


# apps
Individual app claude.md files are bloated with stuff that should be moved out into a specs folder. The audit highlighted that media-markup/CLAUDE.md (at 167 lines) is way too long. Much of its content should be moved elsewhere. The platform adapter stuff should maybe be in the overall architecture.md? You decide. Much of it should form the basis of a new media-markup/spec/media-markup-spec.md. Do we need a separate architecture.md file in each of the apps? It may be confusing what should be in architecture vs the spec vs claude.md, but we need to figure that out.


  Data architecture contradiction: media-annotations/ vs SQLite attach.  fiddle/CLAUDE.md still documents the old approach. media-markup/CLAUDE.md explicitly says this was "the
  earlier plan" and has been replaced by the SQLite attach pattern. We need to ensure that the updated plan is documented in exactly one place, and maybe link to it from elsewhere.
  
 Data flow contradiction: fiddle/CLAUDE.md says "Tune List → reads published/data/**". tune-list/CLAUDE.md line 22–23 says it reads tunehub.db directly via iCloud App Group, and explicitly states the  published JSON pipeline is not TuneList's data source. We need to document the updated plan in exactly one place and link to it from elsewhere.
 
 Broken reference: backlog-readme.md in fiddle/CLAUDE.md needs to be fixed. 
Projects/CLAUDE.md refers to a backlog.readme.md to ignore, but needs to be clear that it might encounter files with that name in multiple project folders.

ear-tuner/ is an active project with no CLAUDE.md
  The current working directory is ear-tuner/. It qualifies as a Sub-App under the 4 semantic criteria and has recent commits. It has no module CLAUDE.md, so there's no project-specific
  context for coding sessions here.
  → Create ear-tuner/CLAUDE.md with purpose, status, target platform, and any app-specific decisions (e.g., the iOS silent switch fix noted in git history). Keep it ≤50 lines.

There is an intonio folder. It holds an app that may or may not be pursued. We should clear up any confusion about it.

The audit complained:  _shared/CLAUDE.md and microbreaker/CLAUDE.md are pure stubs
  Both are 15 lines of "TODO: Fill in when development begins." They contribute ~15 lines to context load with no informational value.
  → Acceptable while not-started, but consider whether these files are worth loading at all yet. Alternatively, make them one-liners: # _shared — see parent fiddle/CLAUDE.md. Development
  not yet started.
Question for you, Claude: If I open a new session in "fiddle", are you loading the claude.md from all of the app folders, or do you wait until we are doing something specific in the app?

Are there other cases where we should break info out into smaller .md files so that we can more easily maintain a SSOT, or only load as much context as we need? Is the architecture.md too big? Is it like the "spec" for the overall family, and we should follow the "specs" pattern in the fiddle folder and move architecture.md to fiddle\specs\fiddle-spec.md? And maybe it is a file that sometimes links smaller files instead of including the content in-line? It could use links that cause the sections to appear "in-line" in obsidian, but you would not need to follow them unless you really needed the information. Does this sound like a good idea? Do you have a better idea for what to do about architecture.md?
