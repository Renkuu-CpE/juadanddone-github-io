# This module draws the DOCUMENTS page (flowchart page 3).
#
# Flowchart steps and the functions that do them:
#   3-A  read q, category and view from the website address  -> read_filters()
#   3-B  search, filter by category or saved view             -> data_functions.search_documents()
#   3-C  "Any matches?" Yes -> show document cards            -> show_documents_page()
#   3-D  No -> "No match" message + "Show all documents"      -> show_documents_page(), show_all_documents()
#   3-E  user changes the search or filter (loop back to 3-A) -> filters_changed()

import streamlit as st

from src import validation
from src import data_functions
from src import html_parts
from src import layout

ALL_CATEGORIES_LABEL = "Lahat ng kategorya"


def make_category_label(category):
    """Return the text shown in the category box, e.g. 'Driving (2)'."""
    return category["label"] + " (" + str(category["count"]) + ")"


def find_slug_for_label(categories, chosen_label):
    """Return the category slug of the label chosen in the box ("" means all categories)."""
    for category in categories:
        if make_category_label(category) == chosen_label:
            return category["slug"]
    return ""


def find_label_for_slug(categories, slug):
    """Return the box label of a category slug (the opposite of find_slug_for_label)."""
    for category in categories:
        if category["slug"] == slug:
            return make_category_label(category)
    return ALL_CATEGORIES_LABEL


def read_filters(categories):
    """Flowchart 3-A: read the search text, category and saved view from the address.

    Returns three values. Invalid values are replaced with safe ones (input validation).
    """
    search_text = validation.clean_search_text(layout.read_url_value("q"))
    category_slug = layout.read_url_value("category")
    # Whitelist check: the category must be one of the real categories.
    valid_slugs = []
    for category in categories:
        valid_slugs.append(category["slug"])
    if category_slug not in valid_slugs:
        category_slug = ""
    saved_only = layout.read_url_value("view") == "saved"
    return search_text, category_slug, saved_only


def filters_changed(profile, categories):
    """Callback of the search box, category box and saved toggle (flowchart 3-E)."""
    search_text = validation.clean_search_text(st.session_state.get("documents_search", ""))
    category_slug = find_slug_for_label(categories, st.session_state.get("documents_category", ALL_CATEGORIES_LABEL))
    saved_only = st.session_state.get("documents_saved", False)
    view = ""
    if saved_only:
        view = "saved"
    # Remember these values so they are not copied again from the address.
    st.session_state["documents_synced"] = [search_text, category_slug, saved_only]
    layout.go_to_page("documents", profile, {"q": search_text, "category": category_slug, "view": view})


def show_all_documents(profile):
    """Callback of the 'Show all documents' button (flowchart 3-D): clear every filter."""
    st.session_state["documents_search"] = ""
    st.session_state["documents_category"] = ALL_CATEGORIES_LABEL
    st.session_state["documents_saved"] = False
    st.session_state["documents_synced"] = ["", "", False]
    layout.go_to_page("documents", profile, {})


def show_documents_page(context):
    """Draw the Documents page."""
    profile = context["profile"]
    categories = data_functions.get_categories(context["documents"])
    search_text, category_slug, saved_only = read_filters(categories)

    # Copy the values from the address into the boxes BEFORE the boxes are drawn.
    # (Changing a box's value after it is drawn would cause a Streamlit error.)
    if st.session_state.get("documents_synced") != [search_text, category_slug, saved_only]:
        st.session_state["documents_search"] = search_text
        st.session_state["documents_category"] = find_label_for_slug(categories, category_slug)
        st.session_state["documents_saved"] = saved_only
        st.session_state["documents_synced"] = [search_text, category_slug, saved_only]

    # Dual alternative decision: the title depends on the saved view.
    if saved_only:
        title = "Checklist ko"
        lead = "Mga dokumentong sinimulan mo na sa computer na ito. Pindutin para ituloy kung saan ka huminto."
    else:
        title = "Mga Dokumento"
        lead = "Hanapin ang papel na kailangan mo. Search by name, agency or keyword, then filter by category."
    layout.show_html(layout.make_page_heading(context, title, lead))

    # INPUT: search box, category box and saved-progress toggle.
    category_labels = [ALL_CATEGORIES_LABEL]
    for category in categories:
        category_labels.append(make_category_label(category))
    search_column, category_column, saved_column = st.columns([2.4, 1.6, 1.3], vertical_alignment="bottom")
    with search_column:
        st.text_input("Hanapin (keyword)", key="documents_search", placeholder="Hal. passport, NBI, LTO, barangay",
                      max_chars=80, on_change=filters_changed, args=(profile, categories))
    with category_column:
        st.selectbox("Kategorya", options=category_labels, key="documents_category", on_change=filters_changed, args=(profile, categories))
    with saved_column:
        st.toggle("May saved progress lang", key="documents_saved", on_change=filters_changed, args=(profile, categories))

    # PROCESS: search and filter (flowchart 3-B).
    only_ids = None
    if saved_only:
        only_ids = []
        for document in layout.get_started_documents(context):
            only_ids.append(document["id"])
    results = data_functions.search_documents(context["documents"], search_text, category_slug, only_ids)

    # OUTPUT: how many documents were found and with which filters.
    filter_text = ""
    if search_text != "":
        filter_text = filter_text + " matching “" + html_parts.escape_html(search_text) + "”"
    if category_slug != "":
        filter_text = filter_text + " in " + html_parts.escape_html(find_label_for_slug(categories, category_slug))
    if saved_only:
        filter_text = filter_text + " with saved progress"
    layout.show_html(f'<div class="jad-results-meta" aria-live="polite"><strong>{len(results)} dokumento</strong>{filter_text}</div>')

    # Decision (flowchart 3-C): any matches?
    if len(results) > 0:
        layout.show_html(layout.make_cards_for(context, results))
        return

    # No matches (flowchart 3-D).
    if saved_only and search_text == "" and category_slug == "":
        layout.show_html(html_parts.make_state_box("Wala pang sinimulan",
                                                   "You have not ticked any checklist item with this profile yet. Pick a document and press 'Start preparing'.",
                                                   "", "", ""))
    else:
        layout.show_html(html_parts.make_state_box("Walang nahanap",
                                                   "No match. Try another word (e.g. an acronym like DFA or LTO) or show every document.",
                                                   "", "", ""))
    left_space, middle_column, right_space = st.columns([1, 1, 1])
    with middle_column:
        st.button("Show all documents", key="documents_show_all", on_click=show_all_documents, args=(profile,), type="primary")
