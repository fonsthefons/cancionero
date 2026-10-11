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

### Not done (not committed)
- Nothing is committed. Review with `git status` / `git diff`, then commit.
