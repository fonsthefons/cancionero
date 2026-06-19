import os
import yaml

from build import (
    group_songs,
    get_all_songs,
    read_hymn,
    write_obsidian_book,
)

HYMNS_DIR = "songs"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "book.md")


def build_book():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    songs = get_all_songs()
    grouped = group_songs(songs)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_obsidian_book(f, songs, grouped)

    print(f"Book generated at {OUTPUT_FILE}")


if __name__ == "__main__":
    build_book()
