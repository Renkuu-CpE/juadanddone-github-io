# This module contains INPUT VALIDATION functions (Lecture 7: Input Validation).
# "Garbage in, garbage out": every value typed by the user or read from the
# website address (URL) is checked here before the program uses it.
#
# Each validation function receives a value as a PARAMETER and RETURNS either
# True/False (a Boolean) or a cleaned-up value. Other modules import them:
#     from src import validation
#     if validation.is_valid_page(page): ...

from src import settings


def clean_text(value):
    """Return the value as a string with extra spaces removed ("" if it is not text)."""
    # Defensive programming: the value might be a number or None instead of a string.
    if type(value) == str:
        # split() breaks the text into words; " ".join() puts them back with single spaces.
        return " ".join(value.split())
    elif type(value) == int or type(value) == float:
        return str(value)
    else:
        return ""


def is_empty(text):
    """Return True if the user entered nothing (Lecture 7: empty input check)."""
    return clean_text(text) == ""


def is_valid_page(page):
    """Return True only if the page name is one of the allowed pages."""
    # Whitelist check: the value must be one of the items in the list.
    return page in settings.VALID_PAGES


def is_allowed_profile_character(character):
    """Return True if the character may appear in a profile name."""
    # isalnum() is True for letters and digits (including Filipino letters like ñ).
    return character.isalnum() or character in settings.PROFILE_EXTRA_CHARACTERS


def get_profile_error(name):
    """Check a profile name typed by the user.

    Returns an error message (string) if the name is invalid,
    or "" (an empty string) if the name is valid.
    """
    name = clean_text(name)
    # Presence check: the user pressed the button without typing a name.
    if name == "":
        return "Please type a profile name first."
    # Length check (like the password length example in Lecture 7).
    if len(name) > settings.PROFILE_MAX_LENGTH:
        return "The profile name is too long. Use " + str(settings.PROFILE_MAX_LENGTH) + " characters or less."
    # Character check: look at every character using a for loop.
    for character in name:
        if not is_allowed_profile_character(character):
            return "Use only letters, numbers, spaces, dots, dashes or underscores. Do not type ID numbers."
    return ""


def clean_profile_name(raw_name):
    """Make a safe profile name from any text (used for values read from the URL).

    Bad characters are removed, the name is cut to the maximum length,
    and an empty result becomes the default profile "Guest".
    """
    text = ""
    if type(raw_name) == str:
        text = raw_name
    # Build a new string that keeps only the allowed characters.
    safe_name = ""
    for character in text:
        if is_allowed_profile_character(character):
            safe_name = safe_name + character
    # Remove extra spaces, then keep only the first characters (string slicing).
    safe_name = clean_text(safe_name)
    safe_name = safe_name[0:settings.PROFILE_MAX_LENGTH].strip()
    if safe_name == "":
        return settings.DEFAULT_PROFILE
    return safe_name


def get_search_error(search_text):
    """Check the Home search box. Returns an error message or ""."""
    if is_empty(search_text):
        return "Please type a document name first, for example: NBI Clearance."
    if len(search_text) > settings.SEARCH_MAX_LENGTH:
        return "Your search is too long. Use " + str(settings.SEARCH_MAX_LENGTH) + " characters or less."
    return ""


def clean_search_text(search_text):
    """Return a search text that is safe to use (cut to the maximum length)."""
    return clean_text(search_text)[0:settings.SEARCH_MAX_LENGTH]


def is_valid_date_text(text):
    """Return True if the text looks like a date written as YYYY-MM-DD (e.g. 2026-10-14)."""
    # Format check (Lecture 7: dates should be checked).
    if len(text) != 10:
        return False
    if text[4] != "-" or text[7] != "-":
        return False
    # The other characters must all be digits.
    digits = text[0:4] + text[5:7] + text[8:10]
    if not digits.isdigit():
        return False
    month = int(digits[4:6])
    day = int(digits[6:8])
    # Range check with the logical AND operator.
    return month >= 1 and month <= 12 and day >= 1 and day <= 31


def get_link_host(url):
    """Return the website name inside a link, e.g. 'passport.gov.ph'."""
    if "//" not in url:
        return ""
    # Take the part after "//" and before the next "/".
    after_slashes = url.split("//", 1)[1]
    host = after_slashes.split("/")[0].lower()
    # Remove "www." at the start, if it is there.
    if host.startswith("www."):
        host = host[4:]
    return host


def is_safe_link(url):
    """Return True if the link is a normal web address that starts with http:// or https://."""
    if type(url) != str:
        return False
    if " " in url:
        return False
    if not (url.startswith("https://") or url.startswith("http://")):
        return False
    return get_link_host(url) != ""


def is_gov_ph_link(url):
    """Return True if the link belongs to a .gov.ph website."""
    host = get_link_host(url)
    return host == "gov.ph" or host.endswith(".gov.ph")
