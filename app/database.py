import sqlite3
import json
from datetime import datetime


DB_NAME = "faq_history.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source TEXT NOT NULL,
            faq_count INTEGER NOT NULL,
            language TEXT NOT NULL,
            tone TEXT NOT NULL,
            faqs TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_faq_history(
    source_type,
    source,
    faq_count,
    language,
    tone,
    faqs
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO faq_history
        (source_type, source, faq_count, language, tone, faqs, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        source_type,
        source,
        faq_count,
        language,
        tone,
        json.dumps(faqs),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_faq_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, source_type, source, faq_count,
               language, tone, faqs, created_at
        FROM faq_history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row[0],
            "source_type": row[1],
            "source": row[2],
            "faq_count": row[3],
            "language": row[4],
            "tone": row[5],
            "faqs": json.loads(row[6]),
            "created_at": row[7]
        })

    return history
