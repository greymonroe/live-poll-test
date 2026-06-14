// ─────────────────────────────────────────────────────────────────────────
// PASTE YOUR FIREBASE CONFIG HERE (one time).
//
// How to get it (≈5 min, uses your normal Google login):
//   1. Go to https://console.firebase.google.com  → "Create a project"
//      (name it anything, e.g. "live-poll"; you can disable Analytics).
//   2. In the project, left sidebar → "Build" → "Realtime Database"
//      → "Create Database" → pick a location → start in **Test mode**
//      (Test mode = open read/write, which is exactly what we want for now).
//   3. Project settings (gear icon, top-left) → scroll to "Your apps"
//      → click the "</>" Web icon → register an app (any nickname).
//   4. It shows you a `firebaseConfig = { ... }` object. Copy the values
//      into the object below, replacing every "PASTE_ME".
//   5. Make sure `databaseURL` is included — if it's not shown, it's
//      https://<your-project-id>-default-rtdb.firebaseio.com  (or the
//      region-specific one shown on the Realtime Database page).
//
// That's it. No server, no deploy step for the backend.
// ─────────────────────────────────────────────────────────────────────────

export const firebaseConfig = {
  apiKey:            "PASTE_ME",
  authDomain:        "PASTE_ME",
  databaseURL:       "PASTE_ME",
  projectId:         "PASTE_ME",
  storageBucket:     "PASTE_ME",
  messagingSenderId: "PASTE_ME",
  appId:             "PASTE_ME"
};
