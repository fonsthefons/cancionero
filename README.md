# Cancionero

A song book with chords, built into **one self-contained `index.html`** (no
internet needed once the page is saved in the browser) and published with
GitHub Pages from the repo root.

## Setup

```bash
gh repo clone fonsthefons/cancionero
cd cancionero
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Adding a song

1. Copy `song_template.md` to `songs/<title>_<author>.md`
   (lowercase, `_` instead of spaces; e.g. `songs/sopla_senor_popular.md`).
2. Fill in the frontmatter and paste the lyrics.
3. Run `venv/bin/python build.py` and commit `index.html` together with the song.

The build checks every song and stops with a list of every problem
(unknown tag, typo in a field name, broken YAML...), so mistakes don't slip in silently.

### Frontmatter

```yaml
---
title: Sopla Señor          # required
autor: popular              # optional, shown next to the title
capo: "2"                   # optional, free text
link: "https://..."         # optional, recording or sheet music
song_tags:                  # optional, see "Tags" below
  misa:
    - comunion
  adoracion: []
---
```

Songs are numbered automatically, alphabetically by title.

### Lyrics and chords

Write chords on their own line, above the lyric they belong to, aligned with
**spaces** (tabs count as 2 spaces). A line counts as a chord line when every
word on it is a chord (`G`, `Am`, `C#m7`, `Bb`, `Dsus4`, `D/F#`...) or a
separator (`|`, `-`, `(`, `)`). A blank line starts a new verse.

```
G              C
First line of lyrics
```

Your spacing is kept exactly: the book uses a monospace font and never wraps
lines, so a chord is always shown over the same letter as in the `.md` file,
at any text size or zoom. Prefer spaces over tabs (a tab's width depends on the
editor). Accents typed as two characters (letter + accent mark) are joined
into one, which keeps them one column wide as the editor shows them.

## Using the book

- **☰ menu**: contents, plus settings: text size (A− / A+), chords and
  columns for the whole book, light/dark theme, keep the screen on, print.
  Settings are remembered on each device.
- **Per song**: show/hide chords, transpose (tap the number to reset), 1 or 2 columns.
- **Text size**: each song is sized so its longest line fits the screen.
  A− / A+ scale that up or down; pinch-zoom always works too.
- **Transposing** keeps every chord on its letter. Only when two chords are a
  single space apart (e.g. `D Em` → `D# Fm`) does the second one shift by the
  one column it needs.

## Tags

Tags and subtags are defined in **`tags.yaml`**. That file is the only place to
edit when adding, renaming or reordering them; the book follows its order.

| Tag | Subtags |
|-----|---------|
| `misa` | `entrada`, `gloria`, `aleluya`, `ofertorio`, `santo`, `cordero`, `comunion`, `salida` |
| `alabanza` | `primer_ciclo`, `segundo_ciclo`, `tercer_ciclo`, `cuarto_ciclo` |
| `adoracion` | none: use `adoracion: []` |
| `tema` | `padre`, `cristo`, `espiritu`, `santo`, `martir`, `virgen` |

A song can have several tags and several subtags per tag. A tag with subtags
needs at least one.

## How it works

```
songs/*.md ─┐
tags.yaml  ─┼─► build.py ─► index.html   (single file, CSS + JS inlined)
web/       ─┘
```

| Path | What it is |
|------|------------|
| `build.py` | Entry point: loads, validates, renders, writes `index.html` |
| `builder/songs.py` | Reads song files (frontmatter + lyrics) and validates fields |
| `builder/tags.py` | Loads `tags.yaml`, validates song tags, groups songs by tag |
| `builder/lyrics.py` | Detects chord lines and turns lyrics into HTML |
| `builder/render.py` | Builds the HTML fragments and fills `web/template.html` |
| `web/template.html` | Page layout, with `{{ placeholders }}` filled by the build |
| `web/song-controls.html` | Buttons shown above each song |
| `web/styles.css` | All styles (theme colours and sizes are variables at the top) |
| `web/js/core.js` | Shared helpers: `onAction`, `songSetting`, `prefs` (saved settings) |
| `web/js/display.js` | Chords, columns, text size, theme |
| `web/js/transpose.js` | Transposition that keeps chords in their columns |
| `web/js/search.js`, `drawer.js`, `index.js`, `print.js`, `wake-lock.js` | One feature each |

### Adding a browser feature

1. Add a button with a `data-action` attribute (in `web/template.html` or
   `web/song-controls.html`):
   `<button data-action="my-feature">...</button>`
2. Create `web/js/my-feature.js` and register a handler. It receives the button
   and the song it belongs to (or `null`):
   ```js
   onAction("my-feature", (button, song) => { ... });
   ```
3. Rebuild. Every file in `web/js/` is included automatically (`core.js` first).

For a show/hide or on/off option that works per song *and* for the whole book,
use `songSetting(name, [default, alternative], onGlobalChange)` from `core.js`,
as `web/js/display.js` does for chords and columns. It stores the value in
`data-<name>` on `<body>` (whole book) and on `.song` (one-song override), CSS
styles both, and the book-wide value is remembered on the device. For any other
remembered value use `prefs.get(key, fallback)` / `prefs.set(key, value)`.

Never add CSS that changes how lyric lines lay out horizontally (wrapping,
`letter-spacing`, proportional fonts, per-character styling that changes
width): it would move chords off their letters.
