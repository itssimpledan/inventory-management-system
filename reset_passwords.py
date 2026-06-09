"""
One-time setup script.
- Resets all non-admin passwords to test123
- Clears all PO / FIFO / ledger data for a clean start
Run this ONCE with the server stopped, then delete this file.
"""
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")
db = sqlite3.connect(DB_PATH)
db.row_factory = sqlite3.Row

# ── 1. Reset passwords ───────────────────────────────────────────────────────
new_hash = generate_password_hash("test123")
db.execute("UPDATE users SET password=? WHERE username != 'daniel'", (new_hash,))
print("\n[1] Passwords updated:")
for u in db.execute("SELECT username, full_name, role FROM users ORDER BY role").fetchall():
    pw = "admin123" if u["username"] == "daniel" else "test123"
    print(f"    {u['role']:20}  {u['username']:25}  → {pw}")

# ── 2. Clear PO data ─────────────────────────────────────────────────────────
tables = ["po_lines", "purchase_orders", "fifo_layers", "inventory_ledger"]
for t in tables:
    db.execute(f"DELETE FROM {t}")
    db.execute("DELETE FROM sqlite_sequence WHERE name=?", (t,))
print("\n[2] PO data cleared:")
for t in tables:
    c = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"    {t}: {c} rows remaining")

db.commit()
db.close()

print("\n✓ Done. You can now delete this file and start the server.")
input("\nPress Enter to close...")
