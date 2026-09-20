// Shared helpers for the live poll engine.
//
// Every page signs in before touching the database. Students get an anonymous
// Firebase session (invisible to them — no prompt, no credential); the host
// signs in with Google once per browser. The database rules key everything off
// those identities, so "host only" actually means something.
//
// See SECURITY.md for the one-time Firebase console setup.
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getDatabase, ref, get, set }
  from "https://www.gstatic.com/firebasejs/10.12.2/firebase-database.js";
import { getAuth, onAuthStateChanged, signInAnonymously, signInWithPopup, signOut,
         GoogleAuthProvider }
  from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { firebaseConfig } from "./firebase-config.js";

export const configured = firebaseConfig.apiKey !== "PASTE_ME";
const app = configured ? initializeApp(firebaseConfig) : null;
export const db = configured ? getDatabase(app) : null;
export const auth = configured ? getAuth(app) : null;

// ---- auth ----------------------------------------------------------------

// Resolves to the signed-in user, or null if sign-in failed (almost always
// "Anonymous provider not enabled in the Firebase console").
export const ready = configured
  ? new Promise((resolve) => {
      let settled = false;
      const done = (u) => { if (!settled) { settled = true; resolve(u); } };
      onAuthStateChanged(auth, (user) => {
        if (user) return done(user);
        // No session yet: take an anonymous one. onAuthStateChanged fires again.
        signInAnonymously(auth).catch((e) => { console.error(e); done(null); });
      });
    })
  : Promise.resolve(null);

// Await this at the top of every page. Returns the signed-in user, or a
// guest sentinel when Firebase Auth isn't provisioned yet (Authentication →
// Get started + enable Anonymous, per SECURITY.md). Guest mode keeps polls
// working while the database rules are still open; once the locked rules are
// published, writes from a guest session fail loudly at the write site, and
// by then auth must be provisioned anyway (it's a prerequisite of the rules).
export async function requireAuth() {
  if (!configured) { notConfigured(); return null; }
  const user = await ready;
  if (!user) {
    console.warn("Firebase sign-in unavailable — continuing without auth (guest mode).");
    return { uid: null, guest: true };
  }
  return user;
}

// The host's uid lives at admin/hostUid. It is claimable exactly once (by a
// Google-signed-in user) and immutable from the client after that.
export async function hostUid() {
  const s = await get(ref(db, "admin/hostUid"));
  return s.exists() ? s.val() : null;
}

export async function amHost() {
  const u = auth && auth.currentUser;
  if (!u) return false;
  return (await hostUid()) === u.uid;
}

// Google popup, then claim admin/hostUid if nobody has yet.
export async function signInAsHost() {
  await signInWithPopup(auth, new GoogleAuthProvider());
  const u = auth.currentUser;
  const existing = await hostUid();
  if (existing === null) await set(ref(db, "admin/hostUid"), u.uid);
  return (await hostUid()) === u.uid;
}

export async function signOutHost() { await signOut(auth); location.reload(); }

// Small "Host mode" / "Sign in as host" widget. Returns true if host.
export async function renderHostBar(el) {
  const host = await amHost();
  el.innerHTML = host
    ? '<span class="hb ok">Host mode</span> <button class="hb-btn" id="hb-out">Sign out</button>'
    : '<button class="hb-btn" id="hb-in">Sign in as host</button>';
  const inBtn = el.querySelector("#hb-in");
  const outBtn = el.querySelector("#hb-out");
  if (inBtn) inBtn.onclick = async () => {
    inBtn.disabled = true;
    try { await signInAsHost(); location.reload(); }
    catch (e) { inBtn.disabled = false; alert("Host sign-in failed: " + e.message); }
  };
  if (outBtn) outBtn.onclick = signOutHost;
  return host;
}

// ---- misc ----------------------------------------------------------------

// ?poll=ID from the URL
export function pollId() {
  return new URLSearchParams(location.search).get("poll");
}

// Absolute URL to a page in this same deployment (works locally and on Pages)
export function pageURL(page, id) {
  const dir = location.origin + location.pathname.replace(/[^/]*$/, "");
  return dir + page + (id ? "?poll=" + encodeURIComponent(id) : "");
}

export function slugify(s) {
  return (s || "").toLowerCase().trim()
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40) || "poll";
}

// Render a QR code into an element (uses the global QRCode from the CDN script tag)
export function makeQR(el, text, size = 150) {
  el.innerHTML = "";
  new QRCode(el, { text, width: size, height: size });
}

export function notConfigured(msg = "Firebase not configured. Paste your config into firebase-config.js.") {
  document.body.innerHTML =
    '<div style="padding:32px;color:#f85149;font:18px/1.5 sans-serif">⚠️ ' + msg + "</div>";
}
