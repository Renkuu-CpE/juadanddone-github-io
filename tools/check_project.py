# Juan and Done: offline project checker.
# It does NOT need Streamlit. Run it from the project folder:
#     python tools\check_project.py
#
# It checks:
#   1. the required files exist
#   2. every Python file has no syntax errors
#   3. data/documents.json is valid and every record has the right fields
#   4. incomplete guides can never show "Ready ka na!"
#   5. the SQLite functions can save, read and reset ticks (in a temporary file)
#   6. the old project name is not used anywhere outside the changelog
# At the end it prints the number of FAIL and WARN results.

import json
import os
import py_compile
import sys
import tempfile

# Windows consoles are not always UTF-8; replace characters they cannot show.
try:
    sys.stdout.reconfigure(errors="replace")
except AttributeError:
    pass

# Find the project folder (one folder above "tools") and let Python import "src" from it.
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_FOLDER)

from src import settings  # noqa: E402
from src import data_functions  # noqa: E402
from src import checklist_functions  # noqa: E402
from src import database_functions  # noqa: E402
from src import validation  # noqa: E402


# The "summary" dictionary is created in main() and passed to every check function,
# so no global variable is needed. It counts the FAIL and WARN results (accumulators).
def show_pass(message):
    print("PASS  " + message)


def show_fail(summary, message):
    summary["fail"] = summary["fail"] + 1
    print("FAIL  " + message)


def show_warn(summary, message):
    summary["warn"] = summary["warn"] + 1
    print("WARN  " + message)


def check_required_files(summary):
    required_files = [
        "app.py", "requirements.txt", "README.md", ".streamlit/config.toml", "data/documents.json",
        "src/__init__.py", "src/settings.py", "src/validation.py", "src/data_functions.py",
        "src/checklist_functions.py", "src/database_functions.py", "src/html_parts.py", "src/style.py",
        "src/layout.py", "src/page_home.py", "src/page_documents.py", "src/page_agencies.py",
        "src/page_about.py", "src/page_details.py", "src/page_checklist.py",
        "assets/favicon.png", "assets/fonts/Bungee-Regular-latin.woff2", "assets/fonts/Figtree-latin.woff2",
        "assets/fonts/SpaceMono-Bold-latin.woff2", "assets/fonts/FONT_LICENSES_OFL.txt",
        "tools/launch_juan_and_done_windows.bat",
    ]
    missing_files = []
    for file_name in required_files:
        if not os.path.isfile(os.path.join(PROJECT_FOLDER, file_name)):
            missing_files.append(file_name)
    if len(missing_files) > 0:
        show_fail(summary, "Missing files: " + ", ".join(missing_files))
    else:
        show_pass(str(len(required_files)) + " required files present")

    if os.path.isdir(os.path.join(PROJECT_FOLDER, "Project_Juan_and_Done")):
        show_fail(summary, "Double-nested folder found: Project_Juan_and_Done/Project_Juan_and_Done")
    else:
        show_pass("No double-nested project folder")


def find_files(extensions):
    """Return every file in the project whose name ends with one of the extensions."""
    found_files = []
    for folder, subfolders, file_names in os.walk(PROJECT_FOLDER):
        if "__pycache__" in folder:
            continue
        for file_name in file_names:
            for extension in extensions:
                if file_name.endswith(extension):
                    found_files.append(os.path.join(folder, file_name))
    return found_files


def check_syntax(summary):
    python_files = find_files([".py"])
    errors = []
    temporary_file = os.path.join(tempfile.gettempdir(), "juan_and_done_check.pyc")
    for file_path in python_files:
        try:
            py_compile.compile(file_path, cfile=temporary_file, doraise=True)
        except py_compile.PyCompileError as error:
            errors.append(os.path.relpath(file_path, PROJECT_FOLDER) + ": " + str(error.msg))
    if len(errors) > 0:
        show_fail(summary, "Syntax errors: " + "; ".join(errors))
    else:
        show_pass(str(len(python_files)) + " Python files compile")


def check_data(summary):
    """Check documents.json and return the list of documents (or [] if it fails)."""
    try:
        with open(settings.DOCUMENTS_FILE, "r", encoding="utf-8-sig") as data_file:
            raw_records = json.load(data_file)
        show_pass("documents.json is valid JSON (" + str(os.path.getsize(settings.DOCUMENTS_FILE)) + " bytes)")
    except (OSError, json.JSONDecodeError) as error:
        show_fail(summary, "documents.json cannot be read: " + str(error))
        return []

    problems = []
    for record in raw_records:
        record_id = str(record.get("id", "?"))
        for field in settings.REQUIRED_FIELDS:
            if field not in record:
                problems.append(record_id + " lacks " + field)
        for entry in record.get("whatToBring", []):
            if entry.get("type") not in settings.ITEM_TYPES:
                problems.append(record_id + " has an unknown item type: " + str(entry.get("type")))
        for step in record.get("steps", []):
            if step.get("mode") not in settings.STEP_MODES:
                problems.append(record_id + " has a step without mode online/in-person")
        for link in record.get("officialLinks", []):
            if not link.startswith("https://"):
                problems.append(record_id + " link is not https: " + link)
    if len(problems) > 0:
        show_fail(summary, "Schema problems: " + " | ".join(problems))
    else:
        show_pass("All records match the schema")

    load_result = data_functions.load_documents(settings.DOCUMENTS_FILE)
    if not load_result["ok"]:
        show_fail(summary, "The app rejected the data: " + load_result["error"] + " " + load_result["detail"])
        return []
    documents = load_result["documents"]
    show_pass("App loader accepts " + str(len(documents)) + " records")
    for warning in load_result["warnings"]:
        show_warn(summary, warning)

    non_gov_links = []
    for document in documents:
        for link in document["officialLinks"]:
            if not validation.is_gov_ph_link(link):
                non_gov_links.append(link)
    if len(non_gov_links) > 0:
        show_warn(summary, "Links that are not .gov.ph (shown with a 'double-check' note in the app): " + ", ".join(non_gov_links))
    return documents


def check_records(summary, documents):
    print("")
    print("Record status:")
    incomplete_count = 0
    for document in documents:
        status = data_functions.get_record_status(document)
        items = checklist_functions.build_checklist_items(document)
        # Pretend the user ticked every item, then ask for the result.
        all_keys = set()
        for item in items:
            all_keys.add(item["key"])
        progress = checklist_functions.count_progress(items, all_keys)
        state = checklist_functions.get_readiness_state(items, progress, status["complete"])

        if status["complete"]:
            status_text = "complete"
        else:
            status_text = "INCOMPLETE: " + "; ".join(status["reasons"])
        print("  " + document["id"].ljust(30) + " bring=" + str(len(document["whatToBring"])).rjust(2)
              + " reqs=" + str(len(document["requirements"])).rjust(2) + " steps=" + str(len(document["steps"])).rjust(2)
              + " links=" + str(len(document["officialLinks"])) + " -> " + status_text)

        if not status["complete"]:
            incomplete_count = incomplete_count + 1
            if state == "ready":
                show_fail(summary, document["id"] + " is incomplete but could show 'Ready ka na!'")
        elif len(items) > 0 and state != "ready":
            show_fail(summary, document["id"] + " is complete but the all-ticked result is " + state)

        # Every checklist item must have its own key.
        if len(all_keys) != len(items):
            show_fail(summary, document["id"] + " has two checklist items with the same key")
    show_pass(str(incomplete_count) + " incomplete record(s) are blocked from 'Ready ka na!'")
    show_pass("Checklist item keys are unique per document")


def check_database(summary):
    temporary_folder = tempfile.mkdtemp()
    test_file = os.path.join(temporary_folder, "test.db")
    try:
        ok = database_functions.create_tables(test_file) and database_functions.create_tables(test_file)
        ok = ok and database_functions.save_tick(test_file, "JAD-QA", "dfa-passport", "k1", "Item 1", True)
        ok = ok and database_functions.save_tick(test_file, "JAD-QA", "dfa-passport", "k2", "Item 2", True)
        ok = ok and database_functions.save_tick(test_file, "JAD-QA", "dfa-passport", "k2", "Item 2", False)
        ok = ok and database_functions.read_checked_keys(test_file, "JAD-QA", "dfa-passport") == {"k1"}
        ok = ok and database_functions.read_checked_keys(test_file, "Guest", "dfa-passport") == set()
        ok = ok and "dfa-passport" in database_functions.read_saved_progress(test_file, "JAD-QA")
        ok = ok and database_functions.reset_checklist(test_file, "JAD-QA", "dfa-passport") == 2
        ok = ok and database_functions.read_checked_keys(test_file, "JAD-QA", "dfa-passport") == set()
        if ok:
            show_pass("SQLite save / untick / separate profiles / reset work (temporary database)")
        else:
            show_fail(summary, "SQLite test gave an unexpected result")
    finally:
        # Remove the temporary test database.
        if os.path.isfile(test_file):
            os.remove(test_file)
        os.rmdir(temporary_folder)


def get_words(line):
    """Return the lowercase words of a line (anything that is not a letter separates words)."""
    letters_only = ""
    for character in line.lower():
        if character.isalpha():
            letters_only = letters_only + character
        else:
            letters_only = letters_only + " "
    return letters_only.split()


def check_old_name(summary):
    # The former project names are written in pieces so this checker does not find itself.
    old_names = ["ga" + "bay", "ka" + "bay"]
    hits = []
    for file_path in find_files([".py", ".md", ".json", ".toml", ".txt", ".bat", ".svg"]):
        if file_path.endswith("FONT_LICENSES_OFL.txt"):
            continue
        with open(file_path, "r", encoding="utf-8", errors="ignore") as text_file:
            line_number = 0
            for line in text_file:
                line_number = line_number + 1
                words = get_words(line)
                for old_name in old_names:
                    if old_name in words:
                        hits.append(os.path.relpath(file_path, PROJECT_FOLDER) + ":" + str(line_number))
    other_hits = []
    for hit in hits:
        if not hit.startswith(os.path.join("docs", "03_TECHNICAL_REFERENCE.md")):
            other_hits.append(hit)
    if len(other_hits) > 0:
        show_fail(summary, "Old brand text outside the changelog: " + ", ".join(other_hits))
    else:
        show_pass("Old project name appears only in the labelled changelog (" + str(len(hits)) + " line(s))")


def main():
    print("Project Juan and Done: offline checks")
    print("Folder: " + PROJECT_FOLDER)
    print("")
    summary = {"fail": 0, "warn": 0}
    check_required_files(summary)
    check_syntax(summary)
    documents = check_data(summary)
    check_records(summary, documents)
    check_database(summary)
    check_old_name(summary)
    print("")
    print("Summary: " + str(summary["fail"]) + " FAIL, " + str(summary["warn"]) + " WARN")
    print("NOTE: this checker does not start Streamlit and does not verify government information.")
    # Exit code 1 tells other programs that something failed.
    if summary["fail"] > 0:
        sys.exit(1)


main()
