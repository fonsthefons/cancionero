# Hymn Book

## SETUP from scratch
### 0. Clone the repo
gh repo clone fonsthefons/cancionero

### 1. Create venv named venv (name doesn't matter change it if necessary)
python3 -m venv venv

### 2. Activate
source venv/bin/activate     # macOS/Linux

### 3. Install PyYAML
pip install -r requirements.txt

### 4. Run the build
python build.py

## Adding a new song

1. Create a new `.md` file in `songs/` (e.g. `songs/mi_cancion.md`).

2. Add metadata at the top, then the lyrics below. If you include chords, use spaces (not tabs) to align them with the desired lyric

```markdown
---
title: "My Song Title"
autor: "Composer Name"
capo: "Capo 2"
link: "https://example.com/song"
song_tags:
  misa:
    - entrada
    - ofertorio
  alabanza:
    - primer_ciclo
  adoracion: []
  tema:
    - padre
    - espiritu
---

Intro: G C D

G              C
First line of lyrics
```

**Frontmatter fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Display name of the song |
| `autor` | No | Composer or autor name (shown below the title in the book) |
| `capo` | No | Capo or key info, free text (shown below the title in the book) |
| `link` | No | URL to sheet music, video, or reference (shown as a clickable link) |
| `song_tags` | Yes | Categories and subcategories (see below) |

You do **not** need a `song_number` — numbers are assigned automatically at build time, sorted alphabetically by title.

**`song_tags` format** — each key is a tag. Tags with subtags use a list; flat tags use an empty list `[]`:

```yaml
song_tags:
  misa:
    - entrada      # pick from fixed misa subtags
  alabanza:
    - primer_ciclo      # pick from fixed alabanza subtags
  adoracion: []         # flat tag — no subtags
  tema:
    - padre             # pick from fixed tema subtags
    - espiritu
```

- A song can belong to **multiple tags** and **multiple subtags** under the same tag
- Use `adoracion: []` for the adoracion flat tag
- If a song is tagged `misa`, `alabanza`, or `tema`, it **must** include at least one subtag — omit the tag key entirely if the song doesn't belong to that category
- `build.py` validates tags at build time and aborts on errors

3. Write the lyrics exactly as you want them to appear. Line breaks and spacing (tabs for chords) are preserved in the HTML/PDF output.

4. Rebuild the book:

```bash
python3 build.py          # generates output/index.html and root/index.html (necessary for github pages)
```


## Tags and subtags

There are four top-level tags, all set in `song_tags`:

### Misa, Alabanza, and Tema (fixed subtags)

**Misa** — pick one or more:

`entrada`, `gloria`, `aleluya`, `ofertorio`, `santo`, `comunion`, `salida`

**Alabanza** — pick one or more:

`primer_ciclo`, `segundo_ciclo`, `tercer_ciclo`, `cuarto_ciclo`

**Tema** — pick one or more (topics that can apply to any song):

`padre`, `cristo`, `espiritu`, `santo`, `martir`, `virgen`

```yaml
song_tags:
  misa:
    - entrada
    - comunion
  alabanza:
    - primer_ciclo
  tema:
    - padre
    - espiritu
```

> **Note:** `santo` under **Misa** is the mass part (Sanctus). `santo` under **Tema** is a topic tag — a song can have both.

To add a new tema topic, add it to the `tema` list in `TAG_WITH_SUBTAGS` in `build.py` and add a matching section in `indexes/tema.md`.

### Adoracion (flat tag, no subtags)

```yaml
song_tags:
  adoracion: []
```

### Book output

The built book lists sections in this order: Misa → Alabanza → Adoracion → Tema.

```
# Tema

- Padre
  - 1. Abba Padre
  - 3. Primero el cielo
- Espiritu
  - 2. Restaurame Espiritu
```

### Tagging a song

1. Edit the song's `song_tags` in frontmatter using only the allowed values above.
2. Rebuild: `python3 build.py`
3. Check the matching note in `indexes/` (e.g. `indexes/misa.md`, `indexes/tema.md`).

To remove a song from a subtag or tag, delete that entry from frontmatter.

New tags or subtags can only be added by editing `TAG_WITH_SUBTAGS` and `FLAT_TAGS` in `build.py`.
