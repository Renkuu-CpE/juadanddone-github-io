# 03 · Technical Reference

## Hierarchy chart (top-down design, Lecture 3)

```text
                                   app.py  main()
          ┌──────────────┬──────────────┼──────────────────┬──────────────────────┐
  load_documents_once  show_loading_error  build_context  layout.show_header   show_selected_page   layout.show_footer
          │                                  │                                   │
  data_functions.load_documents   database_functions.create_tables     ┌──────┬──────┬──────┼──────┬──────┐
                                  database_functions.read_saved_progress  home  docs  agencies about details checklist
                                                                       (page_*.py modules)
  Shared by the page modules:
    layout.py              header, footer, profile box, go_to_page, saved-progress helpers
    html_parts.py          HTML pieces (cards, lists, buttons) with escape_html()
    data_functions.py      load, record status, categories, search, agencies
    checklist_functions.py checklist rows, item keys, counting, readiness, export
    database_functions.py  SQLite: create, read, save, reset
    validation.py          input validation (Lecture 7)
    settings.py            global constants
    style.py               CSS + fonts
```

Only `layout.py`, `app.py` and the `page_*.py` modules import Streamlit. The other modules work only with strings, lists and dictionaries, so `tools/check_project.py` can test them without Streamlit.

## How one page view runs (`app.py`)

1. `main()` → `st.set_page_config(...)` → show the CSS (`make_css_once()`).
2. `load_documents_once()` → `data_functions.load_documents()` returns a dictionary `{"ok", "documents", "error", "detail", "warnings"}`. The `@st.cache_data` decorator remembers the result; the file's modification time is a parameter, so an edited file is read again.
3. If `ok` is False → `show_loading_error()` (message + Retry) and `st.stop()`.
4. `build_context()` puts everything the pages need into one dictionary: documents, documents_by_id, profile, page, database_ok, saved_progress, latest_verified.
5. `layout.show_header()` → `show_selected_page(context)` (if/elif chain) → `layout.show_footer()`.

## Where values are kept

| Value | Stored in | Survives a browser refresh? |
|---|---|---|
| Page, document id, search, category, saved filter | website address (`st.query_params`) | Yes |
| Profile name | address `?profile=` (not added for `Guest`) | Yes |
| Checklist ticks | SQLite file `data/juan_and_done_progress.db` | Yes, and after restarting |
| "Ready ka na ba?" result shown, reset confirmation, error messages | `st.session_state` | No (by design) |

**Session-state rule.** A widget's value is only changed **before** the widget is drawn (for example `read_ticks()` copies saved ticks into the checkboxes) or **inside a callback**. This avoids the `StreamlitAPIException` that the old sidebar menu could cause.

## Data model (`data/documents.json`)

A list of records. Required keys (`settings.REQUIRED_FIELDS`): `id`, `name`, `agency`, `category`, `description`, `whereToGo`, `fees`, `processingTime`, `validity`, `lastVerified`, `officialLinks[]`, `whatToBring[{item,type}]`, `requirements[]`, `steps[{instruction,mode}]`. Optional: `dataStatus` (`"needs-verification"`) and `dataNote`.

`data_functions.clean_record()` trims text and turns missing lists into `[]`. Records without `id`/`name`, or with a duplicate id, are skipped with a warning.

`data_functions.get_record_status()`: a guide is **complete** only if no list or key field is empty and it is not marked `needs-verification`. Incomplete guides show a red badge and can never reach "Ready ka na!".

## Checklist (`src/checklist_functions.py`)

- Built only from `whatToBring` (physical items). Requirements and steps are shown read-only.
- *"Original and photocopy of X"* becomes two rows: **X** [Original] and **Photocopy of X** [Photocopy]. Every other item keeps its exact JSON type label.
- Items ending in `(if …)` / `(for …)` are optional: tagged with a dashed label and counted only when ticked. An item with two such notes (BIR Form 1902 *(for employees)* or 1904 *(for jobseekers)*) is a required choice.
- **Item key** = first 12 characters of a SHA-1 code of `"<group>|<lowercase text>"` (`make_item_key()`). Reordering the JSON keeps the ticks; rewording an item unticks only that item. The refactor kept this formula, so ticks saved before the refactor still load.
- `get_readiness_state()` → `no-items`, `empty` (Simulan natin), `missing` (May kulang ka pa!), `ready` (Ready ka na!), `ready-unverified`.

## SQLite (`src/database_functions.py`)

```sql
CREATE TABLE IF NOT EXISTS checklist_progress (
    profile     TEXT NOT NULL,
    document_id TEXT NOT NULL,
    item_key    TEXT NOT NULL,
    item_label  TEXT NOT NULL DEFAULT '',
    is_done     INTEGER NOT NULL DEFAULT 0 CHECK (is_done IN (0, 1)),
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (profile, document_id, item_key)
)
```

- Each function opens a connection, works, and closes it in `finally:`. Errors are caught (`except sqlite3.Error`) and reported by the return value (`False`, `None` or `-1`); the website never crashes.
- `?` placeholders are used for every value (never text joined into SQL).
- If the database cannot be created (read-only folder), `context["database_ok"]` is False: a warning is shown and ticks live only in the checkboxes for that browser tab.

## Input validation (`src/validation.py`, Lecture 7)

| Input | Check | Function |
|---|---|---|
| `?page=` | whitelist of 6 pages | `is_valid_page()` |
| Profile name typed in the box | presence, length ≤ 32, allowed characters | `get_profile_error()` (error shown, name not applied) |
| `?profile=` in the address | remove bad characters, cut length, empty → Guest | `clean_profile_name()` |
| Home search | presence, length ≤ 80 | `get_search_error()` |
| `?q=` and agency search | cut to 80 characters | `clean_search_text()` |
| `?category=` | must be a real category | `page_documents.read_filters()` |
| `lastVerified` dates | YYYY-MM-DD format and month/day range | `is_valid_date_text()` |
| Official links | starts with http(s)://, no spaces, has a host; `.gov.ph` check | `is_safe_link()`, `is_gov_ph_link()` |

## Styling (`src/style.py`, `src/html_parts.py`)

Mockup palette: flag blue `#0038A8`, red `#C8102E`, yellow `#FCD116`, ink `#1F1A14`, kraft `#F7EDD8`, paper `#FFFBF2`. Fonts (Bungee, Figtree, Space Mono, SIL OFL) are read from `assets/fonts` and placed in the CSS as base64 text, so the look works offline. Streamlit's own header, toolbar and sidebar are hidden; buttons, inputs and checkboxes are restyled with CSS. `html_parts.escape_html()` escapes every data value (including `$`, which Streamlit would read as math). Below 760 px the layout becomes one column with a bottom tab bar; `@media print` hides navigation.

`requirements.txt` asks for `streamlit>=1.42,<2.0`. All Streamlit features used (`st.query_params`, `st.popover`, `st.toggle`, `st.container(key=...)`, `vertical_alignment`) exist in that range. `layout.make_row_container()` catches a `TypeError` in case `key=` is not supported.

## Configuration (`.streamlit/config.toml`)

`server.headless = true` (no first-run `Email:` prompt), `browser.gatherUsageStats = false`, minimal toolbar, no sidebar page list, light theme in the Juan and Done colours. Streamlit reads this file only when started **from the project folder**.

## Deployment

Streamlit needs a Python server, so static hosts (GitHub Pages) cannot run it. For Streamlit Community Cloud: push the folder to GitHub (without `data/*.db`), set the main file to `app.py`, and re-test that links open the right page. On a shared host, progress is shared by everyone who uses the same profile name.

## Changelog / migration (REBRAND-HISTORY)

This section is the only place the project's former names appear, for provenance.

- **Rebrand:** the project was previously called *GABAY* (also spoken as "Project Kabay"). Because that name is taken, everything is now **Project Juan and Done / Juan and Done**: app title, favicon, footer, disclaimers, database file (`data/juan_and_done_progress.db`, previously `data/gabay_progress.db`), Windows launcher (`tools/launch_juan_and_done_windows.bat`), QA profile (`JAD-QA`) and all docs.
- **UI:** plain Streamlit sidebar + tabs replaced with the Juan and Done mockup design and flowchart pages.
- **Fixed:** sidebar navigation state mutation (StreamlitAPIException risk); duplicate progress bars on the checklist; SQLite connections now always closed; progress keyed by stable item hash instead of list position; Windows launch stalling at the `Email:` prompt; double-nested folder layout; partial Mayor's Permit record could claim "READY KA NA!".
- **Data:** switched from the 45,761-byte repaired JSON (Mayor's Permit with 4 items and no requirements/steps) to the 47,703-byte Juan and Done JSON, whose Mayor's Permit record was rebuilt from the team's research notes. Both LGU guides are now flagged `needs-verification` (see doc 05).
- **Not migrated:** any old `gabay_progress.db`. Its rows were keyed by list position and cannot be safely mapped to the new item keys. No such file was included in the handover.
- **Refactor for the course lessons (Nov 2026):** the code was rewritten into 14 beginner-style modules (`settings`, `validation`, `data_functions`, `checklist_functions`, `database_functions`, `html_parts`, `style`, `layout`, six `page_*` modules) with a `main()` entry point. Classes, data classes, regular expressions, list comprehensions, lambdas and type hints were replaced with functions, dictionaries, lists, loops and if/elif decisions. Input validation with error messages was added for the profile name and the Home search. Checklist item keys and the database table did not change, so saved progress still loads.
