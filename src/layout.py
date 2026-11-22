# This module contains the Streamlit parts that EVERY page uses:
#   - reading and changing the website address (which page is open)
#   - the header, the profile box and the footer
#   - the "not found" message
#
# How page switching works (replaces the old sidebar menu):
#   The website address holds the current page, for example
#       http://localhost:8501/?page=details&id=dfa-passport
#   app.py reads ?page=... and calls the matching page module (flowchart 1-A).
#   Links in the header and on the cards simply change this address.
#   Buttons change it inside a CALLBACK function (a function that Streamlit runs
#   when the button is clicked, before the page is drawn again).

import streamlit as st

from src import settings
from src import validation
from src import html_parts
from src import data_functions
from src import checklist_functions


# ======================================================================== website address (URL)
def read_url_value(name):
    """Return one value from the website address, e.g. read_url_value("page") -> "details"."""
    value = st.query_params.get(name, "")
    if value is None:
        return ""
    return str(value).strip()


def get_current_page():
    """Return the page to show. An unknown page name opens Home (input validation)."""
    page = read_url_value("page").lower()
    if validation.is_valid_page(page):
        return page
    return "home"


def get_current_profile():
    """Return the active profile name from the address (cleaned, "Guest" if empty)."""
    return validation.clean_profile_name(read_url_value("profile"))


def go_to_page(page, profile, extra_values):
    """Change the website address to open another page.

    This function is only called inside button callbacks.
    extra_values is a dictionary, e.g. {"id": "dfa-passport", "q": "nbi"}.
    """
    st.query_params.clear()
    st.query_params["page"] = page
    for name in extra_values:
        value = extra_values[name]
        if value != "" and value is not None and value is not False:
            st.query_params[name] = str(value)
    if profile != settings.DEFAULT_PROFILE:
        st.query_params["profile"] = profile


def show_html(markup):
    """Display a piece of HTML on the page (output)."""
    st.markdown(markup, unsafe_allow_html=True)


def get_active_menu(page):
    """Return which menu item to underline ('saved' for the Checklist ko view)."""
    if page == "documents" and read_url_value("view") == "saved":
        return "saved"
    return page


# ======================================================================== profile box
def apply_profile_name():
    """Callback of the 'Gamitin ang pangalang ito' button.

    Input validation (Lecture 7): the name is checked first. If it is invalid,
    an error message is saved and the address is NOT changed, so the user
    must correct the name and press the button again.
    """
    typed_name = st.session_state.get("profile_input", "")
    error_message = validation.get_profile_error(typed_name)
    if error_message != "":
        st.session_state["profile_error"] = error_message
        return
    st.session_state["profile_error"] = ""
    new_profile = validation.clean_text(typed_name)

    # Keep the current page and filters, change only the profile.
    current_values = {}
    for name in st.query_params:
        if name != "profile":
            current_values[name] = read_url_value(name)
    st.query_params.clear()
    for name in current_values:
        st.query_params[name] = current_values[name]
    if new_profile != settings.DEFAULT_PROFILE:
        st.query_params["profile"] = new_profile


def show_profile_box(context):
    """Show the active profile and a small box to change it."""
    note_column, button_column = st.columns([3, 1.25], vertical_alignment="center")
    with note_column:
        if context["database_ok"]:
            storage_text = "naka-save sa computer na ito (SQLite)"
        else:
            storage_text = "HINDI naka-save (session lang)"
        show_html(f'<div class="jad-profile-note">Profile: <strong>{html_parts.escape_html(context["profile"])}</strong> · '
                  f'progress {storage_text}. Profile names are labels, not secure accounts.</div>')
    with button_column:
        # Put the current profile in the text box the first time only.
        if "profile_input" not in st.session_state:
            st.session_state["profile_input"] = context["profile"]
        with st.popover("Palitan ang profile"):
            st.text_input("Profile name (no ID numbers, no full name needed)", key="profile_input", max_chars=settings.PROFILE_MAX_LENGTH)
            st.button("Gamitin ang pangalang ito", key="profile_apply", on_click=apply_profile_name, type="primary")
            st.caption("Ticks are saved per profile name on this computer only. Anyone who types the same name here sees the same checklist.")

    # Show the validation error (if any) outside the box so it is easy to see.
    if st.session_state.get("profile_error", "") != "":
        show_html(html_parts.make_callout("warn", "Hindi tinanggap ang profile name.", html_parts.escape_html(st.session_state["profile_error"]), "!"))


# ======================================================================== header and footer
def show_header(context):
    """Flowchart 1-A: show the header, the profile box and any database warning."""
    show_html(html_parts.make_header(get_active_menu(context["page"]), context["profile"]))
    show_profile_box(context)
    if not context["database_ok"]:
        show_html(html_parts.make_callout(
            "warn", "Hindi ma-save ang progress sa computer na ito.",
            "Ticks will only last while this tab is open. Move the project to a writable folder (e.g. Documents).", "!"))


def show_footer(context):
    """Show the footer and the phone tab bar."""
    show_html(html_parts.make_footer(context["profile"], context["latest_verified"]))
    show_html(html_parts.make_tab_bar(get_active_menu(context["page"]), context["profile"]))


def show_not_found(context, what):
    """Flowchart 6-B / 7-B: the document id in the address does not exist."""
    shown_id = read_url_value("id")
    if shown_id == "":
        shown_id = "(none)"
    browse_button = html_parts.make_link(html_parts.make_page_url("documents", context["profile"], {}),
                                         "Browse all documents →", "jad-btn yellow", False)
    show_html(html_parts.make_state_box("Hindi namin mahanap",
                                        "We could not find that " + what + ". The link may be old or mistyped.",
                                        "", "id = " + shown_id, browse_button))


def make_row_container(key):
    """Return a container with a CSS name (used to color each checklist row).

    st.container(key=...) gives the row the CSS class "st-key-<key>".
    Very old Streamlit versions do not accept "key" and raise a TypeError,
    so we catch the error and use a plain container instead (defensive programming).
    """
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


# ======================================================================== saved progress helpers
def get_saved_keys(context, document_id):
    """Return the set of ticked item keys of one document for the active profile."""
    if document_id in context["saved_progress"]:
        return context["saved_progress"][document_id]["keys"]
    return set()


def get_started_documents(context):
    """Return the documents that have at least one ticked item (flowchart 2-B: saved progress?)."""
    started = []
    for document in context["documents"]:
        done, total = checklist_functions.get_done_and_total(document, get_saved_keys(context, document["id"]))
        if done > 0:
            started.append(document)
    return started


def find_most_recent_document(context, started_documents):
    """Return the started document that was changed last (or None if the list is empty)."""
    most_recent = None
    latest_time = ""
    for document in started_documents:
        updated = context["saved_progress"][document["id"]]["updated"]
        if most_recent is None or updated > latest_time:
            most_recent = document
            latest_time = updated
    return most_recent


def make_cards_for(context, documents):
    """Return the HTML grid of document cards for a list of documents."""
    cards = []
    card_number = 0
    for document in documents:
        done, total = checklist_functions.get_done_and_total(document, get_saved_keys(context, document["id"]))
        status = data_functions.get_record_status(document)
        cards.append(html_parts.make_document_card(document, context["profile"], card_number, status, done, total))
        card_number = card_number + 1
    return html_parts.make_card_grid(cards)


def make_page_heading(context, title, lead):
    """Return the breadcrumb, big title and short description at the top of a page."""
    home_link = html_parts.make_link(html_parts.make_page_url("home", context["profile"], {}), "Home", "", False)
    return html_parts.join_lines(f"""<div class="jad-page-head"><div class="jad-crumbs">{home_link} / {html_parts.escape_html(title)}</div>
<h1 class="jad-h1" style="font-size:clamp(34px,5vw,54px)">{title}</h1><p>{html_parts.escape_html(lead)}</p></div>""")
