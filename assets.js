(function () {

    function isGlobalHidden() {
        return document.body.classList.contains("no-chords-global");
    }

    function toggleSong(song, button) {
        song.classList.toggle("no-chords");

        const localHidden = song.classList.contains("no-chords");

        button.textContent = localHidden ? "Show chords" : "Hide chords";
    }

    function toggleGlobal(btn) {
        document.body.classList.toggle("no-chords-global");

        const hidden = isGlobalHidden();
        btn.textContent = hidden ? "Show chords" : "Hide chords";
    }

    // 🔥 CRITICAL: event delegation (iOS-safe)
    document.addEventListener("click", function (e) {

        const songBtn = e.target.closest(".toggle-chords");
        if (songBtn) {
            const song = songBtn.closest(".song");
            if (!song) return;

            toggleSong(song, songBtn);
            return;
        }

        if (e.target && e.target.id === "toggle-all-chords") {
            toggleGlobal(e.target);
        }

    });

})();