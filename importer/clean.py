"""Tidy a song's text into the book's format.

Input is the song as a site shows it: chords on their own lines above the
lyrics. Sites that mark their chords pass them as [ch]Am[/ch] (Ultimate
Guitar's own markup); pasted text is unmarked and chord lines are detected.

The result:
- spaces instead of tabs (expanded to the column a browser shows them at),
  no invisible or look-alike characters, no trailing spaces;
- chords in letter names (LAm -> Am), each still above the same letter;
- no section labels ([Chorus], Estribillo:, ...) except the intro, written
  "Intro:" with its chords on the next line; when a song has no intro, one is
  added with the song's first chord;
- capo lines turned into the capo field; key / tuning lines dropped;
- at most one blank line in a row.
Anything worth a look is reported in `notes`.
"""

import re
import unicodedata
from dataclasses import dataclass, field

from .chords import Notation, could_be_chord, is_filler, replace_spans

TAB_STOP = 8  # browsers show a tab in a <pre> up to the next multiple of 8

# One character for one character, so no column moves.
CHAR_FIXES = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "´": "'", "`": "'",
    "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
    "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    "♯": "#", "♭": "b",
    " ": " ", " ": " ", " ": " ", " ": " ", " ": " ", "　": " ",
})
# Characters that take no column: dropped.
INVISIBLE_RE = re.compile("[​-‍⁠﻿­\x00-\x08\x0b-\x1f\x7f]")
MARK_RE = re.compile(r"\[(/?)ch\]")
WRAPPER_RE = re.compile(r"\[/?tab\]")

INTRO_WORDS = r"intro|introducci[oó]n|introdu[cç][aã]o"
LABEL_WORDS = (
    r"coro|estribillo|estrofa|verso|puente|pre-?\s?coro|pre-?\s?estribillo|final|outro|interludio"
    r"|instrumental|solo|chorus|pre-?\s?chorus|post-?\s?chorus|verse|bridge|refrain|hook|tag|ending"
    r"|coda|refr[aã]o|pr[eé]-?\s?refr[aã]o|primeira parte|segunda parte|terceira parte|parte|ponte"
)
# "[Chorus]", "[Verse 2]", "[Intro] Am F" ...
BRACKET_LABEL_RE = re.compile(r"\s*\[([^\]]+)\]\s*(.*)")
# "Estribillo:", "CORO 2", "Verse 1:", "Intro: G D", "Puente (x2)" ...
WORD_LABEL_RE = re.compile(
    rf"\s*({INTRO_WORDS}|{LABEL_WORDS})\s*\d*\s*(?:\(?[xX]\s?\d+\)?)?\s*(?::|\.|-)?\s*(.*)", re.IGNORECASE
)
INTRO_RE = re.compile(rf"(?:{INTRO_WORDS})\b", re.IGNORECASE)
CAPO_RE = re.compile(
    r"\s*(?:capo|cejilla|capotraste)\b\D{0,25}?(\d{1,2})(?!\d).*|\s*(?:sin cejilla|no capo|capo\s*:?\s*(?:no|none|-))\s*",
    re.IGNORECASE,
)
META_RE = re.compile(
    r"\s*(?:tono|tonalidad|key|tom|afinaci[oó]n|afina[cç][aã]o|tuning|ritmo|tempo|bpm)\s*:.*", re.IGNORECASE
)
CREDIT_RE = re.compile(r"\s*\(@[\w.]+\)\s*")
# Letters (any accents), digits, spaces and the punctuation songs use.
USUAL_CHAR_RE = re.compile(r"[\w\s.,;:!?¡¿'\"()\[\]{}\-/#&*+=…·%]")


@dataclass
class Cleaned:
    body: str
    capo: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class Line:
    text: str
    chords: list = field(default_factory=list)  # (start, end, name) spans on chord lines

    @property
    def is_chord_line(self):
        return bool(self.chords)


def expand_tabs(text):
    """Tabs to spaces, counting columns the way a browser shows them."""
    out = ""
    for ch in text:
        out += " " * (TAB_STOP - len(out) % TAB_STOP) if ch == "\t" else ch
    return out


def normalize_chars(text):
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    return INVISIBLE_RE.sub("", text.translate(CHAR_FIXES))


def unmark(raw):
    """'[ch]Am[/ch]  [ch]F[/ch]' -> ('Am  F', [(0, 2, 'Am'), (4, 5, 'F')])."""
    text, spans, start = "", [], None
    for i, part in enumerate(MARK_RE.split(raw)):  # text, "" or "/", text, ...
        if i % 2 == 0:
            text = expand_tabs(text + part)
        elif part == "":
            start = len(text)
        elif start is not None:
            spans.append((start, len(text), text[start:].strip()))
            start = None
    return text.rstrip(), spans


def token_spans(text):
    return [(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+", text)]


def detect_chord_line(text, ask):
    """Chord spans if a pasted line is a chord line, else []."""
    tokens = token_spans(text)
    chords = [t for t in tokens if could_be_chord(t[2])]
    if not chords or any(not could_be_chord(t[2]) and not is_filler(t[2]) for t in tokens):
        return []
    # "La la la", "Mi re..." could be lyrics: ask unless the line is clearly chords.
    words_only = all(re.fullmatch(r"(?i)do|re|mi|fa|sol|la|si", t[2]) and not t[2].isupper() for t in chords)
    if words_only and not re.search(r"\S\s{2,}\S|^\s", text) and not ask(text):
        return []
    return chords


def read_lines(text, marked, ask):
    lines = []
    for raw in normalize_chars(WRAPPER_RE.sub("", text)).split("\n"):
        if marked:
            line_text, spans = unmark(raw)
            rest = line_text
            for start, end, _ in reversed(spans):
                rest = rest[:start] + " " * (end - start) + rest[end:]
            # A marked chord inside a lyric line is kept as text.
            if spans and all(is_filler(t[2]) for t in token_spans(rest)):
                lines.append(Line(line_text, spans))
            else:
                lines.append(Line(line_text))
        else:
            line_text = expand_tabs(raw).rstrip()
            lines.append(Line(line_text, detect_chord_line(line_text, ask)))
    return lines


def convert_chords(lines, notes):
    notation = Notation([name for line in lines for _, _, name in line.chords])
    unknown = set()
    for line in lines:
        if not line.chords:
            continue
        spans = []
        for start, end, name in line.chords:
            letters = notation.convert(name)
            if letters is None:
                unknown.add(name)
                letters = name
            spans.append((start, end, letters))
        line.text = replace_spans(line.text, spans)
        line.chords = [t for t in token_spans(line.text) if not is_filler(t[2])]
    if notation.solfege:
        notes.append("Changed Spanish chord names to letters (LAm -> Am, SOL -> G...)"
                     + ("; lower-case chords were read as minor (mi -> Em)" if notation.lowercase_minor else ""))
    if unknown:
        notes.append(f"The book won't recognise these chords, check them: {', '.join(sorted(unknown))}")


def strip_labels(lines, cleaned):
    """Drop section labels, capo/key lines and credits; normalise the intro label."""
    out, removed = [], []
    for line in lines:
        text = line.text
        if not line.is_chord_line and text.strip():
            if CREDIT_RE.fullmatch(text) or META_RE.fullmatch(text):
                continue
            capo = CAPO_RE.fullmatch(text)
            if capo:
                if capo.group(1) and int(capo.group(1)) > 0:
                    cleaned.capo = capo.group(1)
                continue
            label = BRACKET_LABEL_RE.fullmatch(text) or WORD_LABEL_RE.fullmatch(text)
            if label and not (label.re is BRACKET_LABEL_RE and could_be_chord(label.group(1))):
                name, rest = label.group(1).strip(), label.group(2)
                if label.re is WORD_LABEL_RE and rest and not is_chord_text(rest):
                    out.append(line)  # a lyric that starts like a label ("Coro de ángeles...")
                    continue
                if INTRO_RE.match(name):
                    out.append(Line("Intro:"))
                else:
                    removed.append(name)
                    out.append(Line(""))  # a label starts a new section
                if rest:
                    out.append(Line(rest, [t for t in token_spans(rest) if could_be_chord(t[2])]))
                continue
        out.append(line)
    if removed:
        examples = ", ".join(dict.fromkeys(removed[:12]))
        cleaned.notes.append(f"Removed {len(removed)} section labels ({examples})")
    return out


def is_chord_text(text):
    tokens = text.split()
    return any(could_be_chord(t) for t in tokens) and all(could_be_chord(t) or is_filler(t) for t in tokens)


def add_intro(lines, notes):
    """Make sure the song starts with "Intro:" and its chords."""
    content = [i for i, line in enumerate(lines) if line.text.strip()]
    if not content:
        return lines
    first = content[0]
    if lines[first].text == "Intro:":
        return lines
    # Chord lines at the very top that aren't over a lyric are the intro.
    end = first
    while end < len(lines) and lines[end].is_chord_line:
        end += 1
    over_lyric = end < len(lines) and lines[end].text.strip()
    intro_end = end - 1 if over_lyric else end
    if intro_end > first:
        return lines[:first] + [Line("Intro:")] + lines[first:intro_end] + [Line("")] + lines[intro_end:]
    chord = next((line.chords[0][2] for line in lines if line.chords), None)
    if chord is None:
        return lines
    notes.append(f'Added "Intro:" with the first chord ({chord}); change it if the song starts differently')
    return lines[:first] + [Line("Intro:"), Line(chord, [(0, len(chord), chord)]), Line("")] + lines[first:]


def tidy_blank_lines(lines):
    out = []
    for line in lines:
        if not line.text.strip():
            if out and out[-1].text:
                out.append(Line(""))
        else:
            out.append(line)
    while out and not out[-1].text:
        out.pop()
    return out


def unusual_chars(lines):
    found = {}
    for number, line in enumerate(lines, start=1):
        for ch in line.text:
            if not USUAL_CHAR_RE.fullmatch(ch):
                found.setdefault(ch, number)
    return [f"'{ch}' (U+{ord(ch):04X}, line {number})" for ch, number in found.items()]


def clean_song(text, marked=False, ask=lambda line: True):
    """Clean a song's text. `ask(line)` decides doubtful chord lines (pasted text)."""
    cleaned = Cleaned(body="")
    lines = read_lines(text, marked, ask)
    lines = strip_labels(lines, cleaned)
    convert_chords(lines, cleaned.notes)
    lines = tidy_blank_lines(lines)
    lines = add_intro(lines, cleaned.notes)
    lines = tidy_blank_lines(lines)
    odd = unusual_chars(lines)
    if odd:
        cleaned.notes.append("Unusual characters, check them: " + ", ".join(odd))
    cleaned.body = "\n".join(line.text for line in lines)
    return cleaned
