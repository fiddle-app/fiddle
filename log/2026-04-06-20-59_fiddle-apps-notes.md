Fiddle Apps backlogs etc

Monday, March 30, 2026

10:02 AM

 

> Most useful :

1.  MM

2.  TuneList

>  
>
>  
>
> TuneHub
>
>  
>
> Tune meta-data:

- Checked against Slippery hill yet?

- IsTopic- not really a tune

>  
>
> Have a “research“ button that will proactively find information about a tune, including you tube videos and sheet music and ABC. Can a WPA call Claude? Maybe it just generates a prompt and user must paste it. The prompt can cause the AI to send results to the inbox.
>
>  
>
> TuneList

- Can have playlists. Acts as a media player

- Can play tunes slow or with adjusted pitch

- Skips dead air

>  
>
> **MM Tune Structure Markup**
>
> MM can detect BPM and suggest snap boundaries at beat and half- beat intervals
>
> Allow user to “tap along” to establish beats.
>
>  
>
> Have a separate “structure” layer.. Or “tune” segments. A group of hierarchical segments that span:

1.  Whole tune

2.  Reps

3.  Section

4.  Part

5.  Phrase

>  
>
> Can export a tune… just audio or also video
>
>  
>
> We may know how many parts are in a tune and how many times they repeat.
>
>  
>
> User say: map a tune. User taps along to the beat for the entire tune. Hits enter at end.
>
> Tap different keys to indicate the end of a part
>
> Trims “beats” off the end. Fine-tweaks ends. Identifies a part, labels it.
>
> Auto-guess phrases. Manually correct them. Start with positional names in curly brackets until given real names. Auto-Find next part… based on the first. Tweak the selection of beats. Fine -tune boundaries. Select two parts and create a section. Auto detect next section. ….
>
> Pick two Or 3 sections and create a Rep. Auto-detect the rest of the tune.
>
> When we name phrases, auto propagate to like-named parts.
>
>  
>
> In playback, you can select at any granularity in the hierarchy to play. A special mode to compare a phrase to other phrases in the same relative position.
>
>  
>
> Exports tune structure markup
>
>  
>
> Support chords in the markup:
>
> D… G.A. Bm… D.GA
>
>  
>
> Alternative structure format:
>
> A x 2
>
> …. ….. …. ….. (or) 4 5 4 5
>
> C1 R1 C1 R2
>
>  
>
> A1:
>
>  
>
> You can then just replace beats with chords
>
>  
>
> A: could the cloud file system be abstracted ( could be used with OneDrive or Google Drive or iCloud). Are they similar enough?
>
> ! For audio, generate video that is the frequency profile from Intonio, showing the named peaks). Also for regular video. Or can it show that display on-the-fly without generating video?
>
>  
>
> Intonio should be able to detect tonality by displaying the top 3 candidate chords the work with the current frequencies. Chords score higher if there are peaks in their notes. The lose points if there are notes that are small, dissonant intervals away from the chord notes.
>
>  
>
>  
>
>  
>
> Disambiguate OBCCCAR in lessons. Use as one source of original tune SSOT and media SSOT
>
>  
>
> Clean up hi OneNote lists with correct status: lead, learning, want to, aware
>
>  
>
> Define a “note” format in OneNote: after dash? {source} \[tuning \] (tonality)
>
>  
>
> What about images in tune pages?
>
>  
>
> Q: Certain portions of tune data should be persisted and displayed as Md even in TuneHub?
>
>  
>
> TH cleans up display and editing of discrete fields, but “notes on how-to-play“ are mostly Md?
>
>  
>
> TH has 3 categories of notes:

- Original/integrated/own

- Media-linked (maybe copied from caption, maybe tweaked. Remembers a start/end time and segmentID)

- Live comments from media. MM may mark some as private/hidden. Really this is just a view of segments. The tune only persists the mediaID.

> Media-linked notes: Click a media-segment and “copy to notes”. Have a “copied” checkmark to remember which have been copied
>
>  
>
> Q: Should tuneID and mediaID be a friendly guid? 2026-03-23\_13-59-326. Ask advice. Want human readability with no collisions and no central management. 260323-1359-326
>
> Or just search for a new integer? SQLite can manage integers. Lesson extraction cannot figure out a tune id. It just sends new tune requests and new media requests to the TuneHub inbox. TuneHub reconciles and generates the SSOT ids and Md.
>
>  
>
> How will MM (music markup) (media markup) store/edit media metadata?
>
> Desktop WPA can open SQLite directly. iPad could also open SQLite, once it gets the file, but locking for conflicts seems problematic
>
>  
>
> Check for lock data. Have ability to break another app’s lock. Lock will include App-person-date-tim-device
>
>  
>
> MM creates local json with segment data. It could send it to inbox, but merge could be complex.
>
> Maybe start with live db connections, but MM holds lock for minimal time. It periodically checks to see if it is no longer the last editor. If so, it looks for changes to its in-memory data.
>
>  
>
> Q: Can two parties edit different copies of the db via iCloud? If so, which one wins? Have Claude think it through. Use case of editing on airplane. Then edit on desktop before the iPad syncs.
>
>  
>
> Typical workflow. Save zoom. Initiate markup from iPad. It should allow picking the file from OneDrive or iCloud. There’s a chance it is already in the media index, but not if we are selecting a raw file directly.
>
> iOS app can share the db? Or it looks at json view?
>
>  
>
> Ask Claude if it could handle simultaneous editing of segments by both MM WPA and MM iPad. That would be great.
>
>  
>
> It would probably be nice to do initial markup on the desktop or laptop, or at least have Claude or TuneHub create the initial media metadata and add tune associations. On the iPad, MM would list new media first, and when creating segment groups, would suggest ones for the pre-associated tunes.
>
>  
>
> Segment SSOT would be MediaMarkup.db
>
>  
>
> The two dbs attach each other.
>
>  
>
> MM on iOS may just wake up and suggest a list of recent media and new media (only show) a small window of new media, top 3 is probably enough.
>
>  
>
> ! The key of T is a topic, like intonation or rhythm
>
>  
>
> Search in MM covers tune name and file name.
>
>  
>
> TH needs to be SSOT for media, because most media will not have markup.
>
>  

1.  Save zoom

2.  Drag it to TuneHub

3.  TuneHub suggests tune associations based on the zoom filename

4.  User may need to disambiguate tune names or add new tune or topic

>  

1.  Download video or find a mp3

2.  Drag it to a tune. Adds it to Media table and makes the association

>  
>
> MM: Also have the ability to create a singular "mark" like "start of example phrase"… this will avoid having to really segment everything… only segment when you need a new "caption". Marks within the time of a top-level segment will appear as children of that segment.
>
>  
>
> Maybe from TH you can “add YouTube video “ and it will call command line to download it.
>
>  
>
>  
>
> !Always generate a Md view of everything with enough data to rebuild the TuneHub.db
>
> We can bootstrap the project by building out all of the information in md.
>
>  
>
>  
>
> Take a look at notes pasted into Fiddle folder
>
>  
>
> Use play buttons from YouTube? Or just skip and back? They already are. Maybe just make play triangle larger? Consider shading in background of back and skip.
>
>  
>
> Ear tuner. Be able to copy a report that you can email others. As html or md?
>
> In the jam notes, have a section that’s explicitly about people. People that were there, people that I met, notes about them.
>
>  
>
> Larry: import rules:
>
> L: for lyrics
>
> ! Anywhere means “want to learn “
>
> Square bracket for tunings
>
> W: with a person. First heard it from them or otherwise associated with them
>
>  
>
> Need a status for “can lead but not start” or maybe that is just “Learn to start“
>
>  
>
> TH will have a table of sources and their aliases, eg Clyde, Snake, Tommy, Nokosee.
>
>  
>
> Have a People table with aliases. Maddie, Christy, Rhys, Ryck
>
>  
>
> “Can start/ lead”
>
>  
>
> TuneHub

- Maybe have a whole section that is about people. Notes about people gathered through the tune list app

>  
>
> TuneList

- In the jam notes, have a section that’s explicitly about people. People that were there, people that I met, notes about them.

>  
>
> Tune structure diagram
>
> <https://claude.ai/public/artifacts/1974dc00-74ef-4e66-a575-2009bdf2367c>
>
>  
>
>  
>
>  
>
>  
>
>  
