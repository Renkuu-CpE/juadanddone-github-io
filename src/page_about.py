# This module draws the ABOUT page (flowchart page 5): the purpose of the website,
# how it works, where the data comes from, the privacy notice, the disclaimer,
# the limitations, and a table that shows the status of every document guide.

from src import data_functions
from src import html_parts
from src import layout


def make_status_table(documents):
    """Return an HTML table with one row per document guide (a loop builds each row)."""
    rows = ""
    for document in documents:
        status = data_functions.get_record_status(document)
        if status["complete"]:
            status_text = "Complete in dataset"
        else:
            status_text = "Needs verification: " + "; ".join(status["reasons"])
        last_verified = document.get("lastVerified") or "—"
        rows = rows + (f"<tr><td>{html_parts.escape_html(document['name'])}</td><td>{len(document['whatToBring'])}</td>"
                       f"<td>{len(document['requirements'])}</td><td>{len(document['steps'])}</td><td>{len(document['officialLinks'])}</td>"
                       f"<td>{html_parts.escape_html(last_verified)}</td><td>{html_parts.escape_html(status_text)}</td></tr>")
    return ("<div class='jad-table-wrap'><table class='jad-table'><thead><tr><th>DOCUMENT</th><th>BRING</th><th>REQS</th><th>STEPS</th>"
            "<th>LINKS</th><th>LAST VERIFIED</th><th>STATUS</th></tr></thead><tbody>" + rows + "</tbody></table></div>")


def show_about_page(context):
    """Draw the About page."""
    home_link = html_parts.make_link(html_parts.make_page_url("home", context["profile"], {}), "Home", "", False)
    layout.show_html(html_parts.join_lines(f"""<div class="jad-page-head"><div class="jad-crumbs">{home_link} / Tungkol sa amin</div>
<h1 class="jad-h1" style="font-size:clamp(34px,5vw,54px)">Tungkol sa <span class="red">Juan and Done</span></h1>
<p>Juan and Done (a play on “one and done”) helps you arrive at a government office with everything you need, so you get it done on the first try.</p></div>
<div class="jad-info">
<div class="jad-panel"><span class="jad-h3">Bakit namin ginawa</span><p>Many applicants queue for hours only to be turned away for a missing photocopy,
an ID that is not accepted, or a form they did not know about. We put the requirements for common documents in one place, as a checklist you can tick at home.</p></div>
<div class="jad-panel"><span class="jad-h3">Paano gumagana</span><p>1. Pick a document. 2. Tick the physical items you already have (originals, photocopies, printouts).
3. Press “Ready ka na ba?” to see what is still missing, or print your complete list.</p></div>
<div class="jad-panel"><span class="jad-h3">Saan galing ang datos</span><p>Our team compiled each guide from agency websites and Citizen's Charters (the service guides
offices publish under RA 11032). The “Last verified” date on each guide is the date our team recorded; this app does not re-check government sites by itself.</p></div>
</div>
<div class="jad-prose">
<h2 class="jad-h2" style="font-size:30px">Privacy</h2>
<ul><li>There are no accounts. A <strong>profile name</strong> is only a label that keeps checklists apart on one computer; it is <strong>not</strong> a secure login.
Anyone who uses this computer and types the same name sees the same ticks.</li>
<li>Ticks are saved only in <code>data/juan_and_done_progress.db</code> (SQLite) inside the project folder. Nothing is sent to us or to any agency.</li>
<li>We never ask for ID numbers, birth dates, addresses, passwords, payments or document scans. Please do not type them as your profile name.</li>
<li>“Reset this list” removes the ticks for one document and profile. Deleting the .db file removes all saved progress.</li></ul>
<h2 class="jad-h2" style="font-size:30px">Hindi kami website ng gobyerno</h2>
<p>Juan and Done is an independent student project. We are not affiliated with, endorsed by, or connected to any Philippine government agency.
We do not process applications or collect fees. “Ready ka na!” only means you ticked every listed physical item; it is not an approval and does not guarantee that an office will accept your documents.</p>
<h2 class="jad-h2" style="font-size:30px">Limitations</h2>
<ul><li>We cover a selected set of common documents, mostly those that end with an in-person visit.</li>
<li>Some rules differ per office, branch, city or barangay. Guides marked “Kulang ang datos · i-verify” are incomplete and never show “Ready ka na!”.</li>
<li>Special cases (minors, foreign nationals, lost or corrected documents) may need more than what is listed. Items that apply only to some people are tagged and only count once you tick them.</li>
<li>Fees, processing times and links can change at any time. Always confirm on the official website before your visit.</li></ul>
<h2 class="jad-h2" style="font-size:30px">Status ng bawat guide</h2>
</div>"""))
    layout.show_html(make_status_table(context["documents"]))
