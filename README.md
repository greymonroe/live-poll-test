# live-poll-test

A free, self-hosted live audience-response tool — an owned alternative to Slido/Mentimeter.
Static pages on GitHub Pages + one Firebase Realtime Database. No build step, no server.

**One database holds many polls.** You set Firebase up once, then create as many polls as
you want from the control panel — each gets its own QR code. The Firebase setup is NOT
per-poll.

## Pages
- `index.html` — **control panel**: create polls, list them, get each one's display/phone links + QR.
- `display.html?poll=ID` — **big screen** for one poll: QR + live results (text wall or bar chart).
- `submit.html?poll=ID` — **phone view**: text box (text poll) or tappable options (multiple choice).
- `app.js` — shared helpers + Firebase init.
- `firebase-config.js` — paste your Firebase config here once (instructions inside).

## Data model (Firebase Realtime Database)
```
polls/
  <pollId>/
    config/      { type: "text"|"mc", question, options?[], created }
    responses/   push-list of { text } (text) or { choice: <optionIndex> } (mc)
```
To add a poll type later (word cloud, rating, quiz…), add a `type` and render it in
display.html / submit.html. The database stays the same — poll "type" is just rendering.

## Use it
1. Open `index.html` (the control panel).
2. Pick a type, type a question (+ options for multiple choice), Create.
3. Click **Open display** on the screen; people scan the QR or tap **Phone view**.

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
- Possible next types: word cloud, 1–5 rating, ranking, quiz-with-leaderboard, Q&A + upvotes.
- Moderation (approve-before-show) toggle.
