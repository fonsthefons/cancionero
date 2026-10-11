// Core helpers shared by every feature script. Loaded first.
//
// Buttons declare what they do with `data-action="name"`; features register
// a handler for that name with `onAction`. A single click listener dispatches.

const actionHandlers = {};

// handler(button, song) — `song` is the enclosing .song element, or null.
function onAction(name, handler) {
    actionHandlers[name] = handler;
}

document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const handler = actionHandlers[button.dataset.action];
    if (handler) handler(button, button.closest(".song"));
});

// Set the text of every button with this data-action (e.g. global toggles).
function setActionLabel(action, text) {
    document.querySelectorAll(`[data-action="${action}"]`)
        .forEach((button) => { button.textContent = text; });
}

// Preferences remembered on this device. Storage can be unavailable
// (private mode, blocked site data), so every access is guarded.
const prefs = {
    get(key, fallback) {
        try {
            return localStorage.getItem(`cancionero.${key}`) ?? fallback;
        } catch {
            return fallback;
        }
    },
    set(key, value) {
        try {
            localStorage.setItem(`cancionero.${key}`, value);
        } catch {
            // Not remembered; the setting still applies for this visit.
        }
    },
};

// A display setting with a book-wide value (on <body data-NAME>) that a single
// song can override (on <article class="song" data-NAME>). CSS reads both.
// The book-wide value is remembered on this device.
//   values: [default, alternative], e.g. ["show", "hide"]
function songSetting(name, values, onGlobalChange) {
    const other = (value) => (value === values[0] ? values[1] : values[0]);
    const globalValue = () => document.body.dataset[name];

    function setGlobal(value) {
        document.body.dataset[name] = value;
        prefs.set(name, value);
        onGlobalChange(value);
    }

    const saved = prefs.get(name, values[0]);
    setGlobal(values.includes(saved) ? saved : values[0]);

    return {
        // Flip one song; drop the override when it matches the book-wide value.
        toggleSong(song) {
            const next = other(song.dataset[name] || globalValue());
            if (next === globalValue()) delete song.dataset[name];
            else song.dataset[name] = next;
        },
        // Flip the whole book and clear all per-song overrides.
        toggleGlobal() {
            setGlobal(other(globalValue()));
            document.querySelectorAll(`.song[data-${name}]`)
                .forEach((song) => delete song.dataset[name]);
        },
    };
}

// Lowercase and strip accents so "Señor" matches "senor".
function normalizeText(text) {
    return text.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
}
