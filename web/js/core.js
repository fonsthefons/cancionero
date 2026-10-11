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

// A display setting with a book-wide value (on <body data-NAME>) that a single
// song can override (on <article class="song" data-NAME>). CSS reads both.
//   values: [default, alternative], e.g. ["show", "hide"]
function songSetting(name, values) {
    const other = (value) => (value === values[0] ? values[1] : values[0]);
    const globalValue = () => document.body.dataset[name];

    return {
        // Flip one song; drop the override when it matches the book-wide value.
        toggleSong(song) {
            const next = other(song.dataset[name] || globalValue());
            if (next === globalValue()) delete song.dataset[name];
            else song.dataset[name] = next;
        },
        // Flip the whole book and clear all per-song overrides. Returns new value.
        toggleGlobal() {
            const next = other(globalValue());
            document.body.dataset[name] = next;
            document.querySelectorAll(`.song[data-${name}]`)
                .forEach((song) => delete song.dataset[name]);
            return next;
        },
    };
}

// Lowercase and strip accents so "Señor" matches "senor".
function normalizeText(text) {
    return text.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
}
