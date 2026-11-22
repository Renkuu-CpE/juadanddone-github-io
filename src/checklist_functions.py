# This module builds the "Ready ka na ba?" checklist and decides the result.
# It works only with lists and dictionaries (no Streamlit), so it is easy to test.
#
# Flowchart page 7:
#   build_checklist_items()  -> "Display the checklist"
#   count_progress()         -> "Update the progress bar"
#   get_readiness_state()    -> the decisions "All items ticked?" / "Any item ticked?"
#   make_export_text/html()  -> "Print the checklist"

import hashlib
from datetime import datetime

from src import settings
from src import html_parts

# The beginning of an "Original & Photocopy" item that we split into two rows.
BOTH_PREFIXES = [
    "original and photocopy of ",
    "original & photocopy of ",
    "original and a photocopy of ",
    "original and clear photocopy of ",
    "original and a clear photocopy of ",
]
# Words that start a condition, e.g. "(if applicable)" or "(for married females ...)".
CONDITION_STARTS = ["(if ", "(for ", "(only if "]


def make_item_key(group, text):
    """Make a short, stable code for one checklist item.

    The code is saved in the database instead of the item's position in the list,
    so ticks stay correct even if the order of items in documents.json changes.
    hashlib is a Python library that turns any text into a fixed code
    (like a fingerprint). The same text always gives the same code.
    """
    normalized_text = " ".join(text.lower().split())
    code = hashlib.sha1((group + "|" + normalized_text).encode("utf-8")).hexdigest()
    return code[0:12]


def count_condition_notes(text):
    """Count how many '(if ...' or '(for ...' notes are inside an item text."""
    lower_text = text.lower()
    total = 0
    for start_word in CONDITION_STARTS:
        total = total + lower_text.count(start_word)
    return total


def split_condition(text):
    """Separate the condition at the end of an item.

    'PSA Marriage Certificate (for married females)' returns
    ('PSA Marriage Certificate', 'For married females').
    Items with no condition return (text, "").
    Items with TWO notes (e.g. 'Form 1902 (for employees) or Form 1904 (for jobseekers)')
    are choices that everyone needs one of, so they have no condition.
    """
    stripped = text.strip()
    # The text must end with ")" to have a condition at the end.
    if not stripped.endswith(")"):
        return text, ""
    start = stripped.rfind("(")
    if start == -1:
        return text, ""
    # The note must start with "(if", "(for" or "(only if".
    note_start = stripped[start:].lower()
    starts_with_condition = False
    for start_word in CONDITION_STARTS:
        if note_start.startswith(start_word):
            starts_with_condition = True
    if not starts_with_condition or count_condition_notes(stripped) > 1:
        return text, ""
    condition = stripped[start + 1:len(stripped) - 1].strip()
    if condition.lower() == "if applicable":
        condition = "If applicable"
    else:
        condition = condition[0].upper() + condition[1:]
    return stripped[0:start].strip(), condition


def find_both_prefix(text):
    """Return the 'Original and photocopy of ' prefix found at the start of the text, or ""."""
    lower_text = text.lower()
    for prefix in BOTH_PREFIXES:
        if lower_text.startswith(prefix):
            return text[0:len(prefix)]
    return ""


def build_checklist_items(document):
    """Flowchart 7-B: turn the document's 'whatToBring' list into checklist rows.

    Each row is a dictionary:
        {"key", "text", "tag", "source_text", "source_type", "condition"}
    An 'Original & Photocopy' item written as 'Original and photocopy of X'
    becomes two rows (X and 'Photocopy of X') because they are two different papers.
    """
    items = []
    used_keys = []
    for entry in document.get("whatToBring", []):
        text, condition = split_condition(entry["item"])
        item_type = entry["type"]
        prefix = find_both_prefix(text)

        # A list of (text, tag, group) rows to add for this entry.
        rows = []
        if item_type == "Original & Photocopy" and prefix != "":
            base = text[len(prefix):]
            if base != "":
                base = base[0].upper() + base[1:]
            # Keep "the" in lowercase inside "Photocopy of the ...".
            photocopy_base = base
            if base.lower().startswith("the "):
                photocopy_base = base[0].lower() + base[1:]
            rows.append([base, "Original", "original"])
            rows.append(["Photocopy of " + photocopy_base, "Photocopy", "photocopy"])
        else:
            rows.append([text, item_type, item_type.lower()])

        for row in rows:
            row_text = row[0]
            key = make_item_key(row[2], row_text)
            # While loop: if two rows have the same text, give the second one a new key.
            while key in used_keys:
                key = make_item_key(row[2] + "+", row_text + key)
            used_keys.append(key)
            items.append({
                "key": key,
                "text": row_text,
                "tag": row[1],
                "source_text": entry["item"],
                "source_type": entry["type"],
                "condition": condition,
            })
    return items


def count_progress(items, checked_keys):
    """Flowchart 7-C: count the ticked items (accumulator pattern).

    Items with a condition only count when the user ticks them.
    Returns a dictionary: {"total", "done", "missing", "optional_open", "percent"}.
    """
    total = 0
    done = 0
    optional_open = 0
    missing = []
    for item in items:
        is_ticked = item["key"] in checked_keys
        if item["condition"] != "" and not is_ticked:
            # An optional item that is not ticked is not counted.
            optional_open = optional_open + 1
        else:
            total = total + 1
            if is_ticked:
                done = done + 1
            else:
                missing.append(item)
    percent = 0
    if total > 0:
        percent = round(done * 100 / total)
    return {"total": total, "done": done, "missing": missing, "optional_open": optional_open, "percent": percent}


def get_done_and_total(document, checked_keys):
    """Return two numbers: how many items are ticked and how many are counted."""
    progress = count_progress(build_checklist_items(document), checked_keys)
    return progress["done"], progress["total"]


def get_readiness_state(items, progress, record_is_complete):
    """Flowchart 7-D/7-E: decide the "Ready ka na ba?" result.

    Uses an if-elif-else chain (multiple alternative decision):
        no items            -> "no-items"
        nothing ticked      -> "empty"            (Simulan natin)
        something missing   -> "missing"          (May kulang ka pa!)
        all ticked          -> "ready"            (Ready ka na!)
        all ticked, but the guide is incomplete -> "ready-unverified"
    """
    if len(items) == 0:
        return "no-items"
    elif progress["done"] == 0:
        return "empty"
    elif len(progress["missing"]) > 0:
        return "missing"
    elif record_is_complete:
        return "ready"
    else:
        return "ready-unverified"


def get_ready_tips(document):
    """Return a list of short reminders shown under 'Ready ka na!'."""
    all_text = " ".join(document.get("requirements", []))
    for step in document.get("steps", []):
        all_text = all_text + " " + step["instruction"]
    all_text = all_text.lower()

    tips = ["Ilagay ang lahat sa iisang folder o long brown envelope."]
    if "appointment" in all_text:
        tips.append("Check your appointment date, time and branch.")
    if "attire" in all_text or "dress" in all_text or "collared" in all_text:
        tips.append("Wear the proper attire mentioned in the requirements.")
    if document.get("whereToGo", "") != "":
        tips.append("Pumunta sa: " + document["whereToGo"])
    return tips


# ======================================================================== export (print)
def make_export_text(document, items, checked_keys, state, profile, status):
    """Make a plain-text checklist summary that the user can download (.txt)."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        settings.APP_NAME + " - checklist summary",
        "=" * 40,
        "Document : " + document["name"],
        "Agency   : " + (document.get("agency") or "Not listed"),
        "Where    : " + (document.get("whereToGo") or "Not listed"),
        "Fees     : " + (document.get("fees") or "Not listed"),
        "Profile  : " + profile,
        "Printed  : " + now,
        "Status   : " + settings.RESULT_TITLES.get(state, state),
        "Dataset last verified (as recorded by the team): " + (document.get("lastVerified") or "not listed"),
        "",
        "What to bring",
        "-------------",
    ]
    for item in items:
        mark = "[ ]"
        if item["key"] in checked_keys:
            mark = "[x]"
        extra = ""
        if item["condition"] != "":
            extra = " (" + item["condition"] + ")"
        lines.append(mark + " " + item["text"] + " [" + item["tag"] + "]" + extra)

    lines.append("")
    lines.append("Official links listed in our dataset:")
    if len(document.get("officialLinks", [])) == 0:
        lines.append("  - none listed; check with the office directly")
    for link in document.get("officialLinks", []):
        lines.append("  - " + link)

    if not status["complete"]:
        lines.append("")
        lines.append("WARNING: this guide is incomplete or needs verification:")
        for reason in status["reasons"]:
            lines.append("  - " + reason)
        if status["note"] != "":
            lines.append("  - " + status["note"])

    lines.append("")
    lines.append(settings.APP_NAME + " is an independent student project, not a government website.")
    lines.append("Requirements can change. Confirm with the agency's official website or Citizen's Charter.")
    lines.append("This list only covers the physical items in our dataset; it is not an approval of your application.")
    return "\n".join(lines) + "\n"


def make_export_html(document, items, checked_keys, state, profile, status):
    """Make a small printable web page (.html). The user opens it and presses Ctrl+P."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    safe = html_parts.escape_html

    rows = ""
    for item in items:
        if item["key"] in checked_keys:
            row_class = "done"
            box = "&#10003;"
        else:
            row_class = "todo"
            box = ""
        condition = ""
        if item["condition"] != "":
            condition = " <small>(" + safe(item["condition"]) + ")</small>"
        rows = rows + ("<li class='" + row_class + "'><span class='box'>" + box + "</span><span>" + safe(item["text"])
                       + " <em>[" + safe(item["tag"]) + "]</em>" + condition + "</span></li>")

    links = ""
    for link in document.get("officialLinks", []):
        links = links + "<li>" + safe(link) + "</li>"
    if links == "":
        links = "<li>None listed &mdash; check with the office directly.</li>"

    warning = ""
    if not status["complete"]:
        reasons = ""
        for reason in status["reasons"]:
            reasons = reasons + "<li>" + safe(reason) + "</li>"
        note = ""
        if status["note"] != "":
            note = "<p>" + safe(status["note"]) + "</p>"
        warning = "<div class='warn'><strong>Incomplete guide &mdash; verify before you go.</strong><ul>" + reasons + "</ul>" + note + "</div>"

    style = (
        "body{font-family:Figtree,'Segoe UI',Arial,sans-serif;color:#1F1A14;margin:32px;max-width:760px}"
        "h1{font-size:24px;color:#0038A8;margin:0 0 4px}"
        ".stripe{height:6px;background:#0038A8;box-shadow:0 6px 0 #FCD116,0 12px 0 #C8102E;margin-bottom:26px}"
        ".meta{color:#3A3127;font-size:14px;line-height:1.6}"
        ".status{display:inline-block;border:2px solid #1F1A14;border-radius:999px;padding:4px 12px;font-weight:800;margin:12px 0}"
        "ul.items{list-style:none;padding:0} ul.items li{display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px dashed #8A6A3B}"
        ".box{flex:none;width:18px;height:18px;border:2px solid #1F1A14;border-radius:4px;text-align:center;line-height:16px;font-weight:800}"
        "li.todo{color:#B00E28} em{font-style:normal;color:#6E5228;font-size:13px}"
        ".warn{border:2px solid #C8102E;border-radius:10px;padding:10px 14px;margin:16px 0}"
        "footer{margin-top:24px;font-size:12px;color:#6E5228} @media print{body{margin:12mm}}"
    )
    page = (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><title>" + safe(settings.APP_NAME) + " &ndash; "
        + safe(document["name"]) + "</title>\n<style>" + style + "</style></head><body>\n"
        + "<div class=\"stripe\"></div>\n<h1>" + safe(document["name"]) + "</h1>\n"
        + "<div class=\"meta\">" + safe(document.get("agency") or "") + "<br>Where: " + safe(document.get("whereToGo") or "Not listed")
        + "<br>Fees: " + safe(document.get("fees") or "Not listed") + "<br>Profile: " + safe(profile) + " &middot; Printed " + now
        + " &middot; Dataset last verified: " + safe(document.get("lastVerified") or "not listed") + "</div>\n"
        + "<div class=\"status\">" + safe(settings.RESULT_TITLES.get(state, state)) + "</div>\n" + warning + "\n"
        + "<h2>What to bring</h2><ul class=\"items\">" + rows + "</ul>\n"
        + "<h2>Official links in our dataset</h2><ul>" + links + "</ul>\n"
        + "<footer>" + safe(settings.APP_NAME) + " is an independent student project, not a government website. Requirements can change; "
        + "confirm with the agency's official website or Citizen's Charter. This list covers only the physical items in our dataset "
        + "and is not an approval of your application.</footer>\n</body></html>\n"
    )
    return page
