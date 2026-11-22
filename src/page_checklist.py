# This module draws the CHECKLIST page "Ready ka na ba?" (flowchart page 7).
#
# Flowchart steps and the functions that do them:
#   7-A  read the document id; "Document found?"          -> show_checklist_page()
#   7-B  load saved ticks from this computer               -> read_ticks()
#   7-C  display the checklist and ONE progress bar        -> show_checklist_rows()
#        user ticks/unticks -> save -> update progress    -> save_tick_callback()
#   7-D  "Reset this list" -> "Confirm reset?" -> clear     -> reset_callback()
#   7-E  "Ready ka na ba?" pressed:
#            all items ticked?  Yes -> "Ready ka na!" + print     -> show_result()
#            any item ticked?   No  -> "Simulan natin"
#                               Yes -> "May kulang ka pa!" + highlight missing items

import streamlit as st

from src import settings
from src import data_functions
from src import checklist_functions
from src import database_functions
from src import html_parts
from src import layout


# ======================================================================== callbacks
# A callback is a function that Streamlit runs when a checkbox or button is clicked.
# It runs BEFORE the page is drawn again, so it can safely change saved values.

def save_tick_callback(profile, document_id, item_key, item_label, widget_key, database_ok):
    """Flowchart 7-C: save one tick to the SQLite database right away."""
    is_ticked = st.session_state.get(widget_key, False)
    if database_ok:
        was_saved = database_functions.save_tick(settings.DATABASE_FILE, profile, document_id, item_key, item_label, is_ticked)
        if not was_saved:
            st.session_state["save_error"] = "The tick could not be written to the database file."


def set_flag(flag_name, value):
    """Turn a True/False flag on or off (used by the 'Ready ka na ba?' and reset buttons)."""
    st.session_state[flag_name] = value


def reset_callback(profile, document_id, widget_keys, database_ok):
    """Flowchart 7-D: the user confirmed the reset, so clear every tick of this list."""
    if database_ok:
        deleted_rows = database_functions.reset_checklist(settings.DATABASE_FILE, profile, document_id)
        if deleted_rows == -1:
            st.session_state["save_error"] = "The checklist could not be reset in the database file."
    # Untick every checkbox on the screen too.
    for widget_key in widget_keys:
        st.session_state[widget_key] = False
    st.session_state["confirm_reset_" + document_id] = False
    st.session_state["show_result_" + document_id] = False


# ======================================================================== reading ticks
def make_widget_key(profile, document_id, item):
    """Return a unique name for one checkbox, e.g. 'tick::Guest::dfa-passport::3f2a...'."""
    return "tick::" + profile + "::" + document_id + "::" + item["key"]


def read_ticks(context, document_id, items):
    """Flowchart 7-B: return the set of ticked item keys.

    Normally the ticks come from the database, and they are copied into the
    checkboxes BEFORE the checkboxes are drawn. If the database cannot be used,
    the ticks come from the checkboxes themselves (they last only for this tab).
    """
    profile = context["profile"]
    saved_keys = None
    if context["database_ok"]:
        saved_keys = database_functions.read_checked_keys(settings.DATABASE_FILE, profile, document_id)

    checked_keys = set()
    for item in items:
        widget_key = make_widget_key(profile, document_id, item)
        if saved_keys is not None:
            # Database -> checkbox
            st.session_state[widget_key] = item["key"] in saved_keys
        elif widget_key not in st.session_state:
            st.session_state[widget_key] = False
        if st.session_state[widget_key]:
            checked_keys.add(item["key"])
    return checked_keys


# ======================================================================== drawing
def show_checklist_rows(context, document, items, missing_keys):
    """Flowchart 7-C: draw one checkbox row for every item (a nested loop over two groups)."""
    profile = context["profile"]
    document_id = document["id"]

    # Split the items into two lists: needed by everyone, and only for some applicants.
    everyone_items = []
    some_items = []
    for item in items:
        if item["condition"] == "":
            everyone_items.append(item)
        else:
            some_items.append(item)

    groups = [
        ["Ano ang dadalhin", "Lahat ng ito ay kailangan ng bawat aplikante, ayon sa aming datos.", everyone_items],
        ["Kung applicable sa'yo", "Para lang sa ilang aplikante. Tsek-an kung kailangan mo; saka lang ito bibilangin.", some_items],
    ]
    row_number = 0
    for group in groups:
        group_title = group[0]
        group_hint = group[1]
        group_items = group[2]
        if len(group_items) == 0:
            continue
        layout.show_html(f'<div class="jad-q">{html_parts.escape_html(group_title)}</div>'
                         f'<div class="jad-muted" style="margin-bottom:6px">{html_parts.escape_html(group_hint)}</div>')
        for item in group_items:
            row_number = row_number + 1
            # Missing items get the "miss" name so the CSS colors them red.
            if item["key"] in missing_keys:
                row_name = "jadrow-miss-" + str(row_number)
            else:
                row_name = "jadrow-ok-" + str(row_number)
            widget_key = make_widget_key(profile, document_id, item)
            with layout.make_row_container(row_name):
                st.checkbox(item["text"], key=widget_key, on_change=save_tick_callback,
                            args=(profile, document_id, item["key"], item["text"], widget_key, context["database_ok"]))
                layout.show_html(f'<div class="jad-tags">{html_parts.make_type_tag(item["tag"])}{html_parts.make_condition_tag(item["condition"])}</div>')


def show_result(document, items, checked_keys, progress, state, status, profile):
    """Flowchart 7-E: show the result of "Ready ka na ba?"."""
    # Multiple alternative decision on the result state.
    if state == "empty":
        layout.show_html(html_parts.join_lines("""<div class="jad-result empty" role="status"><div class="top"><div>
<h2>Simulan natin</h2><p>Wala ka pang naka-tsek. Go through the list and tick what you already have at home.</p></div></div></div>"""))
        return

    if state == "missing":
        rows = ""
        for item in progress["missing"]:
            rows = rows + f"<li><strong>{html_parts.escape_html(item['text'])}</strong> {html_parts.make_type_tag(item['tag'])}</li>"
        layout.show_html(html_parts.join_lines(f"""<div class="jad-result missing" role="status"><div class="top"><div>
<h2>May kulang ka pa!</h2><p>{len(progress['missing'])} of {progress['total']} item(s) still not ticked. Ihanda muna ang mga ito bago umalis (naka-highlight sa pula sa itaas):</p></div></div>
<div class="bottom"><ul>{rows}</ul></div></div>"""))
        return

    if state == "ready":
        tips = ""
        for tip in checklist_functions.get_ready_tips(document):
            tips = tips + f"<li>{html_parts.escape_html(tip)}</li>"
        site_button = ""
        if len(document.get("officialLinks", [])) > 0:
            site_button = html_parts.make_link(document["officialLinks"][0], "Buksan ang official site ↗", "jad-btn yellow", True)
        layout.show_html(html_parts.join_lines(f"""<div class="jad-result ready" role="status"><div class="top">
<div class="jad-stamp"><div class="big">JUAN<br>AND DONE!</div><div class="small">{html_parts.escape_html(data_functions.get_short_name(document).upper())} · KUMPLETO</div></div>
<div><h2>Ready ka na!</h2><p>Kumpleto ang bitbit mo ayon sa aming listahan. Isang punta na lang, tapos na.</p></div></div>
<div class="bottom"><span class="jad-h3" style="margin:0;color:#0038A8">Bago umalis</span><ul>{tips}</ul>{site_button}
<span class="jad-muted" style="font-size:13px">Requirements can change. Confirm with the agency's official website or Citizen's Charter. Dataset last verified: {html_parts.escape_html(document.get('lastVerified') or 'not listed')}. This is not an approval of your application.</span></div></div>"""))
    else:
        # "ready-unverified": every item is ticked, but the guide itself is incomplete.
        reasons = ""
        for reason in status["reasons"]:
            reasons = reasons + f"<li>{html_parts.escape_html(reason)}</li>"
        note = ""
        if status["note"] != "":
            note = f"<span>{html_parts.escape_html(status['note'])}</span>"
        layout.show_html(html_parts.join_lines(f"""<div class="jad-result unverified" role="status"><div class="top"><div>
<h2>Naka-tsek lahat — pero i-verify muna</h2><p>You ticked every item we list, but this guide is incomplete, so we cannot say “Ready ka na!”. Check with the office before you go.</p></div></div>
<div class="bottom"><ul>{reasons}</ul>{note}</div></div>"""))

    # Print / export (only reached when every item is ticked).
    layout.show_html('<div class="jad-q">I-print / I-export ang checklist</div><div class="jad-muted">Download a clean printable copy, then open it and press Ctrl+P. '
                     'You can also press Ctrl+P on this page.</div>')
    file_suffix = ""
    if state != "ready":
        file_suffix = "-REFERENCE-ONLY"
    file_start = "juan-and-done-" + document["id"] + "-checklist" + file_suffix
    html_column, text_column = st.columns(2)
    with html_column:
        st.download_button("Printable checklist (.html)",
                           data=checklist_functions.make_export_html(document, items, checked_keys, state, profile, status),
                           file_name=file_start + ".html", mime="text/html", key="download_html_" + document["id"])
    with text_column:
        st.download_button("Checklist summary (.txt)",
                           data=checklist_functions.make_export_text(document, items, checked_keys, state, profile, status),
                           file_name=file_start + ".txt", mime="text/plain", key="download_txt_" + document["id"])


def show_checklist_page(context):
    """Draw the Checklist page."""
    profile = context["profile"]
    document_id = layout.read_url_value("id")

    # Decision (flowchart 7-A): was the document found?
    if document_id not in context["documents_by_id"]:
        layout.show_not_found(context, "checklist")
        return
    document = context["documents_by_id"][document_id]
    status = data_functions.get_record_status(document)
    items = checklist_functions.build_checklist_items(document)
    back_link = html_parts.make_link(html_parts.make_page_url("details", profile, {"id": document_id}), "← Bumalik sa detalye", "", False)

    # Decision: a document without items cannot have a checklist.
    if len(items) == 0:
        layout.show_html(html_parts.make_state_box("Walang checklist",
                                                   "Our dataset has no physical items for this document. Check the official website for the current list.",
                                                   "", "", back_link))
        layout.show_html(html_parts.make_links_box(document))
        return

    # PROCESS: read the ticks, count them and decide the result (flowchart 7-B to 7-E).
    checked_keys = read_ticks(context, document_id, items)
    progress = checklist_functions.count_progress(items, checked_keys)
    state = checklist_functions.get_readiness_state(items, progress, status["complete"])
    show_result_flag = "show_result_" + document_id
    confirm_flag = "confirm_reset_" + document_id

    # OUTPUT: the header with ONE progress bar.
    optional_note = ""
    if progress["optional_open"] > 0:
        optional_note = (f'<span class="jad-muted">+{progress["optional_open"]} item(s) na para lang sa ilan — '
                         'hindi bilang hangga’t hindi mo tsine-tsek.</span>')
    layout.show_html(html_parts.join_lines(f"""<div class="jad-check-head">
<div class="jad-crumbs">{back_link}</div>
<span class="jad-overline">{html_parts.escape_html(document.get('agency') or '')}</span>
<h1>{html_parts.escape_html(document['name'])}</h1>
{html_parts.make_progress_bar(progress['done'], progress['total'])}{optional_note}</div>"""))
    layout.show_html(html_parts.make_status_warning(status))
    if st.session_state.get("save_error", "") != "":
        layout.show_html(html_parts.make_callout("warn", "Hindi na-save ang huling tsek.", html_parts.escape_html(st.session_state["save_error"]), "!"))
        st.session_state["save_error"] = ""

    # Missing rows are only highlighted after "Ready ka na ba?" was pressed.
    missing_keys = []
    if st.session_state.get(show_result_flag, False):
        for item in progress["missing"]:
            missing_keys.append(item["key"])
    show_checklist_rows(context, document, items, missing_keys)

    # The three buttons under the list.
    widget_keys = []
    for item in items:
        widget_keys.append(make_widget_key(profile, document_id, item))
    layout.show_html('<div class="jad-space"></div>')
    check_column, reset_column, details_column = st.columns([1.3, 1, 1])
    with check_column:
        st.button("Ready ka na ba?", key="check_button_" + document_id, type="primary", on_click=set_flag, args=(show_result_flag, True))
    with reset_column:
        st.button("Reset this list", key="reset_button_" + document_id, on_click=set_flag, args=(confirm_flag, True))
    with details_column:
        layout.show_html(html_parts.make_link(html_parts.make_page_url("details", profile, {"id": document_id}),
                                              "Tingnan ang detalye", "jad-btn block jad-no-print", False))

    # Flowchart 7-D: "Confirm reset?" — the ticks are only removed after a second click.
    if st.session_state.get(confirm_flag, False):
        layout.show_html(html_parts.make_callout(
            "danger", "Confirm reset?",
            f"All ticks for <strong>{html_parts.escape_html(document['name'])}</strong> under profile "
            f"<strong>{html_parts.escape_html(profile)}</strong> will be removed. Hindi na ito maibabalik.", "!"))
        yes_column, no_column, empty_column = st.columns([1, 1, 1])
        with yes_column:
            st.button("Oo, i-reset", key="reset_yes_" + document_id, type="primary", on_click=reset_callback,
                      args=(profile, document_id, widget_keys, context["database_ok"]))
        with no_column:
            st.button("Huwag na", key="reset_no_" + document_id, on_click=set_flag, args=(confirm_flag, False))

    # Flowchart 7-E: the result appears after "Ready ka na ba?" was pressed.
    if st.session_state.get(show_result_flag, False):
        show_result(document, items, checked_keys, progress, state, status, profile)

    with st.expander("Iba pang requirements at hakbang (hindi kasama sa bilang)"):
        layout.show_html(f'<div>{html_parts.make_requirements_list(document)}</div>')
        layout.show_html(f'<div style="margin-top:14px">{html_parts.make_steps_list(document)}</div>')
