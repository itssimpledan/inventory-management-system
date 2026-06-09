"""
init_db.py  —  Run once to create the SQLite database and seed sample data.
Re-running is safe: skips if data already exists.
"""
import sqlite3, os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    db = get_db()
    db.executescript("""
    -- ── USERS ────────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT    NOT NULL UNIQUE,
        password    TEXT    NOT NULL,
        full_name   TEXT    NOT NULL,
        role        TEXT    NOT NULL CHECK(role IN ('admin','finance_manager','finance_exec','ops_manager','ops_planner','ops_exec')),
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    DEFAULT (datetime('now'))
    );

    -- ── SUPPLIERS ─────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS suppliers (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id     TEXT    NOT NULL UNIQUE,
        name            TEXT    NOT NULL,
        contact_name    TEXT,
        email           TEXT,
        phone           TEXT,
        payment_terms   TEXT,
        lead_days       INTEGER DEFAULT 14,
        currency        TEXT    DEFAULT 'USD',
        bank_name       TEXT,
        bank_account    TEXT,
        swift_code      TEXT,
        status          TEXT    DEFAULT 'Active',
        notes           TEXT
    );

    -- ── ITEMS ────────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS items (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id             TEXT    NOT NULL UNIQUE,
        name                TEXT    NOT NULL,
        description         TEXT,
        category            TEXT,
        unit_of_measure     TEXT    DEFAULT 'Units',
        unit_price          REAL    DEFAULT 0,
        reorder_point       INTEGER DEFAULT 0,
        lead_days           INTEGER DEFAULT 14,
        preferred_supplier  TEXT,
        status              TEXT    DEFAULT 'Active',
        notes               TEXT
    );

    -- ── PURCHASE ORDERS ──────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS purchase_orders (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        po_number               TEXT    NOT NULL UNIQUE,
        po_date                 TEXT    NOT NULL,
        supplier_id             TEXT    NOT NULL,
        item_id                 TEXT    NOT NULL,
        qty_ordered             REAL    NOT NULL DEFAULT 0,
        unit_price              REAL    NOT NULL DEFAULT 0,
        free_units              REAL    DEFAULT 0,
        freight_costs           REAL    DEFAULT 0,
        other_costs             REAL    DEFAULT 0,
        currency                TEXT    DEFAULT 'USD',
        fx_rate                 REAL    DEFAULT 1.0,
        payment_due_date        TEXT,
        deposit_pct             REAL    DEFAULT 0.30,
        status                  TEXT    DEFAULT 'Draft',
        raised_by               TEXT,
        approved_by             TEXT,
        approval_date           TEXT,
        deposit_date            TEXT,
        full_payment_date       TEXT,
        expected_delivery_date  TEXT,
        received_date           TEXT,
        received_qty            REAL,
        notes                   TEXT,
        created_at              TEXT    DEFAULT (datetime('now')),
        updated_at              TEXT    DEFAULT (datetime('now'))
    );

    -- ── INVENTORY LEDGER ─────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS inventory_ledger (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        txn_id      TEXT    NOT NULL UNIQUE,
        txn_date    TEXT    NOT NULL,
        txn_type    TEXT    NOT NULL,
        reference   TEXT,
        item_id     TEXT    NOT NULL,
        qty_in      REAL    DEFAULT 0,
        qty_out     REAL    DEFAULT 0,
        unit_cost   REAL    DEFAULT 0,
        posted_by   TEXT,
        notes       TEXT,
        created_at  TEXT    DEFAULT (datetime('now'))
    );

    -- ── FIFO LAYERS ──────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS fifo_layers (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        layer_id        TEXT    NOT NULL UNIQUE,
        item_id         TEXT    NOT NULL,
        po_reference    TEXT,
        receipt_date    TEXT    NOT NULL,
        qty_received    REAL    NOT NULL,
        unit_cost       REAL    NOT NULL,
        created_at      TEXT    DEFAULT (datetime('now'))
    );


    -- ── BUNDLES ──────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS bundles (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        bundle_id   TEXT    NOT NULL UNIQUE,
        name        TEXT    NOT NULL,
        description TEXT,
        status      TEXT    DEFAULT 'Active',
        created_by  TEXT,
        created_at  TEXT    DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS bundle_components (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        bundle_id TEXT NOT NULL REFERENCES bundles(bundle_id),
        item_id   TEXT NOT NULL,
        qty       REAL NOT NULL DEFAULT 1,
        UNIQUE(bundle_id, item_id)
    );

    -- ── SALES UPLOADS ─────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS sales_uploads (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_ref   TEXT NOT NULL UNIQUE,
        platform     TEXT,
        period_from  TEXT,
        period_to    TEXT,
        filename     TEXT,
        total_rows   INTEGER DEFAULT 0,
        uploaded_by  TEXT,
        status       TEXT DEFAULT 'Draft',
        notes        TEXT,
        created_at   TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS sales_lines (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id          INTEGER NOT NULL REFERENCES sales_uploads(id),
        row_num            INTEGER,
        product_name       TEXT,
        sku_id             TEXT,
        qty_sold           REAL DEFAULT 0,
        unit_selling_price REAL DEFAULT 0,
        gross_revenue      REAL DEFAULT 0,
        platform_fees      REAL DEFAULT 0,
        net_revenue        REAL DEFAULT 0
    );

    -- ── PO LINE ITEMS ────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS po_lines (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        po_id        INTEGER NOT NULL REFERENCES purchase_orders(id),
        item_id      TEXT    NOT NULL,
        qty_ordered  REAL    NOT NULL DEFAULT 0,
        unit_price   REAL    NOT NULL DEFAULT 0,
        free_units   REAL    NOT NULL DEFAULT 0,
        qty_received REAL    NOT NULL DEFAULT 0
    );

    -- ── PO DOCUMENTS ────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS po_documents (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        po_id         INTEGER NOT NULL REFERENCES purchase_orders(id),
        doc_type      TEXT    NOT NULL DEFAULT 'Other',
        filename      TEXT    NOT NULL,
        original_name TEXT    NOT NULL,
        uploaded_by   TEXT    NOT NULL,
        notes         TEXT,
        uploaded_at   TEXT    DEFAULT (datetime('now'))
    );

    -- ── SUPPLIER ITEMS ───────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS supplier_items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id TEXT    NOT NULL,
        item_id     TEXT    NOT NULL,
        unit_price  REAL,
        created_by  TEXT,
        created_at  TEXT    DEFAULT (datetime('now')),
        UNIQUE(supplier_id, item_id)
    );
    -- ── SUPPLIER REQUESTS ────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS supplier_requests (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id          TEXT    NOT NULL UNIQUE,
        request_type        TEXT    NOT NULL CHECK(request_type IN ('New','Edit','Deactivate')),
        status              TEXT    NOT NULL DEFAULT 'Pending'
                            CHECK(status IN ('Pending','Ops Approved','Approved','Rejected')),
        -- Target supplier (NULL for New requests until approved)
        supplier_id         TEXT,
        prop_supplier_id    TEXT,
        -- Proposed field values (used for New and Edit)
        prop_name           TEXT,
        prop_contact_name   TEXT,
        prop_email          TEXT,
        prop_phone          TEXT,
        prop_payment_terms  TEXT,
        prop_lead_days      INTEGER,
        prop_currency       TEXT,
        prop_bank_name      TEXT,
        prop_bank_account   TEXT,
        prop_swift_code     TEXT,
        prop_notes          TEXT,
        -- Request metadata
        reason              TEXT,
        raised_by           TEXT    NOT NULL,
        raised_date         TEXT    NOT NULL DEFAULT (date('now')),
        -- Ops Manager approval
        ops_approved_by     TEXT,
        ops_approval_date   TEXT,
        -- Finance Manager approval
        fin_approved_by     TEXT,
        fin_approval_date   TEXT,
        -- Rejection
        rejected_by         TEXT,
        rejection_reason    TEXT,
        rejected_date       TEXT,
        created_at          TEXT    DEFAULT (datetime('now'))
    );
    """)
    db.commit()
    print("✓ Schema created / verified.")

    # ── SEED DATA (skip if already populated) ─────────────────────────────────
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        print("✓ Database already seeded — skipping.")
        db.close()
        return

    # Users
    users = [
        ("daniel",            generate_password_hash("admin123"),  "Daniel",           "admin"),
        ("finance_manager",   generate_password_hash("test123"),   "Finance Manager",  "finance_manager"),
        ("finance_exec",      generate_password_hash("test123"),   "Finance Exec",     "finance_exec"),
        ("ops_manager",       generate_password_hash("test123"),   "Ops Manager",      "ops_manager"),
        ("ops_planner",       generate_password_hash("test123"),   "Ops Planner",      "ops_planner"),
        ("ops_exec",          generate_password_hash("test123"),   "Ops Exec",         "ops_exec"),
    ]
    db.executemany("INSERT INTO users (username,password,full_name,role) VALUES (?,?,?,?)", users)

    # Suppliers
    suppliers = [
        ("S001","ABC Trading Co.","John Smith","john@abctrading.com","+1-555-0101","Net 30",14,"USD","First National Bank","123-456-7890","FNBAUS33","Active","Primary widget supplier"),
        ("S002","XYZ Manufacturing","Li Wei","lwei@xyzman.com","+86-21-55550202","Net 60",21,"USD","Bank of China","987-654-3210","BKCHCNBJ","Active","Main manufacturing partner"),
        ("S003","Fresh Goods Ltd.","Emma Brown","emma@freshgoods.co","+44-20-75550303","Net 45",7,"GBP","Barclays PLC","111-222-3333","BARCGB22","Active","Fast-turnaround supplier"),
    ]
    db.executemany("INSERT INTO suppliers (supplier_id,name,contact_name,email,phone,payment_terms,lead_days,currency,bank_name,bank_account,swift_code,status,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", suppliers)

    # Items
    items = [
        ("I001","Widget A","Standard Widget – Type A","Electronics","Units",9.99,100,14,"S001","Active",""),
        ("I002","Widget B","Premium Widget – Type B","Electronics","Units",19.99,50,21,"S002","Active",""),
        ("I003","Gadget X","Multi-function Gadget X","Electronics","Units",14.99,30,7,"S003","Active",""),
        ("I004","Gadget Y","Compact Gadget Y","Electronics","Units",12.99,40,14,"S001","Active",""),
        ("I005","Component Z","Base Component Z","Components","Units",4.99,200,21,"S002","Active",""),
    ]
    db.executemany("INSERT INTO items (item_id,name,description,category,unit_of_measure,unit_price,reorder_point,lead_days,preferred_supplier,status,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)", items)

    db.commit()
    db.close()
    print("✓ Seed data inserted.")
    print()
    print("  Default logins:")
    print("  ┌─────────────┬─────────────┬──────────────┐")
    print("  │ Username    │ Password    │ Role         │")
    print("  ├─────────────┼─────────────┼──────────────┤")
    print("  │ daniel      │ admin123    │ Admin        │")
    print("  │ sarah       │ finance123  │ Finance      │")
    print("  │ michael     │ ops123      │ Ops Manager  │")
    print("  │ amy         │ ops123      │ Ops Planner  │")
    print("  │ james       │ ops123      │ Ops Exec     │")
    print("  └─────────────┴─────────────┴──────────────┘")


def migrate_db():
    """Upgrade an existing database to support the new ops sub-roles."""
    db = get_db()
    # Check if migration is needed (old schema has 'ops' role constraint)
    schema = db.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    if schema and ("'ops'" in schema["sql"] or "'finance'" in schema["sql"]) and "'finance_manager'" not in schema["sql"]:
        print("Migrating users table to new ops sub-roles...")
        db.executescript("""
            ALTER TABLE users RENAME TO users_old;
            CREATE TABLE users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL,
                full_name   TEXT    NOT NULL,
                role        TEXT    NOT NULL CHECK(role IN ('admin','finance_manager','finance_exec','ops_manager','ops_planner','ops_exec')),
                active      INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    DEFAULT (datetime('now'))
            );
            INSERT INTO users (id, username, password, full_name, role, active, created_at)
            SELECT id, username, password, full_name,
                CASE WHEN role='ops' THEN 'ops_exec' WHEN role='finance' THEN 'finance_manager' ELSE role END,
                active, created_at
            FROM users_old;
            DROP TABLE users_old;
        """)
        db.commit()
        print("✓ Migration complete. Existing 'ops' users converted to 'ops_exec'.")
    else:
        print("✓ Database schema is up to date.")
    db.close()


if __name__ == "__main__":
    migrate_db()
    init_db()
