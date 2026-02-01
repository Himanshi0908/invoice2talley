import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db", "invoices.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,
            filename TEXT,
            invoice_number TEXT,
            date TEXT,
            vendor_name TEXT,
            total_amount REAL,
            category TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_invoice(invoice_id, filename, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO invoices (id, filename, invoice_number, date, vendor_name, total_amount, category, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_id,
        filename,
        data.get("invoice_number", "N/A"),
        data.get("date", ""),
        data.get("vendor_name", "Unknown"),
        data.get("total_amount", 0.0),
        data.get("category", "Others"),
        json.dumps(data)
    ))
    conn.commit()
    conn.close()

def get_all_invoices():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        item = dict(row)
        item["extracted_data"] = json.loads(item["raw_data"])
        result.append(item)
    return result

init_db()
