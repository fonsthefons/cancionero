// Show/hide chords and 1/2 lyric columns, per song or for the whole book.

const chordsSetting = songSetting("chords", ["show", "hide"]);
const columnsSetting = songSetting("columns", ["1", "2"]);

onAction("toggle-chords", (button, song) => chordsSetting.toggleSong(song));
onAction("toggle-columns", (button, song) => columnsSetting.toggleSong(song));

onAction("toggle-all-chords", (button) => {
    const value = chordsSetting.toggleGlobal();
    button.textContent = value === "hide" ? "Show all chords" : "Hide all chords";
});

onAction("toggle-all-columns", (button) => {
    const value = columnsSetting.toggleGlobal();
    button.textContent = value === "2" ? "1 column" : "2 columns";
});
