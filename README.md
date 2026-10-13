# Cancionero

A song book with chords, as one web page (`index.html`), live at **https://fonsthefons.github.io/cancionero/**.

This repo holds the book's songs and settings. The page is built with
[cancionero-builder](https://github.com/fonsthefons/cancionero-builder): from the
builder's folder,

```bash
.venv/bin/python cancionero.py add cancionero       # add songs (link, search, paste, PDF, list)
.venv/bin/python cancionero.py build cancionero     # rebuild after editing a song by hand
.venv/bin/python cancionero.py publish cancionero   # commit and push: the site updates in a minute
```

| Path | What it is |
|------|------------|
| `songs/*.md` | One file per song: details at the top, then the lyrics with chords above them |
| `book.yaml` | The book's settings (title, author of most songs, which sites to search...) |
| `tags.yaml` | Optional: labels and order of the tags and subtags |
| `index.html`, `sw.js`, `manifest.webmanifest`, `icon-*.png` | Written by the build |

A song file:

```
---
title: Sopla Señor
autor: popular
capo: "2"
link: "https://open.spotify.com/track/..."
song_tags:
  misa: [comunion]
  Adoración: []
---

G              C
First line of lyrics
```

Tags can be anything: a tag written in a song appears in the book's contents.
