// Transpose the chords of one song up or down by semitones.
//
// Chords are aligned by hand to exact letters, so transposing must never move
// a chord to another column. When a chord name gets longer (C -> C#) or
// shorter (C# -> D), the spaces after it shrink or grow to compensate, so
// every following chord still starts at its original column.

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

// Original text between chords (spaces and separators like "(", ")", "|"),
// before any transposition.
const originalGaps = new WeakMap();

// Make a gap between chords `drift` columns shorter (drift > 0) or longer
// (drift < 0) by changing its runs of spaces, so the next chord stays put.
// Separators stay attached to their chord, and at least one space is kept
// wherever there was one. Returns [new text, drift that could not be absorbed].
function adjustGap(text, drift, isLastNode) {
    if (drift < 0) {
        const run = text.search(/ /);
        if (run === -1) return isLastNode ? [text, 0] : [text, drift];
        return [text.slice(0, run) + " ".repeat(-drift) + text.slice(run), 0];
    }
    const parts = text.split(/( +)/); // odd indexes are runs of spaces
    for (let i = 1; i < parts.length && drift > 0; i += 2) {
        const atEnd = isLastNode && i === parts.length - 2 && parts[i + 1] === "";
        const removable = parts[i].length - (atEnd ? 0 : 1);
        const removed = Math.max(0, Math.min(drift, removable));
        parts[i] = parts[i].slice(removed);
        drift -= removed;
    }
    return [parts.join(""), drift];
}

function transposeChordLine(line, shift) {
    const nodes = [...line.childNodes];
    let drift = 0; // columns the next chord would move right (or left if < 0)

    nodes.forEach((node, i) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
            node.dataset.original ??= node.textContent;
            const chord = transposeChord(node.dataset.original, shift);
            drift += chord.length - node.dataset.original.length;
            node.textContent = chord;
            return;
        }
        if (!originalGaps.has(node)) originalGaps.set(node, node.data);
        [node.data, drift] = adjustGap(originalGaps.get(node), drift, i === nodes.length - 1);
    });
}

function setTranspose(song, shift) {
    song.dataset.transpose = shift;
    song.querySelectorAll(".chord-line").forEach((line) => transposeChordLine(line, shift));
    song.querySelector(".transpose-value").textContent = shift > 0 ? `+${shift}` : shift;
    songState.set(song, "transpose", shift || null); // remembered on this device
}

// Steps through -11..+11; one more step wraps back to 0 (same key).
function stepTranspose(song, step) {
    const shift = Number(song.dataset.transpose || 0) + step;
    setTranspose(song, Math.abs(shift) === 12 ? 0 : shift);
}

onAction("transpose-up", (button, song) => stepTranspose(song, +1));
onAction("transpose-down", (button, song) => stepTranspose(song, -1));
onAction("transpose-reset", (button, song) => setTranspose(song, 0));

// Restore the transpositions saved on this device.
songState.each("transpose", (song, shift) => {
    const valid = Number.isInteger(shift) && Math.abs(shift) < 12;
    setTranspose(song, valid ? shift : 0);
});
