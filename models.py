import sqlite3
from datetime import datetime
from config import DB_PATH
from openpyxl import Workbook


def get_connection():
    return sqlite3.connect(DB_PATH)


# ======================
# CREATE TABLE
# ======================

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_type TEXT,
        visitor_name TEXT,
        purpose TEXT,
        to_whom TEXT,
        entered_by TEXT,
        in_time TEXT,
        out_time TEXT
    )
    """)

    conn.commit()
    conn.close()


# ======================
# INSERT ENTRY
# ======================

def insert_entry(entry_type, name, purpose, to_whom, entered_by):

    conn = get_connection()
    cur = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
    INSERT INTO entries
    (entry_type, visitor_name, purpose, to_whom, entered_by, in_time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (entry_type, name, purpose, to_whom, entered_by, current_time))

    conn.commit()
    conn.close()


# ======================
# GET ALL ENTRIES
# ======================

def get_all_entries():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM entries ORDER BY id DESC")

    data = cur.fetchall()

    conn.close()

    return data


# ======================
# SEARCH
# ======================

def search_entries(search_query):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM entries
    WHERE visitor_name LIKE ?
    ORDER BY id DESC
    """, ('%' + search_query + '%',))

    data = cur.fetchall()

    conn.close()

    return data


# ======================
# MARK EXIT
# ======================

def mark_exit(entry_id):

    conn = get_connection()
    cur = conn.cursor()

    exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
    UPDATE entries
    SET out_time = ?
    WHERE id = ?
    """, (exit_time, entry_id))

    conn.commit()
    conn.close()


# ======================
# DELETE
# ======================

def delete_entry(entry_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))

    conn.commit()
    conn.close()


# ======================
# STATISTICS
# ======================

def get_statistics():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM entries")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM entries WHERE out_time IS NULL")
    inside = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM entries WHERE out_time IS NOT NULL")
    completed = cur.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
    SELECT COUNT(*) FROM entries
    WHERE DATE(in_time) = ?
    """, (today,))

    today_count = cur.fetchone()[0]

    conn.close()

    return total, inside, completed, today_count


# ======================
# EXPORT EXCEL
# ======================

def generate_today_report():

    conn = get_connection()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
    SELECT entry_type, visitor_name, purpose, to_whom, entered_by, in_time, out_time
    FROM entries
    WHERE DATE(in_time) = ?
    """, (today,))

    rows = cur.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active

    ws.append([
        "Type",
        "Name",
        "Purpose",
        "To Whom",
        "Entered By",
        "In Time",
        "Out Time"
    ])

    for row in rows:
        ws.append(row)

    filename = f"Gate_Report_{datetime.now().strftime('%d-%m-%Y')}.xlsx"

    wb.save(filename)

    return filename


# ======================
# RECENT ACTIVITY
# ======================

def get_recent_activity():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT entry_type, visitor_name, purpose, to_whom, entered_by, in_time, out_time
    FROM entries
    ORDER BY in_time DESC
    LIMIT 10
    """)

    data = cur.fetchall()

    conn.close()

    return data