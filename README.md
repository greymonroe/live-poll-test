# live-poll-test

A dead-simple, self-hosted, free live audience-response wall. The Slido replacement
feasibility test: **QR on the screen → student types text on their phone → it pops up
live on the screen.** Static page on GitHub Pages + Firebase Realtime Database as the
only backend. No build step, no server.

## Files
- `index.html` — **display view** (big screen): shows the QR code + the live wall.
- `submit.html` — **participant view** (phone): text box + Send.
- `firebase-config.js` — paste your Firebase project config here once (instructions inside).

## One-time setup (~5 min)
1. Create a Firebase project + a **Realtime Database** in *Test mode*, and register a
   Web app — full click-by-click steps are at the top of `firebase-config.js`.
2. Paste the config values into `firebase-config.js`.
3. Open `index.html` (locally or on GitHub Pages). Scan the QR with your phone, type
   something, hit Send — it appears on the screen.

## Run locally first
```
cd ~/repos/live-poll-test
python3 -m http.server 8000
```
Then open http://localhost:8000 on your laptop. To test the phone round-trip on the
same wifi, open http://<your-laptop-IP>:8000/submit.html on your phone.
(`file://` won't work — ES module imports need to be served over http.)

## Deploy to GitHub Pages
Pushed to `greymonroe/live-poll-test`, Pages serves it at
https://greymonroe.github.io/live-poll-test/

## Notes / current scope
- **Open feed, no moderation** — anything submitted shows instantly. Fine for a
  feasibility test; add approve-before-show before using with a rowdy class.
- Test-mode database rules are **open to the public**. That's deliberate for now.
  Don't put anything sensitive in it; lock down the rules before real classroom use.
- The QR/join link is computed from the display page's own URL, so it works both
  locally and on Pages with no editing.
