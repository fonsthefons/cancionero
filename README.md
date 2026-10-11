# Cancionero

A song book with chords for guitar, as **one web page**: `index.html`.

- Live at **https://fonsthefons.github.io/cancionero/** (works on phone, iPad and laptop).
- The whole book is a single file with nothing to download separately, so once
  the page is saved in the browser it works without internet.
- Songs are plain text files in `songs/`. A small Python program turns them into
  `index.html`, and GitHub Pages publishes that file whenever it changes.

## Quick start

| I want to... | Run |
|---|---|
| Set up my laptop (once) | see [Setup](#setup) |
| Add a song (from a link, a search, or pasted) | `venv/bin/python add_song.py` |
| Rebuild the book after editing a song by hand | `venv/bin/python build.py` |
| See the result | open `index.html` in a browser (double-click it) |
| Publish it to the website | `git add -A`, `git commit -m "Add <song>"`, `git push` |

Run every command from inside the `cancionero` folder. On Windows, write
`venv\Scripts\python` instead of `venv/bin/python`.

## Setup

You need:

- **Python 3.10 or newer.** Check with `python3 --version` (Windows: `py --version`).
  If it's missing or older, install it from https://www.python.org/downloads/.
- **Git.** Check with `git --version`. If it's missing, install it from
  https://git-scm.com/downloads (on a Mac, running `git` offers to install it).
- To publish: a GitHub account with write access to this repository.

Then, in a terminal:

```bash
git clone https://github.com/fonsthefons/cancionero.git
cd cancionero
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python build.py
```

(On Windows, use `py -m venv venv` and `venv\Scripts\pip` / `venv\Scripts\python`.)

The last command should print `Built index.html: ... songs`. You're ready.
`venv/` is a private folder with this project's Python packages. It is not
shared through Git, so every laptop creates its own with the commands above.

## Publishing

The website shows whatever `index.html` is on GitHub. After adding or editing songs:

```bash
git add -A
git commit -m "Add Huracán"
git push
```

About a minute later the site is updated. Reload the page on your phone to see
it; if it still shows the old version, close the tab and open it again.
Always commit the song files and `index.html` together.

## Adding a song

### With the script (recommended)

```bash
venv/bin/python add_song.py
```

It needs an internet connection and offers three ways in:

1. **Link**: paste the address of the song's page on Ultimate Guitar,
   Cifra Club, LaCuerda, or another site that shows the song as plain text.
   The path of a page saved from the browser also works.
2. **Paste**: paste the song (chords above the lyrics), then type `END` on its own line.
3. **Search**: type the title and the artist. It searches the web (DuckDuckGo)
   and Ultimate Guitar and lists the best chord pages, your three sites first.
   Enter takes the first; if a page can't be read, or you say the preview
   looks wrong, the list comes back so you can try the next one.

It then:

- **tidies the song**: spaces instead of tabs, no invisible or odd characters,
  section labels (`[Chorus]`, `Estribillo:`...) removed, `Intro:` with its chords
  at the top (when the song has none, it adds one with the first chord: change
  it if needed), capo read from the page when it has one;
- **turns Spanish chord names into letters** (`LAm` → `Am`, `SOL` → `G`,
  `Sib` → `Bb`; in the "DO mi" style, lower case means minor), keeping every
  chord over its letter;
- **shows you the result** and asks if it looks right;
- **asks for the details**: title (it warns if the song is already in the
  book), author, capo, Spotify link and tags (pick numbers from a list);
- **finds the Spotify link**: it offers the matching tracks it finds, each one
  checked with Spotify itself. Enter takes the first, a number picks another,
  `-` means none, or paste your own link;
- **writes** `songs/<title>_<author>.md` and **rebuilds** `index.html`.

Then open `index.html` to check the song, and [publish](#publishing).
If something needs fixing, edit the song file (see below) and run
`venv/bin/python build.py` again.

Good to know:

- **Author names**: if you change an author's name (e.g. "Hakuna Group Music" →
  "Hakuna"), the script remembers it in `author_aliases.yaml` and offers your
  version next time.
- **Cifra Club** only opens in a real browser. The first time you use it, the
  script offers to install a hidden one (about 100 MB, once).
- **Doubtful lines**: when pasting, a line like "La la la" could be lyrics or
  chords, so the script asks. Enter means chords; type `n` when it's lyrics.
- **"The web search is busy"**: after many searches in a short time the search
  asks to prove you're human. Wait a few minutes, or use a link instead.
- `venv/bin/python add_song.py --help` lists the options (`--no-build`, `--offline`).

### By hand

1. Copy `song_template.md` to `songs/<title>_<author>.md`
   (lowercase, `_` instead of spaces, no accents; e.g. `songs/sopla_senor_popular.md`).
2. Fill in the details at the top and paste the lyrics with chords.
3. Run `venv/bin/python build.py`, check `index.html`, and [publish](#publishing).

The build checks every song and stops with a list of every problem
(unknown tag, typo in a field name, broken formatting...), so mistakes don't slip in silently.

### The details at the top of a song file

```yaml
---
title: Sopla Señor          # required
autor: popular              # optional, shown next to the title
capo: "2"                   # optional, free text
link: "https://..."         # optional, Spotify or other recording (must start with http)
song_tags:                  # optional, see "Tags" below
  misa:
    - comunion
  adoracion: []
---
```

Songs are numbered automatically, alphabetically by title in Spanish order:
accents and capitals are ignored (*Déjate* sorts as *dejate*), and ñ comes after n.

### Lyrics and chords

Write chords on their own line, above the lyric they belong to, aligned with
**spaces**. A line counts as a chord line when every word on it is a chord
(`G`, `Am`, `C#m7`, `Bb`, `Dsus4`, `D/F#`...) or a separator (`|`, `-`, `(`, `)`).
A blank line starts a new verse.

```
G              C
First line of lyrics
```

Your spacing is kept exactly: the book uses a fixed-width font and never wraps
lines, so a chord is always shown over the same letter as in the file, at any
text size or zoom. Prefer spaces over tabs, because a tab's width depends on
the editor (the book counts a tab as 2 spaces).

## Tags

Tags and subtags are defined in **`tags.yaml`**. That file is the only place to
edit when adding, renaming or reordering them; the book follows its order, and
`add_song.py` lists them from there.

| Tag | Subtags |
|-----|---------|
| `misa` | `entrada`, `gloria`, `aleluya`, `ofertorio`, `santo`, `cordero`, `comunion`, `salida` |
| `alabanza` | `primer_ciclo`, `segundo_ciclo`, `tercer_ciclo`, `cuarto_ciclo` |
| `adoracion` | none: use `adoracion: []` |
| `tema` | `padre`, `cristo`, `espiritu`, `santo`, `martir`, `virgen` |

A song can have several tags and several subtags per tag. A tag with subtags
needs at least one. A song without tags only appears in *All Songs*.

## Using the book

- **☰ menu**: contents, plus settings: text size (A− / A+), chords and
  columns for the whole book, light/dark theme, keep the screen on, print.
  Settings are remembered on each device.
- **Search** (top bar, and the Sing Session box): type a song number, or any
  words from the title, author or lyrics, in any order and without accents
  ("padre abba", "senor jesus"); the start of a word is enough. Title matches
  come first, then authors, then lyrics, which show the line they were found in.
- **Sing Session** (first in the ☰ menu): a list of songs to practise or play.
  Add songs with its search box or the **+ Session** button on any song;
  reorder by dragging the **⠿** handle (or ↑/↓ keys on a focused handle),
  remove with ✕ (or tap **✓ In session** on the song), and
  *Clear session* empties it. Tap a song in the list to jump to it. Remembered
  on each device.
- **Autoscroll** (top bar): ▶/⏸ starts and stops, − / + change the speed
  (1–10, remembered). Scrolling by hand or jumping to a song while it runs
  continues from there; it pauses while the menu is open and stops at the end.
- **Per song**: show/hide chords, transpose (tap the number to reset), 1 or 2 columns.
  These are remembered per song on each device (e.g. Abba Padre stays at +3);
  ☰ → *Song changes → Reset all* puts every song back as written.
- **Text size**: each song is sized so its longest line fits the screen.
  A− / A+ scale that up or down; pinch-zoom always works too.
- **Printing / PDF** (☰ → Print, or the browser's print): the index is always
  printed fully unfolded, its entries are clickable links to the songs inside
  the PDF, and each song's *Link* stays a clickable web link. Every song starts
  at the top of a new page (a long song continues onto the next pages).
- **Transposing** keeps every chord on its letter. Only when two chords are a
  single space apart (e.g. `D Em` → `D# Fm`) does the second one shift by the
  one column it needs.

## Troubleshooting

| Problem | What to do |
|---|---|
| `python3: command not found`, or a version below 3.10 | Install Python from https://www.python.org/downloads/, then redo the setup. |
| `No such file or directory: venv/bin/python` | You're not in the `cancionero` folder (`cd cancionero`), or the setup wasn't run. |
| `ModuleNotFoundError: No module named 'yaml'` | Run `venv/bin/pip install -r requirements.txt`. |
| The build prints `Invalid songs:` | It lists each file and what's wrong (e.g. an unknown tag). Fix those files and build again. |
| `git push` is refused | Run `git pull` first, then push again. If it says "permission denied", ask the owner for write access. |
| The website still shows the old book | Wait a minute after pushing, then close and reopen the page. |
| `add_song.py` can't read a page | Pick another search result, or open the page, copy the song and use option 2 (paste). |

## How it works

This part is for changing the program itself; it isn't needed to add songs.

```
songs/*.md ─┐
tags.yaml  ─┼─► build.py ─► index.html   (single file, CSS + JS inlined)
web/       ─┘
```

| Path | What it is |
|------|------------|
| `build.py` | Entry point: loads, validates, renders, writes `index.html` |
| `add_song.py` | Asks for a link, a search or a pasted song, writes the song file, rebuilds |
| `importer/sites/` | One reader per website (`ultimate_guitar.py`, `cifraclub.py`, `lacuerda.py`, `generic.py`); add a module and list it in `SITES` to support a new site (the list order is also the search preference) |
| `importer/clean.py`, `chords.py`, `fetch.py` | Text cleanup, Spanish chord names → letters (keeping columns), downloading |
| `importer/search.py` | Finds chord pages for a title + artist (DuckDuckGo + Ultimate Guitar search) |
| `importer/spotify.py` | Finds the song's Spotify track (web search, checked on Spotify's embed page) |
| `author_aliases.yaml` | Author names as sites write them → as the book writes them |
| `builder/songs.py` | Reads song files (frontmatter + lyrics), validates fields, sorts in Spanish order |
| `builder/tags.py` | Loads `tags.yaml`, validates song tags, groups songs by tag |
| `builder/lyrics.py` | Detects chord lines and turns lyrics into HTML |
| `builder/render.py` | Builds the HTML fragments and fills `web/template.html` |
| `web/template.html` | Page layout, with `{{ placeholders }}` filled by the build |
| `web/song-controls.html` | Buttons shown above each song |
| `web/styles.css` | All styles (theme colours and sizes are variables at the top) |
| `web/js/core.js` | Shared helpers: `onAction`, `songSetting`, `prefs` (saved settings), `songState` (saved per-song changes) |
| `web/js/display.js` | Chords, columns, text size, theme |
| `web/js/transpose.js` | Transposition that keeps chords in their columns |
| `web/js/autoscroll.js` | Autoscroll (speed settings at the top of the file) |
| `web/js/search.js` | Song search (number, title, author, lyrics; ranked, with the matching line) |
| `web/js/session.js` | Sing Session (list in the menu, + Session buttons) |
| `web/js/session-drag.js` | Drag-and-drop reordering of the session (pointer events) |
| `web/js/drawer.js`, `index.js`, `print.js`, `wake-lock.js` | One feature each |
| `song_template.md` | Starting point for a song written by hand |
| `PROGRESS.md` | Log of what was changed and why |

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

A `.search` box with `data-search="<action>"` turns its results into buttons
that run that action with `data-song="<song id>"` (the Sing Session box uses
`session-add`); without it, results jump to the song.

For a show/hide or on/off option that works per song *and* for the whole book,
use `songSetting(name, [default, alternative], onGlobalChange)` from `core.js`,
as `web/js/display.js` does for chords and columns. It stores the value in
`data-<name>` on `<body>` (whole book) and on `.song` (one-song override), CSS
styles both, and the book-wide value is remembered on the device. For any other
remembered value use `prefs.get(key, fallback)` / `prefs.set(key, value)`, or
`songState.get(song, key)` / `songState.set(song, key, value)` for a value that
belongs to one song (`null` forgets it). Saved data is keyed by the song's file
name, so renaming a song file forgets its saved changes.

Never add CSS that changes how lyric lines lay out horizontally (wrapping,
`letter-spacing`, proportional fonts, per-character styling that changes
width): it would move chords off their letters.
