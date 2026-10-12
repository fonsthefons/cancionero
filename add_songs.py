"""Add a whole list of songs to the book, without questions.

    venv/bin/python add_songs.py Want.txt --section Want --report Checked.txt

The list has one song per line, "Title - Artist" or just "Title". Blank lines
are skipped. A line ending with ":" (or equal to the --section name) starts a
section; with --section only that section is read, so "NOT YET:" lists can sit
below it.

For each song it does what add_song.py's search does, but decides by itself:
search the web and Ultimate Guitar, read the best chord pages, clean the song
(importer/clean.py), find a Spotify link (or a YouTube one), and write
songs/<title>_<author>.md with no tags. When it isn't sure, it creates
nothing and says why:
- the song is already in the book;
- no readable chord page whose title has every word of the song's title (and
  whose artist matches, when one is given);
- no artist given and the pages found are by different artists.
Then the book is rebuilt once. With --report FILE the results are added to
that file under "claude-added:" and "claude-uncertain:".
"""

import argparse
import re
import sys
import time
from pathlib import Path

import build
from add_song import alias_for, existing_song, free_path, load_aliases, slug, song_file
from builder.lyrics import is_chord_line
from builder.songs import SongError, load_song
from importer.clean import clean_song
from importer.fetch import FetchError
from importer.read import read_song_any_way
from importer.search import plain_words, search
from importer.sites import SiteError
from importer.spotify import find_tracks
from importer.youtube import find_video

NO_ARTIST = {"popular", "anonimo", "anónimo", "tradicional"}
MAX_VERSIONS = 4  # chord pages read per song
MIN_PAIRS = 4  # chord lines over lyrics needed for a page to count
PAUSE = 15  # seconds between songs, so the web search doesn't get busy
GENERIC_ARTISTS = {"popular", "misc", "praise", "songs", "catolicas", "catolica", "musica", "musicas",
                   "cantos", "canciones", "religiosas", "cristianas", "worship", "christian", "unknown"}


# ---------- reading the list ----------

def read_list(path, section=None):
    """[(title, artist)] from a list file."""
    songs, current = [], None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if text.endswith(":") or (section and text.casefold() == section.casefold()):
            current = text.rstrip(":").strip()
            continue
        if section and (current or "").casefold() != section.casefold():
            continue
        title, _, artist = text.partition(" - ")
        songs.append((title.strip(), artist.strip()))
    return songs


# ---------- choosing a version ----------

def chord_pairs(body):
    lines = body.split("\n")
    return sum(1 for i in range(1, len(lines)) if is_chord_line(lines[i - 1]) and lines[i].strip()
               and not is_chord_line(lines[i]))


def real_artist(name):
    """Artist words, or set() for compilations like 'Misc Praise Songs' / 'Músicas Católicas'."""
    words = set(plain_words(name or ""))
    return set() if not words or words <= GENERIC_ARTISTS else words


def matching_versions(title, artist):
    """Readable chord pages for the song: [(result, draft, cleaned)]."""
    title_words = set(plain_words(title))
    artist_words = set(plain_words(artist))
    versions = []
    for result in search(title, artist):
        if len(versions) == MAX_VERSIONS:
            break
        try:
            draft = read_song_any_way(result.url)
        except (FetchError, SiteError, OSError):
            continue
        page_title = draft.title or result.label
        if not title_words <= set(plain_words(page_title)):
            continue
        page_artist = set(plain_words(draft.artist or "")) or set(plain_words(result.label + " " + result.url))
        if artist_words and not artist_words & page_artist:
            continue
        cleaned = clean_song(draft.text, draft.marked, ask=lambda line: False)
        if chord_pairs(cleaned.body) >= MIN_PAIRS:
            versions.append((result, draft, cleaned))
    return versions


def choose(title, artist):
    """(result, draft, cleaned) to use, or a reason why not."""
    if artist.casefold() in NO_ARTIST:  # "popular" isn't a name to look for
        artist = ""
    versions = matching_versions(title, artist)
    if not versions:
        return "no readable chord page with that title" + (f" by {artist}" if artist else "")
    if not artist:
        named = {}
        for result, draft, _ in versions:
            words = real_artist(draft.artist)
            if words:
                named.setdefault(frozenset(words), draft.artist)
        groups = list(named.values())
        if len(groups) > 1 and not all(set(plain_words(groups[0])) & set(plain_words(g)) for g in groups[1:]):
            return "no artist given and the pages are by different artists: " + ", ".join(groups) + \
                   " (add the artist to the list: Title - Artist)"
    return versions[0]


# ---------- writing ----------

def nice_title(typed, found):
    """The site's spelling (accents) with the capitals as typed: 'Dios está aqui' + 'Dios Está Aquí'
    -> 'Dios está aquí'. Falls back to what was typed."""
    if not found or plain_words(typed) != plain_words(found):
        return typed[:1].upper() + typed[1:]
    typed_words = re.findall(r"[^\W_]+", typed)
    found_words = re.findall(r"[^\W_]+", found)
    if len(typed_words) != len(found_words):
        return typed[:1].upper() + typed[1:]
    parts = re.split(r"([^\W_]+)", found)
    out, n = [], 0
    for part in parts:
        if re.fullmatch(r"[^\W_]+", part):
            mine = typed_words[n]
            part = part.lower() if mine.islower() else part
            n += 1
        out.append(part)
    title = "".join(out)
    return title[:1].upper() + title[1:]


def book_authors(songs_dir):
    authors = {}
    for path in songs_dir.glob("*.md"):
        try:
            autor = load_song(path).autor
        except SongError:
            continue
        if autor:
            authors.setdefault(" ".join(plain_words(autor)), autor)
    return authors


def choose_author(typed, site_artist, aliases, songs_dir):
    """A remembered alias of the site's name; else the book's spelling of the typed
    artist ('schoenstatt' -> 'Schoenstatt'); else the site's name (not compilations
    like 'Misc Praise Songs'); else the typed artist; else 'popular'."""
    if site_artist and alias_for(site_artist, aliases) != site_artist:
        return alias_for(site_artist, aliases)
    if typed:
        authors = book_authors(songs_dir)
        known = authors.get(" ".join(plain_words(typed)))
        # 'Trigo' -> 'Trigo Trece' when exactly one author in the book contains the typed words
        containing = [a for key, a in authors.items() if set(plain_words(typed)) <= set(key.split())]
        if known or len(containing) == 1:
            return known or containing[0]
    if real_artist(site_artist):
        return site_artist
    if typed:
        return " ".join(w[:1].upper() + w[1:] for w in typed.split())
    return "popular"


def find_link(title, artist):
    try:
        tracks = find_tracks(title, artist)
        if tracks:
            return tracks[0].url
        return find_video(title, artist) or ""
    except FetchError:
        return ""


def add_one(title, artist, songs_dir, aliases):
    """('added', path, details) or ('uncertain', None, reason)."""
    found = existing_song(title, songs_dir)
    if found:
        return "uncertain", None, f"already in the book as {found.stem}"
    try:
        chosen = choose(title, artist)
    except FetchError as e:
        return "uncertain", None, f"search failed ({e}); try again later"
    if isinstance(chosen, str):
        return "uncertain", None, chosen
    result, draft, cleaned = chosen

    song_title = nice_title(title, draft.title)
    autor = choose_author(artist, (draft.artist or "").strip(), aliases, songs_dir)
    capo = draft.capo or cleaned.capo
    link = find_link(song_title, autor if autor != "popular" else artist)

    path = free_path(songs_dir, slug(song_title) + "_" + slug(autor or "popular"))
    path.write_text(song_file(song_title, autor, capo, link, {}, cleaned.body), encoding="utf-8")
    try:
        load_song(path)
    except SongError as e:
        path.unlink()
        return "uncertain", None, f"the song file came out invalid ({e})"
    details = f"from {result.url}" + (f", link {link}" if link else ", no Spotify/YouTube link found")
    if cleaned.notes:
        details += "; notes: " + "; ".join(cleaned.notes)
    return "added", path, details


# ---------- report ----------

def record(report_file, section, entries):
    """Add entries under 'section:' in report_file (creating the section at the end)."""
    if not entries:
        return
    path = Path(report_file)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    header = f"{section}:"
    if header in [line.strip() for line in lines]:
        start = [line.strip() for line in lines].index(header)
        end = start + 1
        while end < len(lines) and lines[end].strip() and not lines[end].strip().endswith(":"):
            end += 1
        lines[end:end] = entries
    else:
        while lines and not lines[-1].strip():
            lines.pop()
        lines += ["", header] + entries
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Add a list of songs to the book.")
    parser.add_argument("list", type=Path, help="file with one song per line: Title - Artist")
    parser.add_argument("--section", help="only read this section of the list (e.g. Want)")
    parser.add_argument("--report", type=Path, help="add the results to this file (e.g. Checked.txt)")
    parser.add_argument("--songs-dir", type=Path, default=build.SONGS_DIR, help=argparse.SUPPRESS)
    parser.add_argument("--no-build", action="store_true", help="don't rebuild index.html afterwards")
    args = parser.parse_args()

    songs = read_list(args.list, args.section)
    if not songs:
        print("No songs in the list.")
        return 1
    aliases = load_aliases()
    added, uncertain = [], []
    for n, (title, artist) in enumerate(songs, start=1):
        if n > 1:
            time.sleep(PAUSE)
        label = title + (f" - {artist}" if artist else "")
        print(f"[{n}/{len(songs)}] {label}", flush=True)
        status, path, details = add_one(title, artist, args.songs_dir, aliases)
        print(f"    {status.upper()}: {path.name if path else ''} {details}", flush=True)
        if status == "added":
            added.append(f"{path.stem}  ({label}; {details})")
        else:
            uncertain.append(f"{label}  ({details})")

    print(f"\nAdded {len(added)}, uncertain {len(uncertain)}.")
    if args.report:
        record(args.report, "claude-added", added)
        record(args.report, "claude-uncertain", uncertain)
        print(f"Results added to {args.report}.")
    if added and not args.no_build and args.songs_dir == build.SONGS_DIR:
        build.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
