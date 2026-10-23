#!/usr/bin/env python3
"""
Import CPTS finding templates into a SysReptor instance.

Usage:
    python import.py --url http://localhost:8000 --user reptor --password YOUR_PASSWORD
    python import.py --url http://localhost:8000 --user reptor --password YOUR_PASSWORD --file templates/sql-njection-sqli.json
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests first: pip install requests")
    sys.exit(1)


def login(base_url, username, password):
    s = requests.Session()
    r = s.post(f"{base_url}/api/v1/auth/login/", json={"username": username, "password": password})
    r.raise_for_status()
    s.headers.update({
        "X-CSRFToken": s.cookies.get("csrftoken", ""),
        "Referer": base_url,
    })
    return s


def import_template(session, base_url, template_data):
    payload = {
        "translations": [{
            "language": t.get("language", "en-US"),
            "is_main": t.get("is_main", True),
            "status": t.get("status", "finished"),
            "data": t["data"],
        } for t in template_data["translations"]],
        "tags": template_data.get("tags", []),
    }
    r = session.post(f"{base_url}/api/v1/findingtemplates/", json=payload)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Import CPTS finding templates into SysReptor")
    parser.add_argument("--url", required=True, help="SysReptor base URL (e.g. http://localhost:8000)")
    parser.add_argument("--user", required=True, help="SysReptor username")
    parser.add_argument("--password", required=True, help="SysReptor password")
    parser.add_argument("--file", help="Import a single template JSON file instead of all")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be imported without doing it")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")

    if args.file:
        files = [Path(args.file)]
    else:
        templates_dir = Path(__file__).parent / "templates"
        files = sorted(templates_dir.glob("*.json"))

    if not files:
        print("No template files found.")
        sys.exit(1)

    print(f"Found {len(files)} template(s) to import.\n")

    if args.dry_run:
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            title = data["translations"][0]["data"].get("title", "Untitled")
            tags = ", ".join(data.get("tags", []))
            print(f"  [DRY RUN] {title} ({tags})")
        print(f"\nDry run complete. {len(files)} template(s) would be imported.")
        return

    print("Logging in...")
    session = login(base_url, args.user, args.password)
    print("Authenticated.\n")

    success = 0
    failed = 0
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        title = data["translations"][0]["data"].get("title", "Untitled")
        try:
            result = import_template(session, base_url, data)
            print(f"  [OK] {title}")
            success += 1
        except requests.HTTPError as e:
            print(f"  [FAIL] {title} - {e.response.status_code}: {e.response.text[:200]}")
            failed += 1

    print(f"\nDone. {success} imported, {failed} failed.")


if __name__ == "__main__":
    main()
