// Sing Session: an ordered list of songs to practise or play, shown first in
// the menu. Songs are added from the session's search box or with the
// "+ Session" button on each song; reordered with ↑ ↓; removed with ✕.
// The list is remembered on this device.

const SESSION_KEY = "session";

let session = (() => {
    try {
        const saved = JSON.parse(prefs.get(SESSION_KEY, "[]"));
        if (!Array.isArray(saved)) return [];
        // Keep songs that still exist, once each.
        return [...new Set(saved)].filter((id) => document.getElementById(id)?.classList.contains("song"));
    } catch {
        return [];
    }
})();

const songTitle = (id) => document.getElementById(id).dataset.title;

function sessionButton(action, id, label, text, disabled = false) {
    const button = document.createElement("button");
    Object.assign(button.dataset, { action, song: id });
    button.setAttribute("aria-label", label);
    button.textContent = text;
    button.disabled = disabled;
    return button;
}

function renderSession() {
    const list = document.querySelector(".session-list");
    list.replaceChildren(...session.map((id, i) => {
        const item = document.createElement("li");
        const link = Object.assign(document.createElement("a"), { href: "#" + id, textContent: songTitle(id) });
        item.append(
            link,
            sessionButton("session-up", id, "Move up", "↑", i === 0),
            sessionButton("session-down", id, "Move down", "↓", i === session.length - 1),
            sessionButton("session-remove", id, "Remove from session", "✕"),
        );
        return item;
    }));

    document.querySelector(".session-count").textContent = session.length ? `(${session.length})` : "";
    document.querySelector(".session-empty").hidden = session.length > 0;
    document.querySelector(".session-clear").hidden = session.length === 0;

    document.querySelectorAll('.song [data-action="session-toggle"]').forEach((button) => {
        const inSession = session.includes(button.closest(".song").id);
        button.textContent = inSession ? "✓ In session" : "+ Session";
        button.setAttribute("aria-pressed", inSession);
    });
}

function setSession(ids) {
    session = ids;
    prefs.set(SESSION_KEY, JSON.stringify(session));
    renderSession();
}

function addToSession(id) {
    if (!session.includes(id)) setSession([...session, id]);
}

function removeFromSession(id) {
    setSession(session.filter((other) => other !== id));
}

function moveInSession(id, step) {
    const from = session.indexOf(id);
    const to = from + step;
    if (from === -1 || to < 0 || to >= session.length) return;
    const ids = [...session];
    [ids[from], ids[to]] = [ids[to], ids[from]];
    setSession(ids);
}

onAction("session-add", (button) => addToSession(button.dataset.song));
onAction("session-remove", (button) => removeFromSession(button.dataset.song));
onAction("session-up", (button) => moveInSession(button.dataset.song, -1));
onAction("session-down", (button) => moveInSession(button.dataset.song, +1));
onAction("session-toggle", (button, song) => {
    if (session.includes(song.id)) removeFromSession(song.id);
    else addToSession(song.id);
});
onAction("session-clear", () => {
    if (confirm("Clear the whole session?")) setSession([]);
});

renderSession();
