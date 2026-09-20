#!/usr/bin/env python3
"""Create a poll in the live poll engine — the agent-facing creation path.

Usage:
  python3 newpoll.py text      <id> "Question?"
  python3 newpoll.py wordcloud <id> "Question?"
  python3 newpoll.py mc        <id> "Question?" "Option A" "Option B" [more options...]
  python3 newpoll.py number    <id> "Question?" [unit] [min] [max] [binWidth]

number polls show a live histogram of the guesses on the display, with n /
mean / median. Give min+max+binWidth to fix the axis (comparable across
rounds of a multi-round guessing game); omit them to auto-bin from the data.

The <id> becomes part of the URL. Use a short slug, e.g. pls152-week3.
Prints the display + phone URLs when done.

Reads the database URL straight from firebase-config.js, so it always targets
whatever project that file points at. No extra config.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

PAGES_BASE = "https://greymonroe.github.io/live-poll-test/"


def database_url() -> str:
    cfg = (Path(__file__).parent / "firebase-config.js").read_text()
    m = re.search(r'databaseURL:\s*"([^"]+)"', cfg)
    if not m or "PASTE_ME" in m.group(1):
        sys.exit("databaseURL not set in firebase-config.js")
    return m.group(1).rstrip("/")


def put(url: str, data: dict) -> None:
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PUT",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            if r.status not in (200, 204):
                sys.exit(f"Firebase write failed: HTTP {r.status}")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit("Firebase refused the write (permission denied). Poll ids are "
                     "create-only under the security rules — that id is already taken, "
                     "or the rules aren't published yet. See SECURITY.md.")
        sys.exit(f"Firebase write failed: HTTP {e.code} {e.reason}")


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 3:
        sys.exit(__doc__)
    ptype, pid, question, *options = args
    if ptype not in ("text", "mc", "wordcloud", "number"):
        sys.exit('type must be "text", "wordcloud", "mc", or "number"')
    pid = re.sub(r"[^a-z0-9]+", "-", pid.lower()).strip("-")
    if not pid:
        sys.exit("invalid id")

    cfg = {"type": ptype, "question": question, "created": 0}
    if ptype == "mc":
        if len(options) < 2:
            sys.exit("multiple choice needs at least 2 options")
        cfg["options"] = options
    elif ptype == "number":
        # settings ride in the "options" slot (the only free child the
        # database rules allow on config)
        settings = {}
        if options:
            settings["unit"] = options[0]
        for key, val in zip(("min", "max", "binWidth"), options[1:4]):
            try:
                settings[key] = float(val)
            except ValueError:
                sys.exit(f"{key} must be a number, got {val!r}")
        if "min" in settings and "max" in settings and settings["max"] <= settings["min"]:
            sys.exit("max must be greater than min")
        if settings:
            cfg["options"] = settings

    db = database_url()
    # Refuse to clobber an existing poll's config silently
    try:
        with urllib.request.urlopen(f"{db}/polls/{pid}/config.json") as r:
            if json.load(r) is not None:
                sys.exit(f'poll id "{pid}" already exists — pick another or delete it first')
    except urllib.error.URLError:
        pass

    # created timestamp: use a server-ordered counter via the existing poll count
    put(f"{db}/polls/{pid}/config.json", cfg)
    print(f'Created {ptype} poll "{pid}": {question}')
    print(f"  Display (screen): {PAGES_BASE}display.html?poll={pid}")
    print(f"  Phone (QR target): {PAGES_BASE}submit.html?poll={pid}")
    print(f"  All polls:        {PAGES_BASE}")


if __name__ == "__main__":
    main()
