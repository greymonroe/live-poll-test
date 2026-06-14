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
  apiKey:            "AIzaSyBhcWFAF48VN-D8h2lBnVi5TdUWmMxBc4LE",
  authDomain:        "live-poll-8088d.firebaseapp.com",
  databaseURL:       "https://live-poll-8088d-default-rtdb.firebaseio.com",
  projectId:         "live-poll-8088d",
  storageBucket:     "live-poll-8088d.firebasestorage.app",
  messagingSenderId: "1037141242834",
  appId:             "1:1037141242834:web:5a1f81d86c5ec0a6a8e0b"
};
