# live-poll-test

A free, self-hosted live audience-response tool — an owned alternative to Slido/Mentimeter.
Static pages on GitHub Pages + one Firebase Realtime Database. No build step, no server.

**One database holds many polls.** You set Firebase up once, then create as many polls as
you want from the control panel — each gets its own QR code. The Firebase setup is NOT
per-poll.

## Pages
- `index.html` — **poll list** (read-only): open a display, grab a QR, clear results, or delete.
- `display.html?poll=ID` — **big screen** for one poll: QR + live results (text wall, bar chart, or word cloud) + a Clear button.
- `submit.html?poll=ID` — **phone view**: text box or tappable options depending on type.
- `quiz.html?quiz=ID` — **Kahoot-style quiz host** (big screen, controls the game).
- `quiz-play.html?quiz=ID` — **quiz player** (phone).
- `app.js` — shared helpers + Firebase init.
- `firebase-config.js` — paste your Firebase config here once (instructions inside).

## Creating polls/quizzes (agent workflow — there is no GUI builder)
Polls and quizzes are created by running a helper (designed to be run by a Claude Code agent):
```
python3 newpoll.py text      pls152-w3 "What's one thing you learned?"
python3 newpoll.py wordcloud pls152-w3 "One word: how's class going?"
python3 newpoll.py mc        pls152-w3 "Confidence level?" "Lost" "Shaky" "Getting it" "Nailed it"
python3 newquiz.py pls152-quiz1 quiz.json    # quiz.json format below
```
Each prints the display/host URL + the phone/QR URL.

quiz.json format:
```json
{ "title": "Plant Genetics Warm-up",
  "questions": [
    { "q": "What pigment makes leaves green?",
      "options": ["Chlorophyll","Carotene","Anthocyanin","Xanthophyll"], "correct": 0 }
  ] }
```

## Data model (Firebase Realtime Database)
```
polls/<id>/config      { type: "text"|"mc"|"wordcloud", question, options?[], created }
polls/<id>/responses   push-list of { text } or { choice: <optionIndex> }
quizzes/<id>/config    { title, questions:[{q,options[],correct}], created }
quizzes/<id>/state     { phase, q, startedAt }     (host-written)
quizzes/<id>/players/<pid>      { name, score }
quizzes/<id>/answers/<q>/<pid>  { choice, ts }
```
A poll "type" is just how display.html renders the same stored data — adding a type
(rating, ranking, Q&A…) is front-end only, no backend change.

## Limits (Firebase free "Spark" plan)
- Storage 1 GB, download 10 GB/mo — irrelevant for text/vote data (store hundreds of thousands).
- **100 simultaneous connections** — the real ceiling. Fine for a class; only bites if many
  live sessions run at the same instant totalling 100+ connected devices.
- No payment method on Spark = cannot be billed. If you ever upgrade to Blaze, lock the DB
  rules down first.

## Run locally
```
cd ~/repos/live-poll-test && python3 -m http.server 8000
```
Open http://localhost:8000 . (`file://` won't work — ES modules need http.)

## Live
https://greymonroe.github.io/live-poll-test/

## Current scope / TODO before real classroom use
- DB rules are wide open (anyone with a link can read/write). Tighten to "append-only short
  messages, no full-tree read/delete" before pointing a real class at it.
- One-vote-per-person is a soft localStorage guard only (clears if they switch devices/clear data).
- Possible next types: 1–5 rating, ranking, Q&A + upvotes.
- Moderation (approve-before-show) toggle.
