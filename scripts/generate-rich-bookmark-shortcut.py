#!/usr/bin/env python3
"""
Generate rich-bookmark-capture.shortcut

This script produces a binary plist (.shortcut) file that can be installed on
iPhone via iCloud Drive / Files app. When installed it will show an
"Untrusted Shortcut" warning (expected — it's unsigned).

Output: C:/Users/CaseyM/iCloud/iCloudDrive/iCloud~md~obsidian/Scratch/rich-bookmark-capture.shortcut

Action identifiers that are uncertain and may need adjustment if Shortcuts
shows "Action Not Found":
  - is.workflow.actions.safari.getwebpagedetail  (might be .safari.getdetails)
  - is.workflow.actions.text.substring            (might need different param names)
  - is.workflow.actions.text.changecase           (fairly confident)
  - WFReplaceTextRegularExpression param          (might need WFMatchTextRegularExpression)
"""

import plistlib
import uuid
import sys
from pathlib import Path

# ─── Ref / value helpers ────────────────────────────────────────────────────

def uid():
    return str(uuid.uuid4()).upper()

def var(name):
    """Reference a named variable."""
    return {
        "Value": {"Type": "Variable", "VariableName": name},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def out(u):
    """Reference an action output by UUID."""
    return {
        "Value": {"Type": "ActionOutput", "OutputUUID": u},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def inp():
    """The share-sheet input (the URL)."""
    return {
        "Value": {"Type": "ExtensionInput"},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def txt(*parts):
    """
    Build a WFTextTokenString from mixed strings and refs.
    Parts:
      str              → literal text
      {"v": "Name"}   → variable reference
      {"u": "UUID"}   → action output reference
      {"i": True}     → Shortcut Input reference (the shared URL)
    """
    s, att = "", {}
    for p in parts:
        if isinstance(p, str):
            s += p
        else:
            i = len(s)
            s += "\uFFFC"   # Unicode Object Replacement Character — placeholder
            if "v" in p:
                att[f"{{{i}, 1}}"] = {"Type": "Variable", "VariableName": p["v"]}
            elif "u" in p:
                att[f"{{{i}, 1}}"] = {"Type": "ActionOutput", "OutputUUID": p["u"]}
            elif "i" in p:
                att[f"{{{i}, 1}}"] = {"Type": "ExtensionInput"}
    return {
        "Value": {"string": s, "attachmentsByRange": att},
        "WFSerializationType": "WFTextTokenString"
    }

# ─── Action builders ─────────────────────────────────────────────────────────

def act(ident, **params):
    """Build an action dict, dropping any None-valued keys."""
    return {
        "WFWorkflowActionIdentifier": ident,
        "WFWorkflowActionParameters": {k: v for k, v in params.items() if v is not None}
    }

def set_var(name, value):
    return act("is.workflow.actions.setvariable", WFVariableName=name, WFInput=value)

def if_has_value(ref, group):
    return act("is.workflow.actions.conditional",
               WFControlFlowMode=0, WFCondition=100,
               WFInput=ref, GroupingIdentifier=group)

def end_if(group):
    return act("is.workflow.actions.conditional",
               WFControlFlowMode=2, GroupingIdentifier=group)

def get_text_action(token, u=None):
    return act("is.workflow.actions.gettext", WFTextActionText=token, UUID=u)


# ─── Main build ──────────────────────────────────────────────────────────────

def build():
    actions = []
    add = actions.append

    # Pre-assign UUIDs for every action whose output is referenced later.
    u_host            = uid()
    u_html            = uid()
    u_meta_matches    = uid()
    u_meta_first      = uid()
    u_content_matches = uid()
    u_content_first   = uid()
    u_og_strip        = uid()
    u_og_title        = uid()
    u_safari_title    = uid()
    u_ts_file         = uid()
    u_ts_human        = uid()
    u_clip_raw        = uid()
    u_clip_trunc      = uid()
    u_note            = uid()
    u_slug_lower      = uid()
    u_slug_hyph       = uid()
    u_slug_trim       = uid()
    u_slug_final      = uid()
    u_note_empty      = uid()
    u_clip_empty      = uid()
    u_note_text       = uid()
    u_clip_text       = uid()
    u_markdown        = uid()

    # GroupingIdentifiers link matching If / End If blocks.
    g_og_meta    = uid()
    g_og_content = uid()
    g_safari     = uid()
    g_note       = uid()
    g_clip       = uid()

    # ── 1. Extract URL host → default Title and permanent Source ─────────────
    add(act("is.workflow.actions.geturlcomponent",
            WFURLComponent="Host", WFURL=inp(), UUID=u_host))
    add(set_var("Title",  out(u_host)))
    add(set_var("Source", out(u_host)))   # Source = host; never overwritten

    # ── 2. OG title fetch ────────────────────────────────────────────────────
    # Download the page HTML.
    add(act("is.workflow.actions.downloadurl", WFURL=inp(), UUID=u_html))

    # Match the full <meta ... og:title ...> tag.
    add(act("is.workflow.actions.text.match",
            WFMatchTextPattern=r'<meta[^>]+og:title[^>]*/?>',
            WFInput=out(u_html), UUID=u_meta_matches))

    add(if_has_value(out(u_meta_matches), g_og_meta))
    add(act("is.workflow.actions.getitemfromlist",
            WFItemIndex=1, WFInput=out(u_meta_matches), UUID=u_meta_first))

    # Match content="..." within that tag.
    add(act("is.workflow.actions.text.match",
            WFMatchTextPattern=r'content="([^"]+)"',
            WFInput=out(u_meta_first), UUID=u_content_matches))

    add(if_has_value(out(u_content_matches), g_og_content))
    add(act("is.workflow.actions.getitemfromlist",
            WFItemIndex=1, WFInput=out(u_content_matches), UUID=u_content_first))

    # Strip 'content="' prefix, then trailing '"'.
    add(act("is.workflow.actions.text.replace",
            WFReplaceTextFind='content="', WFReplaceTextReplace="",
            WFReplaceTextCaseSensitive=False,
            WFInput=out(u_content_first), UUID=u_og_strip))
    add(act("is.workflow.actions.text.replace",
            WFReplaceTextFind='"', WFReplaceTextReplace="",
            WFReplaceTextCaseSensitive=False,
            WFInput=out(u_og_strip), UUID=u_og_title))

    add(set_var("Title", out(u_og_title)))
    add(end_if(g_og_content))
    add(end_if(g_og_meta))

    # ── 3. Safari title (best source — overrides OG if available) ────────────
    # Note: this action only fires when shared directly from Safari.
    # Identifier uncertainty: might be is.workflow.actions.safari.getdetails
    add(act("is.workflow.actions.safari.getwebpagedetail",
            WFSafariWebPageDetailType="Page Title",
            WFInput=inp(), UUID=u_safari_title))
    add(if_has_value(out(u_safari_title), g_safari))
    add(set_var("Title", out(u_safari_title)))
    add(end_if(g_safari))

    # ── 4. Timestamps ────────────────────────────────────────────────────────
    add(act("is.workflow.actions.format.date",
            WFDateFormatStyle="Custom", WFDateFormat="yyyy-MM-dd-HH-mm-ss",
            UUID=u_ts_file))
    add(set_var("TimestampFile", out(u_ts_file)))

    add(act("is.workflow.actions.format.date",
            WFDateFormatStyle="Custom", WFDateFormat="yyyy-MM-dd HH:mm:ss",
            UUID=u_ts_human))
    add(set_var("TimestampHuman", out(u_ts_human)))

    # ── 5. Clipboard (raw text, truncated to 4000 chars) ─────────────────────
    add(act("is.workflow.actions.getclipboard", UUID=u_clip_raw))
    # Note: text.substring param names may vary; WFSubstringFromIndex/ToIndex is best guess.
    add(act("is.workflow.actions.text.substring",
            WFSubstringFromIndex=0, WFSubstringToIndex=4000,
            WFInput=out(u_clip_raw), UUID=u_clip_trunc))
    add(set_var("Clipboard", out(u_clip_trunc)))

    # ── 6. User note prompt ───────────────────────────────────────────────────
    add(act("is.workflow.actions.ask",
            WFAskActionPrompt="Add a note? (leave blank to skip)",
            WFInputType="Text",
            WFAllowEmptyInput=True,
            UUID=u_note))
    add(set_var("Note", out(u_note)))

    # ── 7. Slug generation ────────────────────────────────────────────────────
    add(act("is.workflow.actions.text.changecase",
            WFCaseType="lowercase", WFInput=var("Title"), UUID=u_slug_lower))
    # Replace any run of non-alphanumeric chars with a single hyphen.
    add(act("is.workflow.actions.text.replace",
            WFReplaceTextFind=r"[^a-z0-9]+", WFReplaceTextReplace="-",
            WFReplaceTextCaseSensitive=False, WFReplaceTextRegularExpression=True,
            WFInput=out(u_slug_lower), UUID=u_slug_hyph))
    # Trim leading/trailing hyphens.
    add(act("is.workflow.actions.text.replace",
            WFReplaceTextFind=r"^-+|-+$", WFReplaceTextReplace="",
            WFReplaceTextCaseSensitive=False, WFReplaceTextRegularExpression=True,
            WFInput=out(u_slug_hyph), UUID=u_slug_trim))
    # Truncate to 40 chars.
    add(act("is.workflow.actions.text.substring",
            WFSubstringFromIndex=0, WFSubstringToIndex=40,
            WFInput=out(u_slug_trim), UUID=u_slug_final))
    add(set_var("Slug", out(u_slug_final)))

    # ── 8. Optional Note section (omit if user left note blank) ──────────────
    add(get_text_action(txt(""), u_note_empty))
    add(set_var("NoteSection", out(u_note_empty)))

    add(if_has_value(var("Note"), g_note))
    add(get_text_action(txt("\n\n## Note\n", {"v": "Note"}), u_note_text))
    add(set_var("NoteSection", out(u_note_text)))
    add(end_if(g_note))

    # ── 9. Optional Clipboard section (omit if clipboard was empty) ───────────
    add(get_text_action(txt(""), u_clip_empty))
    add(set_var("ClipboardSection", out(u_clip_empty)))

    add(if_has_value(var("Clipboard"), g_clip))
    add(get_text_action(
        txt("\n\n## Clipboard\n```\n", {"v": "Clipboard"}, "\n```"),
        u_clip_text))
    add(set_var("ClipboardSection", out(u_clip_text)))
    add(end_if(g_clip))

    # ── 10. Assemble final Markdown ───────────────────────────────────────────
    add(get_text_action(txt(
        "# [", {"v": "Title"}, "](", {"i": True}, ")\n\n",
        "**Date:** ", {"v": "TimestampHuman"}, "\n",
        "**Source:** ", {"v": "Source"}, "\n",
        {"v": "NoteSection"},
        {"v": "ClipboardSection"},
    ), u_markdown))
    add(set_var("Markdown", out(u_markdown)))

    # ── 11. Save file ─────────────────────────────────────────────────────────
    # Path is relative to iCloud Drive root. Obsidian's container = iCloud~md~obsidian.
    # If WFAskWhereToSave ends up prompting anyway, accept it and pick ai-inbox manually.
    add(act("is.workflow.actions.documentpicker.save",
            WFInput=out(u_markdown),
            WFAskWhereToSave=False,
            WFSaveFilePath=txt(
                "iCloud~md~obsidian/Documents/Scratch/ai-inbox/",
                {"v": "TimestampFile"}, "_", {"v": "Slug"}, ".md"
            )))

    return actions


def main():
    actions = build()

    workflow = {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "1282.14",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 431817727,   # teal
            "WFWorkflowIconGlyphNumber": 59511        # bookmark-ish glyph
        },
        "WFWorkflowInputContentItemClasses": [
            "WFURLContentItem",
            "WFSafariWebPageContentItem"
        ],
        "WFWorkflowTypes": ["ShareExtension"],
        "WFWorkflowImportQuestions": [],
        "WFWorkflowOutputContentItemClasses": [],
    }

    out_path = Path(r"C:\Users\CaseyM\iCloud\iCloudDrive\iCloud~md~obsidian\Scratch\rich-bookmark-capture.shortcut")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "wb") as f:
        plistlib.dump(workflow, f, fmt=plistlib.FMT_BINARY)

    print(f"Written: {out_path}")
    print(f"Actions: {len(actions)}")


if __name__ == "__main__":
    main()
