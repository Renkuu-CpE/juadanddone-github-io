# This module draws the HOME page (flowchart page 2).
#
# Flowchart steps and the functions that do them:
#   2-A  show search bar, suggestions, popular documents, categories  -> show_home_page()
#   2-B  "Saved progress?" decision -> "Continue where you left off"   -> show_continue_card()
#   2-C  user presses Enter in the search bar -> Documents page        -> search_from_home()
#   2-D  user picks a suggestion -> Details page                       -> open_suggestion()

import streamlit as st

from src import settings
from src import validation
from src import data_functions
from src import checklist_functions
from src import html_parts
from src import layout


def search_from_home(profile):
    """Callback of the 'Hanapin' button (flowchart 2-C).

    Input validation: an empty or too long search shows an error message
    instead of opening the Documents page.
    """
    typed_text = st.session_state.get("home_search", "")
    error_message = validation.get_search_error(typed_text)
    if error_message != "":
        st.session_state["home_search_error"] = error_message
    else:
        st.session_state["home_search_error"] = ""
        layout.go_to_page("documents", profile, {"q": validation.clean_search_text(typed_text)})


def make_suggestion_label(document):
    """Return the text shown in the suggestion list, e.g. 'NBI Multi-Purpose Clearance  ·  National ...'."""
    return document["name"] + "  ·  " + document.get("agency", "")


def open_suggestion(profile, documents):
    """Callback of the suggestion box (flowchart 2-D): open the chosen document's Details page."""
    chosen_label = st.session_state.get("home_suggestion")
    # Search the list for the document whose label was chosen.
    for document in documents:
        if make_suggestion_label(document) == chosen_label:
            layout.go_to_page("details", profile, {"id": document["id"]})


def make_illustration():
    """Return the envelope, checklist paper, stamp and queue ticket drawing."""
    rows = ""
    for label in ["Appointment printout", "Valid ID (original)", "Photocopy ng ID", "Eksaktong bayad"]:
        rows = rows + f'<div class="row"><span class="jad-tick">{html_parts.TICK_SVG}</span>{label}</div>'
    return html_parts.join_lines(f"""<div><div class="jad-illus" aria-hidden="true">
<div class="jad-env"><div class="btn1"></div><div class="str"></div><span class="lbl">LONG BROWN ENVELOPE</span></div>
<div class="jad-paperlist"><span class="t">Bitbit ko</span>{rows}</div>
<div class="jad-stamp"><div class="big">KUMPLETO</div><div class="small">JUAN AND DONE · OK NA</div></div>
<div class="jad-ticket"><span class="k">NOW SERVING</span><span class="n">025</span><span class="w">Window 3 · Juan D.</span></div>
</div></div>""")


def show_hero(context):
    """Flowchart 2-A: the big title, the search bar, live suggestions and popular documents."""
    profile = context["profile"]
    left_column, right_column = st.columns([1.15, 1], gap="large")
    with left_column:
        layout.show_html(html_parts.join_lines("""<div class="jad-hero-copy">
<span class="jad-badge-dark" style="align-self:flex-start">PARA SA BAWAT JUAN AT JUANA</span>
<h1 class="jad-h1">Isang punta, <span class="red">tapos na.</span></h1>
<p class="jad-lead">Alamin ang eksaktong dadalhin bago ka pumila. Your requirements, checked one by one, so Juan only goes once.</p>
</div>"""))

        # INPUT: the search bar. A form sends the text when Enter or "Hanapin" is pressed.
        with st.form("home_search_form", border=True):
            text_column, button_column = st.columns([3.2, 1.2], vertical_alignment="bottom")
            with text_column:
                st.text_input("Anong papel ang aayusin mo?", key="home_search", placeholder="Anong papel? Hal. NBI Clearance",
                              label_visibility="collapsed")
            with button_column:
                st.form_submit_button("Hanapin", type="primary", on_click=search_from_home, args=(profile,))

        # OUTPUT: the validation error message, if the search was empty.
        if st.session_state.get("home_search_error", "") != "":
            layout.show_html(html_parts.make_callout("warn", "Walang hinahanap.", html_parts.escape_html(st.session_state["home_search_error"]), "!"))

        # Live suggestions: typing inside this box filters the list of documents.
        suggestion_labels = []
        for document in context["documents"]:
            suggestion_labels.append(make_suggestion_label(document))
        st.selectbox("Live suggestions", options=suggestion_labels, index=None,
                     placeholder="…o mag-type dito para sa live suggestions", key="home_suggestion",
                     on_change=open_suggestion, args=(profile, context["documents"]), label_visibility="collapsed")

        # Popular document chips
        chips = ""
        for document_id in settings.POPULAR_IDS:
            if document_id in context["documents_by_id"]:
                document = context["documents_by_id"][document_id]
                url = html_parts.make_page_url("details", profile, {"id": document_id})
                chips = chips + html_parts.make_link(url, html_parts.escape_html(data_functions.get_short_name(document)), "jad-chip", False)
        layout.show_html(f'<div class="jad-chips"><span class="label">Madalas hanapin:</span>{chips}</div>')
    with right_column:
        layout.show_html(make_illustration())


def show_continue_card(context):
    """Flowchart 2-B: show "Continue where you left off" only if there is saved progress."""
    started_documents = layout.get_started_documents(context)
    # Single alternative decision: if there is no saved progress, show nothing.
    if len(started_documents) == 0:
        return
    document = layout.find_most_recent_document(context, started_documents)
    done, total = checklist_functions.get_done_and_total(document, layout.get_saved_keys(context, document["id"]))
    more_text = ""
    if len(started_documents) > 1:
        more_text = " · " + str(len(started_documents) - 1) + " pang ibang checklist"
    profile = context["profile"]
    continue_button = html_parts.make_link(html_parts.make_page_url("checklist", profile, {"id": document["id"]}),
                                           "Ituloy ang checklist →", "jad-btn yellow", False)
    all_button = html_parts.make_link(html_parts.make_page_url("documents", profile, {"view": "saved"}),
                                      "Lahat ng checklist ko", "jad-btn", False)
    layout.show_html(html_parts.join_lines(f"""<div class="jad-continue">
<div class="txt"><span class="jad-overline">Ituloy kung saan ka huminto{html_parts.escape_html(more_text)}</span>
<span class="jad-h3" style="margin:0;color:#0038A8">{html_parts.escape_html(document['name'])}</span>{html_parts.make_progress_bar(done, total)}</div>
{continue_button}
{all_button}
</div>"""))


def show_how_it_works():
    """The blue 'Paano ba 'to?' section with the three steps."""
    layout.show_html(html_parts.join_lines("""<div class="jad-bleed-blue jad-band"><div class="jad-section-head">
<h2 class="jad-h2">Paano ba 'to?</h2><p class="sub">Tatlong hakbang lang. No guesswork, no second trip.</p></div>
<div class="jad-how-grid">
<div class="jad-how-card"><div class="hd"><span class="num">1</span><span class="ttl">Pili ka ng papel</span></div>
<p>Search or browse the documents we cover, from NBI Clearance to passport. Each guide shows fees, processing time, validity and where to go.</p></div>
<div class="jad-how-card"><div class="hd"><span class="num">2</span><span class="ttl">I-tsek ang bitbit</span></div>
<p>Tick the physical items you already have: originals, photocopies and printouts. Your ticks are saved on this computer.</p></div>
<div class="jad-how-card"><div class="hd"><span class="num">3</span><span class="ttl">Kumpleto? Gora!</span></div>
<p>Press "Ready ka na ba?". Kung may kulang pa, sasabihin namin kung ano mismo ang kulang.</p></div>
</div></div>"""))


def show_home_page(context):
    """Draw the whole Home page, section by section (sequence structure)."""
    profile = context["profile"]
    all_documents_link = html_parts.make_link(html_parts.make_page_url("documents", profile, {}), "Lahat ng dokumento →", "", False)

    show_hero(context)
    show_continue_card(context)
    show_how_it_works()

    # Categories (flowchart 2-A)
    layout.show_html(f'<div class="jad-section-head"><h2 class="jad-h2">Mga kategorya</h2>{all_documents_link}</div>')
    layout.show_html(html_parts.make_category_grid(data_functions.get_categories(context["documents"]), profile))

    # Common documents ("Saan ka papunta?")
    layout.show_html(f'<div class="jad-space"></div><div class="jad-section-head"><h2 class="jad-h2">Saan ka papunta?</h2>{all_documents_link}</div>')
    common_documents = []
    for document_id in settings.COMMON_IDS:
        if document_id in context["documents_by_id"]:
            common_documents.append(context["documents_by_id"][document_id])
    if len(common_documents) == 0:
        # If none of the chosen ids exist, show the first six documents (list slicing).
        common_documents = context["documents"][0:6]
    layout.show_html(layout.make_cards_for(context, common_documents))

    # "Bawal ang fixer" banner
    agencies_button = html_parts.make_link(html_parts.make_page_url("agencies", profile, {}), "Tingnan ang mga ahensya →", "jad-btn", False)
    layout.show_html(html_parts.join_lines(f"""<div class="jad-banner"><div style="flex:1 1 420px">
<h2 class="jad-h2">Bawal ang fixer.</h2>
<p>Official links lang mula sa aming datos, walang shortcut, walang dagdag-bayad. Links that are not .gov.ph addresses are clearly flagged.</p></div>
{agencies_button}</div>"""))

    # Website information panels
    number_of_documents = len(context["documents"])
    number_of_agencies = len(data_functions.group_by_agency(context["documents"]))
    number_incomplete = data_functions.count_incomplete(context["documents"])
    about_link = html_parts.make_link(html_parts.make_page_url("about", profile, {}), "Basahin pa →", "", False)
    layout.show_html(html_parts.join_lines(f"""<div class="jad-info">
<div class="jad-panel"><span class="jad-h3">Ano ang Juan and Done?</span>
<p>An independent student guide to {number_of_documents} common Philippine government documents from {number_of_agencies} agencies and offices. Hindi ito website ng gobyerno.</p></div>
<div class="jad-panel"><span class="jad-h3">Saan galing ang datos?</span>
<p>Compiled by our team from agency websites and Citizen's Charters. {number_incomplete} guide(s) are marked incomplete and never show "Ready ka na!".</p></div>
<div class="jad-panel"><span class="jad-h3">Privacy</span>
<p>No accounts, no ID numbers, no uploads. Your ticks stay in a small file on this computer. {about_link}</p></div>
</div>"""))
