# This module reads and processes the document data stored in data/documents.json.
# It does NOT draw anything on the screen; it only works with data
# (lists and dictionaries), so it can be tested without Streamlit.
#
# Main functions:
#   load_documents()       flowchart page 1: load the JSON file (with error checking)
#   get_record_status()    decide if a document guide is complete or incomplete
#   search_documents()     flowchart page 3: keyword + category + saved filter
#   group_by_agency()      flowchart page 4: group documents by agency

import json
import os

from src import settings
from src import validation

TEXT_FIELDS = ["agency", "category", "description", "whereToGo", "fees", "processingTime", "validity", "lastVerified"]
LIST_FIELDS = ["officialLinks", "whatToBring", "requirements", "steps"]
FIELD_LABELS = {
    "officialLinks": "official links",
    "whatToBring": "'What to bring' items",
    "requirements": "general requirements",
    "steps": "step-by-step instructions",
    "agency": "agency",
    "whereToGo": "where to apply",
    "fees": "fees",
    "processingTime": "processing time",
    "validity": "validity",
    "lastVerified": "last-verified date",
}


# ======================================================================== loading
def make_load_result(ok, documents, error, detail, warnings):
    """Put the result of loading into one dictionary so it can be returned together."""
    return {"ok": ok, "documents": documents, "error": error, "detail": detail, "warnings": warnings}


def clean_step_mode(mode):
    """Turn spellings like 'In Person' or 'onsite' into 'in-person' or 'online'."""
    mode = validation.clean_text(mode).lower().replace("_", "-").replace(" ", "-")
    if mode == "online" or mode == "on-line":
        return "online"
    elif mode == "in-person" or mode == "inperson" or mode == "onsite" or mode == "on-site" or mode == "walk-in":
        return "in-person"
    else:
        return mode


def clean_record(raw):
    """Return a clean copy of one document record from the JSON file.

    Missing text becomes "" and missing lists become [] so the pages never crash.
    Nothing is invented: empty fields stay empty.
    """
    document = {}
    # Copy every key first, so extra keys in the file are kept.
    for key in raw:
        document[key] = raw[key]

    document["id"] = validation.clean_text(raw.get("id"))
    document["name"] = validation.clean_text(raw.get("name"))
    for field in TEXT_FIELDS:
        document[field] = validation.clean_text(raw.get(field))

    # officialLinks and requirements: keep only non-empty text items.
    for field in ["officialLinks", "requirements"]:
        clean_list = []
        if type(raw.get(field)) == list:
            for entry in raw.get(field):
                text = validation.clean_text(entry)
                if text != "":
                    clean_list.append(text)
        document[field] = clean_list

    # whatToBring: a list of dictionaries with "item" and "type".
    bring_list = []
    if type(raw.get("whatToBring")) == list:
        for entry in raw.get("whatToBring"):
            if type(entry) == dict and validation.clean_text(entry.get("item")) != "":
                item_type = validation.clean_text(entry.get("type"))
                if item_type == "":
                    item_type = "Item"
                bring_list.append({"item": validation.clean_text(entry.get("item")), "type": item_type})
    document["whatToBring"] = bring_list

    # steps: a list of dictionaries with "instruction" and "mode".
    step_list = []
    if type(raw.get("steps")) == list:
        for entry in raw.get("steps"):
            if type(entry) == dict and validation.clean_text(entry.get("instruction")) != "":
                step_list.append({
                    "instruction": validation.clean_text(entry.get("instruction")),
                    "mode": clean_step_mode(entry.get("mode")),
                })
    document["steps"] = step_list

    document["dataStatus"] = validation.clean_text(raw.get("dataStatus")).lower()
    document["dataNote"] = validation.clean_text(raw.get("dataNote"))
    return document


def load_documents(file_path):
    """Flowchart page 1 (1-A): read documents.json and check that it is usable.

    Returns a dictionary: {"ok", "documents", "error", "detail", "warnings"}.
    """
    # Decision: does the file exist?
    if not os.path.isfile(file_path):
        return make_load_result(False, [], "The document database was not found.", "Missing file: " + file_path, [])

    # Exception handling: reading or decoding the file can fail.
    try:
        with open(file_path, "r", encoding="utf-8-sig") as data_file:
            data = json.load(data_file)
    except json.JSONDecodeError as error:
        detail = error.msg + " (line " + str(error.lineno) + ", column " + str(error.colno) + ")"
        return make_load_result(False, [], "The document database is not valid JSON.", detail, [])
    except OSError as error:
        return make_load_result(False, [], "The document database could not be opened.", str(error), [])

    if type(data) != list:
        return make_load_result(False, [], "The document database has the wrong shape.", "Expected a JSON list of records.", [])

    documents = []
    warnings = []
    used_ids = []
    record_number = 0
    # Loop through every record in the file.
    for raw in data:
        record_number = record_number + 1
        if type(raw) != dict:
            warnings.append("Record #" + str(record_number) + " skipped: not an object.")
            continue
        document = clean_record(raw)
        if document["id"] == "" or document["name"] == "":
            warnings.append("Record #" + str(record_number) + " skipped: missing id or name.")
            continue
        if document["id"] in used_ids:
            warnings.append("Record #" + str(record_number) + " skipped: duplicate id '" + document["id"] + "'.")
            continue
        used_ids.append(document["id"])
        documents.append(document)

    if len(documents) == 0:
        return make_load_result(False, [], "The document database is empty.", "No usable records (each needs an id and a name).", warnings)
    return make_load_result(True, documents, "", "", warnings)


def make_documents_by_id(documents):
    """Return a dictionary so a document can be found quickly by its id."""
    documents_by_id = {}
    for document in documents:
        documents_by_id[document["id"]] = document
    return documents_by_id


# ======================================================================== record status
def get_record_status(document):
    """Decide if a document guide is complete.

    A guide is complete only if no important field is empty and it is not
    marked "needs-verification". Incomplete guides never show "Ready ka na!".
    """
    missing = []
    for field in LIST_FIELDS:
        if len(document.get(field, [])) == 0:
            missing.append(field)
    for field in ["agency", "whereToGo", "fees", "processingTime", "validity", "lastVerified"]:
        if document.get(field, "") == "":
            missing.append(field)

    needs_verification = document.get("dataStatus") == "needs-verification"

    reasons = []
    for field in missing:
        reasons.append("No " + FIELD_LABELS.get(field, field) + " in our dataset")
    if needs_verification:
        reasons.append("Marked 'needs verification' by the data team")

    # Boolean flag: True only when nothing is missing AND it is not flagged.
    is_complete = len(missing) == 0 and not needs_verification
    return {
        "complete": is_complete,
        "missing": missing,
        "needs_verification": needs_verification,
        "has_checklist": len(document.get("whatToBring", [])) > 0,
        "reasons": reasons,
        "note": document.get("dataNote", ""),
    }


def count_incomplete(documents):
    """Count how many document guides are incomplete (accumulator pattern)."""
    total = 0
    for document in documents:
        if not get_record_status(document)["complete"]:
            total = total + 1
    return total


# ======================================================================== categories and names
def make_slug(text):
    """Turn 'Clearances and Employment' into 'clearances-and-employment' for the URL."""
    slug = ""
    for character in text.lower():
        if (character >= "a" and character <= "z") or (character >= "0" and character <= "9"):
            slug = slug + character
        elif not slug.endswith("-"):
            # Any other character becomes one dash.
            slug = slug + "-"
    slug = slug.strip("-")
    if slug == "":
        return "other"
    return slug


def get_category_label(category_name):
    """Return the short label of a category (or the name itself)."""
    if category_name == "":
        return "Other"
    return settings.CATEGORY_LABELS.get(category_name, category_name)


def get_categories(documents):
    """Return a list of categories: [{"slug", "name", "label", "count"}, ...]."""
    categories = []
    for document in documents:
        name = document.get("category") or "Other"
        found = False
        # Look for the category in the list we are building.
        for category in categories:
            if category["name"] == name:
                category["count"] = category["count"] + 1
                found = True
        if not found:
            categories.append({"slug": make_slug(name), "name": name, "label": get_category_label(name), "count": 1})
    return categories


def get_short_name(document):
    """Return the short card name, e.g. 'Passport'."""
    return settings.SHORT_NAMES.get(document.get("id", ""), document.get("name", ""))


def get_step_modes(document):
    """Return a list of the step modes used by a document, e.g. ['online', 'in-person']."""
    modes = []
    for step in document.get("steps", []):
        if step["mode"] != "" and step["mode"] not in modes:
            modes.append(step["mode"])
    return modes


# ======================================================================== search
def make_search_text(document):
    """Join the searchable fields of a document into one lowercase string."""
    parts = [document.get("name", ""), document.get("agency", ""), document.get("category", ""),
             document.get("id", ""), document.get("description", ""), document.get("whereToGo", ""),
             get_short_name(document)]
    return " ".join(parts).lower()


def matches_all_words(text, words):
    """Return True if every word appears in the text (logical AND across all words)."""
    for word in words:
        if word not in text:
            return False
    return True


def search_documents(documents, search_text, category_slug, only_ids):
    """Flowchart page 3 (3-A to 3-D): search and filter the documents.

    search_text   words typed by the user ("" means no keyword)
    category_slug category from the URL ("" means all categories)
    only_ids      list of ids to keep (saved-progress filter) or None for all
    Documents whose NAME matches are listed first.
    """
    words = search_text.lower().split()
    name_matches = []
    other_matches = []
    for document in documents:
        # Category filter
        if category_slug != "" and make_slug(document.get("category") or "Other") != category_slug:
            continue
        # Saved-progress filter
        if only_ids is not None and document["id"] not in only_ids:
            continue
        # Keyword filter
        if matches_all_words(make_search_text(document), words):
            name_text = (document["name"] + " " + get_short_name(document)).lower()
            if len(words) > 0 and matches_all_words(name_text, words):
                name_matches.append(document)
            else:
                other_matches.append(document)
    return name_matches + other_matches


# ======================================================================== agencies
def split_agency_name(agency):
    """Split 'Department of Foreign Affairs (DFA)' into the full name and its acronyms.

    Returns two values: the full name and a list of acronyms, e.g.
    ('Department of Foreign Affairs', ['DFA']).
    """
    if agency == "":
        agency = "Agency not listed"
    full_name = ""
    acronyms = []
    position = 0
    # While loop: walk through the text and pick out each "( ... )" part.
    while position < len(agency):
        start = agency.find("(", position)
        if start == -1:
            full_name = full_name + agency[position:]
            position = len(agency)
        else:
            end = agency.find(")", start)
            if end == -1:
                end = len(agency) - 1
            full_name = full_name + agency[position:start] + " "
            acronyms.append(agency[start + 1:end].strip())
            position = end + 1
    full_name = validation.clean_text(full_name)
    if full_name == "":
        full_name = agency
    return full_name, acronyms


def make_monogram(full_name, acronyms):
    """Choose the short code shown in the yellow box of an agency card."""
    candidates = []
    for acronym in acronyms:
        code = settings.AGENCY_MONOGRAMS.get(acronym, acronym)
        # Remove the parent agency part, e.g. 'DOJ-NBI' becomes 'NBI'.
        if code.startswith("DOJ-"):
            code = code[4:]
        if code.startswith("DOTr-"):
            code = code[5:]
        code = code.split("/")[0].strip()
        if code != "":
            candidates.append(code)
    if len(candidates) == 0:
        # No acronym: use the first letters of the capitalized words.
        letters = ""
        for word in full_name.split():
            if word[0].isupper():
                letters = letters + word[0]
        candidates.append(letters)
    # Pick the shortest candidate.
    shortest = candidates[0]
    for code in candidates:
        if len(code) < len(shortest):
            shortest = code
    return shortest[0:7]


def group_by_agency(documents):
    """Flowchart page 4 (4-A): group documents by agency.

    Returns a list of dictionaries: {"name", "acronyms", "docs", "links", "monogram"},
    sorted alphabetically by agency name.
    """
    groups = {}
    for document in documents:
        full_name, acronyms = split_agency_name(document.get("agency", ""))
        group_key = full_name.lower()
        # Create the group the first time we see this agency.
        if group_key not in groups:
            groups[group_key] = {"name": full_name, "acronyms": [], "docs": [], "links": []}
        group = groups[group_key]
        for acronym in acronyms:
            if acronym not in group["acronyms"]:
                group["acronyms"].append(acronym)
        group["docs"].append(document)
        for link in document.get("officialLinks", []):
            if validation.is_safe_link(link) and link not in group["links"]:
                group["links"].append(link)

    agency_list = []
    for group_key in sorted(groups):
        group = groups[group_key]
        group["monogram"] = make_monogram(group["name"], group["acronyms"])
        agency_list.append(group)
    return agency_list


def search_agencies(agency_list, search_text):
    """Flowchart page 4 (4-C): keep only agencies that match every typed word."""
    words = search_text.lower().split()
    if len(words) == 0:
        return agency_list
    found = []
    for agency in agency_list:
        document_names = ""
        for document in agency["docs"]:
            document_names = document_names + " " + document["name"]
        text = (agency["name"] + " " + " ".join(agency["acronyms"]) + " " + document_names + " " + " ".join(agency["links"])).lower()
        if matches_all_words(text, words):
            found.append(agency)
    return found


def get_latest_verified_date(documents):
    """Return the newest 'lastVerified' date in the data (or "" if there is none)."""
    latest = ""
    for document in documents:
        date_text = document.get("lastVerified", "")
        # Dates written as YYYY-MM-DD can be compared like normal strings.
        if validation.is_valid_date_text(date_text) and date_text > latest:
            latest = date_text
    return latest
