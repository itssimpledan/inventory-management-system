"""
clear_po_data.py
────────────────
Clears all PO transactional data from the test environment.
Preserves: users, suppliers, items, bundles, settings.

Run this AFTER stopping the Flask app (close the terminal / Ctrl-C).
Then restart the app normally via start.bat.
"""

import sqlite3
import os
import glob

DB_PATH   = os.path.join(os.path.dirname(__file__), "inventory.db")
DOCS_PATH = os.path.join(os.path.dirname(__file__), "po_docs")

def main():
    print("=" * 55)
    print("  PO Data Reset — Test Environment")
    print("=" * 55)

    if not os.path.exists(DB_PATH):
        print(f"\nERROR: Database not found at:\n  {DB_PATH}")
        input("\nPress Enter to exit.")
        return

    confirm = input("\nThis will permanently delete all PO, ledger, FIFO,\nstockcount, and sales data. Type YES to continue: ")
    if confirm.strip().upper() != "YES":
        print("Aborted.")
        input("Press Enter to exit.")
        return

    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur  = conn.cursor()

    tables = [
        "po_documents",
        "po_lines",
        "purchase_orders",
        "inventory_ledger",
        "fifo_layers",
        "stockcount_lines",
        "stockcount_uploads",
        "period_opening_balances",
        "periods",
        "sales_lines",
        "sales_uploads",
    ]

    print("\nClearing tables...")
    for t in tables:
        try:
            n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            cur.execute(f"DELETE FROM {t}")
            print(f"  ✓  {t}  ({n} rows removed)")
        except Exception as e:
            print(f"  ⚠  {t}: {e}")

    # Reset auto-increment counters
    try:
        for t in tables:
            cur.execute("DELETE FROM sqlite_sequence WHERE name=?", (t,))
        print("\n  ✓  Auto-increment counters reset")
    except Exception:
        pass  # sqlite_sequence may not exist in older DBs

    conn.commit()
    conn.close()

    # Delete uploaded PO document files
    deleted = 0
    if os.path.isdir(DOCS_PATH):
        for f in glob.glob(os.path.join(DOCS_PATH, "*")):
            if os.path.isfile(f):
                try:
                    os.remove(f)
                    deleted += 1
                except Exception:
                    pass
    print(f"  ✓  {deleted} document file(s) removed from po_docs/")

    # Verify
    print("\nVerification:")
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    all_clear = True
    for t in tables:
        try:
            n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            status = "✓ empty" if n == 0 else f"⚠  {n} rows remain"
            if n > 0: all_clear = False
        except:
            status = "(table not found)"
        print(f"  {t}: {status}")

    print()
    preserved = {}
    for t in ["users", "suppliers", "items"]:
        try:
            preserved[t] = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except:
            preserved[t] = "?"
    conn.close()

    print(f"  Preserved — users: {preserved['users']}  |  "
          f"suppliers: {preserved['suppliers']}  |  "
          f"items: {preserved['items']}")

    print()
    if all_clear:
        print("✅  All PO data cleared successfully.")
        print("    You can now restart the app and begin fresh.")
    else:
        print("⚠   Some tables still have data. Check above.")

    input("\nPress Enter to exit.")

if __name__ == "__main__":
    main()
