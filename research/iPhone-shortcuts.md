
# iOS Shortcuts for working with Claude

**Role for Claude:** You are an expert iOS Shortcuts developer. Your goal is to write .shortcut files for Casey to install on his iPhone to facilitate him working efficiently with you.

---

## Global Environment Settings
* **Storage Provider:** iCloud Drive
* **Root Directory:** `/iCloud~md~obsidian/Scratch/ai-inbox/` (Ensure the shortcut checks for this folder or creates it if missing). That is a folder inside Obsidian's special folder at the root of my iCloud drive
* **Filename Standard:** `yyyy-MM-dd-HH-mm-ss_description` (e.g., 2026-04-12-14-30-05_youtube_url).

C:\Users\CaseyM\iCloud\iCloudDrive\iCloud~md~obsidian\Scratch\ai-inbox

* **Obsidian Integration:** All `.md` files should be formatted with clean Markdown syntax to be compatible with Obsidian's vault structure.  
---

## 1. Shortcut: "Rich Bookmark Capture"
**Trigger:** Share Sheet (URLs and Safari Webpages)
**Logic:**
1. **Extract Metadata:** Use `Get Details of Safari Web Page` to grab the **Page Title**.  I also want this to work for YouTube and Facebook and Google search app... or perhaps other apps to send you most anything that can be productively represented as a .md file.
2. **User Input:** Prompt the user: "Add a note about this link?"
3. **Clipboard Check:** Automatically grab any text currently on the **Clipboard**. Ignore images or non-text content, but convert rich text or html-encoded text to plain text, if possible.
4. **File Creation:** * Generate a Markdown file.
   * **Title:** Use the Page Title as an H1 (`# Title`).
   * **Body:** Include the Date, the URL, the User Note, and the Clipboard Snippet.
1. **Output:** Save as a unique file `[Timestamp]_[description].md` in `/inbox/`. Please suggest what kind of info that you might use to generate the [description]. Maybe the source app?
2. Notes:
	1. Initially, I'd like to capture everything you can. I want to see what is available. Maybe later I'll decide that some of it is useless.
	2. When I add some text, it is likely to be a note to you about the relevance of capture, e.g. I may say "Add a backlog item to research this" and you would add to the fiddle-apps backlog, copy the captured message to the research folder, and link it from the backlog item.


> [!claude] Note that I have not reviewed the entries below. They were generated from a summary by Gemini. They are future ideas to consider after we tackle the one above.
## 2. Shortcut: "Voice Note & Transcript"
**Trigger:** Siri / Hands-free
**Logic:**
1. **Capture:** Record audio from the microphone.
2. **Process:** Perform a text transcription of the recorded audio.
3. **Naming:** Generate a single timestamp string.
4. **Output:** * Save the audio file as `[Timestamp].m4a`.
   * Save the transcript as `[Timestamp].md`.
   * Both files must exist in `/inbox/` with identical names for easy pairing.

## 3. Shortcut: "Screenshot OCR Task"
**Trigger:** Share Sheet (Images) or "Take Screenshot" action
**Logic:**
1. **OCR:** Use `Extract Text from Image` on the screenshot.
2. **Context:** Prompt user for "Additional Task Context."
3. **Output:** Save a Markdown file named `task-[Timestamp].md` in `/inbox/`. Include the extracted text and the user's manual notes.

## 4. Shortcut: "Allowance Spending Tracker"
**Trigger:** Home Screen / Manual
**Logic:**
1. **Select Child:** Menu options for "Collin" and "Claire".
2. **Amount:** Prompt for a Number input (Currency).
3. **Reason:** Prompt for Text input (e.g., "Gum", "Donuts").
4. **Email Action:** * **Recipient:** [Enter My Email Address]
   * **Subject:** `$[Amount] from [Child]'s allowance for [Reason]`
   * **Body:** Automated timestamp and details.
   * **Setting:** Set `Show Compose Sheet` to **OFF** for instant sending.

---

## Future Roadmap & Notes
* **AI-Managed Allowance:** Note that these emails are currently used for tracking. Future iterations should aim to have an AI agent parse these emails (or files) to maintain a central ledger automatically.
