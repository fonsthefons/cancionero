// -----------------------------
// -----------------------------
// SHOW/HIDE CHORDS LOGIC
// -----------------------------
// -----------------------------
document.addEventListener("click", function (e) {

    // -------------------------
    // GLOBAL TOGGLE
    // -------------------------
    if (e.target.id === "toggle-all-chords") {

        document.body.classList.toggle("hide-all-chords");

        const hidden = document.body.classList.contains("hide-all-chords");
        e.target.textContent = hidden ? "Show all chords" : "Hide all chords";

        // ONLY clear overrides (cheap, no heavy DOM work)
        document.querySelectorAll(".song.force-hide-chords, .song.force-show-chords")
            .forEach(song => {
                song.classList.remove("force-hide-chords", "force-show-chords");

                const btn = song.querySelector(".toggle-chords");
                if (btn) {
                    btn.textContent = hidden ? "Show chords" : "Hide chords";
                }
            });

        return;
    }

    // -------------------------
    // LOCAL TOGGLE
    // -------------------------
    const btn = e.target.closest(".toggle-chords");
    if (!btn) return;

    const song = btn.closest(".song");
    if (!song) return;

    const globalHidden = document.body.classList.contains("hide-all-chords");

    const forceHide = song.classList.contains("force-hide-chords");
    const forceShow = song.classList.contains("force-show-chords");

    let currentlyHidden;

    if (forceHide) {
        currentlyHidden = true;
    } else if (forceShow) {
        currentlyHidden = false;
    } else {
        currentlyHidden = globalHidden;
    }

    // clear previous override
    song.classList.remove("force-hide-chords", "force-show-chords");

    // apply new override (flip current state)
    if (currentlyHidden) {
        song.classList.add("force-show-chords");
    } else {
        song.classList.add("force-hide-chords");
    }

    btn.textContent = currentlyHidden ? "Hide chords" : "Show chords";

});


// -----------------------------
// -----------------------------
// TRANSPOSE LOGIC
// -----------------------------
// -----------------------------
const NOTES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const NOTES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];

function transposeNote(note, shift) {
    let scale = note.includes("b") ? NOTES_FLAT : NOTES_SHARP;
    let index = scale.indexOf(note);

    if (index === -1) return note;

    let newIndex = (index + shift) % 12;
    if (newIndex < 0) newIndex += 12;

    return scale[newIndex];
}
// -----------------------------
// TRANSPOSE CHORD
// -----------------------------
function transposeChord(chord, shift) {
    return chord.replace(
        /^([A-G](#|b)?)/,
        (match) => transposeNote(match, shift)
    );
}

// -----------------------------
// APPLY TRANSPOSE TO SONG
// -----------------------------
function applyTranspose(song) {
    const shift = parseInt(song.dataset.transpose || "0");

    song.querySelectorAll(".chord").forEach(el => {
        const original = el.dataset.original;
        if (!original) return;

        el.textContent = transposeChord(original, shift);
    });

    const label = song.querySelector(".transpose-value");
    if (label) {
        label.textContent = shift > 0 ? `+${shift}` : `${shift}`;
    }
}

// -----------------------------
// INITIALIZE ORIGINAL CHORDS
// -----------------------------
function initChords(song) {
    song.querySelectorAll(".chord").forEach(el => {
        if (!el.dataset.original) {
            el.dataset.original = el.textContent.trim();
        }
    });

    if (!song.dataset.transpose) {
        song.dataset.transpose = "0";
    }
}

// -----------------------------
// EVENT HANDLING
// -----------------------------
document.addEventListener("click", function (e) {

    const song = e.target.closest(".song");
    if (!song) return;

    // INIT ON FIRST USE
    initChords(song);

    // -------------------------
    // TRANSPOSE UP
    // -------------------------
    if (e.target.closest(".transpose-up")) {
        song.dataset.transpose = parseInt(song.dataset.transpose) + 1;
        applyTranspose(song);
        return;
    }

    // -------------------------
    // TRANSPOSE DOWN
    // -------------------------
    if (e.target.closest(".transpose-down")) {
        song.dataset.transpose = parseInt(song.dataset.transpose) - 1;
        applyTranspose(song);
        return;
    }

});

// -----------------------------
// -----------------------------
// COLUMN TOGGLE LOGIC
// -----------------------------
// -----------------------------
document.addEventListener("click", function (e) {
    const colBtn = e.target.closest(".toggle-columns");
    if (colBtn) {
        console.log(`HIT COLUMN BUTTON`);
        const song = colBtn.closest(".song");
        if (!song) return;

        song.classList.toggle("two-columns");

        const isTwo = song.classList.contains("two-columns");
        colBtn.textContent = isTwo ? "1 column" : "2 columns";

        return;
    }
});


// -----------------------------
// -----------------------------
// Search Logic
// -----------------------------
// -----------------------------
function normalize(text) {
    return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}


function searchSongs(query) {

    const q = normalize(query.trim());

    if (!q) {
        return [];
    }

    return SONG_INDEX.filter(song => {

        const searchable =
            normalize(
                song.title +
                " " +
                song.author +
                " " +
                song.text
            );

        return searchable.includes(q);
    });
}



function showSearchResults(results) {

    const container =
        document.getElementById("search-results");

    container.innerHTML = "";


    results.slice(0, 50).forEach(song => {

        const link =
            document.createElement("a");

        link.href =
            "#" + song.id;


        link.textContent =
            song.title +
            (song.author
                ? " — " + song.author
                : "");


        link.className =
            "search-result";


        container.appendChild(link);

        container.appendChild(
            document.createElement("br")
        );
    });
}



document.addEventListener(
    "DOMContentLoaded",
    () => {

        const box =
            document.getElementById("search-box");


        box.addEventListener(
            "input",
            () => {

                const results =
                    searchSongs(box.value);

                showSearchResults(results);
            }
        );
    }
);


document.addEventListener("click", function (e) {

    // -------------------------
    // SIDEBAR TOGGLE
    // -------------------------
    if (e.target.id === "toc-toggle") {

        const sidebar = document.getElementById("toc-sidebar");
        const btn = e.target;

        sidebar.classList.toggle("open");

        btn.textContent = sidebar.classList.contains("open") ? "◀" : "➤";

        return;
    }

    // -------------------------
    // CLOSE SIDEBAR ON LINK CLICK
    // -------------------------
    if (e.target.closest("#toc-sidebar a")) {

        const sidebar = document.getElementById("toc-sidebar");
        const btn = document.getElementById("toc-toggle");

        sidebar.classList.remove("open");

        if (btn) btn.textContent = "➤";

        return;
    }

});