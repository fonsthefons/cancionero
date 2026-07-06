document.addEventListener("DOMContentLoaded", function () {

    function songHasChords(song) {
        return !song.classList.contains("no-chords");
    }

    function updateSongButton(button, song) {
        button.textContent = songHasChords(song)
            ? "Hide chords"
            : "Show chords";
    }

    document.querySelectorAll(".toggle-chords").forEach(button => {
        button.addEventListener("click", () => {
            const song = button.closest(".song");
            song.classList.toggle("no-chords");
            updateSongButton(button, song);
        });
    });

    const globalBtn = document.getElementById("toggle-all-chords");

    if (globalBtn) {
        globalBtn.addEventListener("click", () => {
            document.body.classList.toggle("no-chords-global");

            const hidden = document.body.classList.contains("no-chords-global");
            globalBtn.textContent = hidden ? "Show chords" : "Hide chords";
        });
    }

});