import argparse
import html
import os
import re
import subprocess
import sys
import yaml

HYMNS_DIR = "songs"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "book.md")
OUTPUT_PDF_MD = os.path.join(OUTPUT_DIR, "book-pdf.md")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "book.pdf")
OUTPUT_HTML = os.path.join(OUTPUT_DIR, "book.html")
PANDOC_HEADER = os.path.join(OUTPUT_DIR, "pandoc-header.html")

# Tags with a fixed list of subtags (in display order)
TAG_WITH_SUBTAGS = {
    "misa": [
        "entrada",
        "gloria",
        "aleluya",
        "ofertorio",
        "santo",
        "cordero",
        "comunion",
        "salida",
    ],
    "alabanza": [
        "primer_ciclo",
        "segundo_ciclo",
        "tercer_ciclo",
        "cuarto_ciclo",
    ],
    "tema": [
        "padre",
        "cristo",
        "espiritu",
        "santo",
        "martir",
        "virgen",
    ],
}

# Tags with no subtags — songs are listed directly under the tag heading
FLAT_TAGS = [
    "adoracion",
]

TAG_ORDER = ["misa", "alabanza", "adoracion", "tema"]

LYRICS_CSS = """
.lyrics {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: inherit;
  margin: 1em 0;
  border: none;
  background: none;
  padding: 0;
}
.lyrics strong {
  font-weight: bold;
}
"""

# Matches standard chord symbols: Em, B7, Cmaj7, D/F#, G#m, Bb, Asus4, etc.
CHORD_RE = re.compile(
    r"(?<!\w)"
    r"("
    r"[A-G]"
    r"(?:#|b)?"
    r"(?:"
    r"(?:maj|min|dim|aug|sus|add|dom)\d*"
    r"|"
    r"m\d*"
    r"|"
    r"\d+"
    r")?"
    r"(?:\/[A-G](?:#|b)?)?"
    r")"
    r"(?!\w)"
)


def hymn_anchor(number, title):
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return f"hymn-{number}-{slug}"


def read_hymn(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        _, frontmatter, body = content.split("---", 2)
        meta = yaml.safe_load(frontmatter)
        return meta, body.strip()

    return {}, content


def parse_song_tags(meta):
    """Parse song_tags as {tag: [subtag, ...]}. Flat tags use an empty list."""
    raw = meta.get("song_tags", {})

    if isinstance(raw, dict):
        categories = {
            tag: list(subtags) if subtags else []
            for tag, subtags in raw.items()
        }
    elif isinstance(raw, list):
        categories = {tag: [] for tag in raw}
    else:
        categories = {}

    return categories


def validate_categories(title, categories):
    errors = []

    for tag, subtags in categories.items():
        if tag in TAG_WITH_SUBTAGS:
            allowed = TAG_WITH_SUBTAGS[tag]
            if not subtags:
                errors.append(
                    f'  {title}: "{tag}" requires at least one subtag '
                    f"({', '.join(allowed)})"
                )
            for subtag in subtags:
                if subtag not in allowed:
                    errors.append(
                        f'  {title}: unknown subtag "{subtag}" under "{tag}" '
                        f"(allowed: {', '.join(allowed)})"
                    )
        elif tag in FLAT_TAGS:
            if subtags:
                errors.append(
                    f'  {title}: "{tag}" has no subtags — use `{tag}: []`'
                )
        else:
            errors.append(f'  {title}: unknown tag "{tag}"')

    return errors


def format_label(name):
    return name.replace("_", " ").capitalize()


def tag_sort_key(tag):
    if tag in TAG_ORDER:
        return (0, TAG_ORDER.index(tag))
    return (1, tag)


def subtag_sort_key(tag, subtag):
    allowed = TAG_WITH_SUBTAGS.get(tag, [])
    if subtag in allowed:
        return allowed.index(subtag)
    return len(allowed)


def get_all_songs():
    songs = []
    all_errors = []

    for file in os.listdir(HYMNS_DIR):
        if file.endswith(".md"):
            meta, body = read_hymn(os.path.join(HYMNS_DIR, file))
            title = meta.get("title", file)
            categories = parse_song_tags(meta)
            capo = meta.get("capo")
            if capo is not None:
                capo = str(capo).strip() or None

            all_errors.extend(validate_categories(title, categories))

            songs.append({
                "title": title,
                "autor": meta.get("autor") or None,
                "link": meta.get("link") or None,
                "capo": capo,
                "categories": categories,
                "content": body,
            })

    if all_errors:
        print("Tag errors:", file=sys.stderr)
        for error in all_errors:
            print(error, file=sys.stderr)
        sys.exit(1)

    songs.sort(key=lambda x: x["title"].casefold())

    for number, song in enumerate(songs, start=1):
        song["number"] = number
        song["heading"] = f"{number}. {song['title']}"
        song["anchor"] = hymn_anchor(number, song["title"])

    return songs


def group_songs(songs):
    grouped = {}

    for song in songs:
        for tag, subtags in song["categories"].items():
            if tag not in grouped:
                grouped[tag] = {}

            if subtags:
                for subtag in subtags:
                    grouped[tag].setdefault(subtag, []).append(song)
            else:
                grouped[tag].setdefault("_ungrouped", []).append(song)

    return grouped


# def write_tag_sections(f, grouped, link_fn):
#     for tag in sorted(grouped.keys(), key=tag_sort_key):
#         subgroups = grouped[tag]
#         f.write(f"\n# {format_label(tag)}\n\n")

#         for h in sorted(subgroups.get("_ungrouped", []), key=lambda x: x["number"]):
#             f.write(link_fn(h))

#         subtags = sorted(
#             (k for k in subgroups if k != "_ungrouped"),
#             key=lambda k: subtag_sort_key(tag, k),
#         )
#         for subtag in subtags:
#             f.write(f"- {format_label(subtag)}\n")
#             for h in sorted(subgroups[subtag], key=lambda x: x["number"]):
#                 f.write(link_fn(h, indent=1))

#         f.write("\n")
def write_tag_sections(f, grouped, link_fn):
    for tag in sorted(grouped.keys(), key=tag_sort_key):
        subgroups = grouped[tag]
        
        # Main Section Title (Level 1 Heading)
        f.write(f"\n# {format_label(tag)}\n\n")

        # Flat songs if any
        for h in sorted(subgroups.get("_ungrouped", []), key=lambda x: x["number"]):
            f.write(link_fn(h))

        subtags = sorted(
            (k for k in subgroups if k != "_ungrouped"),
            key=lambda k: subtag_sort_key(tag, k),
        )
        
        for subtag in subtags:
            # Change to Heading 2 so it appears in the TOC sidebar as a nested item
            f.write(f"\n## {format_label(subtag)}\n\n")
            
            # Songs under this subsection
            for h in sorted(grouped[tag][subtag], key=lambda x: x["number"]):
                f.write(link_fn(h, indent=1))
        # Add a blank line to separate sections cleanly
        f.write("\n")



def bold_chords(line):
    return CHORD_RE.sub(r"<strong>\1</strong>", line)


def format_lyrics(content):
    lines = [bold_chords(html.escape(line)) for line in content.split("\n")]
    return f'<pre class="lyrics">{"\n".join(lines)}</pre>'


def write_song_meta(f, song):
    if song.get("autor"):
        f.write(f"*Autor: {song['autor']}*\n\n")
    if song.get("capo") is not None:
        f.write(f"*Capo: {song['capo']}*\n\n")
    if song.get("link"):
        f.write(f"[Link]({song['link']})\n\n")


def write_obsidian_book(f, songs, grouped):
    f.write("# Hymn Book\n\n")

    def link(song, indent=0):
        prefix = "  " * indent
        return f"{prefix}- [[#{song['heading']}]]\n"

    write_tag_sections(f, grouped, link)

    f.write("## All Songs\n\n")
    for h in songs:
        f.write(f"### {h['heading']}\n\n")
        write_song_meta(f, h)
        f.write(h["content"] + "\n\n---\n\n")




def write_pdf_book(f, songs, grouped):
    f.write("# Hymn Book\n\n")

    def link(song, indent=0):
        prefix = "  " * indent
        return f"{prefix}- [{song['heading']}](#{song['anchor']})\n"

    write_tag_sections(f, grouped, link)

    f.write("## All Songs\n\n")
    for h in songs:
        f.write(f"### {h['heading']} {{#{h['anchor']}}}\n\n")
        write_song_meta(f, h)
        f.write(format_lyrics(h["content"]) + "\n\n---\n\n")


def build_html():
    with open(PANDOC_HEADER, "w", encoding="utf-8") as f:
        f.write(f"<style>{LYRICS_CSS}</style>\n")

    subprocess.run(
        [
            "pandoc",
            OUTPUT_PDF_MD,
            "-o",
            OUTPUT_HTML,
            "--toc",
            "--standalone",
            "-H",
            PANDOC_HEADER,
        ],
        check=True,
    )


def build_pdf():
    subprocess.run(
        [
            "pandoc",
            OUTPUT_PDF_MD,
            "-o",
            OUTPUT_PDF,
            "--toc",
            "-V",
            "geometry:margin=1in",
        ],
        check=True,
    )


def build_book(pdf=False, html=False):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    songs = get_all_songs()
    grouped = group_songs(songs)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_obsidian_book(f, songs, grouped)
    print(f"Obsidian book generated at {OUTPUT_FILE}")

    with open(OUTPUT_PDF_MD, "w", encoding="utf-8") as f:
        write_pdf_book(f, songs, grouped)
    print(f"PDF source generated at {OUTPUT_PDF_MD}")

    if html:
        build_html()
        print(f"HTML generated at {OUTPUT_HTML}")

    if pdf:
        build_pdf()
        print(f"PDF generated at {OUTPUT_PDF}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the hymn book")
    parser.add_argument(
        "--html",
        action="store_true",
        help="Also generate output/book.html via pandoc",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also generate output/book.pdf via pandoc",
    )
    args = parser.parse_args()

    try:
        build_book(pdf=args.pdf, html=args.html)
    except subprocess.CalledProcessError as exc:
        print(f"Pandoc failed with exit code {exc.returncode}", file=sys.stderr)
        sys.exit(exc.returncode)
