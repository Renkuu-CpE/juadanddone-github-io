# This module stores the CSS (the colors, fonts and layout rules) of the website.
# CSS is the language browsers use for styling. Streamlit has no setting for most of
# these designs, so we keep the CSS inside a Python string and the app shows it with
#     st.markdown("<style>...</style>", unsafe_allow_html=True)
# The project's source code stays 100% Python: the CSS is only text inside a variable.
#
# The fonts (Bungee, Figtree, Space Mono) are saved in assets/fonts. They are read
# from the files and placed inside the CSS so the website looks right even offline.
# Font licence: SIL Open Font License (assets/fonts/FONT_LICENSES_OFL.txt).

import base64
import os

from src import settings

FONT_FILES = [
    # [font name, file name, font weights, characters covered]
    ["Bungee", "Bungee-Regular-latin.woff2", "400", "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"],
    ["Figtree", "Figtree-latin.woff2", "300 900", "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"],
    ["Figtree", "Figtree-latin-ext.woff2", "300 900", "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF"],
    ["Space Mono", "SpaceMono-Bold-latin.woff2", "400 700", "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"],
]


def read_font_as_text(file_name):
    """Read one font file and return it as base64 text (or "" if the file is missing).

    base64 is a Python library that turns the bytes of a file into normal letters,
    so the font can be written directly inside the CSS text.
    """
    file_path = os.path.join(settings.FONTS_FOLDER, file_name)
    if not os.path.isfile(file_path):
        return ""
    try:
        with open(file_path, "rb") as font_file:
            return base64.b64encode(font_file.read()).decode("ascii")
    except OSError:
        return ""


def make_font_css():
    """Return one @font-face rule for every font file that exists."""
    font_css = ""
    for font in FONT_FILES:
        font_text = read_font_as_text(font[1])
        # If the file is missing, skip it: the browser then uses a normal system font.
        if font_text != "":
            font_css = font_css + ("@font-face{font-family:'" + font[0] + "';font-style:normal;font-weight:" + font[2]
                                   + ";font-display:swap;src:url(data:font/woff2;base64," + font_text
                                   + ") format('woff2');unicode-range:" + font[3] + ";}")
    return font_css


def make_page_css():
    """Return the complete <style> block (fonts + design rules) as one string."""
    lines = BASE_CSS.splitlines()
    css_rules = ""
    # Remove empty lines and the spaces at the start of each line.
    for line in lines:
        if line.strip() != "":
            css_rules = css_rules + line.strip() + " "
    return "<style>" + make_font_css() + css_rules + "</style>"


# The design rules. Colors come from the mockup: blue #0038A8, red #C8102E,
# yellow #FCD116, ink #1F1A14, kraft paper #F7EDD8.
BASE_CSS = """
:root{--jad-blue:#0038A8;--jad-blue-dark:#00256F;--jad-blue-shadow:#001E5C;--jad-red:#C8102E;
--jad-red-text:#B00E28;--jad-yellow:#FCD116;--jad-yellow-hover:#E9BE00;--jad-ink:#1F1A14;
--jad-ink-soft:#3A3127;--jad-brown:#6E5228;--jad-brown-line:#8A6A3B;--jad-kraft:#F7EDD8;
--jad-paper:#FFFBF2;--jad-envelope:#D9B477;--jad-sand:#E9DFC9;--jad-t-original:#FCF1C4;
--jad-t-photo:#EFE4CC;--jad-t-printed:#E3EBFA;--jad-t-cash:#DDF0E3;
--jad-display:'Bungee','Arial Black',Impact,sans-serif;--jad-body:'Figtree','Segoe UI',system-ui,-apple-system,sans-serif;
--jad-mono:'Space Mono',Consolas,'Courier New',monospace;}

/* ---------- Streamlit shell ---------- */
[class^="jad-"],[class*=" jad-"],[class^="jad-"] *{box-sizing:border-box;}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--jad-kraft)!important;color:var(--jad-ink);}
.stApp,.stApp p,.stApp li,.stApp label,.stApp input,.stApp textarea,.stApp button,.stApp [data-testid="stMarkdownContainer"],
.stApp [data-baseweb="select"] div{font-family:var(--jad-body);}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer,
[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"],[data-testid="stSidebar"]{display:none!important;}
.block-container,[data-testid="stMainBlockContainer"]{max-width:1200px!important;padding:0 24px 40px!important;}
.stApp a{color:var(--jad-blue);} .stApp a:hover{color:var(--jad-blue-dark);}
.stApp :focus-visible{outline:3px solid var(--jad-blue)!important;outline-offset:3px;}
[data-testid="stMarkdownContainer"] p{font-size:17px;line-height:1.55;}
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style),
.element-container:has(style){margin:0!important;height:0;}

/* ---------- Streamlit widgets in the Juan and Done style ---------- */
[data-testid="stPopover"]{width:100%;}
.stButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button,
[data-testid="stPopover"] button,[data-testid="stLinkButton"] a{width:100%;background:var(--jad-paper)!important;color:var(--jad-ink)!important;
border:2.5px solid var(--jad-ink)!important;border-radius:12px!important;box-shadow:0 4px 0 var(--jad-ink);min-height:48px;
font-weight:800!important;font-size:16px!important;transition:transform 120ms ease,box-shadow 120ms ease;}
.stButton>button p,[data-testid="stFormSubmitButton"] button p,[data-testid="stDownloadButton"] button p,[data-testid="stPopover"] button p{font-weight:800!important;font-size:16px!important;}
.stButton>button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover,[data-testid="stPopover"] button:hover{background:var(--jad-yellow)!important;border-color:var(--jad-ink)!important;}
.stButton>button:active,[data-testid="stFormSubmitButton"] button:active,[data-testid="stDownloadButton"] button:active{transform:translateY(3px);box-shadow:0 1px 0 var(--jad-ink);}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"],[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primaryFormSubmit"]{background:var(--jad-yellow)!important;}
.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover{background:var(--jad-yellow-hover)!important;}
.stButton>button:disabled{background:var(--jad-sand)!important;color:#5C4A2E!important;border-style:dashed!important;border-color:var(--jad-brown-line)!important;box-shadow:none;}
[data-testid="stTextInput"] label p,[data-testid="stSelectbox"] label p,[data-testid="stToggle"] label p,[data-testid="stCheckbox"] label p{font-weight:700;font-size:15px;color:var(--jad-ink);}
[data-testid="stTextInput"] [data-baseweb="input"],[data-testid="stSelectbox"] [data-baseweb="select"]>div{background:var(--jad-paper)!important;
border:2.5px solid var(--jad-ink)!important;border-radius:14px!important;min-height:52px;box-shadow:0 4px 0 var(--jad-ink);}
[data-testid="stTextInput"] input{font-size:17px!important;color:var(--jad-ink)!important;background:transparent!important;}
[data-testid="stTextInput"] [data-baseweb="input"]>div{background:transparent!important;}
[data-testid="stForm"]{border:2.5px solid var(--jad-ink)!important;border-radius:18px!important;background:var(--jad-paper);box-shadow:0 6px 0 var(--jad-ink);padding:12px 14px!important;}
[data-testid="stForm"] [data-testid="stTextInput"] [data-baseweb="input"]{box-shadow:none;border-width:2px!important;}
[data-testid="stExpander"] details{border:2px solid var(--jad-ink)!important;border-radius:14px!important;background:var(--jad-paper);}
[data-testid="stExpander"] summary p{font-weight:800;}
[data-testid="stAlert"]{border-radius:14px;border:2px solid var(--jad-ink);}
div[data-testid="stPopoverBody"]{background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:14px;}

/* ---------- Header, stripes, footer, tab bar ---------- */
.jad-header{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px 24px;padding:20px 0 16px;}
.jad-brand{display:flex;align-items:center;gap:10px;text-decoration:none!important;color:var(--jad-ink)!important;}
.jad-brand-name{font-family:var(--jad-display);font-size:24px;letter-spacing:.01em;line-height:1;}
.jad-brand-name .and{color:var(--jad-red);}
.jad-nav{display:flex;flex-wrap:wrap;align-items:center;gap:8px 22px;font-weight:700;font-size:16px;}
.jad-nav a{color:var(--jad-ink)!important;text-decoration:none;padding:6px 0;border-bottom:3px solid transparent;}
.jad-nav a:hover{border-bottom-color:var(--jad-yellow);}
.jad-nav a.active{border-bottom-color:var(--jad-red);}
.jad-nav a.jad-cta{background:var(--jad-yellow);padding:10px 18px;border-radius:999px;border:2.5px solid var(--jad-ink);
box-shadow:0 4px 0 var(--jad-ink);min-height:48px;display:inline-flex;align-items:center;}
.jad-nav a.jad-cta:hover{background:var(--jad-yellow-hover);}
.jad-stripes{display:flex;flex-direction:column;box-shadow:none;}
.jad-stripes span{display:block;height:6px;}
.jad-bleed{position:relative;}
.jad-bleed-blue{background:var(--jad-blue);box-shadow:0 0 0 100vmax var(--jad-blue);clip-path:inset(0 -100vmax);}
.jad-bleed-dark{background:var(--jad-ink);box-shadow:0 0 0 100vmax var(--jad-ink);clip-path:inset(0 -100vmax);}
.jad-stripes.jad-bleed span{box-shadow:0 0 0 100vmax currentColor;clip-path:inset(0 -100vmax);}
.jad-profile-note{font-size:14px;color:var(--jad-brown);font-weight:600;padding-top:12px;}
.jad-footer{color:#E9DFC9;padding:44px 0 36px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:28px;}
.jad-footer .jad-brand-name{color:var(--jad-paper);} .jad-footer .jad-brand-name .and{color:var(--jad-yellow);}
.jad-footer p{margin:12px 0;font-size:15px!important;max-width:58ch;color:#E9DFC9;}
.jad-footer nav{display:flex;flex-direction:column;gap:8px;font-weight:600;font-size:15px;}
.jad-footer nav a{color:var(--jad-paper)!important;}
.jad-mono{font-family:var(--jad-mono);font-size:13px;letter-spacing:.04em;}
.jad-tabbar{display:none;}

/* ---------- Typography helpers ---------- */
.jad-badge-dark{display:inline-block;background:var(--jad-ink);color:var(--jad-yellow);font-weight:800;font-size:13px;letter-spacing:.12em;padding:8px 14px;border-radius:999px;}
.jad-h1{margin:0;font-family:var(--jad-display);font-weight:400;font-size:clamp(40px,6vw,72px);line-height:1.02;color:var(--jad-blue);}
.jad-h1 .red,.jad-h2 .red{color:var(--jad-red);}
.jad-h2{margin:0;font-family:var(--jad-display);font-weight:400;font-size:clamp(28px,4vw,44px);line-height:1.1;color:var(--jad-blue);}
.jad-h3{margin:0 0 10px;font-family:var(--jad-display);font-weight:400;font-size:19px;color:var(--jad-ink);}
.jad-lead{margin:0;font-size:20px;line-height:1.55;max-width:40ch;color:var(--jad-ink-soft);}
.jad-overline{font-size:13px;font-weight:800;letter-spacing:.08em;color:var(--jad-brown);text-transform:uppercase;}
.jad-muted{color:var(--jad-brown);font-size:15px;}
.jad-section-head{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px;margin:8px 0 22px;}
.jad-section-head a{font-weight:700;font-size:17px;}
.jad-space{height:22px;}

/* ---------- Hero ---------- */
.jad-hero-copy{display:flex;flex-direction:column;gap:20px;padding:44px 0 6px;}
.jad-chips{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:6px;}
.jad-chips .label{font-weight:700;font-size:15px;color:var(--jad-brown);margin-right:4px;}
.jad-chip{background:var(--jad-paper);border:2px solid var(--jad-ink);color:var(--jad-ink)!important;text-decoration:none!important;font-weight:600;
font-size:15px;padding:8px 14px;border-radius:999px;min-height:44px;display:inline-flex;align-items:center;}
.jad-chip:hover{background:var(--jad-yellow);}
.jad-illus{position:relative;width:100%;max-width:460px;height:470px;margin:30px auto 0;}
.jad-env{position:absolute;left:6%;top:18px;width:82%;height:400px;background:var(--jad-envelope);border:2.5px solid var(--jad-ink);border-radius:14px;transform:rotate(-4deg);box-shadow:0 8px 0 var(--jad-ink);}
.jad-env .btn1{position:absolute;left:50%;top:22px;width:34px;height:34px;margin-left:-17px;border-radius:50%;background:var(--jad-kraft);border:2.5px solid var(--jad-ink);}
.jad-env .str{position:absolute;left:50%;top:52px;width:3px;height:80px;margin-left:-1px;background:var(--jad-ink);}
.jad-env .lbl{position:absolute;left:22px;bottom:18px;font-family:var(--jad-mono);font-size:13px;color:#4A361A;}
.jad-paperlist{position:absolute;left:14%;top:58px;width:72%;background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:12px;padding:22px 22px 26px;transform:rotate(2deg);display:flex;flex-direction:column;gap:12px;}
.jad-paperlist .t{font-family:var(--jad-display);font-size:18px;color:var(--jad-blue);}
.jad-paperlist .row{display:flex;align-items:center;gap:10px;font-weight:600;font-size:16px;}
.jad-tick{width:24px;height:24px;border-radius:6px;background:var(--jad-blue);display:inline-flex;align-items:center;justify-content:center;flex:none;}
.jad-stamp{border:4px solid var(--jad-red);outline:2px solid var(--jad-red);outline-offset:4px;border-radius:10px;padding:8px 18px;background:rgba(255,251,242,.92);text-align:center;}
.jad-stamp .big{font-family:var(--jad-display);font-size:34px;line-height:1;color:var(--jad-red);}
.jad-stamp .small{font-family:var(--jad-mono);font-size:12px;color:var(--jad-red);margin-top:6px;}
.jad-illus .jad-stamp{position:absolute;right:0;top:196px;transform:rotate(-12deg);}
.jad-ticket{position:absolute;left:0;bottom:0;width:200px;background:#FFFFFF;border:2.5px dashed var(--jad-ink);border-radius:10px;padding:14px 16px;transform:rotate(-6deg);box-shadow:0 6px 0 var(--jad-ink);display:flex;flex-direction:column;gap:2px;}
.jad-ticket .k{font-family:var(--jad-mono);font-size:12px;letter-spacing:.1em;color:var(--jad-brown);}
.jad-ticket .n{font-family:var(--jad-display);font-size:44px;line-height:1.05;color:var(--jad-blue);}
.jad-ticket .w{font-weight:700;font-size:14px;}
.jad-suggest-hint{font-size:14px;color:var(--jad-brown);font-weight:600;margin:-4px 0 0;}

/* ---------- Blue "Paano ba 'to?" band ---------- */
.jad-band{color:#FFFFFF;padding:60px 0 64px;margin:26px 0 10px;}
.jad-band .jad-h2{color:#FFFFFF;}
.jad-band .sub{margin:0;font-size:18px;color:#D6E1F7;max-width:44ch;}
.jad-how-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:24px;}
.jad-how-card{background:var(--jad-paper);color:var(--jad-ink);border:2.5px solid var(--jad-ink);border-radius:16px;overflow:hidden;box-shadow:0 8px 0 var(--jad-blue-shadow);}
.jad-how-card .hd{background:var(--jad-yellow);border-bottom:2.5px solid var(--jad-ink);padding:12px 20px;display:flex;align-items:center;gap:12px;}
.jad-how-card .num{font-family:var(--jad-display);font-size:30px;line-height:1;color:var(--jad-red);}
.jad-how-card .ttl{font-family:var(--jad-display);font-size:17px;}
.jad-how-card p{margin:0;padding:18px 20px 22px;font-size:16px!important;}

/* ---------- Cards ---------- */
.jad-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:24px;}
.jad-card{display:flex;flex-direction:column;background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:16px;overflow:hidden;
text-decoration:none!important;color:var(--jad-ink)!important;box-shadow:0 6px 0 var(--jad-ink);transition:transform 150ms ease,box-shadow 150ms ease;}
.jad-card:hover{transform:translateY(-4px);box-shadow:0 10px 0 var(--jad-ink);}
.jad-card .hd{padding:14px 20px;font-family:var(--jad-display);font-size:21px;letter-spacing:.02em;line-height:1.15;text-transform:uppercase;}
.jad-card .hd.red{background:var(--jad-red);color:#FFFFFF;} .jad-card .hd.blue{background:var(--jad-blue);color:#FFFFFF;}
.jad-card .hd.yellow{background:var(--jad-yellow);color:var(--jad-ink);border-bottom:2.5px solid var(--jad-ink);}
.jad-card .bd{padding:16px 20px 20px;display:flex;flex-direction:column;gap:11px;flex:1;}
.jad-card .nm{font-weight:700;font-size:16px;line-height:1.35;}
.jad-card .facts{font-size:14px;color:var(--jad-ink-soft);line-height:1.45;}
.jad-card .go{font-weight:800;color:var(--jad-blue);margin-top:auto;}
.jad-pills{display:flex;flex-wrap:wrap;gap:6px;}
.jad-pill{background:var(--jad-t-photo);border:1.5px solid var(--jad-ink);border-radius:999px;padding:3px 10px;font-size:13px;font-weight:700;line-height:1.35;color:var(--jad-ink);}
.jad-pill.inperson{background:var(--jad-t-original);} .jad-pill.online{background:var(--jad-t-printed);}
.jad-pill.saved{background:var(--jad-t-cash);} .jad-pill.warn{background:#FFE3E6;border-color:var(--jad-red);color:var(--jad-red-text);}
.jad-pill.cat{background:var(--jad-paper);}
.jad-cats{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;}
.jad-cat{display:flex;align-items:center;gap:14px;padding:14px 16px;background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:14px;
box-shadow:0 4px 0 var(--jad-ink);text-decoration:none!important;color:var(--jad-ink)!important;min-height:76px;}
.jad-cat:hover{background:var(--jad-yellow);}
.jad-cat .ic{flex:none;width:46px;height:46px;border-radius:12px;border:2px solid var(--jad-ink);background:var(--jad-t-printed);display:grid;place-items:center;}
.jad-cat .t{font-weight:800;font-size:16px;line-height:1.25;} .jad-cat .m{font-size:14px;color:var(--jad-brown);}
.jad-banner{background:var(--jad-red);color:#FFFFFF;border:2.5px solid var(--jad-ink);border-radius:22px;box-shadow:0 8px 0 var(--jad-ink);padding:36px 40px;
display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:24px;margin:40px 0 16px;}
.jad-banner .jad-h2{color:#FFFFFF;} .jad-banner p{margin:10px 0 0;font-size:18px!important;max-width:52ch;color:#FFE9EC;}
.jad-btn{background:var(--jad-paper);color:var(--jad-ink)!important;text-decoration:none!important;font-weight:800;font-size:17px;border:2.5px solid var(--jad-ink);
border-radius:999px;padding:12px 22px;min-height:50px;display:inline-flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 5px 0 var(--jad-ink);}
.jad-btn:hover{background:var(--jad-yellow);} .jad-btn.yellow{background:var(--jad-yellow);} .jad-btn.yellow:hover{background:var(--jad-yellow-hover);}
.jad-btn.block{display:flex;width:100%;border-radius:14px;min-height:56px;font-size:18px;}
[data-testid="stColumn"] .jad-btn.block{min-height:48px;font-size:16px;border-radius:12px;padding:8px 16px;box-shadow:0 4px 0 var(--jad-ink);}
.jad-info{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin:26px 0 10px;}
.jad-panel{background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:16px;padding:20px 22px;box-shadow:0 5px 0 var(--jad-ink);}
.jad-panel p{margin:6px 0 0;font-size:16px!important;}

/* ---------- Continue card & progress ---------- */
.jad-continue{display:flex;flex-wrap:wrap;align-items:center;gap:14px 24px;background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-left:12px solid var(--jad-blue);
border-radius:16px;padding:18px 22px;box-shadow:0 6px 0 var(--jad-ink);margin:18px 0 0;}
.jad-continue .txt{flex:1 1 300px;display:flex;flex-direction:column;gap:6px;}
.jad-progress{display:flex;flex-direction:column;gap:6px;}
.jad-progress .hd{display:flex;justify-content:space-between;gap:12px;font-weight:800;font-size:15px;}
.jad-progress .hd .n{font-family:var(--jad-mono);}
.jad-track{height:14px;background:var(--jad-kraft);border:2px solid var(--jad-ink);border-radius:999px;overflow:hidden;}
.jad-fill{height:100%;background:var(--jad-blue);border-radius:999px;}
.jad-progress.done .jad-fill{background:#1D7A45;}

/* ---------- Page heads, states, callouts ---------- */
.jad-page-head{padding:30px 0 10px;display:flex;flex-direction:column;gap:10px;}
.jad-page-head p{margin:0;font-size:18px!important;color:var(--jad-ink-soft);max-width:70ch;}
.jad-crumbs{font-size:15px;font-weight:700;} .jad-crumbs a{text-decoration:none;}
.jad-state{display:flex;flex-direction:column;align-items:center;text-align:center;gap:10px;padding:44px 24px;background:var(--jad-paper);
border:2.5px dashed var(--jad-brown-line);border-radius:18px;margin:10px 0;}
.jad-state .big{font-family:var(--jad-display);font-size:30px;color:var(--jad-red);line-height:1.1;}
.jad-state p{margin:0;max-width:52ch;color:var(--jad-ink-soft);}
.jad-state .detail{font-family:var(--jad-mono);font-size:13px;color:var(--jad-brown);overflow-wrap:anywhere;}
.jad-state.error{border-color:var(--jad-red);border-style:solid;}
.jad-callout{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-radius:14px;border:2px solid var(--jad-ink);background:var(--jad-t-printed);font-size:15px;line-height:1.5;margin:8px 0;}
.jad-callout.warn{background:#FFF1E2;border-color:#A85208;} .jad-callout.danger{background:#FFE3E6;border-color:var(--jad-red);}
.jad-callout .ic{flex:none;font-family:var(--jad-display);font-size:18px;line-height:1.2;}
.jad-callout ul{margin:6px 0 0 18px;padding:0;}
.jad-results-meta{font-size:15px;color:var(--jad-brown);font-weight:600;margin:4px 0 14px;}
.jad-results-meta strong{color:var(--jad-ink);}

/* ---------- Details ---------- */
.jad-detail-head{background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:20px;box-shadow:0 6px 0 var(--jad-ink);padding:24px 26px;margin:14px 0 24px;display:flex;flex-direction:column;gap:10px;}
.jad-detail-head h1{margin:0;font-family:var(--jad-display);font-weight:400;font-size:clamp(28px,4vw,40px);line-height:1.08;color:var(--jad-blue);}
.jad-detail-head p{margin:0;font-size:17px!important;color:var(--jad-ink-soft);max-width:75ch;}
.jad-detail-grid{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:26px;align-items:start;}
.jad-col{display:flex;flex-direction:column;gap:22px;min-width:0;}
.jad-facts{display:grid;gap:0;margin:0;}
.jad-fact{padding:10px 0;border-top:1.5px dashed var(--jad-brown-line);}
.jad-fact:first-child{border-top:0;padding-top:0;}
.jad-fact dt{font-family:var(--jad-mono);font-size:12px;letter-spacing:.06em;color:var(--jad-brown);text-transform:uppercase;}
.jad-fact dd{margin:3px 0 0;font-weight:700;font-size:15px;line-height:1.45;overflow-wrap:anywhere;}
.jad-fact dd ul{margin:0;padding-left:18px;}
.jad-links{display:flex;flex-direction:column;gap:10px;}
.jad-link-row{display:flex;align-items:center;gap:12px;min-height:52px;padding:8px 14px;border:2px solid var(--jad-ink);border-radius:12px;background:#FFFFFF;
text-decoration:none!important;color:var(--jad-ink)!important;overflow-wrap:anywhere;}
.jad-link-row:hover{background:var(--jad-t-printed);}
.jad-link-row .d{font-weight:800;color:var(--jad-blue);} .jad-link-row .h{font-size:13px;color:var(--jad-brown);}
.jad-link-row .arrow{margin-left:auto;font-weight:800;}
.jad-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px;}
.jad-list li{display:flex;gap:12px;align-items:flex-start;padding:11px 14px;background:#FFFFFF;border:1.5px solid var(--jad-ink);border-radius:12px;font-size:16px;line-height:1.45;}
.jad-list li .dot{flex:none;width:10px;height:10px;margin-top:8px;border-radius:50%;background:var(--jad-blue);}
.jad-list li .body{display:flex;flex-direction:column;gap:6px;min-width:0;}
.jad-tag{align-self:flex-start;border:1.5px solid var(--jad-ink);border-radius:999px;padding:1px 9px;font-size:13px;font-weight:700;background:var(--jad-t-photo);font-family:var(--jad-body);}
.jad-tag.original{background:var(--jad-t-original);} .jad-tag.photocopy{background:var(--jad-t-photo);}
.jad-tag.printed,.jad-tag.digital{background:var(--jad-t-printed);} .jad-tag.both{background:#F6E2A8;}
.jad-tag.cond{background:transparent;border-style:dashed;color:var(--jad-brown);font-weight:600;}
.jad-tags{display:flex;flex-wrap:wrap;gap:6px;}
.jad-steps{list-style:none;margin:0;padding:0;counter-reset:st;display:flex;flex-direction:column;gap:12px;}
.jad-step{display:grid;grid-template-columns:44px minmax(0,1fr);gap:12px;align-items:start;}
.jad-step .num{width:44px;height:44px;border-radius:50%;border:2.5px solid var(--jad-ink);display:grid;place-items:center;font-family:var(--jad-display);font-size:17px;background:var(--jad-t-printed);color:var(--jad-blue);}
.jad-step.inperson .num{background:var(--jad-yellow);color:var(--jad-ink);}
.jad-step .body{display:flex;flex-direction:column;gap:6px;padding-top:4px;font-size:16px;line-height:1.5;}
.jad-legend{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px;}

/* ---------- Checklist ---------- */
.jad-check-head{background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:20px;padding:18px 22px 20px;box-shadow:0 6px 0 var(--jad-ink);
margin:14px 0 16px;display:flex;flex-direction:column;gap:12px;}
.jad-check-head h1{margin:0;font-family:var(--jad-display);font-weight:400;font-size:clamp(26px,4vw,36px);line-height:1.1;color:var(--jad-blue);}
.jad-q{font-family:var(--jad-display);font-size:24px;color:var(--jad-blue);margin:6px 0 2px;}
div[class*="st-key-jadrow-"]{background:var(--jad-paper);border:2px dashed var(--jad-brown-line);border-radius:14px;padding:12px 14px 12px;gap:6px!important;}
div[class*="st-key-jadrow-"]:has(input:checked){background:var(--jad-t-printed);border:2px solid var(--jad-blue);}
div[class*="st-key-jadrow-miss"]{border:2.5px dashed var(--jad-red)!important;background:#FFF0F2!important;}
div[class*="st-key-jadrow-"] [data-testid="stCheckbox"] label p{font-size:16px!important;font-weight:700!important;line-height:1.35;}
div[class*="st-key-jadrow-"] [data-testid="stCheckbox"] label{align-items:flex-start;}
div[class*="st-key-jadrow-"] [data-testid="stMarkdownContainer"]{padding-left:28px;}
.jad-result{border:2.5px solid var(--jad-ink);border-radius:20px;overflow:hidden;box-shadow:0 6px 0 var(--jad-ink);margin:14px 0;}
.jad-result .top{padding:24px 22px;display:flex;flex-wrap:wrap;align-items:center;gap:18px 26px;}
.jad-result .top h2{margin:0;font-family:var(--jad-display);font-weight:400;font-size:30px;line-height:1.1;}
.jad-result .top p{margin:6px 0 0;font-size:17px!important;}
.jad-result .bottom{background:var(--jad-kraft);border-top:2.5px solid var(--jad-ink);padding:16px 22px;display:flex;flex-direction:column;gap:10px;}
.jad-result.ready .top{background:var(--jad-blue);color:#FFFFFF;} .jad-result.ready h2{color:var(--jad-yellow);} .jad-result.ready .top p{color:#E3EBFA;}
.jad-result.ready .jad-stamp{transform:rotate(-8deg);background:var(--jad-paper);outline-color:var(--jad-paper);}
.jad-result.missing .top{background:#FFF0F2;} .jad-result.missing h2{color:var(--jad-red-text);}
.jad-result.empty .top{background:var(--jad-t-original);} .jad-result.empty h2{color:var(--jad-blue);}
.jad-result.unverified .top{background:#FFF1E2;} .jad-result.unverified h2{color:#A85208;}
.jad-result ul{margin:0;padding-left:20px;} .jad-result li{margin:4px 0;font-size:16px;}

/* ---------- Agencies ---------- */
.jad-agency{background:var(--jad-paper);border:2.5px solid var(--jad-ink);border-radius:16px;box-shadow:0 6px 0 var(--jad-ink);padding:20px;display:flex;flex-direction:column;gap:14px;min-width:0;}
.jad-agency .head{display:flex;gap:14px;align-items:flex-start;}
.jad-monogram{flex:none;min-width:56px;height:56px;padding:0 6px;border-radius:12px;border:2.5px solid var(--jad-ink);background:var(--jad-yellow);display:grid;place-items:center;
font-family:var(--jad-display);font-size:14px;color:var(--jad-ink);}
.jad-agency h2{margin:0;font-size:18px;line-height:1.3;font-weight:800;color:var(--jad-blue);font-family:var(--jad-body);}
.jad-doclinks{display:flex;flex-wrap:wrap;gap:6px;}
.jad-doclinks a{font-size:14px;font-weight:700;padding:6px 12px;border-radius:999px;background:#FFFFFF;border:1.5px solid var(--jad-ink);color:var(--jad-ink)!important;text-decoration:none;}
.jad-doclinks a:hover{background:var(--jad-yellow);}
.jad-label{font-family:var(--jad-mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--jad-brown);margin-bottom:6px;}

/* ---------- About ---------- */
.jad-prose{display:flex;flex-direction:column;gap:12px;max-width:78ch;}
.jad-prose p,.jad-prose li{font-size:17px;line-height:1.6;}
.jad-prose ul{margin:0;padding-left:22px;}
.jad-table{width:100%;border-collapse:collapse;font-size:14px;background:#FFFFFF;border:2px solid var(--jad-ink);border-radius:12px;overflow:hidden;}
.jad-table th,.jad-table td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--jad-sand);vertical-align:top;}
.jad-table th{background:var(--jad-ink);color:var(--jad-paper);font-family:var(--jad-mono);font-size:12px;letter-spacing:.04em;}
.jad-table-wrap{overflow-x:auto;}

/* ---------- Responsive ---------- */
@media (max-width: 900px){
  .jad-detail-grid{grid-template-columns:minmax(0,1fr);}
  .jad-illus{transform:scale(.82);transform-origin:top center;height:400px;margin-top:0;}
}
@media (max-width: 760px){
  .block-container,[data-testid="stMainBlockContainer"]{padding:0 14px 96px!important;}
  .jad-nav a.jad-hide-sm{display:none;}
  .jad-header{padding:14px 0 12px;} .jad-brand-name{font-size:20px;}
  .jad-band{padding:44px 0 48px;} .jad-banner{padding:26px 22px;} .jad-lead{font-size:18px;}
  .jad-illus{display:none;}
  .jad-tabbar{display:grid;grid-template-columns:repeat(4,1fr);position:fixed;left:0;right:0;bottom:0;z-index:999990;background:var(--jad-paper);
  border-top:2.5px solid var(--jad-ink);padding-bottom:env(safe-area-inset-bottom);}
  .jad-tabbar a{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:60px;font-size:12px;font-weight:800;color:var(--jad-ink)!important;text-decoration:none;gap:2px;}
  .jad-tabbar a .i{font-family:var(--jad-display);font-size:16px;line-height:1;}
  .jad-tabbar a.active{background:var(--jad-yellow);}
}
@media (prefers-reduced-motion: reduce){.jad-card,.stButton>button{transition:none!important;}.jad-card:hover{transform:none;}}

/* ---------- Print: a clean checklist ---------- */
@media print{
  .jad-header,.jad-tabbar,.jad-footer,.jad-stripes,.jad-no-print,.stButton,[data-testid="stDownloadButton"],[data-testid="stPopover"],
  [data-testid="stExpander"],.jad-band,.jad-banner{display:none!important;}
  html,body,.stApp,[data-testid="stAppViewContainer"]{background:#FFFFFF!important;}
  .jad-check-head,.jad-result,.jad-detail-head,.jad-panel,.jad-card{box-shadow:none!important;}
  div[class*="st-key-jadrow-"]{break-inside:avoid;}
}

/* =========================================
   FORCE LIGHT MODE - SEARCH & SUGGESTIONS
========================================= */

:root,
html,
body,
.stApp {
    color-scheme: light !important;
}

/* SEARCH INPUT */
.stApp [data-testid="stTextInput"] div[data-baseweb="input"],
.stApp [data-testid="stTextInput"] div[data-baseweb="base-input"] {
    background: #FFFBF2 !important;
    background-color: #FFFBF2 !important;
    border-color: #1F1A14 !important;
}

.stApp [data-testid="stTextInput"] input {
    background: transparent !important;
    background-color: transparent !important;
    color: #1F1A14 !important;
    -webkit-text-fill-color: #1F1A14 !important;
    color-scheme: light !important;
}

.stApp [data-testid="stTextInput"] input::placeholder {
    color: #8A8178 !important;
    -webkit-text-fill-color: #8A8178 !important;
    opacity: 1 !important;
}

/* LIVE SUGGESTIONS SELECTBOX */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #FFFBF2 !important;
    background-color: #FFFBF2 !important;
    color: #1F1A14 !important;
    border-color: #1F1A14 !important;
    color-scheme: light !important;
}

/* SELECTBOX TEXT */
.stApp [data-testid="stSelectbox"] input {
    color: #1F1A14 !important;
    -webkit-text-fill-color: #1F1A14 !important;
    color-scheme: light !important;
}

/* DROPDOWN MENU */
.stApp [data-baseweb="popover"],
.stApp [data-baseweb="menu"],
.stApp [role="listbox"],
.stApp [role="option"] {
    background-color: #FFFBF2 !important;
    color: #1F1A14 !important;
}

"""
