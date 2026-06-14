#!/usr/bin/env python3
"""Create a Kahoot-style live quiz — the agent-facing creation path.

Usage:
  python3 newquiz.py <id> path/to/quiz.json

The <id> becomes part of the URL. Use a short slug, e.g. pls152-final.
Prints the host (big-screen) + player (phone) URLs when done.

Reads the database URL straight from firebase-config.js, so it always targets
whatever project that file points at. No extra config.

The quiz.json file must look like:

  {
    "title": "PLS 152 Pop Quiz",
    "questions": [
      {
        "q": "What pigment makes leaves green?",
        "options": ["Chlorophyll", "Carotene", "Anthocyanin", "Xanthophyll"],
        "correct": 0
      },
      {
        "q": "How many chromosomes does Arabidopsis have (n)?",
        "options": ["3", "5", "7", "10"],
        "correct": 1
      }
    ]
  }

Rules for the JSON:
  - "title": a string (optional; defaults to the id).
  - "questions": a non-empty list. Each question needs:
      - "q": the question text (string).
      - "options": a list of 2-4 answer strings.
      - "correct": the 0-based index of the correct option (0..len-1).
      - "image": OPTIONAL image URL shown above the answers (e.g. a bird photo for
        "What species is this?"). Any publicly reachable https URL works.
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


def put(url: str, data) -> None:
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PUT",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        if r.status not in (200, 204):
            sys.exit(f"Firebase write failed: HTTP {r.status}")


def load_and_validate(path: str) -> dict:
    try:
        raw = Path(path).read_text()
    except OSError as e:
        sys.exit(f"can't read quiz file: {e}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"quiz file is not valid JSON: {e}")
    if not isinstance(data, dict):
        sys.exit("quiz JSON must be an object with a 'questions' list")

    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        sys.exit("quiz JSON needs a non-empty 'questions' list")

    clean_qs = []
    for i, q in enumerate(questions):
        where = f"question {i + 1}"
        if not isinstance(q, dict):
            sys.exit(f"{where}: must be an object")
        text = q.get("q")
        if not isinstance(text, str) or not text.strip():
            sys.exit(f"{where}: 'q' must be a non-empty string")
        options = q.get("options")
        if not isinstance(options, list) or not (2 <= len(options) <= 4):
            sys.exit(f"{where}: 'options' must be a list of 2-4 strings")
        if not all(isinstance(o, str) and o.strip() for o in options):
            sys.exit(f"{where}: every option must be a non-empty string")
        correct = q.get("correct")
        if not isinstance(correct, int) or isinstance(correct, bool) \
                or not (0 <= correct < len(options)):
            sys.exit(f"{where}: 'correct' must be an index 0..{len(options) - 1}")
        cleaned = {"q": text, "options": options, "correct": correct}
        image = q.get("image")
        if image is not None:
            if not isinstance(image, str) or not image.strip():
                sys.exit(f"{where}: 'image' must be a URL string")
            cleaned["image"] = image.strip()
        clean_qs.append(cleaned)

    title = data.get("title")
    if title is not None and not isinstance(title, str):
        sys.exit("'title' must be a string")
    return {"title": title, "questions": clean_qs}


def main() -> None:
    args = sys.argv[1:]
    if len(args) != 2:
        sys.exit(__doc__)
    qid, path = args
    qid = re.sub(r"[^a-z0-9]+", "-", qid.lower()).strip("-")
    if not qid:
        sys.exit("invalid id")

    quiz = load_and_validate(path)
    title = quiz["title"] or qid
    cfg = {"title": title, "questions": quiz["questions"], "created": 0}

    db = database_url()

    # Refuse to clobber an existing quiz's config.
    try:
        with urllib.request.urlopen(f"{db}/quizzes/{qid}/config.json") as r:
            if json.load(r) is not None:
                sys.exit(f'quiz id "{qid}" already exists — pick another or delete it first')
    except urllib.error.URLError:
        pass

    put(f"{db}/quizzes/{qid}/config.json", cfg)
    n = len(quiz["questions"])
    print(f'Created quiz "{qid}": {title} ({n} question{"s" if n != 1 else ""})')
    print(f"  Host (big screen): {PAGES_BASE}quiz.html?quiz={qid}")
    print(f"  Player (QR target): {PAGES_BASE}quiz-play.html?quiz={qid}")
    print(f"  Pages base:         {PAGES_BASE}")


if __name__ == "__main__":
    main()
