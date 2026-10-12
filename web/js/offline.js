// Offline home-screen app: on the hosted site, register sw.js so the book is
// saved and opens without internet. Skipped when index.html is opened as a file.
//
// The first visit also shows a small tip on adding the book to the home screen
// (not inside the home-screen app itself, and not when opened as a file).

if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol)) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("sw.js").catch(() => {});
    });
}

const installTip = document.querySelector(".install-tip");
const runningAsApp = matchMedia("(display-mode: standalone)").matches
    || navigator.standalone === true; // iOS
if (/^https?:$/.test(location.protocol) && !runningAsApp && !prefs.get("installTipShown")) {
    installTip.hidden = false;
    prefs.set("installTipShown", "1"); // only the first time on this browser
}

onAction("close-install-tip", () => { installTip.hidden = true; });
