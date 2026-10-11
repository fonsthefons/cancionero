"""Add a song to the book, from a web page or typed / pasted in.

    venv/bin/python add_song.py

Asks for a link (Ultimate Guitar, Cifra Club, LaCuerda, or another site that
shows the song as plain text) or for the song itself, cleans it up (see
importer/clean.py), asks for title, author, capo, Spotify link and tags,
writes songs/<title>_<author>.md and rebuilds index.html.
"""

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import yaml

import build
from builder.songs import SongError, load_song, spanish_sort_key
from builder.tags import Taxonomy
from importer.clean import clean_song
from importer.fetch import Blocked, FetchError, browser_available, fetch
from importer.sites import Follow, SiteError, saved_page_address, site_for

ROOT = Path(__file__).parent
ALIASES_FILE = ROOT / "author_aliases.yaml"
END_MARK = "END"


# ---------- asking ----------

def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        print()
        answer = ""
    return answer or (default or "")


def ask_yes(prompt, default=False):
    answer = ask(f"{prompt} ({'Y/n' if default else 'y/N'})").lower()
    return default if not answer else answer.startswith(("y", "s"))


def read_pasted():
    print(f"Paste the song (chords above the lyrics). When done, type {END_MARK} on its own line"
          " (or press Ctrl-D):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == END_MARK:
            break
        lines.append(line)
    return "\n".join(lines)


def ask_chord_line(line):
    return ask_yes(f'Is this a line of chords?  "{line.strip()}"', default=True)


# ---------- getting the song ----------

def from_link(link):
    """(Draft, link) from a link or a saved page, or None on failure."""
    use_browser = False
    for _ in range(3):  # a site may send us to the page that holds the song
        try:
            path = Path(link).expanduser()
            if path.is_file():  # a page saved from the browser
                page = path.read_text(encoding="utf-8")
                link = saved_page_address(page) or link
            else:
                page = fetch(link, use_browser)
            draft = site_for(link).parse(page, link)
        except Blocked:
            if use_browser or not offer_browser():
                print("Tip: open the page, copy the song, then choose option 2 and paste it.")
                return None
            use_browser = True
            continue
        except (FetchError, SiteError, OSError) as e:
            print(f"Couldn't read the song: {e}.")
            return None
        if isinstance(draft, Follow):
            link = draft.url
            continue
        return draft
    print("Couldn't find the song on that page.")
    return None


def offer_browser():
    """Blocked site: use (and if needed install) the headless browser engine."""
    print("This site only lets real browsers in, so it has to be opened in a hidden browser.")
    if browser_available():
        return True
    if not ask_yes("That needs a browser engine (about 100 MB, installed once). Install it now?"):
        return False
    for command in (
        [sys.executable, "-m", "pip", "install", "playwright"],
        [sys.executable, "-m", "playwright", "install", "webkit"],
    ):
        if subprocess.run(command).returncode != 0:
            print("The installation failed.")
            return False
    return browser_available()


# ---------- details ----------

def load_aliases():
    if not ALIASES_FILE.exists():
        return {}
    return {str(k): str(v) for k, v in (yaml.safe_load(ALIASES_FILE.read_text(encoding="utf-8")) or {}).items()}


def alias_for(artist, aliases):
    lowered = {k.casefold(): v for k, v in aliases.items()}
    return lowered.get(artist.casefold(), artist)


def remember_alias(site_name, book_name):
    with ALIASES_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{yaml_value(site_name)}: {yaml_value(book_name)}\n")
    print(f'Remembered: "{site_name}" will be written "{book_name}" next time.')


def ask_tags(taxonomy):
    choices = []
    for tag in taxonomy.tags.values():
        if tag.is_flat:
            choices.append((tag.id, None, tag.label))
        for sub_id, sub_label in tag.subtags.items():
            choices.append((tag.id, sub_id, f"{tag.label}: {sub_label}"))
    print("\nTags:")
    for number, (_, _, label) in enumerate(choices, start=1):
        print(f"  {number:2}  {label}")
    while True:
        answer = ask("Tag numbers, separated by spaces (Enter for none)")
        numbers = answer.replace(",", " ").split()
        if all(n.isdigit() and 1 <= int(n) <= len(choices) for n in numbers):
            break
        print(f"Please type numbers between 1 and {len(choices)}.")
    tags = {}
    for n in numbers:
        tag_id, sub_id, _ = choices[int(n) - 1]
        subtags = tags.setdefault(tag_id, [])
        if sub_id and sub_id not in subtags:
            subtags.append(sub_id)
    return tags


def existing_song(title, songs_dir):
    key = spanish_sort_key(title)
    for path in sorted(songs_dir.glob("*.md")):
        try:
            if spanish_sort_key(load_song(path).title) == key:
                return path
        except (SongError, yaml.YAMLError):
            continue
    return None


# ---------- writing ----------

def slug(text):
    plain = unicodedata.normalize("NFD", text.casefold())
    plain = "".join(c for c in plain if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", plain).strip("_")


def yaml_value(text):
    """Text as a YAML value: plain if YAML reads it back unchanged, else quoted."""
    try:
        if yaml.safe_load(f"k: {text}") == {"k": text}:
            return text
    except yaml.YAMLError:
        pass
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def song_file(title, autor, capo, link, tags, body):
    lines = ["---", f"title: {yaml_value(title)}"]
    if autor:
        lines.append(f"autor: {yaml_value(autor)}")
    if capo:
        lines.append(f'capo: "{capo}"')
    if link:
        lines.append(f'link: "{link}"')
    if tags:
        lines.append("song_tags:")
        for tag_id, subtags in tags.items():
            if subtags:
                lines.append(f"  {tag_id}:")
                lines.extend(f"    - {sub}" for sub in subtags)
            else:
                lines.append(f"  {tag_id}: []")
    return "\n".join(lines + ["---", "", body, ""])


def free_path(songs_dir, name):
    path = songs_dir / f"{name}.md"
    number = 2
    while path.exists():
        path = songs_dir / f"{name}_{number}.md"
        number += 1
    return path


# ---------- main ----------

def main():
    global ALIASES_FILE
    parser = argparse.ArgumentParser(description="Add a song to the book.")
    parser.add_argument("--songs-dir", type=Path, default=build.SONGS_DIR, help=argparse.SUPPRESS)
    parser.add_argument("--aliases-file", type=Path, default=ALIASES_FILE, help=argparse.SUPPRESS)
    parser.add_argument("--no-build", action="store_true", help="don't rebuild index.html afterwards")
    args = parser.parse_args()
    songs_dir = args.songs_dir
    ALIASES_FILE = args.aliases_file
    taxonomy = Taxonomy.load(build.TAGS_FILE)

    print("Add a song to the book\n")
    print("  1) From a web page (Ultimate Guitar, Cifra Club, LaCuerda or another site)")
    print("  2) Type or paste it in")
    choice = ask("Choose 1 or 2", "1")

    draft = None
    if choice == "1":
        link = ask("Link to the song (or a saved web page file)")
        draft = from_link(link) if link else None
        if draft is None and not ask_yes("Paste the song instead?", default=True):
            return 1
    text = draft.text if draft else read_pasted()
    if not text.strip():
        print("No song text, nothing added.")
        return 1

    cleaned = clean_song(text, marked=draft.marked if draft else False, ask=ask_chord_line)
    print("\n" + "-" * 60 + "\n" + cleaned.body + "\n" + "-" * 60)
    for note in cleaned.notes:
        print(f"* {note}")
    if not ask_yes("\nDoes the song look right?", default=True):
        print("Nothing added. Tip: paste the song (option 2) and fix it by hand, or fix the file after adding it.")
        return 1

    print()
    title = ask("Title", draft.title if draft else None)
    while not title:
        title = ask("Title (required)")
    found = existing_song(title, songs_dir)
    if found and not ask_yes(f'"{title}" is already in the book ({found.name}). Add it anyway?'):
        return 1

    aliases = load_aliases()
    site_artist = (draft.artist or "").strip() if draft else ""
    autor = ask("Author", alias_for(site_artist, aliases) if site_artist else "popular")
    if site_artist and autor and autor != alias_for(site_artist, aliases) and autor != site_artist:
        remember_alias(site_artist, autor)
    capo = ask("Capo (Enter for none)", (draft.capo if draft else None) or cleaned.capo)
    link = ask("Spotify link (Enter for none)")
    while link and not re.match(r"https?://", link):
        link = ask("The link must start with https:// (Enter for none)")
    tags = ask_tags(taxonomy)

    path = free_path(songs_dir, slug(title) + "_" + slug(autor or "popular"))
    path.write_text(song_file(title, autor, capo, link, tags, cleaned.body), encoding="utf-8")
    try:
        load_song(path)
        problems = taxonomy.validate(load_song(path).tags)
    except (SongError, yaml.YAMLError) as e:
        problems = [str(e)]
    if problems:
        path.unlink()
        print("Couldn't add the song:\n  " + "\n  ".join(problems))
        return 1

    print(f"\nAdded {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    if not tags:
        print("It has no tags yet, so it only appears in All Songs.")
    if not args.no_build and songs_dir == build.SONGS_DIR:
        build.main()
        print("Open index.html to check it, then commit the song and index.html.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled, nothing added.")
        sys.exit(1)
