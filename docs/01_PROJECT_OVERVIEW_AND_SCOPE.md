# 01 · Project Overview and Scope

## Name

- **Project name:** Project Juan and Done
- **Website title:** Juan and Done (a play on "one and done")
- **Tagline:** *Isang punta, tapos na.* One trip, done.

## Problem

Many applicants queue for hours at a government office and are turned away for a missing photocopy, an ID that is not accepted, an unprinted appointment slip or a missing form. Requirements are spread across many websites and old articles.

## Solution

Juan and Done collects the requirements for 16 common Philippine government documents in one place and turns each guide's **physical items ("What to bring")** into a checklist the user ticks at home. Pressing **"Ready ka na ba?"** shows one of three results:

1. **Simulan natin**: nothing ticked yet.
2. **May kulang ka pa!**: some items ticked; the missing physical items are listed and highlighted.
3. **Ready ka na!**: every counted item is ticked; the user can print or download the checklist.

Guides that are incomplete or marked *needs verification* never show "Ready ka na!". They show *"Naka-tsek lahat — pero i-verify muna"* instead.

## Target users

College students, fresh graduates, job seekers and anyone handling routine government paperwork. The design is readable on phones, uses plain English with everyday Filipino, and works offline after installation (fonts are bundled).

## In scope

| Area | Included |
|---|---|
| Pages | Home, Documents, Agencies, About, Details, Checklist (+ startup error screen) |
| Data | 16 records in `data/documents.json` (14 complete in the dataset, 2 LGU records marked *needs verification*) |
| Progress | Per **profile name** per document, saved in local SQLite |
| Output | Printable `.html` and `.txt` checklist downloads; Ctrl+P print styles |
| Safety | Incomplete-record badges, non-`.gov.ph` link flags, independent-guide disclaimer, no sensitive data collected |

## Out of scope

- Online applications, payments, appointment booking or any connection to agency systems.
- User accounts or authentication (a profile name is only a label).
- Automatic checking of live government websites. The `lastVerified` dates are the team's recorded research dates.
- Branching checklists per applicant type. Items that apply only to some people ("(if applicable)", "(for married females …)") are tagged and only counted when ticked.

## Technology decision (why Python only)

The original planning research and `FLOWCHART.pdf` describe a static HTML/CSS/JavaScript site that stores ticks in the browser's `localStorage`. The class requirement is **Python-only source**, so Project Juan and Done is built with:

| Flowchart (static web plan) | Juan and Done (submitted build) |
|---|---|
| HTML pages + JS routing | One Streamlit app; the page comes from `?page=` in the URL |
| `main.js` header/footer/tab bar | `src/html_parts.py` + `src/layout.py` (HTML made by Python functions) |
| `css/styles.css` | CSS string in `src/style.py`, shown with `st.markdown` |
| `localStorage` ticks | SQLite file `data/juan_and_done_progress.db` |
| `fetch('data/documents.json')` | `src/data_functions.load_documents()` with validation |

This supersedes the `localStorage` / static-hosting notes in the flowchart. The *logic* (decisions, states, messages) follows the flowchart exactly; see `02_FLOWCHART_TO_PYTHON_MAPPING.md`.

## Team decisions still open

- Keep all 16 guides for the demo, or present the 14 complete ones and show the 2 LGU guides as "needs verification" (current build does the latter automatically).
- Which city/municipality's Barangay Clearance and Mayor's Permit rules to use if those guides are completed.
- Whether to re-verify every guide before demo day and update each `lastVerified` date (strongly recommended; see doc 05).
