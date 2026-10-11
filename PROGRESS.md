# Progress

## 2026-10-11 — Refactor for maintainability

### Phase 1: understand the repo
- Read `build.py`, `assets.js`, `book.css`, `README.md`, `indexes/*.md`; sampled song files.
- Found: one song silently untagged (mis-indented YAML), a `..md` filename, `fname`
  duplicating the filename (and mismatching in one song), unused `capo_notes`,
  first chord line losing its indentation, slash chords transposed wrongly,
  committed build artefacts (`output/`, `__pycache__/`, stale `search-index.json`).

### Phase 2: refactor
- **Song data** (`songs/`): removed `fname` (145 files) and `capo_notes` (62 files);
  fixed tag indentation in `sopla_senor_popular.md`; renamed
  `no_temas_jaime_olguin..md` → `no_temas_jaime_olguin.md`.
- **Build**: `build.py` is now a thin entry point over `builder/`
  (`songs.py`, `tags.py`, `lyrics.py`, `render.py`). Tags live in `tags.yaml`.
  Unknown fields, bad tags and broken YAML now stop the build with a full error list.
  Song anchors are `song-<filename>` (stable when songs are added).
- **Web**: `web/template.html` (layout), `web/song-controls.html`,
  `web/styles.css`, `web/js/*.js` (one file per feature, `core.js` first).
  Search is built from the page itself, so lyrics are no longer duplicated in a JSON blob.
  Output went from 1.73 MB to 0.98 MB.
- **Removed**: Obsidian `indexes/`, `output/`, `__pycache__/`, `search-index.json`,
  `book.css`, `assets.js`. Added `.gitignore`, `song_template.md`, new `README.md`.
- Moved `songs/CLAUDE.md` to the repo root (the build treats every `.md` in `songs/` as a song).

### Verification (all scripts in `scratch/`, gitignored)
- `run_old_build.py` + `extract.py` + `compare.py`: old vs new build, per song
  (heading, meta, every chord/lyric line and chord). Only differences:
  first chord line indentation restored in 4 songs (bug fix), and the order of the two
  songs titled "Aleluya" (now deterministic: by file name).
- `compare_index.py`: tag index identical except "Sopla Señor" now listed under its 3 tags.
- `test_validation.py`: 9 kinds of broken song files all reported correctly.
- `run_browser_test.py` (Playwright, headless Chromium): 29 UI checks pass
  (chords, columns, transpose incl. `D/F#`→`E/G#`, search, sidebar, links, print dialog), no JS errors.

### Main commands
- `venv/bin/python build.py`
- `venv/bin/pip install playwright` (test-only, not in `requirements.txt`);
  Chromium downloaded to `scratch/browsers/`.

### Blocked
- Arc browser ignores `--headless`, so it could not be used for tests; used Playwright instead.

### Phase 3: commit and merge
- Committed on branch `refactor/maintainable-build` (c89ad2f), opened
  https://github.com/fonsthefons/cancionero/pull/1 and merged it into `main` (4dedfda).
- Local `main` fast-forwarded; feature branch deleted locally and on GitHub.
- `.claude/settings.json` (local Claude Code permissions) was left uncommitted on purpose.

## 2026-10-11 — Phone / iPad / laptop experience

### Audit (scratch/mobile_audit.py, line_lengths.py, alignment_risks.py)
- Phone rendered the page 575px wide on a 390px screen (`min-width: fit-content`
  on body), causing zoomed-out text and sideways wobble.
- First song ~13,000px down; floating `<` button covered content; per-song buttons
  overflowed; search input 13px (iOS zooms on focus); sticky hover states on touch.
- Widest lyric line per song: median 40 chars, max 63.
- Alignment risks: 57 combining accents (now NFC-joined, same columns);
  `viva_cristo_rey_jaire.md` uses tabs (kept at width 2 as before; review by hand).

### Changes
- Lyrics size themselves per song so the widest line fits the screen
  (`--chars` from the build + CSS container units), capped at 15px; A−/A+ scale it.
  Pinch-zoom always allowed. Lines never wrap; if made bigger than the screen,
  the song scrolls sideways inside its box, never the page.
- Top bar (menu, title, search) replaces the floating button; menu drawer holds
  the contents and settings (text size, chords, columns, theme, keep screen on, print).
- Index sections and subsections are collapsible, open by default; links into a
  folded section unfold it.
- Transposition keeps every chord on its column, absorbing longer/shorter chord
  names in the following spaces (also after `(`/`)` separators).
- Settings remembered per device (localStorage, guarded). Dark theme (auto/light/dark).
- New files: `web/js/drawer.js`, `index.js`, `wake-lock.js`; removed `sidebar.js`.

### Verification
- `scratch/ui_test.py` (Playwright, Chromium + WebKit, phone 390px / iPad 820px /
  laptop 1440px): all 8,778 chords on their exact pixel column in 1 and 2 columns
  and at 40% / 250% text; every song fits; page never scrolls sideways; 96,558
  transposed chord positions checked: shifts only where chords are one space
  apart or glued (`C#m-Bm`); back to 0 restores every line; all UI features pass;
  no JS errors.
- `scratch/compare.py`: every chord/lyric line still identical to the original build.
- Tools: `venv/bin/python -m playwright install webkit` (into `scratch/browsers/`).
- Merged as PR #2 and deployed to https://fonsthefons.github.io/cancionero/ (live file
  verified identical to the local build).

## 2026-10-11 — Autoscroll

- `web/js/autoscroll.js` + top-bar group: ▶/⏸, −, speed number, +. Speed 1–10
  (6 px/s per step, default 3), remembered per device. Smooth requestAnimationFrame
  scrolling with fractional positions; follows manual scrolls/jumps; pauses while the
  menu is open; stops at the end of the page.
- On screens ≤ 560px the "Cancionero" title is hidden to make room (Contenido is in
  the menu) and search results span the screen width.
- `scratch/ui_test.py`: 10 new autoscroll checks + top-bar fit on phone/iPad/laptop;
  full suite passes in Chromium and WebKit.
- Merged as PR #3 and deployed (live file verified identical).

## 2026-10-11 — Remember per-song changes

- `songState` in `web/js/core.js`: per-song transpose / chords / columns saved in
  localStorage (`cancionero.songs`, keyed by song id = file name), only non-default
  values; entries of songs that no longer exist are pruned on load.
- Restored on load (`transpose.js`, `songSetting`). A book-wide chords/columns
  toggle clears the saved per-song overrides of that kind.
- Menu: *Song changes → Reset all*.
- `scratch/ui_test.py`: 7 new persistence checks (Abba Padre +3 survives reload with
  chords aligned, per-song chords/columns restored, global toggle clears, reset);
  full suite passes in Chromium and WebKit.
- Merged as PR #4 and deployed (live file verified identical).

## 2026-10-11 — Sing Session

- `web/js/session.js`: ordered list of song ids in localStorage (`cancionero.session`),
  deduplicated, pruned of songs that no longer exist. Shown first in the menu
  (`<details id="session" open>`): count, empty message, numbered list with
  link + ↑ ↓ ✕, own search box, Clear session (with confirmation).
- Every song gets a "+ Session" / "✓ In session" toggle button.
- `search.js` generalized: `data-search="<action>"` makes results action buttons
  (session box adds songs and stays focused); top-bar search unchanged.
- Build adds `data-title` to each song (plain title for the session list).
- `scratch/ui_test.py`: 16 new session checks; full suite passes in Chromium and WebKit.
- Merged as PR #5 and deployed (live file verified identical).

## 2026-10-11 — Drag and drop in Sing Session

- ↑ ↓ buttons replaced by a ⠿ handle on the right of each row
  (`web/js/session-drag.js`): pointer events (mouse/finger/pencil), handle has
  `touch-action: none` so only drags from it reorder and swipes elsewhere scroll the
  menu; dragged row lifts and follows, others slide aside; saved on release;
  pointercancel reverts; holding near the menu edge scrolls it; ↑/↓ keys on a
  focused handle. Position numbers hidden while dragging.
- `moveInSession(id, to)` now moves to a position.
- Tests: mouse drags (both engines), real touch drag via Chrome DevTools touch
  events, swipe on a title doesn't reorder, tap without move does nothing,
  keyboard, edge auto-scroll with a 20-song session; full suite passes.
- Merged as PR #6 and deployed (live file verified identical).

## 2026-10-11 — Printing: unfolded index, clickable PDF links

- Interpreted "the menu should always be open" as the Contenido index (the ☰ drawer
  is hidden on paper). `print.js`: on `beforeprint` every folded index section is
  opened, `afterprint` restores the user's folds; CSS fallback via
  `::details-content` in `@media print`; no ▼ markers on paper.
- Links: index/All Songs entries become internal PDF links (Chrome), song *Link*s
  stay web links. Found `cordero_de_dios_popular.md` with capo text in `link`
  ("0, 0-5" -> became a broken file:// link); moved to `capo`. Build now rejects
  links not starting with http(s)://.
- `scratch/pdf_test.py` (Chromium printToPDF + pypdf): folded sections printed,
  584/584 internal links resolve (first one lands on the song's page), 138 web
  links, folds restored after printing. Full UI suite passes.
- Not verifiable here: Safari/iOS's own PDF export (Playwright can't print WebKit).
- Merged as PR #7 and deployed (live file verified identical).

## 2026-10-11 — Each song starts on a new printed page

- Print CSS: `.song { break-before: page }` replaces `break-inside: avoid` (which,
  for songs not fitting the remaining space, left titles at the bottom of a page);
  title and meta line get `break-after: avoid`.
- `scratch/pdf_test.py` now checks every song heading is the first line of its own
  page, in order, with no page holding two song starts, for default print and for
  2 columns + no chords. Confirmed it FAILS on the previous build (146/150 and
  71/150) and passes now (150/150 both). Takes an optional path to a built page.

## 2026-10-11 — Pinch-zoom top bar: tried and reverted

- PR #9 kept the top bar and menu at normal size on screen while pinch-zoomed
  (visualViewport + a counter-scaling transform). Automated Chromium tests passed, but on
  the user's real device it felt buggy and crashed the page, so it was reverted (PR #10).
  The code is back to the PR #8 state. Test kept in `scratch/zoom_test.py`.
- Lesson: pinch-zoom behaviour must be judged on the real phone/iPad; headless tests
  do not reproduce iOS Safari's zoom.

## 2026-10-11 — Spanish alphabetical order

- `builder/songs.py`: `spanish_sort_key` ignores accents and case (é = e, ü = u) and keeps
  ñ as its own letter after n. Previously accented letters sorted after z, so e.g. Déjate
  came after Dulce locura. 16 songs renumbered (Déjate, Quédate Señor, Ven Espíritu...);
  saved per-song changes and the session are keyed by file name, so unaffected.
- `scratch/sort_check.py`: key unit checks + list of moved songs. Full UI and PDF suites pass.

## 2026-10-11 — Better search

- `web/js/search.js`: searches lyric lines only (before, chord lines were glued to the
  lyrics, so phrases across lines failed and chord names matched), plus title, author
  (`data-autor`, added by `builder/render.py`) and song number. Accents, case and
  punctuation ignored; every typed word must appear, in any order, prefixes OK. Ranked:
  number, title start, title, author, exact phrase in lyrics, scattered words. Lyric
  matches show the matching line (`.search-snippet`). No extra data in the file.
- `scratch/search_test.py`: old vs new on real queries ("padre abba" 0 -> 1, "senor,
  jesus" 0 -> 16, phrase across two lines 0 -> 1, "31" -> song 31 only), ranking,
  snippets, session box, and speed: slowest keystroke 10 ms with 6x slower CPU.

## 2026-10-11 — add_song.py: import songs from a link or paste

- `add_song.py` (interactive) + `importer/` package: link (Ultimate Guitar, Cifra Club,
  LaCuerda, generic <pre> sites, or a saved page file) or pasted text -> cleanup ->
  preview -> title/author/capo/Spotify/tags -> `songs/<title>_<author>.md` -> rebuild.
- Cleanup (`importer/clean.py`): tabs -> spaces at 8-column browser stops, 1:1 fixes for
  quotes/dashes/nbsp/sharps, invisible chars removed, NFC; section labels removed except
  intro (`Intro:` + chords; if none, `Intro:` + first chord, as in the existing songs);
  capo lines -> capo field; key/tuning/credit lines dropped; blank lines collapsed;
  unusual characters and unrecognised chords reported.
- Spanish chords (`importer/chords.py`): DO/Do/do + #/b + suffix + /bass -> letters;
  lower case = minor only when mixed with ALL-CAPS majors ("DO mi"). Chords keep their
  start column; a longer name (º -> dim) borrows following spaces. Doubtful pasted lines
  ("La la la") are asked about.
- Sites: UG embedded JSON ([ch] markup); Cifra Club <pre> with <b> chords, capo and artist
  from embedded data; it blocks non-browsers (Akamai), so it is read with headless WebKit
  (Playwright), which the script offers to install on first use; LaCuerda <pre> with <A>
  chords (song page -> first .shtml version).
- Author aliases remembered in `author_aliases.yaml` (seeded: Hakuna Group Music -> Hakuna).
- `scratch/add_song_test.py [--network]`: 50 checks (chord conversion and columns, chars,
  tabs, labels, capo, intro, paste detection, end-to-end runs on saved pages from all three
  sites, duplicates, aliases, live downloads). All pass.
- Choices: kept Spotify-only links (source page not stored); a removed label leaves a
  verse break; doubtful chord lines default to "yes" when Enter is pressed.

## 2026-10-11 — add_song.py option 3: search by title and artist

- `importer/search.py`: DuckDuckGo plain-HTML search ("<title> <artist> acordes"; Google and
  Bing only answer real browsers) + Ultimate Guitar's own search (Chords, artist match, most
  voted first) as a second source. Drops results not mentioning the title/artist, merges the
  same page under other addresses (UG tab ids, LaCuerda acordes./chords./.shtml, Cifra
  .com/.com.br), max 3 per site, supported sites first in `SITES` order (now UG, LaCuerda,
  Cifra Club: Cifra needs the browser engine, so last).
- `add_song.py`: option 3 lists up to 8 results; Enter takes the first untried; a page that
  can't be read, or a preview answered "no", goes back to the list (tried ones marked).
- Generic reader now refuses pages without chords (akordes, bananacifras draw them with
  JS); downloads detect the page's charset (losacordes.com is Windows-1252).
- Tests: 6 offline ranking checks (fake search answers) + 5 live option-3 checks in
  `scratch/add_song_test.py --network`; all 61 pass.
