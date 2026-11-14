# DARK CRIMENET v5.3.1 — Windows Quick Start

## 1. Extract the ZIP

Extract the project to a normal folder such as:

```text
C:\DARK_CRIMENET
```

## 2. One-command launch

Double-click:

```text
RUN_WINDOWS.bat
```

The launcher:

- detects Python 3.11+;
- creates `venv` when needed;
- installs `requirements.txt` into the local environment;
- starts the app (UI and API together) on `127.0.0.1:8000` and opens your browser;
- does **not** seed unrelated demo graph data automatically.

## 3. Manual launch

PowerShell:

```powershell
cd "C:\DARK_CRIMENET"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://localhost:8000
```

API documentation (demo mode only):

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 4. Sign in

Open `CREDENTIALS.txt`. The main admin is **Officer ID `Divymathur12345678901@gmail.com`** with the demo password written in that file (Officer IDs are not case-sensitive). Change the password from the Account button (top right) after signing in.

**Forgot the admin or a password?** Edit the ACCOUNT TABLE at the bottom of `CREDENTIALS.txt`, then double-click `RESET_CREDENTIALS.bat`. It re-creates or resets every listed account and switches two-step sign-in off for them. See `DEMO_ACCOUNTS.md`.

The release ships with a ready database (demo data included), so the accounts work immediately.

## 5. Fresh FIR workbench

For a completely separate investigation:

```text
Sidebar → ＋ New Workbench → Create fresh workbench
```

Admin and Supervisor can create a workbench. Investigators and Auditors cannot change case data.

## 6. FIR processing flow

```text
Upload FIR
   ↓
OCR / language detection
   ↓
Structured FIR extraction
   ↓
Human review
   ↓
Verify entities + relationships
   ↓
FIR-centric graph
   ↓
Cross-FIR relationship intelligence
   ↓
Timeline + Map
   ↓
KNN candidate resolution
   ↓
Signals / Evidence / Audit
   ↓
Reports
```

## 7. Hindi / Marathi OCR

The release bundles `eng`, `hin`, `mar`, OSD and Devanagari Tesseract assets. The UI exposes:

- original OCR text;
- detected language + confidence;
- English interpretation/transliteration;
- field-level comparison;
- orientation correction for photographed/scanned pages.

The original FIR text always remains the authoritative source.

## 8. KNN Entity Resolution

Open:

```text
Entity Resolution → KNN Entity Resolution Workbench
```

The resolver combines:

- character n-gram KNN cosine similarity;
- lexical similarity;
- normalized identifier similarity.

It returns ranked candidates and an explanation. It does **not** auto-merge identities.

## 9. Load Neighborhood

Open:

```text
Knowledge Graph → Center entity → Hops → Node type → Relation → Load neighborhood
```

The graph is strictly scoped to the active FIR workspace. Use the entity table below the graph to inspect the exact IDs and types.

## 10. Useful validation commands

```powershell
python -m pytest -q
python -m compileall -q .
python -m py_compile backend\app\main.py backend\app\services\app_service.py security\auth.py ai_engine\nlp\document_intelligence.py ai_engine\nlp\translation.py
```

Install `requirements-dev.txt` to run the test suite. The v5.0.0 UI was exercised in headless Chromium for all three roles against a live server (every tab, upload and review, password change, session expiry).


### Load the bundled demo dataset
After logging in as `admin`, open **Admin Portal → Demo lab** and click **Load synthetic demo dataset** (demo mode only). The synthetic world is then available as `CASE-2026-101` and the other demo cases. It is isolated from fresh FIR workspaces. The loader is idempotent, so clicking it again will not duplicate the dataset.

The login screen no longer displays any credentials.

### Theme
Use the **Theme** button in the top bar to switch between dark and light. The choice is remembered in the browser.
