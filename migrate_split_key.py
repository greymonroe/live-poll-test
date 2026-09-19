#!/usr/bin/env python3
"""One-time migration: move answer keys out of the public quiz config.

Quizzes created before the config/key split store the correct answer inside
quizzes/<id>/config, which is public-readable. This moves each one to
quizzes/<id>/key (host-read-only) and strips it from the config.

  python3 migrate_split_key.py --dry-run     # show what would change
  python3 migrate_split_key.py --backup out.json

RUN THIS BEFORE PUBLISHING database.rules.json. The new rules make config and
key create-only, so the rewrite has to happen while the database is still open.
If you've already published, paste the old open rules back for a minute, run
this, then re-publish.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def database_url() -> str:
    import re
    cfg = (Path(__file__).parent / "firebase-config.js").read_text()
    m = re.search(r'databaseURL:\s*"([^"]+)"', cfg)
    if not m or "PASTE_ME" in m.group(1):
        sys.exit("databaseURL not set in firebase-config.js")
    return m.group(1).rstrip("/")


def get(url):
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def put(url, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PUT",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            if r.status not in (200, 204):
                sys.exit(f"write failed: HTTP {r.status}")
    except urllib.error.HTTPError as e:
        sys.exit(f"write failed: HTTP {e.code} {e.reason} — are the locked-down "
                 "rules already published? See the docstring.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backup", metavar="PATH", help="write current quizzes/ to a file first")
    args = ap.parse_args()

    db = database_url()
    quizzes = get(f"{db}/quizzes.json") or {}

    if args.backup:
        Path(args.backup).write_text(json.dumps(quizzes, indent=2, sort_keys=True))
        print(f"backed up {len(quizzes)} quizzes -> {args.backup}")

    for qid, q in sorted(quizzes.items()):
        cfg = (q or {}).get("config")
        if not cfg or not isinstance(cfg.get("questions"), list):
            print(f"{qid}: no config, skipped")
            continue
        questions = cfg["questions"]
        if not any("correct" in x for x in questions):
            print(f"{qid}: already split, skipped")
            continue
        key = [x.get("correct", 0) for x in questions]
        clean = [{k: v for k, v in x.items() if k != "correct"} for x in questions]
        print(f"{qid}: {len(key)} questions -> key {key}")
        if args.dry_run:
            continue
        put(f"{db}/quizzes/{qid}/key.json", key)
        put(f"{db}/quizzes/{qid}/config/questions.json", clean)

    if args.dry_run:
        print("\n(dry run — nothing written)")


if __name__ == "__main__":
    main()
