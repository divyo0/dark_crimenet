"""Create or reset the accounts listed in CREDENTIALS.txt (the way back in if you forget the admin or a password).

    python scripts/apply_credentials.py               # create missing accounts AND reset the listed passwords
    python scripts/apply_credentials.py --if-missing  # only create accounts that do not exist yet (changes nothing else)

Reads the "ACCOUNT TABLE" lines of CREDENTIALS.txt:   Officer ID | Password | Role
Resetting also switches two-step sign-in off for those accounts, re-activates them and signs out their sessions.
Runs on the machine that hosts the database, so it needs no login. Officer IDs are matched case-insensitively.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi import HTTPException  # noqa: E402
from sqlalchemy import func, text  # noqa: E402

from backend.app.db.database import Base, SessionLocal, engine, ensure_schema_columns  # noqa: E402
from backend.app.models.models import User  # noqa: E402
from security.auth import _hash, bump_token_version  # noqa: E402
from security.passwords import validate_password  # noqa: E402
from security.rbac import ROLES  # noqa: E402

ID_RE = re.compile(r"[A-Za-z0-9._@+-]{3,100}")


def read_table(path: Path):
    rows, errors = [], []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3 or not ID_RE.fullmatch(parts[0]) or parts[0].lower() == "officer id":
            continue
        uid, pw, role = parts[0], parts[1], parts[2].lower()
        if role not in ROLES:
            errors.append(f"line {n}: unknown role '{role}' (use: {', '.join(ROLES)})"); continue
        rows.append((uid, pw, role))
    return rows, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(ROOT / "CREDENTIALS.txt"))
    ap.add_argument("--if-missing", action="store_true", help="only create accounts that do not exist; never change existing ones")
    args = ap.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"{path} not found."); return 1
    rows, errors = read_table(path)
    for e in errors: print("  ! " + e)
    if not rows:
        print("No accounts found in the ACCOUNT TABLE of CREDENTIALS.txt."); return 1
    Base.metadata.create_all(bind=engine); ensure_schema_columns()
    bad = 0
    with SessionLocal() as db:
        for uid, pw, role in rows:
            u = db.query(User).filter(func.lower(User.username) == uid.lower()).first()
            if u is not None and args.if_missing:
                continue
            try:
                validate_password(pw, uid)
            except HTTPException as exc:
                print(f"  ! {uid}: {exc.detail}"); bad += 1; continue
            if u is None:
                u = User(username=uid, password_hash=_hash(pw), role=role, active=True); db.add(u); db.flush()
                print(f"  + created  {uid}  ({role})")
            else:
                u.password_hash = _hash(pw); u.role = role; u.active = True
                u.mfa_enabled = False; u.mfa_secret_enc = ""; u.mfa_last_step = 0; u.mfa_enrolled_at = None
                try:
                    db.execute(text("DELETE FROM mfa_recovery_codes WHERE user_id = :i"), {"i": u.id})
                except Exception:
                    pass
                bump_token_version(u)
                print(f"  ~ reset    {uid}  ({role})")
        db.commit()
    print("Done." if not bad else f"Done with {bad} problem(s) - fix the lines above and run again.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
