# Juan and Done: Your Guide to Government Documents

**Project Juan and Done** · Programming Logic and Design final project

*Isang punta, tapos na.* Juan and Done helps Filipinos prepare every physical requirement (originals, photocopies, printouts) before going to a government office, so they only have to go once. Pick a document, tick what you already have, then press **"Ready ka na ba?"** to see what's still missing.

The app is written **only in Python**: **Streamlit** draws the web page, **JSON** holds the document data, and **SQLite** saves checklist progress on your own computer. The colorful Pinoy look (flag stripes, kraft-paper background, Bungee / Figtree / Space Mono fonts) is CSS written inside Python (`src/ui_theme.py`) and injected with `st.markdown(..., unsafe_allow_html=True)`.

> **Disclaimer:** Juan and Done is an independent student project. It is not a government website and is not affiliated with any Philippine government agency. Requirements, fees and links can change; always confirm with the agency's official website or Citizen's Charter. "Ready ka na!" only means you ticked every listed physical item. It is not an approval.

---

## Quick start (Windows PowerShell)

```powershell
# 1. Go to the folder that contains app.py (adjust the path to where you unzipped it)
cd "$HOME\Downloads\Project_Juan_and_Done"
Test-Path .\app.py            # must print True

# 2. Install Streamlit into the SAME Python you will run with
python -m pip install -r requirements.txt

# 3. Check code + data offline (no Streamlit needed for this step)
python tools\check_project.py

# 4. Run
python -m streamlit run app.py
```

Then open **http://localhost:8501**. Use the exact "Local URL" the terminal prints if it shows a different port. Keep PowerShell open while you use the site; press **Ctrl+C** to stop it.

You can also just **double-click `tools\launch_juan_and_done_windows.bat`**. It finds Python, installs Streamlit the first time, runs the checker, starts the server and opens your browser.

There is **no more `Email:` prompt**: `.streamlit/config.toml` sets `server.headless = true`. If `python` is not recognised, try `py -3` instead of `python` in every command. Full help: `docs/04_WINDOWS_SETUP_AND_TROUBLESHOOTING.md`.

Requirements: Windows 10/11 (macOS/Linux also work), Python 3.10+ recommended (3.9 minimum), internet for the first `pip install` only.

---

## Features (matching FLOWCHART.pdf)

| Page | What it does |
|---|---|
| **Startup** | Loads `data/documents.json`; if it is missing or broken, shows a clear message and a working **Retry** button. |
| **Home** | Hero search (Enter → Documents results), **live suggestions** (type in the suggestion box → jump to a guide), popular shortcuts, categories, common documents, website info, and a **"Continue where you left off"** card when the active profile has saved ticks. |
| **Documents** | Keyword search, category filter, "saved progress only" filter (all kept in the URL), styled cards, and a **"Walang nahanap"** state with **Show all documents**. |
| **Agencies** | Documents grouped by agency, agency search with **"Walang nahanap"**, official website buttons (non-`.gov.ph` links are flagged), links to each guide. |
| **Details** | Agency, where to apply, fees, processing time, validity, last-verified date, official links, general requirements, **What to bring** with exact Original / Photocopy / Printed / Digital labels, steps with **Online** / **In person** badges, not-found fallback, and **Start preparing / Continue preparing** (or a **Check the official website** notice). |
| **Checklist ("Ready ka na ba?")** | Checkboxes saved to SQLite instantly, one progress bar, **Reset this list** with **Confirm reset?**, and three results: **Simulan natin** (nothing ticked), **May kulang ka pa!** (missing items listed and highlighted), **Ready ka na!** (+ printable `.html` and `.txt` export). Incomplete guides never say "Ready ka na!". |
| **About** | Purpose, how it works, data sources, privacy (profiles are labels, not accounts; no IDs collected), limitations, disclaimer, and a status table of every guide. |

Phones: the layout stacks to one column and a bottom tab bar appears below 760 px wide.

---

## Folder layout

```text
Project_Juan_and_Done/
├── app.py                      # MAIN MODULE: main() starts the website (python -m streamlit run app.py)
├── requirements.txt            # streamlit>=1.42,<2.0
├── README.md
├── .streamlit/config.toml      # theme + headless (no Email: prompt)
├── data/documents.json         # 16 document guides (edit content here only)
├── assets/                     # favicon + bundled fonts (SIL OFL licence)
├── src/                        # our Python modules
│   ├── settings.py             #   global constants (paths, colors, labels)
│   ├── validation.py           #   input validation functions (Lecture 7)
│   ├── data_functions.py       #   load, search and group the documents
│   ├── checklist_functions.py  #   checklist rows, counting, "Ready ka na ba?" result, export
│   ├── database_functions.py   #   SQLite: save / read / reset ticks
│   ├── html_parts.py           #   HTML pieces (cards, lists, header, footer)
│   ├── style.py                #   CSS + fonts
│   ├── layout.py               #   header, footer, profile box, page switching
│   └── page_home.py, page_documents.py, page_agencies.py,
│       page_about.py, page_details.py, page_checklist.py   # one module per flowchart page
├── docs/01–07                  # overview, flowchart mapping, tech ref, Windows, data audit, QA, code explanation
└── tools/
    ├── check_project.py        # offline syntax + JSON + incomplete-record + SQLite checker
    └── launch_juan_and_done_windows.bat
```

`data/juan_and_done_progress.db` is created automatically the first time someone ticks an item. **Back it up before deleting or moving the project folder** if you want to keep saved progress.

## Editing document data

Edit only `data/documents.json`, then run `python tools\check_project.py`. Each record needs `id`, `name`, `agency`, `category`, `description`, `whereToGo`, `fees`, `processingTime`, `validity`, `lastVerified` (YYYY-MM-DD), `officialLinks`, `whatToBring` (`{item, type}`), `requirements`, `steps` (`{instruction, mode: online | in-person}`). Optional: `"dataStatus": "needs-verification"` and `"dataNote"` to mark a guide incomplete. **Never add fees, requirements or links that you have not checked on the official source.** See `docs/05_DATA_AUDIT_AND_LIMITATIONS.md`.

## Deployment

Streamlit needs a running Python server, so it **cannot** go on static hosting such as GitHub Pages. Use Streamlit Community Cloud (or another Python host); see `docs/03_TECHNICAL_REFERENCE.md`. On a shared host, SQLite progress is shared by everyone who uses the same profile name and may be wiped when the host restarts.
