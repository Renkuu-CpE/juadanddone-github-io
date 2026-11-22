# This module builds small pieces of HTML text (cards, buttons, lists, header, footer).
# The page modules call these functions and show the result on the screen.
# Each function RECEIVES data through its parameters and RETURNS a string of HTML.
#
# Two important ideas used here:
#   1. escape_html() is called on every value that comes from documents.json or from
#      the user, so special characters like < > & are shown as text and never run as code.
#   2. Formatted strings (f-strings): f"<b>{name}</b>" puts the value of the variable
#      "name" inside the text. It is the Python way to "Display" text and variables together.

from urllib.parse import quote

from src import settings
from src import validation
from src import data_functions

# The special characters that must be replaced to show text safely inside HTML.
# "&" must be replaced first, so the other replacements are not changed again.
HTML_REPLACEMENTS = [
    ["&", "&amp;"],
    ["<", "&lt;"],
    [">", "&gt;"],
    ['"', "&quot;"],
    ["'", "&#x27;"],
    ["$", "&#36;"],  # "$" would make Streamlit show math formulas
]


def escape_html(value):
    """Return the value as text that is safe to place inside HTML."""
    if value is None:
        value = ""
    text = str(value)
    # For loop: apply every replacement in the list, one by one.
    for pair in HTML_REPLACEMENTS:
        text = text.replace(pair[0], pair[1])
    return text


def join_lines(markup):
    """Join a multi-line HTML text into one line.

    Streamlit reads HTML as Markdown, and a blank or indented line could break it,
    so we remove the line breaks and the spaces at the start of each line.
    """
    clean_lines = []
    for line in markup.splitlines():
        if line.strip() != "":
            clean_lines.append(line.strip())
    return " ".join(clean_lines)


def make_page_url(page, profile, extra_values):
    """Build a website address such as  ?page=details&id=dfa-passport

    page          the page name, e.g. "details"
    profile       the active profile ("Guest" is not added to the address)
    extra_values  a dictionary of other values, e.g. {"id": "dfa-passport"}
    """
    url = "?page=" + quote(page)
    for name in extra_values:
        value = extra_values[name]
        # Skip empty values so the address stays short.
        if value != "" and value is not None and value is not False:
            url = url + "&" + name + "=" + quote(str(value))
    if profile != "" and profile != settings.DEFAULT_PROFILE:
        url = url + "&profile=" + quote(profile)
    return url


def make_link(url, inner_html, css_class, open_in_new_tab):
    """Return an <a> link. Website links open in a new tab; page links stay in this tab."""
    if open_in_new_tab:
        target = ' target="_blank" rel="noopener noreferrer"'
    else:
        target = ' target="_self"'
    class_text = ""
    if css_class != "":
        class_text = f' class="{css_class}"'
    return f'<a href="{escape_html(url)}"{class_text}{target}>{inner_html}</a>'


# ======================================================================== icons (SVG drawings)
LOGO_SVG = (
    '<svg width="52" height="34" viewBox="0 0 52 34" aria-hidden="true">'
    '<path d="M3 25 L26 5 L49 25 Q26 32 3 25 Z" fill="#E3C48F" stroke="#1F1A14" stroke-width="2.5" stroke-linejoin="round"></path>'
    '<path d="M14 16 L38 16 M9 21 L43 21 M26 5 L20 27 M26 5 L32 27" stroke="#8A6A3B" stroke-width="1.6" fill="none"></path>'
    '<circle cx="26" cy="5" r="3" fill="#C8102E" stroke="#1F1A14" stroke-width="2"></circle></svg>'
)
TICK_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3.2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg>'
)
CATEGORY_ICON_PATHS = {
    "Travel": '<path d="M2 16l20-6-20-6 4 6-4 6z"/><path d="M6 10h8"/>',
    "Clearances and Employment": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "Identity and Civil Records": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M5.8 16c.6-1.6 1.8-2.4 3.2-2.4s2.6.8 3.2 2.4M14.5 10h4M14.5 13.5h3"/>',
    "Driving": '<path d="M5 16V11l2-5h10l2 5v5z"/><path d="M3 11h18"/><circle cx="8" cy="16.5" r="1.8"/><circle cx="16" cy="16.5" r="1.8"/>',
    "Tax Administration": '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    "Social Insurance": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "Business and Enterprise": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 12h18"/>',
}


def make_category_icon(category_name):
    """Return the small drawing (SVG) for a category."""
    path = CATEGORY_ICON_PATHS.get(category_name, '<path d="M4 6h6l2 2h8v11H4z"/>')
    return ('<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#0038A8" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>')


# ======================================================================== header, footer, tab bar
def make_stripes(colors):
    """Return the three colored flag stripes (blue, yellow, red)."""
    spans = ""
    for color in colors:
        spans = spans + f'<span style="background:{color};box-shadow:0 0 0 100vmax {color};clip-path:inset(0 -100vmax)"></span>'
    return f'<div class="jad-stripes" aria-hidden="true">{spans}</div>'


def make_header(active_page, profile):
    """Flowchart 1-A: the header with the logo and the main menu."""
    # Each menu item is a list: [key, label, address]
    menu = [
        ["documents", "Mga Dokumento", make_page_url("documents", profile, {})],
        ["saved", "Checklist ko", make_page_url("documents", profile, {"view": "saved"})],
        ["agencies", "Ahensya", make_page_url("agencies", profile, {})],
        ["about", "Tungkol sa amin", make_page_url("about", profile, {})],
    ]
    links = ""
    for entry in menu:
        css_class = ""
        if entry[0] == active_page:
            css_class = "active "
        # On phones, every menu item except "About" moves to the bottom tab bar.
        if entry[0] != "about":
            css_class = css_class + "jad-hide-sm"
        links = links + make_link(entry[2], escape_html(entry[1]), css_class.strip(), False)
    call_to_action = make_link(make_page_url("documents", profile, {"view": "saved"}), "Kumpleto ka na ba?", "jad-cta jad-hide-sm", False)
    brand = make_link(make_page_url("home", profile, {}),
                      LOGO_SVG + '<span class="jad-brand-name">Juan <span class="and">and</span> Done</span>', "jad-brand", False)
    return join_lines(f"""
<div>
<header class="jad-header">{brand}
<nav class="jad-nav" aria-label="Main">{links}{call_to_action}</nav>
</header>
{make_stripes([settings.BLUE, settings.YELLOW, settings.RED])}
</div>""")


def make_tab_bar(active_page, profile):
    """The bottom menu that appears only on phones."""
    tabs = [
        ["home", "Home", "⌂", make_page_url("home", profile, {})],
        ["documents", "Dokumento", "▤", make_page_url("documents", profile, {})],
        ["saved", "Checklist ko", "✓", make_page_url("documents", profile, {"view": "saved"})],
        ["agencies", "Ahensya", "◆", make_page_url("agencies", profile, {})],
    ]
    inner = ""
    for tab in tabs:
        css_class = ""
        if tab[0] == active_page:
            css_class = "active"
        inner = inner + make_link(tab[3], f'<span class="i" aria-hidden="true">{tab[2]}</span>{escape_html(tab[1])}', css_class, False)
    return f'<div><nav class="jad-tabbar" aria-label="Phone navigation">{inner}</nav></div>'


def make_footer(profile, last_verified):
    """The dark footer with the disclaimer and the last-verified date of the data."""
    if last_verified != "":
        verified = escape_html(last_verified)
    else:
        verified = "NOT LISTED"
    return join_lines(f"""
<div>
{make_stripes([settings.RED, settings.YELLOW, settings.BLUE])}
<div class="jad-bleed-dark">
<footer class="jad-footer">
<div style="flex:1 1 360px">
<span class="jad-brand-name">Juan <span class="and">and</span> Done</span>
<p>{escape_html(settings.APP_NAME)} is an independent student project (Project Juan and Done). Hindi ito website ng gobyerno at hindi kaanib ng anumang ahensya.
Requirements can change, so always confirm with the agency's official website or Citizen's Charter.</p>
<span class="jad-mono" style="color:#CDBF9F">DATASET LAST VERIFIED (AS RECORDED BY THE TEAM): {verified}</span>
</div>
<nav aria-label="Footer">
{make_link(make_page_url("home", profile, {}), "Home", "", False)}
{make_link(make_page_url("documents", profile, {}), "Mga Dokumento", "", False)}
{make_link(make_page_url("agencies", profile, {}), "Ahensya", "", False)}
{make_link(make_page_url("about", profile, {}), "Tungkol sa amin", "", False)}
</nav>
</footer>
</div>
</div>""")


# ======================================================================== small pieces
def get_tag_class(type_label):
    """Choose the color of a type tag (Original, Photocopy, Printed ...)."""
    lower_label = type_label.lower()
    if lower_label == "original & photocopy":
        return "both"
    elif "printed" in lower_label:
        return "printed"
    elif "digital" in lower_label:
        return "digital"
    elif lower_label.startswith("photocopy"):
        return "photocopy"
    elif lower_label.startswith("original"):
        return "original"
    else:
        return ""


def make_type_tag(type_label):
    """Return a small colored label such as [Original] or [Photocopy]."""
    return f'<span class="jad-tag {get_tag_class(type_label)}">{escape_html(type_label)}</span>'


def make_condition_tag(condition):
    """Return a dashed label like [For married females], or "" if there is no condition."""
    if condition == "":
        return ""
    return f'<span class="jad-tag cond">{escape_html(condition)}</span>'


def make_mode_pills(document):
    """Return the 'In person' / 'May online na hakbang' labels of a document."""
    modes = data_functions.get_step_modes(document)
    pills = ""
    if "in-person" in modes:
        pills = pills + '<span class="jad-pill inperson">In person</span>'
    if "online" in modes:
        pills = pills + '<span class="jad-pill online">May online na hakbang</span>'
    return pills


def make_progress_bar(done, total):
    """Return the progress bar. The width is a percentage: done / total * 100."""
    percent = 0
    if total > 0:
        percent = round(done * 100 / total)
    css_class = "jad-progress"
    if total > 0 and done >= total:
        css_class = "jad-progress done"
    return (f'<div class="{css_class}"><div class="hd"><span>Bitbit mo na</span><span class="n">{done} of {total} ready</span></div>'
            f'<div class="jad-track" role="progressbar" aria-label="Checklist progress" aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="{done}">'
            f'<div class="jad-fill" style="width:{percent}%"></div></div></div>')


def make_callout(kind, title, body_html, icon):
    """Return a colored message box. kind can be 'info', 'warn' or 'danger'."""
    body = ""
    if body_html != "":
        body = " " + body_html
    return join_lines(f"""<div class="jad-callout {kind}"><span class="ic" aria-hidden="true">{escape_html(icon)}</span>
<div><strong>{escape_html(title)}</strong>{body}</div></div>""")


def make_state_box(title, text, kind, detail, action_html):
    """Return a big message box used for errors, empty results and 'not found'."""
    detail_html = ""
    if detail != "":
        detail_html = f'<div class="detail">{escape_html(detail)}</div>'
    return join_lines(f"""<div class="jad-state {kind}">
<div class="big">{escape_html(title)}</div><p>{escape_html(text)}</p>
{detail_html}{action_html}</div>""")


# ======================================================================== cards
CARD_COLORS = ["red", "blue", "yellow"]


def split_into_parts(text):
    """Split text at ';' but never inside brackets ( ... ).

    'A; B (x; y)' becomes ['A', 'B (x; y)'].
    The variable "depth" counts how many brackets are open.
    """
    parts = []
    depth = 0
    current = ""
    for character in text:
        if character == "(":
            depth = depth + 1
        elif character == ")":
            depth = depth - 1
        if character == ";" and depth <= 0:
            parts.append(current.strip())
            current = ""
        else:
            current = current + character
    parts.append(current.strip())

    non_empty_parts = []
    for part in parts:
        if part != "":
            non_empty_parts.append(part)
    return non_empty_parts


def make_short_fact(text):
    """Return only the first part of a long fee text (at most 110 characters)."""
    parts = split_into_parts(text)
    if len(parts) == 0:
        return ""
    first = parts[0]
    if len(first) <= 110:
        return first
    return first[0:107].rstrip() + "…"


def make_document_card(document, profile, card_number, status, done, total):
    """Return one clickable document card (flowchart: document cards)."""
    pills = make_mode_pills(document)
    if not status["complete"]:
        pills = pills + '<span class="jad-pill warn">Kulang ang datos · i-verify</span>'
    if done > 0:
        pills = pills + f'<span class="jad-pill saved">{done} of {total} naka-tsek</span>'

    fees = make_short_fact(document.get("fees", ""))
    if fees == "":
        fees = "Not listed"

    # Decision: a started checklist opens the Checklist page, otherwise the Details page.
    if done > 0:
        go_text = "Ituloy ang checklist →"
        target_page = "checklist"
    else:
        go_text = "Tingnan ang detalye →"
        target_page = "details"

    # The modulus operator % repeats the colors red, blue, yellow, red, blue ...
    color = CARD_COLORS[card_number % 3]
    inner = join_lines(f"""
<div class="hd {color}">{escape_html(data_functions.get_short_name(document))}</div>
<div class="bd">
<span class="jad-overline">{escape_html(document.get('agency') or 'Agency not listed')}</span>
<span class="nm">{escape_html(document['name'])}</span>
<span class="facts">Bayad: {escape_html(fees)}</span>
<div class="jad-pills">{pills}</div>
<span class="go">{go_text}</span>
</div>""")
    return make_link(make_page_url(target_page, profile, {"id": document["id"]}), inner, "jad-card", False)


def make_card_grid(cards):
    """Put a list of card HTML strings inside one grid."""
    return '<div class="jad-grid">' + "".join(cards) + "</div>"


def make_category_grid(categories, profile):
    """Return the category tiles shown on Home (flowchart 2-A)."""
    tiles = ""
    for category in categories:
        inner = (f'<span class="ic">{make_category_icon(category["name"])}</span><span><span class="t">{escape_html(category["label"])}</span><br>'
                 f'<span class="m">{category["count"]} dokumento</span></span>')
        tiles = tiles + make_link(make_page_url("documents", profile, {"category": category["slug"]}), inner, "jad-cat", False)
    return f'<div class="jad-cats">{tiles}</div>'


# ======================================================================== details page parts
def make_fact_value(value):
    """Return one value of the Key info box (a list if it has several parts)."""
    if value == "":
        return '<span style="color:#A85208">Not listed — check the official site</span>'
    parts = split_into_parts(value)
    if len(parts) > 1:
        items = ""
        for part in parts:
            items = items + f"<li>{escape_html(part)}</li>"
        return "<ul>" + items + "</ul>"
    return escape_html(value)


def make_facts_box(document):
    """Flowchart 6-C: agency, where to apply, fees, processing time, validity, last verified."""
    rows = [
        ["Ahensya / Agency", document.get("agency", "")],
        ["Saan mag-a-apply", document.get("whereToGo", "")],
        ["Bayad / Fees", document.get("fees", "")],
        ["Processing time", document.get("processingTime", "")],
        ["Validity", document.get("validity", "")],
        ["Last verified (dataset)", document.get("lastVerified", "")],
    ]
    items = ""
    for row in rows:
        items = items + f'<div class="jad-fact"><dt>{escape_html(row[0])}</dt><dd>{make_fact_value(row[1])}</dd></div>'
    return f'<dl class="jad-facts">{items}</dl>'


def make_website_button(url, hint):
    """Return one official website button that opens in a new tab."""
    inner = (f'<span><span class="d">{escape_html(validation.get_link_host(url))}</span><br>'
             f'<span class="h">{escape_html(hint)}</span></span><span class="arrow">↗</span>')
    return make_link(url, inner, "jad-link-row", True)


def make_links_box(document):
    """Flowchart 6-C: the official links of a document."""
    rows = ""
    for url in document.get("officialLinks", []):
        # Input validation: skip links that are not normal web addresses.
        if not validation.is_safe_link(url):
            rows = rows + f'<div class="jad-callout warn"><span class="ic">!</span><div>Skipped an invalid link in the dataset: {escape_html(url)}</div></div>'
        elif validation.is_gov_ph_link(url):
            rows = rows + make_website_button(url, "Opens in a new tab")
        else:
            rows = rows + make_website_button(url, "Not a .gov.ph address — double-check it is the agency's real site")
    if rows == "":
        return make_callout("info", "Walang official link sa aming datos.",
                            "Requirements can differ per office. Call or visit the office directly, or look for its Citizen's Charter.", "i")
    return f'<div class="jad-links">{rows}</div>'


def make_requirements_list(document):
    """Flowchart 6-C: the general requirements (or a message if there are none)."""
    requirements = document.get("requirements", [])
    if len(requirements) == 0:
        return make_callout("warn", "Information not available.",
                            "Our dataset has no general requirements for this document yet. Check the official website.", "!")
    items = ""
    for requirement in requirements:
        items = items + f'<li><span class="dot"></span><span class="body">{escape_html(requirement)}</span></li>'
    return '<ul class="jad-list">' + items + "</ul>"


def make_bring_list(document):
    """Flowchart 6-C: the physical 'What to bring' items with their exact type labels."""
    bring_items = document.get("whatToBring", [])
    if len(bring_items) == 0:
        return make_callout("warn", "Information not available.",
                            "Our dataset has no 'What to bring' list for this document. Check the official website.", "!")
    items = ""
    for entry in bring_items:
        items = items + f'<li><span class="dot"></span><span class="body"><span>{escape_html(entry["item"])}</span>{make_type_tag(entry["type"])}</span></li>'
    return '<ul class="jad-list">' + items + "</ul>"


def make_steps_list(document):
    """Flowchart 6-C: the numbered steps with 'Online' or 'In person' labels."""
    steps = document.get("steps", [])
    if len(steps) == 0:
        return make_callout("warn", "Information not available.",
                            "Our dataset has no step-by-step instructions for this document. Check the official website.", "!")
    items = ""
    step_number = 0
    for step in steps:
        # Counter variable: increase by 1 for every step.
        step_number = step_number + 1
        mode = step.get("mode", "")
        if mode == "in-person":
            css_class = "inperson"
            badge = '<span class="jad-pill inperson" style="align-self:flex-start">In person</span>'
        elif mode == "online":
            css_class = "online"
            badge = '<span class="jad-pill online" style="align-self:flex-start">Online</span>'
        elif mode != "":
            css_class = ""
            badge = f'<span class="jad-pill" style="align-self:flex-start">{escape_html(mode)}</span>'
        else:
            css_class = ""
            badge = ""
        items = items + (f'<li class="jad-step {css_class}"><span class="num">{step_number}</span><div class="body">'
                         f'<span>{escape_html(step["instruction"])}</span>{badge}</div></li>')
    legend = '<div class="jad-legend"><span class="jad-pill online">Online</span><span class="jad-pill inperson">In person</span></div>'
    return legend + '<ol class="jad-steps">' + items + "</ol>"


def make_status_warning(status):
    """Return the red warning for incomplete guides (or "" when the guide is complete)."""
    if status["complete"]:
        return ""
    reasons = ""
    for reason in status["reasons"]:
        reasons = reasons + f"<li>{escape_html(reason)}</li>"
    note = ""
    if status["note"] != "":
        note = f"<p style='margin:8px 0 0'>{escape_html(status['note'])}</p>"
    return make_callout("danger", "Hindi kumpleto ang guide na ito — i-verify muna.",
                        f"Juan and Done will not show 'Ready ka na!' for this document.<ul>{reasons}</ul>{note}", "!")


def make_agency_card(agency, profile):
    """Flowchart 4-B: one agency card with its documents and official websites."""
    category_labels = []
    for document in agency["docs"]:
        label = data_functions.get_category_label(document.get("category", ""))
        if label not in category_labels:
            category_labels.append(label)
    acronym_text = " · ".join(agency["acronyms"])
    separator = ""
    if acronym_text != "":
        separator = " · "

    document_links = ""
    for document in agency["docs"]:
        document_links = document_links + make_link(make_page_url("details", profile, {"id": document["id"]}), escape_html(document["name"]), "", False)

    if len(agency["links"]) > 0:
        buttons = ""
        for url in agency["links"]:
            if validation.is_gov_ph_link(url):
                buttons = buttons + make_website_button(url, "Official website · new tab")
            else:
                buttons = buttons + make_website_button(url, "Not a .gov.ph address — double-check")
        links_block = f'<div class="jad-links">{buttons}</div>'
    else:
        links_block = make_callout("info", "Walang iisang official website.",
                                   "Requirements differ per office, so call or visit your local office first.", "i")

    return join_lines(f"""<article class="jad-agency">
<div class="head"><span class="jad-monogram" aria-hidden="true">{escape_html(agency['monogram'])}</span>
<div><h2>{escape_html(agency['name'])}</h2><div class="jad-muted">{escape_html(acronym_text)}{separator}{escape_html(' · '.join(category_labels))}</div></div></div>
<div><div class="jad-label">Mga guide sa Juan and Done</div><div class="jad-doclinks">{document_links}</div></div>
{links_block}
</article>""")
