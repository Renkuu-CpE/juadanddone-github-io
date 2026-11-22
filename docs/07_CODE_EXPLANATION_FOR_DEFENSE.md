# 07 · Code Explanation for the Project Defense

This document explains how the source code of **Juan and Done** uses the lessons of CpE 203 Programming Logic and Design (Lectures 1–7, Module 6 Functions, Module 8 Exceptions).

---

## A. Lesson-to-Code Alignment

| Programming lesson | Concept applied | Python file | Function or code section |
|---|---|---|---|
| Ch 1 · Main memory vs secondary storage | Short-lived values in memory vs saved ticks on disk | `database_functions.py`, `page_checklist.py` | `st.session_state` flags vs `save_tick()` writing to the `.db` file |
| Ch 2 · Input–Process–Output | Each page reads input, processes it, displays output | `page_documents.py` | `show_documents_page()` (comments mark INPUT / PROCESS / OUTPUT) |
| Ch 2 · Variables, initialization | Variables set to a starting value before use | `checklist_functions.py` | `count_progress()`: `total = 0`, `done = 0` |
| Ch 2 · Named constants | UPPERCASE values that never change | `settings.py` | `APP_NAME`, `DATABASE_FILE`, `PROFILE_MAX_LENGTH`, `VALID_PAGES` |
| Ch 2 · Internal documentation | `#` comments and docstrings | every module | module header comments, function docstrings |
| Ch 3 · Data types | `str`, `int`, `float`, `bool`, `list`, `dict`, `set` | `data_functions.py`, `database_functions.py` | records are `dict`s, documents are a `list`, ticks are a `set` |
| Ch 3 · Relational operators | `==`, `!=`, `<`, `>`, `<=`, `>=` | `validation.py` | `is_valid_date_text()` (`month >= 1 and month <= 12`) |
| Ch 3 · Modules, divide and conquer | Program split into modules with one job each | `src/` folder | 14 modules (see Part B) |
| Ch 3 · Main module and calls | `main()` calls the other modules; called at the end of the file | `app.py` | `main()`, last line `main()` |
| Ch 3 · Hierarchy chart / top-down design | main → page modules → helper modules | `docs/03`, `app.py` header comment | hierarchy chart |
| Ch 3 · Arguments and parameters | Data passed into functions | all modules | e.g. `make_document_card(document, profile, card_number, status, done, total)` |
| Ch 3 · Local variables / avoid global variables | Values passed in a `context` dictionary instead of globals | `app.py` | `build_context()`; pages receive `context` as a parameter |
| Ch 3 · Global constants | Shared read-only values | `settings.py` | imported with `from src import settings` |
| Ch 3.1 · Sequence structure | Statements run top to bottom | `page_home.py` | `show_home_page()`: hero → continue card → how-it-works → categories → cards |
| Ch 4 · Single alternative (if-then) | Do something only if a condition is true | `page_home.py` | `show_continue_card()`: `if len(started_documents) == 0: return` |
| Ch 4 · Dual alternative (if-then-else) | Two paths | `page_documents.py` | `if saved_only:` title "Checklist ko" `else:` "Mga Dokumento" |
| Ch 4 · Nested decisions | A decision inside another decision | `page_details.py` | `make_preparing_box()`: has checklist? → started? |
| Ch 4 · If-elif-else (multi-way) | Choose among many results | `checklist_functions.py` | `get_readiness_state()` (5 results) |
| Ch 4 · Case structure with default | Choose the page; default = Home | `app.py` | `show_selected_page()` |
| Ch 4 · Logical operators AND / OR / NOT | Compound conditions | `validation.py`, `data_functions.py` | `is_safe_link()`; `get_record_status()`: `len(missing) == 0 and not needs_verification` |
| Ch 4 · String comparison and case | Compare text after `.lower()` | `data_functions.py` | `search_documents()`, `matches_all_words()` |
| Ch 4 · Boolean flags | True/False values that remember a state | `page_checklist.py` | `"show_result_<id>"`, `"confirm_reset_<id>"`, `database_ok` |
| Ch 5 · Count-controlled loop (for) | Repeat for every item in a list | `html_parts.py` | `make_steps_list()` with a step counter |
| Ch 5 · Condition-controlled loop (while) | Repeat while a condition is true | `data_functions.py`, `checklist_functions.py` | `split_agency_name()`; duplicate-key loop in `build_checklist_items()` |
| Ch 5 · Running total / accumulator | Add up values in a loop, start at 0 | `checklist_functions.py`, `data_functions.py` | `count_progress()`, `count_incomplete()` |
| Ch 5 · Nested loops | A loop inside a loop | `page_checklist.py` | `show_checklist_rows()`: loop over groups, then over items |
| Ch 5 · Avoiding infinite loops | Loop variable changes every pass | `data_functions.py` | `split_agency_name()` always moves `position` forward |
| Module 6 · Functions that return values | `def …: return …` | every module | e.g. `get_short_name()`, `make_slug()` |
| Module 6 · Returning two values | `return done, total` | `checklist_functions.py` | `get_done_and_total()`, `data_functions.split_agency_name()` |
| Module 6 · Library functions | `len()`, `str()`, `int()`, `round()`, `.lower()`, `.upper()`, slicing, `json`, `hashlib`, `base64` | many | `validation.clean_profile_name()` (slicing), `checklist_functions.make_item_key()` |
| Module 6 · Functions passed as arguments | Streamlit callbacks: `on_click=search_from_home` | page modules | buttons, checkboxes, search boxes |
| Module 6 · Decorators | `@st.cache_data` wraps a function to remember its result | `app.py` | `load_documents_once()`, `make_css_once()` |
| Lecture 7 · GIGO, input validation | Check input before using it | `validation.py` | all functions |
| Lecture 7 · Validation functions returning True/False | Clean caller code | `validation.py` | `is_valid_page()`, `is_safe_link()`, `is_valid_date_text()` |
| Lecture 7 · Presence (empty input) check | Reject an empty entry | `validation.py`, `page_home.py`, `layout.py` | `get_search_error()`, `get_profile_error()` |
| Lecture 7 · Length check | Like the 6-character password example | `validation.py` | `len(name) > settings.PROFILE_MAX_LENGTH` |
| Lecture 7 · Format check (dates) | YYYY-MM-DD and month/day ranges | `validation.py` | `is_valid_date_text()` |
| Lecture 7 · Whitelist / set inclusion | Value must be in an allowed list | `validation.py`, `page_documents.py` | `is_valid_page()`, `read_filters()` (category) |
| Lecture 7 · Error message and re-entry | Show why the input was rejected; user corrects it | `layout.py`, `page_home.py` | "Hindi tinanggap ang profile name", "Walang hinahanap" |
| Lecture 7 · Defensive programming | Expect wrong data types, missing files, bad links | `data_functions.py` | `clean_record()`, `load_documents()` |
| Module 8 · Exceptions | `try` / `except` for `JSONDecodeError`, `OSError`, `sqlite3.Error`, `TypeError` | `data_functions.py`, `database_functions.py`, `layout.py` | `load_documents()`, `save_tick()`, `make_row_container()` |

### Techniques beyond the lessons (kept because the website needs them)

| Technique | Where | Why it is needed |
|---|---|---|
| Streamlit commands (`st.button`, `st.checkbox`, `st.session_state`, `st.query_params`) | page modules, `layout.py` | Streamlit is how Python shows a web page; these replace `Input`/`Display` |
| f-strings `f"…{name}…"` | `html_parts.py`, page modules | The Python way to "Display" text with variables; much shorter than `+` for long HTML |
| HTML/CSS text inside Python strings | `html_parts.py`, `style.py` | To match the approved mockup design; it is only text stored in variables |
| SQL statements (`CREATE`, `SELECT`, `INSERT`, `DELETE`) | `database_functions.py` | To save ticks permanently in SQLite |
| `with open(...)` | `data_functions.py`, `style.py` | Opens a file and closes it automatically |
| `finally:` | `database_functions.py` | Makes sure the database connection is always closed, even after an error |
| `hashlib`, `base64` (library functions) | `checklist_functions.py`, `style.py` | Stable item codes so saved ticks survive reordering; fonts embedded in CSS |

**Removed** because they are beyond the lessons: classes and data classes, regular expressions, list comprehensions, `lambda`, type hints, `inspect`, `contextlib`, `pathlib`, `functools`.

---

## B. Modular Programming Explanation

**Why modules?** The five benefits from Lecture 3: simpler code (no 600-line file), code reuse (`html_parts.make_document_card()` is used on Home and Documents), isolated testing (`tools/check_project.py` tests the data, checklist and database modules without Streamlit), faster development and **teamwork** (each member can own a page module).

| Module | Why it exists | Main functions |
|---|---|---|
| `app.py` | Main module / entry point | `main()`, `build_context()`, `show_selected_page()`, `show_loading_error()`, `load_documents_once()` |
| `settings.py` | One place for global constants | (constants only) |
| `validation.py` | All input validation (Lecture 7) | `is_valid_page()`, `get_profile_error()`, `clean_profile_name()`, `get_search_error()`, `is_valid_date_text()`, `is_safe_link()` |
| `data_functions.py` | Load and process document data | `load_documents()`, `get_record_status()`, `get_categories()`, `search_documents()`, `group_by_agency()` |
| `checklist_functions.py` | Checklist logic | `build_checklist_items()`, `count_progress()`, `get_readiness_state()`, `make_export_text()`, `make_export_html()` |
| `database_functions.py` | File storage (SQLite) | `create_tables()`, `read_checked_keys()`, `save_tick()`, `reset_checklist()`, `read_saved_progress()` |
| `html_parts.py` | Reusable HTML pieces | `escape_html()`, `make_page_url()`, `make_header()`, `make_document_card()`, `make_steps_list()` |
| `style.py` | The look (CSS + fonts) | `make_page_css()` |
| `layout.py` | Streamlit parts shared by every page | `get_current_page()`, `go_to_page()`, `show_header()`, `show_footer()`, `show_not_found()` |
| `page_home.py` … `page_checklist.py` | One module per flowchart page | `show_home_page()`, `show_documents_page()`, `show_agencies_page()`, `show_about_page()`, `show_details_page()`, `show_checklist_page()` |

**How the modules communicate.** Modules import each other with `from src import module_name` and call functions with arguments. Data moves through **parameters and return values**, mainly the `context` dictionary built in `app.build_context()`. The only shared values are **global constants** in `settings.py`. Lower modules never import higher ones: `data_functions` does not know about pages.

**How the program starts.** Streamlit runs `app.py` from top to bottom. The imports load the modules; the last line calls `main()`. `main()` sets up the page, loads the data, decides "is the data loaded?", builds the context, shows the header, calls the selected page module, and shows the footer. When the user clicks something, Streamlit first runs the button's callback, then runs `app.py` again from the top. This works like the lesson's `While keepGoing == "y"` loop around `main()`.

**Lesson match.** This is the top-down design of Lecture 3: the big task "show the website" is broken into page modules, and each page module is broken into smaller functions (for example `show_hero()`, `show_continue_card()`). Each function has a descriptive name with no spaces that starts with a letter.

---

## C. Flowchart-to-Code Mapping

See `docs/02_FLOWCHART_TO_PYTHON_MAPPING.md` for every box. Summary:

| Flowchart page | Module | Key function(s) |
|---|---|---|
| 1 Startup | `app.py` | `main()`, `load_documents_once()`, `show_loading_error()`, `retry_loading()`, `show_selected_page()` |
| 2 Home | `page_home.py` | `show_hero()`, `show_continue_card()`, `search_from_home()`, `open_suggestion()` |
| 3 Documents | `page_documents.py` | `read_filters()`, `filters_changed()`, `show_all_documents()` + `data_functions.search_documents()` |
| 4 Agencies | `page_agencies.py` | `show_agencies_page()`, `clear_agency_search()` + `data_functions.group_by_agency()` |
| 5 About | `page_about.py` | `show_about_page()`, `make_status_table()` |
| 6 Details | `page_details.py` | `show_details_page()`, `make_preparing_box()` |
| 7 Checklist | `page_checklist.py` | `read_ticks()`, `show_checklist_rows()`, `save_tick_callback()`, `reset_callback()`, `show_result()` + `checklist_functions.get_readiness_state()` |

**Differences from the flowchart (kept on purpose):**
1. The flowchart saves to the browser (`localStorage`); the build saves to SQLite, because the app is Python-only.
2. Added safety path: an incomplete guide with every item ticked shows "Naka-tsek lahat — pero i-verify muna" instead of "Ready ka na!".
3. Added validation messages for an empty Home search and an invalid profile name (Lecture 7).

---

## D. DWI Compliance

> **Note:** no separate DWI file was in the uploaded materials. The requirements below come from `docs/01_PROJECT_OVERVIEW_AND_SCOPE.md` and the original project brief (functional requirements 1–10). Please compare them with your official DWI and tell us about any difference.

| Requirement | How it is met |
|---|---|
| Objective: prepare every physical requirement before going to an office | Checklist page with "Ready ka na ba?" results |
| Users: students, fresh graduates, job seekers | Plain English + everyday Filipino, phone layout, no sign-up |
| 1. Home page with name, explanation, navigation, search | `page_home.py` |
| 2. Directory with keyword search and category filter | `page_documents.py` |
| 3. Details: agency, where, fees, time, validity, last verified, links | `page_details.py` + `html_parts.make_facts_box()` |
| 4. What to bring separate from requirements, Original/Photocopy kept | `make_bring_list()` (exact labels) vs `make_requirements_list()` |
| 5. Steps with online / in-person mode | `make_steps_list()` |
| 6. Checkbox progress with count, percent, saved between sessions | `page_checklist.py` + SQLite |
| 7. "Ready ka na!" / "May kulang ka pa!" with the missing list | `get_readiness_state()`, `show_result()` |
| 8. Agencies directory and About/disclaimer | `page_agencies.py`, `page_about.py` |
| 9. Last verified dates and official links | facts box, links box, footer date |
| 10. Responsive, pleasing design | `style.py` (mockup colors/fonts, phone layout) |
| Limitations: not a government site, no sensitive data, incomplete guides flagged | About page, footer, `get_record_status()`, profile validation |

---

## E. Changes Made in This Refactor

| Change | Reason |
|---|---|
| Split the 600-line `views.py` into six `page_*.py` modules + `layout.py` | One module per flowchart page (Lecture 3 modules, hierarchy chart) |
| Added `main()` in `app.py` and an if/elif page chooser | Matches the lesson's main module and Case structure |
| Replaced classes/data classes (`LoadResult`, `ProgressStore`, `Ctx`, `ChecklistItem`, `Tally`) with dictionaries and functions | Classes are not in our lessons |
| Replaced regular expressions with string methods and loops | Regex is not in our lessons; loops and `.lower()`, `.find()`, slicing are |
| Replaced list comprehensions, `lambda`, `any()`, `next()` with `for` loops and named functions | Lesson-style loops and accumulators |
| Removed type hints, `inspect`, `contextlib`, `pathlib`, `functools` | Not covered; `os.path` and `finally` do the same job simply |
| Removed the in-memory store class; fallback now uses the checkboxes' own state | Simpler, no class needed |
| Added `validation.py` with error messages for the profile name and Home search | Lecture 7 input validation and defensive programming |
| Renamed modules to plain names (`data_functions`, `database_functions`, …) | Easier to explain |
| Added beginner comments that point to flowchart steps and lessons | Internal documentation (Lecture 2) |
| **Kept** the item-key formula, database table, JSON data, CSS and every feature | Preserve the website and saved user progress |

---

## F. Running Instructions (Windows PowerShell)

```powershell
cd "$HOME\Downloads\Project_Juan_and_Done"
py -3 --version                                  # if "not recognized": winget install Python.Python.3.13
py -3 -m pip install -r requirements.txt         # first time only
py -3 tools\check_project.py                     # expect: Summary: 0 FAIL, 1 WARN
py -3 -m streamlit run app.py                    # then open http://localhost:8501
```

Keep the window open while using the site; press **Ctrl+C** to stop. If `python` (not MSYS2) is your normal Python, `python` works in place of `py -3`. You can also double-click `tools\launch_juan_and_done_windows.bat`.

---

## G. Possible Defense Questions

1. **What is the main module and what does it do?**
   `main()` in `app.py`. It sets up the page, loads the data, decides whether loading worked, builds the `context` dictionary, then calls the header, the selected page module and the footer. The last line of `app.py` calls `main()`.

2. **Why did you divide the program into modules?**
   To follow the divide-and-conquer approach. Each module has one job (data, checklist, database, validation, one page each). This makes the code simpler, reusable (`make_document_card()` is used on two pages), testable (`check_project.py` tests modules without Streamlit), and easy to split among team members.

3. **How do the modules communicate?**
   With imports (`from src import data_functions`) and function calls. Data goes in through parameters and comes back through `return`. Pages receive one `context` dictionary instead of using global variables; shared fixed values are global constants in `settings.py`.

4. **Where do you use a decision structure with many branches?**
   `get_readiness_state()` uses if-elif-else to choose no-items, empty (Simulan natin), missing (May kulang ka pa!), ready (Ready ka na!) or ready-unverified. `show_selected_page()` works like a Case structure, with Home as the default.

5. **Give an example of a loop and an accumulator.**
   `count_progress()` starts `total = 0` and `done = 0`, loops through every checklist item, and adds 1 for each counted and ticked item. The accumulators must start at 0, or the count would be wrong.

6. **Where is a while loop, and how do you avoid an infinite loop?**
   `split_agency_name()` uses `while position < len(agency)`. Every pass moves `position` forward (to the end or past the next `)`), so the condition eventually becomes False.

7. **How do you validate user input?**
   `validation.py` has validation functions (Lecture 7). `get_profile_error()` checks presence (empty), length (≤ 32) and allowed characters. If the name is invalid, an error message is shown and the name is not used, so the user must type it again. The Home search rejects an empty search. Values in the address are cleaned or checked against a whitelist.

8. **What happens if documents.json is missing or broken?**
   `load_documents()` checks whether the file exists, then uses `try`/`except` for `json.JSONDecodeError` and `OSError`. It returns `ok = False` with a message, and `main()` shows the error screen with a Retry button instead of crashing (flowchart page 1).

9. **How are the ticks saved, and why not in a variable?**
   Variables live in main memory and disappear when the page reloads. `save_tick()` writes each tick to the SQLite file (secondary storage) right away, using `?` placeholders. The connection is closed in `finally:`, so the ticks survive refreshes and restarts.

10. **How does the code follow the flowchart?**
    Each flowchart page has its own module, and the comment at the top lists its flowchart steps (for example 7-E in `page_checklist.py`). Flowchart decisions map to if statements: "Is the data loaded?" → `if not load_result["ok"]`; "Document found?" → `if document_id not in context["documents_by_id"]`; "All items ticked?" → `get_readiness_state()`.
