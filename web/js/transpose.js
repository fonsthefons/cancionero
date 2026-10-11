// Transpose the chords of one song up or down by semitones.

const NOTES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const NOTES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
const NOTE_RE = /[A-G][#b]?/g; // chord suffixes (m, maj7, sus4...) are lowercase

function transposeNote(note, shift) {
    const scale = note.includes("b") ? NOTES_FLAT : NOTES_SHARP;
    const index = scale.indexOf(note);
    if (index === -1) return note;
    return scale[(((index + shift) % 12) + 12) % 12];
}

// Transposes the root and the bass note: D/F# +2 -> E/G#
function transposeChord(chord, shift) {
    return chord.replace(NOTE_RE, (note) => transposeNote(note, shift));
}

function setTranspose(song, shift) {
    song.dataset.transpose = shift;
    song.querySelectorAll(".chord").forEach((chord) => {
        chord.dataset.original ??= chord.textContent;
        chord.textContent = transposeChord(chord.dataset.original, shift);
    });
    song.querySelector(".transpose-value").textContent = shift > 0 ? `+${shift}` : shift;
}

// Steps through -11..+11; one more step wraps back to 0 (same key).
function stepTranspose(song, step) {
    const shift = Number(song.dataset.transpose || 0) + step;
    setTranspose(song, Math.abs(shift) === 12 ? 0 : shift);
}

onAction("transpose-up", (button, song) => stepTranspose(song, +1));
onAction("transpose-down", (button, song) => stepTranspose(song, -1));
