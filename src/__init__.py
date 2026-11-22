# This file tells Python that the "src" folder is a group of modules (a package).
# Because of this file, app.py can write:  from src import data_functions
#
# Modules inside this folder (see docs/07 for the hierarchy chart):
#   settings.py             global constants (file paths, colors, labels)
#   validation.py           input validation functions (Lecture 7)
#   data_functions.py       load and search the document data (documents.json)
#   checklist_functions.py  build the checklist and decide "Ready ka na ba?"
#   database_functions.py   save and read checklist ticks (SQLite)
#   html_parts.py           small pieces of HTML used by the pages
#   style.py                the CSS that gives the website its Pinoy look
#   layout.py               header, footer, profile box and page switching
#   page_home.py            Home page            (flowchart page 2)
#   page_documents.py       Documents page       (flowchart page 3)
#   page_agencies.py        Agencies page        (flowchart page 4)
#   page_about.py           About page           (flowchart page 5)
#   page_details.py         Details page         (flowchart page 6)
#   page_checklist.py       Checklist page       (flowchart page 7)
