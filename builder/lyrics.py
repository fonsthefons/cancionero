"""Turning a song body (chords written above lyrics) into HTML.

A line is a chord line when every word on it is a chord (or a separator such
as `|`, `-`, `(`, `)`). Each chord line is paired with the lyric line below it
so the two never get split across columns or pages.
"""

import re
from html import escape

# Standard chord symbols: Em, B7, Cmaj7, D/F#, G#m, Bb, Asus4, ...
CHORD_RE = re.compile(
    r"(?<!\w)("
    r"[A-G][#b]?"
    r"(?:(?:maj|min|dim|aug|sus|add|dom)\d*|m\d*|\d+)?"
    r"(?:/[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|dom)?\d*)?"
    r")(?!\w)"
)
SEPARATOR_RE = re.compile(r"[-|()]+")
VERSE_BREAK_RE = re.compile(r"\n\s*\n")
TAB_WIDTH = 2


def is_chord_line(line):
    words = line.split()
    if not words:
        return False
    has_chord = False
    for word in words:
        if CHORD_RE.search(word):
            has_chord = True
        elif not SEPARATOR_RE.fullmatch(word):
            return False
    return has_chord


def chord_line_html(line):
    chords = CHORD_RE.sub(r'<span class="chord">\1</span>', escape(line, quote=False))
    return f'<div class="chord-line">{chords}</div>'


def lyric_line_html(line):
    return f'<div class="lyric-line">{escape(line, quote=False)}</div>'


def pair_html(*lines):
    return f'<div class="line-pair">{"".join(lines)}</div>'


def verse_html(verse):
    parts = []
    pending_chords = None  # chord line waiting for its lyric line

    for raw in verse.split("\n"):
        line = raw.replace("\xa0", " ").expandtabs(TAB_WIDTH).rstrip()
        if not line.strip():
            continue
        if is_chord_line(line):
            if pending_chords:
                parts.append(pair_html(pending_chords))
            pending_chords = chord_line_html(line)
        elif pending_chords:
            parts.append(pair_html(pending_chords, lyric_line_html(line)))
            pending_chords = None
        else:
            parts.append(lyric_line_html(line))

    if pending_chords:
        parts.append(pair_html(pending_chords))
    return f'<div class="verse">{"".join(parts)}</div>' if parts else ""


def lyrics_html(body):
    # Only trim blank lines around the body: the first line's indentation
    # (e.g. a chord placed mid-line) must be kept.
    body = body.strip("\n")
    verses = "\n".join(filter(None, map(verse_html, VERSE_BREAK_RE.split(body))))
    return f'<div class="lyrics">\n{verses}\n</div>'
