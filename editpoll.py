#!/usr/bin/env python3
"""Edit or delete an existing poll or quiz — the agent-facing edit path.

The security rules make poll/quiz configs create-only from the browser (so a
student can't rewrite your question mid-class). This helper uses your own Google
Cloud login (`gcloud auth print-access-token`, the same credential used to
publish the rules), which has admin access and bypasses the rules.

Usage:
  python3 editpoll.py show     <poll-id>
  python3 editpoll.py question <poll-id> "New question text"
  python3 editpoll.py options  <poll-id> "Option A" "Option B" [more...]      (mc)
  python3 editpoll.py range    <poll-id> <unit> <min> <max> <binWidth>       (number)
  python3 editpoll.py multi    <poll-id> on|off                            (number: many entries per person)
  python3 editpoll.py clear    <poll-id>          # delete responses, keep the poll
  python3 editpoll.py delete   <poll-id>          # delete the poll entirely

  python3 editpoll.py quiz        <quiz-id> quiz.json   # replace questions + answer key
  python3 editpoll.py deletequiz  <quiz-id>

Editing a poll's options/question does not touch its responses; clear them if the
old answers no longer make sense. Replacing a quiz also resets its game state.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request

from newpoll import database_url
from newquiz import load_and_validate


def token() -> str:
    try:
        return subprocess.run(["gcloud", "auth", "print-access-token"], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f"gcloud login needed (run `gcloud auth login`): {e}")


def call(method: str, path: str, data=None):
    url = f"{database_url()}/{path}.json"
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Firebase {method} {path} failed: HTTP {e.code} {e.read().decode()[:200]}")


def poll_config(pid: str) -> dict:
    cfg = call("GET", f"polls/{pid}/config")
    if cfg is None:
        sys.exit(f'no poll "{pid}"')
    return cfg


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, pid, rest = sys.argv[1], sys.argv[2], sys.argv[3:]

    if cmd == "show":
        print(json.dumps(poll_config(pid), indent=2, ensure_ascii=False))
    elif cmd == "question":
        poll_config(pid)
        if len(rest) != 1 or not rest[0].strip() or len(rest[0]) > 500:
            sys.exit("give the new question as one quoted string (<= 500 chars)")
        call("PUT", f"polls/{pid}/config/question", rest[0])
        print(f'Updated question of "{pid}"')
    elif cmd == "options":
        if poll_config(pid).get("type") != "mc":
            sys.exit("options only apply to multiple-choice polls")
        if len(rest) < 2:
            sys.exit("give at least 2 options")
        call("PUT", f"polls/{pid}/config/options", rest)
        print(f'Updated options of "{pid}" (consider `clear` — old votes refer to old options)')
    elif cmd == "range":
        cfg = poll_config(pid)
        if cfg.get("type") != "number":
            sys.exit("range only applies to number polls")
        if len(rest) != 4:
            sys.exit("usage: range <poll-id> <unit> <min> <max> <binWidth>")
        unit, lo, hi, bw = rest
        opts = {"unit": unit, "min": float(lo), "max": float(hi), "binWidth": float(bw)}
        if (cfg.get("options") or {}).get("multi"):
            opts["multi"] = True
        call("PUT", f"polls/{pid}/config/options", opts)
        print(f'Updated range of "{pid}"')
    elif cmd == "multi":
        if poll_config(pid).get("type") != "number":
            sys.exit("multi only applies to number polls")
        if rest not in (["on"], ["off"]):
            sys.exit("usage: multi <poll-id> on|off")
        call("PUT", f"polls/{pid}/config/options/multi", rest[0] == "on")
        print(f'Multiple entries per person {rest[0]} for "{pid}"')
    elif cmd == "clear":
        poll_config(pid)
        call("DELETE", f"polls/{pid}/responses")
        print(f'Cleared responses of "{pid}"')
    elif cmd == "delete":
        poll_config(pid)
        call("DELETE", f"polls/{pid}")
        print(f'Deleted poll "{pid}"')
    elif cmd == "quiz":
        if len(rest) != 1:
            sys.exit("usage: quiz <quiz-id> quiz.json")
        if call("GET", f"quizzes/{pid}/config") is None:
            sys.exit(f'no quiz "{pid}" (create it with newquiz.py)')
        q = load_and_validate(rest[0])
        call("PUT", f"quizzes/{pid}/config",
             {"title": q["title"] or pid, "questions": q["questions"], "created": 0})
        call("PUT", f"quizzes/{pid}/key", q["key"])
        for sub in ("players", "answers"):
            call("DELETE", f"quizzes/{pid}/{sub}")
        call("PUT", f"quizzes/{pid}/state", {"phase": "lobby", "q": 0, "startedAt": 0})
        print(f'Replaced quiz "{pid}" ({len(q["questions"])} questions); game reset')
    elif cmd == "deletequiz":
        call("DELETE", f"quizzes/{pid}")
        print(f'Deleted quiz "{pid}"')
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
