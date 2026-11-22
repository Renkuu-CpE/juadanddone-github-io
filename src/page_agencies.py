# This module draws the AGENCIES page (flowchart page 4).
#
# Flowchart steps and the functions that do them:
#   4-A  group documents by issuing agency            -> data_functions.group_by_agency()
#   4-B  show the agency search bar and agency cards  -> show_agencies_page()
#   4-C  "Any agency matches?" No -> "Walang nahanap" -> show_agencies_page()
#   4-D  official website button -> opens a new tab   -> html_parts.make_agency_card()
#   4-E  document guide link -> Details page          -> html_parts.make_agency_card()

import streamlit as st

from src import validation
from src import data_functions
from src import html_parts
from src import layout


def clear_agency_search():
    """Callback of the 'Ipakita lahat ng ahensya' button: empty the search box."""
    st.session_state["agency_search"] = ""


def show_agencies_page(context):
    """Draw the Agencies page."""
    profile = context["profile"]
    agency_list = data_functions.group_by_agency(context["documents"])

    layout.show_html(layout.make_page_heading(context, "Mga Ahensya",
                                              "Every agency and office in our dataset, with the official links we have and direct links to each document guide."))

    # INPUT: the agency search bar.
    typed_text = st.text_input("Hanapin ang ahensya", key="agency_search", placeholder="Hal. DFA, LTO, PhilHealth, barangay", max_chars=80)
    search_text = validation.clean_search_text(typed_text)

    # PROCESS: keep only the agencies that match.
    found_agencies = data_functions.search_agencies(agency_list, search_text)

    # OUTPUT: the number of agencies found.
    matching_text = ""
    if search_text != "":
        matching_text = " matching “" + html_parts.escape_html(search_text) + "”"
    layout.show_html(f'<div class="jad-results-meta" aria-live="polite"><strong>{len(found_agencies)} ahensya</strong>{matching_text}</div>')

    # Decision (flowchart 4-C): any agency matches?
    if len(found_agencies) > 0:
        cards = ""
        for agency in found_agencies:
            cards = cards + html_parts.make_agency_card(agency, profile)
        layout.show_html(f'<div class="jad-grid">{cards}</div>')
    else:
        layout.show_html(html_parts.make_state_box("Walang nahanap", "No agency matches that search. Try an acronym like “DFA” or “LTO”.", "", "", ""))
        left_space, middle_column, right_space = st.columns([1, 1, 1])
        with middle_column:
            st.button("Ipakita lahat ng ahensya", key="agency_show_all", on_click=clear_agency_search)
