# This module stores the GLOBAL CONSTANTS of the website.
# A constant is a value that never changes while the program runs.
# Constants are written in UPPERCASE so we can recognize them easily.
# Other modules import this module to read these values, for example:
#     from src import settings
#     print(settings.APP_NAME)
#
# We use global constants instead of global variables because constants
# cannot be changed by mistake (Lecture 3: Global Variables vs Global Constants).

import os

# ---------------------------------------------------------------- website name
APP_NAME = "Juan and Done"
PROJECT_NAME = "Project Juan and Done"
TAGLINE = "Isang punta, tapos na."

# ---------------------------------------------------------------- file paths
# os.path.dirname gives the folder of a file. We go up one folder from "src"
# to reach the main project folder, so the paths work on any computer.
SRC_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(SRC_FOLDER)
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
FONTS_FOLDER = os.path.join(PROJECT_FOLDER, "assets", "fonts")
DOCUMENTS_FILE = os.path.join(DATA_FOLDER, "documents.json")
DATABASE_FILE = os.path.join(DATA_FOLDER, "juan_and_done_progress.db")
FAVICON_FILE = os.path.join(PROJECT_FOLDER, "assets", "favicon.png")

# ---------------------------------------------------------------- pages
# These are the only page names allowed in the website address (?page=...).
VALID_PAGES = ["home", "documents", "agencies", "about", "details", "checklist"]

# ---------------------------------------------------------------- profile names
DEFAULT_PROFILE = "Guest"
PROFILE_MAX_LENGTH = 32
# A profile name may only use letters, numbers and these extra characters.
PROFILE_EXTRA_CHARACTERS = " .-_"

# ---------------------------------------------------------------- search
SEARCH_MAX_LENGTH = 80

# ---------------------------------------------------------------- document data
# The exact "type" labels allowed for each item in "whatToBring".
ITEM_TYPES = ["Original", "Photocopy", "Original & Photocopy", "Original/Printed", "Original/Digital"]
# The two allowed step modes.
STEP_MODES = ["online", "in-person"]
# The fields every document record must have.
REQUIRED_FIELDS = [
    "id", "name", "agency", "category", "description", "whereToGo", "fees",
    "processingTime", "validity", "lastVerified", "officialLinks", "whatToBring",
    "requirements", "steps",
]

# ---------------------------------------------------------------- colors (from the mockup)
BLUE = "#0038A8"
RED = "#C8102E"
YELLOW = "#FCD116"
INK = "#1F1A14"

# ---------------------------------------------------------------- category labels
# A dictionary: the key is the category in documents.json, the value is the short label.
CATEGORY_LABELS = {
    "Travel": "Travel",
    "Clearances and Employment": "Clearances & Employment",
    "Identity and Civil Records": "Identity & Civil Records",
    "Driving": "Driving",
    "Tax Administration": "Tax",
    "Social Insurance": "Social Insurance",
    "Business and Enterprise": "Business",
}

# Short names shown on the colored header of each document card.
SHORT_NAMES = {
    "dfa-passport": "Passport",
    "nbi-clearance": "NBI Clearance",
    "philsys-national-id": "National ID",
    "lto-student-permit": "Student Permit",
    "lto-drivers-license": "Driver's License",
    "pnp-police-clearance": "Police Clearance",
    "bir-tin": "TIN",
    "sss-number": "SSS Number",
    "philhealth-number": "PhilHealth PIN",
    "pagibig-mid": "Pag-IBIG MID",
    "psa-civil-certificates": "PSA Certificates",
    "comelec-voters-certification": "Voter's Certification",
    "phlpost-postal-id": "Postal ID",
    "dti-business-name": "DTI Business Name",
    "lgu-barangay-clearance": "Barangay Clearance",
    "lgu-mayors-permit": "Mayor's Permit",
}

# Short codes shown in the yellow box of some agency cards.
AGENCY_MONOGRAMS = {"PhilHealth": "PHIC", "Barangay Government": "BRGY", "HDMF / Pag-IBIG Fund": "HDMF"}

# Documents shown as chips ("Madalas hanapin") and as cards ("Saan ka papunta?") on Home.
POPULAR_IDS = ["nbi-clearance", "dfa-passport", "pnp-police-clearance", "lto-drivers-license"]
COMMON_IDS = ["nbi-clearance", "dfa-passport", "pnp-police-clearance", "philsys-national-id", "lto-drivers-license", "bir-tin"]

# ---------------------------------------------------------------- readiness results
# The titles of the possible "Ready ka na ba?" results (flowchart page 7).
RESULT_TITLES = {
    "no-items": "Walang checklist",
    "empty": "Simulan natin",
    "missing": "May kulang ka pa!",
    "ready": "Ready ka na!",
    "ready-unverified": "Naka-tsek lahat, pero i-verify muna",
}
