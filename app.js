// Shared helpers for the live poll engine.
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-database.js";
import { firebaseConfig } from "./firebase-config.js";

export const configured = firebaseConfig.apiKey !== "PASTE_ME";
export const db = configured ? getDatabase(initializeApp(firebaseConfig)) : null;

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
