document.addEventListener("click", function (e) {

    // -------------------------
    // GLOBAL TOGGLE
    // -------------------------
    if (e.target.id === "toggle-all-chords") {

        document.body.classList.toggle("hide-all-chords");

        const hidden = document.body.classList.contains("hide-all-chords");
        e.target.textContent = hidden ? "Show all chords" : "Hide all chords";

        // ✅ RESET ALL LOCAL OVERRIDES
        document.querySelectorAll(".song").forEach(song => {
            song.classList.remove("force-hide-chords", "force-show-chords");

            const btn = song.querySelector(".toggle-chords");
            if (!btn) return;

            btn.textContent = hidden ? "Show chords" : "Hide chords";
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