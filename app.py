# ============================================================================
# Juan and Done: a guide to Philippine government documents
# Project Juan and Done (CpE 203 Programming Logic and Design, final project)
#
# This is the MAIN MODULE (the entry point of the program).
# Run it from this folder with:
#     python -m streamlit run app.py
# then open http://localhost:8501 in your browser.
#
# Like the main() module in our lessons, main() here only CALLS other modules:
#     main()
#       ├── load_documents_once()          -> data_functions.load_documents()   (flowchart 1-A)
#       ├── show_loading_error()           (flowchart 1: "Is the data loaded? No")
#       ├── build_context()                -> database_functions, validation
#       ├── layout.show_header()
#       ├── show_selected_page()           -> page_home / page_documents / page_agencies /
#       │                                     page_about / page_details / page_checklist
#       └── layout.show_footer()
#
# Streamlit runs this whole file again from top to bottom every time the user
# clicks something. Saved values live in the website address, in
# st.session_state, and in the SQLite database file.
# ============================================================================

import os

import streamlit as st

# Import our own modules from the "src" folder.
from src import settings
from src import style
from src import data_functions
from src import database_functions
from src import html_parts
from src import layout
from src import page_home
from src import page_documents
from src import page_agencies
from src import page_about
from src import page_details
from src import page_checklist


# @st.cache_data is a DECORATOR (Module 6). It wraps the function so Streamlit keeps
# the result in memory and does not read the JSON file again on every click.
# The file's modification time is a parameter, so editing the file loads it again.
@st.cache_data(show_spinner=False)
def load_documents_once(file_path, modified_time):
    """Load documents.json (the result is remembered by Streamlit)."""
    return data_functions.load_documents(file_path)


def make_css_once():
    """Build the CSS once and remember it."""
    return style.make_page_css()


def get_file_time(file_path):
    """Return the time the file was last changed, or -1 if the file is missing."""
    if os.path.isfile(file_path):
        return os.path.getmtime(file_path)
    return -1


def retry_loading():
    """Callback of the Retry button: forget the remembered result so the file is read again."""
    load_documents_once.clear()


def show_loading_error(load_result):
    """Flowchart 1: "Is the data loaded?" No -> show an error message and a Retry button."""
    layout.show_html(html_parts.make_header("", settings.DEFAULT_PROFILE))
    layout.show_html(html_parts.make_state_box(
        "Hindi ma-load ang datos",
        load_result["error"] + " Juan and Done needs data/documents.json next to app.py. "
        "Restore the file from the project package (do not replace it with the old, truncated raw database file), then press Retry.",
        "error", load_result["detail"], ""))
    left_space, middle_column, right_space = st.columns([1, 1, 1])
    with middle_column:
        st.button("Retry / Subukan ulit", type="primary", on_click=retry_loading, key="retry_button")
    layout.show_html(html_parts.make_callout(
        "info", "Hindi pa rin gumagana?",
        "You can still check the agencies' official websites directly. See docs/04_WINDOWS_SETUP_AND_TROUBLESHOOTING.md.", "i"))


def build_context(documents):
    """Collect everything the pages need into ONE dictionary called "context".

    The context is passed to every page function as an argument, so we do not
    need global variables (Lecture 3: avoid global variables).
    """
    profile = layout.get_current_profile()
    database_ok = database_functions.create_tables(settings.DATABASE_FILE)

    saved_progress = {}
    if database_ok:
        result = database_functions.read_saved_progress(settings.DATABASE_FILE, profile)
        if result is None:
            database_ok = False
        else:
            saved_progress = result

    context = {
        "documents": documents,
        "documents_by_id": data_functions.make_documents_by_id(documents),
        "profile": profile,
        "page": layout.get_current_page(),
        "database_ok": database_ok,
        "saved_progress": saved_progress,
        "latest_verified": data_functions.get_latest_verified_date(documents),
    }
    return context


def show_selected_page(context):
    """Flowchart 1-A: "Documents ready -> which page?"

    A multiple alternative decision (like the Case structure in Lecture 4)
    calls the module of the page named in the website address.
    """
    page = context["page"]
    if page == "documents":
        page_documents.show_documents_page(context)
    elif page == "agencies":
        page_agencies.show_agencies_page(context)
    elif page == "about":
        page_about.show_about_page(context)
    elif page == "details":
        page_details.show_details_page(context)
    elif page == "checklist":
        page_checklist.show_checklist_page(context)
    else:
        # Default: any other value opens the Home page.
        page_home.show_home_page(context)


def main():
    """The main module: start the website and show the selected page."""
    # Page setup must be the first Streamlit command.
    page_icon = "📁"
    if os.path.isfile(settings.FAVICON_FILE):
        page_icon = settings.FAVICON_FILE
    st.set_page_config(page_title=settings.APP_NAME, page_icon=page_icon, layout="wide", initial_sidebar_state="collapsed")
    layout.show_html(make_css_once())

    # Flowchart 1-A: load the document data.
    load_result = load_documents_once(settings.DOCUMENTS_FILE, get_file_time(settings.DOCUMENTS_FILE))

    # Decision: is the data loaded?
    if not load_result["ok"]:
        show_loading_error(load_result)
        st.stop()

    # The data is ready: build the context, then show header, page and footer.
    context = build_context(load_result["documents"])
    layout.show_header(context)
    show_selected_page(context)
    layout.show_footer(context)


# Call the main module to start the program.
main()
