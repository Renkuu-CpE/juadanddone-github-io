# This module draws the DETAILS page of one document (flowchart page 6).
#
# Flowchart steps and the functions that do them:
#   6-A  read the document id from the website address        -> show_details_page()
#   6-B  "Document found?" No -> not-found + Browse all        -> layout.show_not_found()
#   6-C  show key info, links, requirements, what to bring, steps
#   6-D  "Has checklist items?" No -> "Check the official website"
#        Yes -> "Start preparing" / "Continue preparing"       -> make_preparing_box()

from src import data_functions
from src import checklist_functions
from src import html_parts
from src import layout


def make_preparing_box(context, document, status):
    """Flowchart 6-D: decide what to show in the 'Ready ka na ba?' box."""
    # Decision: does this document have checklist items?
    if not status["has_checklist"]:
        return (html_parts.make_callout("warn", "Walang checklist para dito.",
                                        "Our dataset has no physical items for this document. Check the official website for the current list.", "!")
                + html_parts.make_links_box(document))

    done, total = checklist_functions.get_done_and_total(document, layout.get_saved_keys(context, document["id"]))
    # Nested decision: has the user started the checklist already?
    if done > 0:
        button_text = "Continue preparing →"
        progress_html = html_parts.make_progress_bar(done, total)
    else:
        button_text = "Start preparing →"
        progress_html = '<p class="jad-muted" style="margin:0">Hindi mo pa nasisimulan ang checklist na ito.</p>'

    warning = ""
    if not status["complete"]:
        warning = html_parts.make_callout("danger", "Check the official website.",
                                          "This guide is incomplete, so the checklist can help you prepare but will not say “Ready ka na!”.", "!")
    checklist_url = html_parts.make_page_url("checklist", context["profile"], {"id": document["id"]})
    return progress_html + html_parts.make_link(checklist_url, button_text, "jad-btn yellow block", False) + warning


def show_details_page(context):
    """Draw the Details page."""
    profile = context["profile"]
    document_id = layout.read_url_value("id")

    # Decision (flowchart 6-B): was the document found?
    if document_id not in context["documents_by_id"]:
        layout.show_not_found(context, "document")
        return
    document = context["documents_by_id"][document_id]
    status = data_functions.get_record_status(document)

    # The labels under the title.
    pills = f'<span class="jad-pill cat">{html_parts.escape_html(document.get("category") or "Other")}</span>' + html_parts.make_mode_pills(document)
    if not status["complete"]:
        pills = pills + '<span class="jad-pill warn">Kulang ang datos · i-verify</span>'

    home_link = html_parts.make_link(html_parts.make_page_url("home", profile, {}), "Home", "", False)
    documents_link = html_parts.make_link(html_parts.make_page_url("documents", profile, {}), "Mga Dokumento", "", False)
    layout.show_html(html_parts.join_lines(f"""<div class="jad-detail-head">
<div class="jad-crumbs">{home_link} / {documents_link} / {html_parts.escape_html(data_functions.get_short_name(document))}</div>
<span class="jad-overline">{html_parts.escape_html(document.get('agency') or 'Agency not listed')}</span>
<h1>{html_parts.escape_html(document['name'])}</h1>
<p>{html_parts.escape_html(document.get('description') or '')}</p>
<div class="jad-pills">{pills}</div></div>"""))

    # Flowchart 6-C: all the information, in two columns.
    layout.show_html(html_parts.join_lines(f"""<div class="jad-detail-grid">
<div class="jad-col">
{html_parts.make_status_warning(status)}
<section class="jad-panel"><h2 class="jad-h3">Ano ang dadalhin (What to bring)</h2>
<p class="jad-muted" style="margin:0 0 12px">Physical items to put in your folder, with their exact type: Original, Photocopy, Printed or Digital.</p>{html_parts.make_bring_list(document)}</section>
<section class="jad-panel"><h2 class="jad-h3">General requirements</h2>{html_parts.make_requirements_list(document)}</section>
<section class="jad-panel"><h2 class="jad-h3">Mga hakbang (Steps)</h2>{html_parts.make_steps_list(document)}</section>
</div>
<aside class="jad-col">
<section class="jad-panel" style="display:flex;flex-direction:column;gap:12px"><h2 class="jad-h3" style="margin:0">Ready ka na ba?</h2>{make_preparing_box(context, document, status)}</section>
<section class="jad-panel"><h2 class="jad-h3">Key info</h2>{html_parts.make_facts_box(document)}</section>
<section class="jad-panel"><h2 class="jad-h3">Official links</h2>{html_parts.make_links_box(document)}
<p class="jad-muted" style="margin:10px 0 0;font-size:13px">Links come from our dataset and were not re-checked by this app.</p></section>
</aside></div>"""))
