# 06 · QA Test Plan

Use the profile **`JAD-QA`** (never a real name). Mark each line **Pass / Fail / Blocked** with the date, tester and Streamlit version (`python -c "import streamlit; print(streamlit.__version__)"`).

## Already verified in the build environment (Linux, Python 3.13, no Streamlit installed)

| Check | Result |
|---|---|
| All Python files compile | Pass |
| `documents.json` valid, schema OK, 16 unique ids | Pass |
| Incomplete-record guard (2 LGU guides cannot reach "Ready ka na!") | Pass |
| SQLite save / untick / separate profiles / reset in a temp file | Pass |
| No old-brand text outside the labelled changelog | Pass |
| 89 page-flow checks run against a **fake** Streamlit stub (every page, every record, search, filters, input-validation errors, three readiness states, reset confirm, export, persistence after simulated refresh, load-error Retry, read-only DB fallback) | Pass |
| Static HTML/CSS screenshots at 1280 px and 390 px in headless Chrome | Reviewed |

The stub test proves the Python logic and HTML, **not** real Streamlit rendering. Everything below must be run on your Windows machine.

## 1. Install and launch

- [ ] `python tools\check_project.py` → `Summary: 0 FAIL` (1 WARN about non-.gov.ph links is expected)
- [ ] `python -m streamlit run app.py` starts with **no `Email:` prompt** and prints a Local URL
- [ ] `http://localhost:8501` opens; no red traceback in browser or terminal
- [ ] Double-clicking `tools\launch_juan_and_done_windows.bat` does the same and opens the browser by itself

## 2. Startup error + Retry (flowchart page 1)

- [ ] Stop the server. Rename `data\documents.json` → `documents.bak`. Start again → "Hindi ma-load ang datos" + "was not found" + **Retry**
- [ ] Rename it back, press **Retry** → Home loads without restarting
- [ ] (Optional, on a copy) delete the last `]` in the JSON → message shows line/column; restore

## 3. Home (page 2)

- [ ] Hero, search box, suggestion box, 4 popular chips, 7 categories, 6 document cards, red banner, footer
- [ ] Type `nbi` + **Hanapin** → Documents shows NBI
- [ ] Type `pass` in the suggestion box → pick Passport → Details opens
- [ ] Before any ticks: no "Ituloy kung saan ka huminto" card. After ticking one item (section 6): card appears with the right document and progress

## 4. Documents (page 3)

- [ ] 16 documents with no filters; `?page=documents&q=lto` → 2; category Driving → 2
- [ ] Search `zzzz` → "Walang nahanap" → **Show all documents** → 16 again
- [ ] Toggle "May saved progress lang" with no ticks → "Wala pang sinimulan"; with ticks → only started guides
- [ ] Filters survive a browser refresh (F5) because they are in the URL

## 5. Agencies (page 4) and About (page 5)

- [ ] 14 agency cards; search `dfa` → 1; search `zzzz` → "Walang nahanap" → "Ipakita lahat"
- [ ] Official link opens in a **new tab**; PNP and Pag-IBIG links show "Not a .gov.ph address — double-check"
- [ ] LGU cards show "Walang iisang official website"
- [ ] About shows privacy (profile ≠ account, no IDs collected), disclaimer, limitations and a 16-row status table

## 6. Details + Checklist (pages 6–7)

- [ ] Passport details: key info, 1 link, requirements, What to bring with exact labels, steps with Online / In person badges, **Start preparing**
- [ ] `?page=details&id=wrong` → not-found + **Browse all documents**
- [ ] Mayor's Permit: red badge + reasons + note; "Check the official website" under the button
- [ ] NBI checklist (profile `JAD-QA`): header says `0 of 3 ready`; **one** progress bar only; 2 items under "Kung applicable sa'yo"
- [ ] Press **Ready ka na ba?** with nothing ticked → **Simulan natin**
- [ ] Tick 1 → bar moves immediately → result **May kulang ka pa!** lists 2 items; those rows turn red-dashed
- [ ] Tick all 3 → **Ready ka na!** with stamp, tips, official-site button, two download buttons
- [ ] Download the `.html`, open it, press Ctrl+P → clean one-page checklist; the `.txt` opens in Notepad
- [ ] Tick a "Kung applicable" item → total becomes 4
- [ ] Press **F5** → ticks stay. Stop the server (Ctrl+C), start again → ticks stay
- [ ] Details now says **Continue preparing**
- [ ] **Reset this list** → "Confirm reset?" → **Huwag na** keeps ticks → **Reset** again → **Oo, i-reset** → `0 of 3`
- [ ] Mayor's Permit: tick everything → result is "Naka-tsek lahat — pero i-verify muna", **never** "Ready ka na!"; downloads end in `-REFERENCE-ONLY`

## 7. Profiles and privacy

- [ ] "Palitan ang profile" → type `JAD-QA2` → URL gets `profile=JAD-QA2`, progress empty; switch back → old ticks return
- [ ] Type `<b>Juan</b>` → **rejected** with "Hindi tinanggap ang profile name"; an empty name → "Please type a profile name first"
- [ ] Press **Hanapin** on Home with an empty search → "Walang hinahanap" message, page stays on Home

## 8. Phone widths and accessibility

- [ ] Browser DevTools (F12 → device toolbar) at **390 px** and **768 px**: one column, bottom tab bar (Home / Dokumento / Checklist ko / Ahensya), no sideways scrolling, checkboxes easy to tap
- [ ] Tab key reaches every link/button with a visible focus outline
- [ ] Ctrl+P on a checklist page hides header, footer, tab bar and buttons

## 9. Sign-off

- [ ] All sections Pass, or failures logged with a screenshot + terminal output
- [ ] Data re-verification (doc 05) done or the remaining risk explained in the presentation
