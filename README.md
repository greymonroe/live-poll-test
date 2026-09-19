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
- `app.js` — shared helpers + Firebase init + sign-in.
- `firebase-config.js` — paste your Firebase config here once (instructions inside).
- `database.rules.json` — the security rules. Source of truth; paste into the console.
- `SECURITY.md` — **one-time setup + what the rules guarantee. Read this first.**

## Setup
Three console steps, once: enable **Anonymous** and **Google** sign-in, publish
`database.rules.json`, then click **Sign in as host** on `index.html` to claim host.
Walkthrough in [SECURITY.md](SECURITY.md). Nothing works until they're done.

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
admin/hostUid          the host's Google uid; claim-once, then immutable from the client
polls/<id>/config      { type: "text"|"mc"|"wordcloud", question, options?[], created }
polls/<id>/responses   push-list of { text } or { choice } + server ts — no identity
quizzes/<id>/config    { title, questions:[{q,options[],image?}], created }   public
quizzes/<id>/key       [correctIndex, …]                                      HOST ONLY
quizzes/<id>/state     { phase, q, startedAt, correct?, count?, results? }    host-written
quizzes/<id>/players/<uid>      { name, score, rank, awarded{} }   name self-written, rest host
quizzes/<id>/answers/<q>/<uid>  { choice, ts }                     write-once, server ts
```
`<uid>` is an anonymous Firebase uid — per-browser, not tied to any account.
The answer key is a separate path so player phones never download it; the host
publishes the correct index into `state.correct` at reveal time.

Player rosters are erased when a game finishes. See [SECURITY.md](SECURITY.md).

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

## Scope
**Ungraded, in-class, for fun.** Nicknames only, erased at the end of every game.
Anything that counts toward a grade belongs in Canvas or the campus clicker
system, not here — the reasoning is in [SECURITY.md](SECURITY.md).

## TODO
- Possible next poll types: 1–5 rating, ranking, Q&A + upvotes.
- Moderation (approve-before-show) toggle for text/word-cloud polls.
- Poll voting is still one-per-tap with a soft localStorage guard — fine for
  "add as many as you like" prompts, but it isn't a one-vote-per-person ballot.
