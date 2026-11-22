# This module saves and reads checklist ticks using SQLite.
# SQLite is a small database that is stored as ONE file on this computer:
#     data/juan_and_done_progress.db
# This is SECONDARY STORAGE (Lecture 1): the ticks stay saved even after the
# computer is turned off, unlike variables in main memory (RAM).
#
# Every function opens a connection, does its job, then CLOSES the connection.
# If something goes wrong, the function catches the error (exception handling)
# and returns a value that tells the caller it failed, so the website never crashes.
#
# The table has one row per (profile, document, checklist item).

import sqlite3
from datetime import datetime, timezone

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS checklist_progress (
    profile     TEXT NOT NULL,
    document_id TEXT NOT NULL,
    item_key    TEXT NOT NULL,
    item_label  TEXT NOT NULL DEFAULT '',
    is_done     INTEGER NOT NULL DEFAULT 0 CHECK (is_done IN (0, 1)),
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (profile, document_id, item_key)
)
"""


def get_current_time():
    """Return the current date and time as text, e.g. '2026-11-21T08:30:00Z'."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_tables(database_file):
    """Create the progress table if it does not exist yet.

    Returns True if the database is ready, or False if it cannot be used
    (for example, the folder is read-only).
    """
    try:
        connection = sqlite3.connect(database_file, timeout=10)
    except sqlite3.Error:
        return False
    try:
        connection.execute(CREATE_TABLE_SQL)
        connection.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        # "finally" runs whether there was an error or not, so the connection is always closed.
        connection.close()


def read_checked_keys(database_file, profile, document_id):
    """Return a set of the item keys that are ticked for one profile and document.

    Returns None if the database could not be read.
    """
    try:
        connection = sqlite3.connect(database_file, timeout=10)
    except sqlite3.Error:
        return None
    try:
        # The "?" marks are filled in by sqlite3 safely (never join user text into SQL).
        rows = connection.execute(
            "SELECT item_key FROM checklist_progress WHERE profile = ? AND document_id = ? AND is_done = 1",
            (profile, document_id),
        ).fetchall()
    except sqlite3.Error:
        return None
    finally:
        connection.close()

    checked_keys = set()
    for row in rows:
        checked_keys.add(row[0])
    return checked_keys


def save_tick(database_file, profile, document_id, item_key, item_label, is_done):
    """Save one checkbox (ticked or not ticked). Returns True if it was saved."""
    if is_done:
        done_number = 1
    else:
        done_number = 0
    try:
        connection = sqlite3.connect(database_file, timeout=10)
    except sqlite3.Error:
        return False
    try:
        # INSERT a new row, or UPDATE the row if this item was saved before.
        connection.execute(
            "INSERT INTO checklist_progress (profile, document_id, item_key, item_label, is_done, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT (profile, document_id, item_key) "
            "DO UPDATE SET is_done = excluded.is_done, item_label = excluded.item_label, updated_at = excluded.updated_at",
            (profile, document_id, item_key, item_label[0:300], done_number, get_current_time()),
        )
        connection.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def reset_checklist(database_file, profile, document_id):
    """Delete all ticks of one profile for one document (flowchart 7: Reset this list).

    Returns the number of rows deleted, or -1 if the database could not be changed.
    """
    try:
        connection = sqlite3.connect(database_file, timeout=10)
    except sqlite3.Error:
        return -1
    try:
        cursor = connection.execute(
            "DELETE FROM checklist_progress WHERE profile = ? AND document_id = ?",
            (profile, document_id),
        )
        connection.commit()
        return cursor.rowcount
    except sqlite3.Error:
        return -1
    finally:
        connection.close()


def read_saved_progress(database_file, profile):
    """Return the saved progress of one profile for ALL documents.

    Returns a dictionary:  {document_id: {"keys": set of ticked keys, "updated": last time}}
    or None if the database could not be read.
    """
    try:
        connection = sqlite3.connect(database_file, timeout=10)
    except sqlite3.Error:
        return None
    try:
        rows = connection.execute(
            "SELECT document_id, item_key, updated_at FROM checklist_progress WHERE profile = ? AND is_done = 1",
            (profile,),
        ).fetchall()
    except sqlite3.Error:
        return None
    finally:
        connection.close()

    saved_progress = {}
    for row in rows:
        document_id = row[0]
        item_key = row[1]
        updated = row[2]
        if document_id not in saved_progress:
            saved_progress[document_id] = {"keys": set(), "updated": ""}
        saved_progress[document_id]["keys"].add(item_key)
        # Keep the newest time (text dates in this format compare correctly).
        if updated > saved_progress[document_id]["updated"]:
            saved_progress[document_id]["updated"] = updated
    return saved_progress
