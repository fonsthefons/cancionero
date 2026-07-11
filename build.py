import html
import json
import os
import re
import shutil
import sys
import yaml

HYMNS_DIR = "songs"
OUTPUT_DIR = "output"
ROOT_HTML = "index.html"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "book.md")
OUTPUT_PDF_MD = os.path.join(OUTPUT_DIR, "book-pdf.md")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "book.pdf")
OUTPUT_HTML = os.path.join(OUTPUT_DIR, "index.html")
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
    r"(?:/[A-G](?:#|b)?(?:m|maj|min|dim|aug|sus|add|dom)?\d*)?"
    r")"
    r"(?!\w)"
)

SEPARATOR_RE = re.compile(r"^[-|]+$")  # allows -, --, |, || etc.


def hymn_anchor(number, uniqueId):
    slug = re.sub(r"[^\w\s-]", "", uniqueId.lower())
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
            tag: list(subtags) if subtags else [] for tag, subtags in raw.items()
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
                errors.append(f'  {title}: "{tag}" has no subtags — use `{tag}: []`')
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
            fname = meta.get("fname", file)
            categories = parse_song_tags(meta)
            capo = meta.get("capo")
            if capo is not None:
                capo = str(capo).strip() or None

            all_errors.extend(validate_categories(title, categories))

            songs.append(
                {
                    "fname": fname,
                    "title": title,
                    "autor": meta.get("autor") or None,
                    "link": meta.get("link") or None,
                    "capo": capo,
                    "categories": categories,
                    "content": body,
                }
            )

    if all_errors:
        print("Tag errors:", file=sys.stderr)
        for error in all_errors:
            print(error, file=sys.stderr)
        sys.exit(1)

    songs.sort(key=lambda x: x["title"].casefold())

    for number, song in enumerate(songs, start=1):
        song["number"] = number
        song["heading"] = f"{number}. {song['title']}"
        song["anchor"] = hymn_anchor(number, song["fname"])

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


def write_song_link_html(f, song, indent=False):
    prefix = "&nbsp;&nbsp;" if indent else ""
    autor = song.get("autor") or ""
    text = f"{song['heading']}{f' - {autor}' if autor else ''}"

    f.write(f'{prefix}<a href="#{song["anchor"]}">{text}</a><br>\n')


def write_tag_sections_html(f, grouped):
    for tag in sorted(grouped.keys(), key=tag_sort_key):
        f.write(f'<h2 id="{tag}">{format_label(tag)}</h2>\n')

        subgroups = grouped[tag]

        # flat songs
        for h in sorted(subgroups.get("_ungrouped", []), key=lambda x: x["number"]):
            write_song_link_html(f, h)

        subtags = sorted(
            (k for k in subgroups if k != "_ungrouped"),
            key=lambda k: subtag_sort_key(tag, k),
        )

        for subtag in subtags:
            f.write(f'<h3 id="{tag}-{subtag}">{format_label(subtag)}</h3>\n')

            for h in sorted(subgroups[subtag], key=lambda x: x["number"]):
                write_song_link_html(f, h, indent=True)

        f.write("<br>\n")


def split_embedded_chords(token):
    return re.split(r"-", token)


def extract_chords(token):
    # Find all chord-like matches inside the token
    return CHORD_RE.findall(token)


def is_chord_line(line):
    stripped = line.strip()

    if not stripped:
        return False

    tokens = re.split(r"\s+", stripped)

    has_chord = False

    for token in tokens:
        # Extract all chords inside token
        chords = extract_chords(token)

        if chords:
            has_chord = True
            continue

        # Allow pure separators
        if re.fullmatch(r"[-|()]+", token):
            continue

        # If token has no chords and isn't just separators → fail
        return False

    return has_chord


def format_lyrics(content):
    verses = []
    lines = []

    # Split verses: two or more newlines = verse break
    raw_verses = re.split(r"\n\s*\n", content.strip())

    for verse in raw_verses:
        pending_chord = None
        verse_lines = []

        for line in verse.split("\n"):
            working_line = line.replace("\xa0", " ").expandtabs(2)
            stripped = working_line.strip()

            # escape + preserve spacing
            escaped = html.escape(working_line, quote=False).replace(" ", "&nbsp;")

            if not stripped:
                continue

            elif is_chord_line(line):
                wrapped = CHORD_RE.sub(r'<span class="chord">\1</span>', escaped)

                pending_chord = f'<span class="chord-line">{wrapped}</span>'

            else:
                lyric_line = f'<span class="lyric-line">{escaped}</span>'

                if pending_chord:
                    verse_lines.append(
                        '<div class="chord-lyric-line-pair">'
                        + pending_chord
                        + lyric_line
                        + "</div>"
                    )
                    pending_chord = None
                else:
                    verse_lines.append(lyric_line)

        # flush trailing chord line in this verse
        if pending_chord:
            verse_lines.append(
                '<div class="chord-lyric-line-pair">' + pending_chord + "</div>"
            )

        if verse_lines:
            verses.append('<div class="verse">' + "".join(verse_lines) + "</div>")

    return '<div class="lyrics">' + "".join(verses) + "</div>"


def write_song_meta(f, song):
    if song.get("autor"):
        f.write(f"*Autor: {song['autor']}*\n\n")
    if song.get("capo") is not None:
        f.write(f"*Capo: {song['capo']}*\n\n")
    if song.get("link"):
        f.write(f"[Link]({song['link']})\n\n")


def write_all_songs_links(f, songs):
    f.write('<h2 id="all-songs-list">All Songs</h2>\n')

    for s in songs:
        autor = s.get("autor") or ""
        text = f"{s['heading']}{f' - {autor}' if autor else ''}"

        f.write(f'<a href="#{s["anchor"]}">{text}</a><br>\n')


# Mini Index of indexes
def write_mini_toc_html(f, grouped):
    f.write('<div class="mini-toc">\n')
    f.write("<h2>Contenido</h2>\n")

    # 🔥 All Songs link
    f.write(f'<a href="#all-songs-list" class="mini-toc-tag">All Songs</a><br>\n')
    f.write("<hr>\n")

    for tag in sorted(grouped.keys(), key=tag_sort_key):
        f.write(f'<a href="#{tag}" class="mini-toc-tag">{format_label(tag)}</a><br>\n')

        subgroups = grouped[tag]

        subtags = sorted(
            (k for k in subgroups if k != "_ungrouped"),
            key=lambda k: subtag_sort_key(tag, k),
        )

        for subtag in subtags:
            f.write(
                f'&nbsp;&nbsp;<a href="#{tag}-{subtag}" class="mini-toc-subtag">{format_label(subtag)}</a><br>\n'
            )
        f.write("<hr>\n")

    f.write(f'<a href="#settings" class="mini-toc-tag">Settings</a><br>\n')
    f.write("</div>\n")


def write_html_book(output_path, songs, grouped):
    with open(output_path, "w", encoding="utf-8") as f:

        # =========================
        # HTML HEAD (FROM YOUR example.html)
        # =========================
        f.write(
            """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cancionero</title>
            </head>
            <body>
            """
        )

        # ---- INSERT YOUR FULL CSS HERE ----
        with open("book.css", "r", encoding="utf-8") as ccs_file:
            book_css = ccs_file.read()
        f.write(f"<style>\n{book_css}\n</style>\n")

        # ---- INSERT YOUR FULL JS HERE ----
        with open("assets.js", "r", encoding="utf-8") as js_file:
            script = js_file.read()
            f.write(f"""<script>{script}</script>""")

        f.write("</head><body>\n")

        # MINI TOC SIDEBAR
        f.write(
            """
            <div id="toc-sidebar" class="toc-sidebar">
                <div class="toc-content">
        """
        )
        write_mini_toc_html(f, grouped)
        f.write(
            """
                </div>
                <div id="search-container-toc" class="search-container-toc">
                    <input id="search-box-toc" type="search" placeholder="Search songs...">
                    <div id="search-results-toc"></div>
                </div>
            </div>
            <button id="toc-toggle" class="toc-toggle">➤</button>
        """
        )

        # =========================
        # HEADER
        # =========================
        f.write("<h1>Cancionero</h1>\n")

        # =========================
        # SEARCH UI (now REAL HTML, not escaped)
        # =========================
        f.write(
            """
            <div id="search-container-main">
                <input id="search-box-main" type="search" placeholder="Search songs...">
                <div id="search-results-main"></div>
            </div>
        """
        )

        # =========================
        # MINI TOC (TOP NAV)
        # =========================
        write_mini_toc_html(f, grouped)
        f.write("<hr>\n")

        # =========================
        # FULL CONTENTS TABLE
        # =========================
        write_tag_sections_html(f, grouped)
        f.write("<hr>\n")

        # =========================
        # ALL SONGS (IN CONTENTS)
        # =========================
        write_all_songs_links(f, songs)
        f.write("<hr>\n")

        # =========================
        # ALL SONGS
        # =========================
        f.write("<hr>\n")
        f.write("<h1>All Songs</h1>\n")

        search_index = []

        for h in songs:
            autor = h.get("autor") or ""
            heading_text = f"{h['heading']}{f' - {autor}' if autor else ''}"

            f.write(
                f'<div class="song" data-song-id="{h["fname"]}" id="{h["anchor"]}">\n'
            )

            # ---- TITLE ----
            f.write(f"<h3>{heading_text}</h3>\n")

            # ---- CONTROLS ----
            f.write(
                """
                <div class="controls">
                    <button class="toggle-chords">Toggle chords</button>
                    <div class="transpose-controls">
                        <button class="transpose-down">-</button>
                        <span class="transpose-value">0</span>
                        <button class="transpose-up">+</button>
                    </div>
                    <button class="toggle-columns">Toggle columns</button>
                </div>
            """
            )

            # ---- META ----
            if h.get("autor"):
                f.write(f'<p><em>Autor: {h["autor"]}</em></p>\n')
            if h.get("capo") is not None:
                f.write(f'<p><em>Capo: {h["capo"]}</em></p>\n')
            if h.get("link"):
                f.write(f'<p><a href="{h["link"]}" target="_blank">Link</a></p>\n')

            # ---- LYRICS (YOUR FUNCTION, UNTOUCHED) ----
            f.write(format_lyrics(h["content"]))

            f.write("<hr>\n")

            f.write("</div>\n\n")

            # ---- Create SEARCH INDEX ----
            search_index.append(
                {
                    "id": h["anchor"],
                    "title": h["heading"],
                    "author": h.get("autor", ""),
                    "text": h["content"],
                }
            )

        f.write("<hr>\n")
        f.write(
            """
            <div class="settings" id="settings">
                <h1>Settings</h1>
                <button id="toggle-all-chords">Hide all chords</button>
                <button id="toggle-global-columns">2 columns</button>
                <button id="print-button">Print</button>
                <div id="print-dialog" class="print-dialog">
                    <h3>Print settings</h3>
                    <label>
                        Columns:
                        <select id="print-columns">
                            <option value="1">1 column</option>
                            <option value="2">2 columns</option>
                        </select>
                    </label>

                    <br>

                    <label>
                        Chords:
                        <select id="print-chords">
                            <option value="on">Show chords</option>
                            <option value="off">Hide chords</option>
                        </select>
                    </label>

                    <br><br>

                    <button id="confirm-print">
                        Print PDF
                    </button>

                </div>
            </div>
        """
        )
        # =========================
        # SAVE SEARCH INDEX
        # =========================
        f.write("<script>\n")
        f.write("const SONG_INDEX = ")
        json.dump(search_index, f, ensure_ascii=False)
        f.write(";\n</script>\n")

        f.write("</body></html>")


if __name__ == "__main__":
    print("[START]: Gathering all songs")
    songs = get_all_songs()
    print("[END]: Gathering all songs")
    print("[START]: Grouping all songs")
    grouped = group_songs(songs)
    print("[END]: Grouping all songs")
    print("[START]: Writing HTML BOOK")
    write_html_book(OUTPUT_HTML, songs, grouped)
    print("[END]: Writing HTML BOOK")
    print("[START]: Copying HTML BOOK TO INDEX")
    shutil.copyfile(OUTPUT_HTML, ROOT_HTML)
    print("[END]: Copying HTML BOOK TO INDEX")
