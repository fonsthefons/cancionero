"""Build the song book: songs/*.md -> index.html (one self-contained page).

    python build.py
"""

import sys
from pathlib import Path

from builder.render import render_book
from builder.songs import SongError, load_songs
from builder.tags import Taxonomy

ROOT = Path(__file__).parent
SONGS_DIR = ROOT / "songs"
TAGS_FILE = ROOT / "tags.yaml"
WEB_DIR = ROOT / "web"
OUTPUT = ROOT / "index.html"  # must stay at the repo root for GitHub Pages


def main():
    taxonomy = Taxonomy.load(TAGS_FILE)
    try:
        songs = load_songs(SONGS_DIR, taxonomy)
    except SongError as e:
        print(e, file=sys.stderr)
        return 1

    untagged = [song.id for song in songs if not song.tags]
    if untagged:
        print(f"Warning: songs without tags: {', '.join(untagged)}", file=sys.stderr)

    html = render_book(songs, taxonomy.group(songs), WEB_DIR)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Built {OUTPUT.name}: {len(songs)} songs, {len(html) / 1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
