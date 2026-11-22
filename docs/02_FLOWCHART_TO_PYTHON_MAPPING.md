# 02 · FLOWCHART.pdf → Python Mapping

`FLOWCHART.pdf` (7 pages) was drawn for a static HTML + JavaScript site. This table shows which **module and function** carries out every box in the Python build. Connector labels (1-A, 2-B, …) are the flowchart's own. Each page module also lists these steps in a comment at the top of the file.

## How Streamlit replaces browser page switching

- **Where the user is** = the website address, e.g. `?page=details&id=dfa-passport`. `layout.get_current_page()` reads `?page=`; `validation.is_valid_page()` rejects unknown names (they open Home).
- **Links** in the header, cards and chips simply change the address (`html_parts.make_page_url()`).
- **Buttons and search boxes** change the address inside a *callback* (`layout.go_to_page()`), which Streamlit runs before the page is drawn again.
- **Browser `localStorage`** → SQLite file `data/juan_and_done_progress.db` (`database_functions.py`).

## Page 1 · Startup (1-A) — `app.py`

| Flowchart box | Python |
|---|---|
| Start | `main()` is called on the last line of `app.py` |
| Build header/footer/tab bar | `layout.show_header()` / `layout.show_footer()` → `html_parts.make_header()`, `make_footer()`, `make_tab_bar()` |
| Load `data/documents.json` | `load_documents_once()` → `data_functions.load_documents()` |
| Is the data loaded? **No** → error + **Retry** | `if not load_result["ok"]:` → `show_loading_error()` (message + Retry button → `retry_loading()`) |
| Does the user retry? No → End | `st.stop()` keeps the error screen |
| Documents ready → which page? | `build_context()` then `show_selected_page()` (if / elif / else chain) |

## Page 2 · Home — `page_home.py`

| Flowchart box | Function |
|---|---|
| 2-A Search bar, suggestions, popular, categories, website info | `show_home_page()` → `show_hero()`, `make_category_grid()`, info panels |
| 2-B Saved progress? Yes → *Continue where you left off* | `show_continue_card()` (uses `layout.get_started_documents()` and `find_most_recent_document()`) |
| 2-C Presses Enter → Documents (3-C) | `search_from_home()` callback; empty search → error message (Lecture 7) |
| 2-D Picks a suggestion → Details (6-B) | `open_suggestion()` callback |
| Clicks a card / chip / category / banner | links made by `html_parts.make_page_url()` |

## Page 3 · Documents — `page_documents.py`

| Flowchart box | Function |
|---|---|
| 3-A Read q, category, view from the address | `read_filters()` (category is checked against the real categories) |
| 3-B Search / filter | `data_functions.search_documents()` |
| 3-C Any matches? **Yes** → document cards | `layout.make_cards_for()` → `html_parts.make_document_card()` |
| 3-D **No** → "Walang nahanap" + **Show all documents** | `make_state_box()` + `show_all_documents()` callback |
| 3-E Changes the search/filter (loop) | `filters_changed()` callback |

## Page 4 · Agencies — `page_agencies.py`

| Flowchart box | Function |
|---|---|
| 4-A Group documents by agency | `data_functions.group_by_agency()` (14 groups) |
| 4-B Agency search bar + cards | `show_agencies_page()`, `data_functions.search_agencies()` |
| 4-C Any agency matches? **No** → "Walang nahanap" | state box + `clear_agency_search()` |
| 4-D Official website → new tab | `html_parts.make_website_button()` (non-`.gov.ph` links labelled "double-check") |
| 4-E Document guide → Details | links in `html_parts.make_agency_card()` |

## Page 5 · About — `page_about.py`

`show_about_page()`: purpose, how it works, data sources, privacy notice, disclaimer, limitations; `make_status_table()` lists every guide's status.

## Page 6 · Details — `page_details.py`

| Flowchart box | Function |
|---|---|
| 6-A Read the id | `layout.read_url_value("id")` |
| 6-B Found? **No** → not-found + **Browse all documents** | `layout.show_not_found()` |
| 6-C Key info, links, requirements, what to bring, steps | `html_parts.make_facts_box()`, `make_links_box()`, `make_requirements_list()`, `make_bring_list()`, `make_steps_list()` |
| 6-D Has checklist items? **No** → check the official website; **Yes** → Start / Continue preparing | `make_preparing_box()` |

## Page 7 · Checklist — `page_checklist.py`

| Flowchart box | Function |
|---|---|
| 7-A Read id → found? | `show_checklist_page()` → `layout.show_not_found()` |
| 7-B Load saved ticks | `read_ticks()` → `database_functions.read_checked_keys()` |
| 7-C Show checklist + ONE progress bar; tick → save → update (loop) | `show_checklist_rows()`, `html_parts.make_progress_bar()`, `save_tick_callback()` → `database_functions.save_tick()` |
| 7-D **Reset this list** → **Confirm reset?** → clear | `set_flag()` → confirm box → `reset_callback()` → `database_functions.reset_checklist()` |
| 7-E **Ready ka na ba?** → All ticked? Any ticked? | `checklist_functions.get_readiness_state()` → `show_result()` |
| All ticked → **Ready ka na!** + print | `show_result()` state `ready` + `make_export_html()` / `make_export_text()` downloads |
| None ticked → **Simulan natin** | state `empty` |
| Some ticked → **May kulang ka pa!** + highlight missing | state `missing`; red rows from `layout.make_row_container("jadrow-miss-N")` |
| *(Added safety)* incomplete guide, all ticked | state `ready-unverified`: no "Ready ka na!", reasons shown, files named `…-REFERENCE-ONLY` |
