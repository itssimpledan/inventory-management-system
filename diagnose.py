"""
IMS Diagnostic Script — run with: python diagnose.py
Shows exactly where the app fails to start.
"""
import sys, os, traceback

# Fix encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")
print()

# Step 1: Basic stdlib imports
print("=== Step 1: stdlib imports ===")
try:
    import sqlite3, re
    from datetime import datetime, date
    from functools import wraps
    print("OK: sqlite3, re, datetime, functools")
except Exception as e:
    print(f"FAIL: {e}"); traceback.print_exc(); sys.exit(1)

# Step 2: Flask
print("=== Step 2: Flask imports ===")
try:
    from flask import (Flask, render_template, request, redirect, url_for,
                       session, flash, jsonify, g, send_file)
    print("OK: flask core imports")
except Exception as e:
    print(f"FAIL: {e}"); traceback.print_exc(); sys.exit(1)

# Step 3: Werkzeug
print("=== Step 3: Werkzeug imports ===")
try:
    from werkzeug.security import check_password_hash
    from werkzeug.utils import secure_filename
    print("OK: werkzeug imports")
except Exception as e:
    print(f"FAIL: {e}"); traceback.print_exc(); sys.exit(1)

# Step 4: openpyxl
print("=== Step 4: openpyxl ===")
try:
    import openpyxl
    print(f"OK: openpyxl {openpyxl.__version__}")
except Exception as e:
    print(f"FAIL: {e}")

# Step 5: reportlab
print("=== Step 5: reportlab ===")
try:
    from reportlab.pdfgen import canvas
    print("OK: reportlab")
except Exception as e:
    print(f"FAIL: {e}")

# Step 6: Try loading app.py as a module (catches decorator-time errors)
print()
print("=== Step 6: Loading app.py module ===")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("app_module",
               os.path.join(os.path.dirname(__file__), "app.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("OK: app.py loaded without errors")
except SystemExit as e:
    print(f"SystemExit({e.code}) — app called sys.exit() during import")
except Exception as e:
    print(f"FAIL during module load: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 7: Run migrations
print()
print("=== Step 7: run_migrations() ===")
try:
    mod.run_migrations()
    print("OK: migrations ran")
except Exception as e:
    print(f"FAIL: {e}"); traceback.print_exc()

# Step 8: Try starting Flask (3 seconds then kill)
print()
print("=== Step 8: Flask app.run() test ===")
import threading, time
result = {"started": False, "error": None}

def run_flask():
    try:
        mod.app.run(debug=False, host="127.0.0.1", port=5001, use_reloader=False)
        result["started"] = True
    except Exception as e:
        result["error"] = str(e)

t = threading.Thread(target=run_flask, daemon=True)
t.start()
time.sleep(3)

if result["error"]:
    print(f"FAIL: Flask failed to start: {result['error']}")
else:
    import urllib.request
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:5001/login", timeout=2)
        print(f"OK: Flask is responding (HTTP {resp.status})")
    except urllib.error.HTTPError as e:
        print(f"OK: Flask is responding (HTTP {e.code})")
    except Exception as e:
        print(f"Flask may not have started: {e}")

print()
print("=== Diagnosis complete — check above for any FAIL lines ===")
input("Press Enter to exit...")
