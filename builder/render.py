"""Rendering the whole book into one self-contained HTML page.

The page layout lives in web/template.html; this module only fills its
`{{ placeholders }}` with HTML fragments built from the songs.
"""

import re
from html import escape
from pathlib import Path

from .lyrics import lyrics_columns, lyrics_html

PLACEHOLDER_RE = re.compile(r"{{\s*(\w+)\s*}}")


def fill_template(template, values):
    """Replace each {{ name }} once; inserted values are never re-scanned."""

    def replace(match):
        name = match.group(1)
        if name not in values:
            raise KeyError(f"template placeholder {{{{ {name} }}}} has no value")
        return values[name]

    return PLACEHOLDER_RE.sub(replace, template)


def tag_anchor(tag_id, subtag_id=None):
    return f"tag-{tag_id}" + (f"-{subtag_id}" if subtag_id else "")


def song_label(song):
    return f"{song.heading} - {song.autor}" if song.autor else song.heading


def song_link(song):
    return f'<li><a href="#{song.anchor}">{escape(song_label(song))}</a></li>'


def song_list(songs):
    return '<ul class="song-list">\n' + "\n".join(map(song_link, songs)) + "\n</ul>"


def collapsible(anchor, heading_tag, title, body, css_class, open_=False):
    """A section that can be folded away; folded by default (printing unfolds all)."""
    return (
        f'<details class="{css_class}" id="{anchor}"{" open" if open_ else ""}>'
        f"<summary><{heading_tag}>{escape(title)}</{heading_tag}></summary>\n"
        f"{body}\n</details>"
    )


def nav_html(groups):
    """Compact table of contents (tags and subtags) for the menu drawer."""
    items = [
        '<li><a class="nav-tag" href="#index">Contenido</a></li>',
        '<li><a class="nav-tag" href="#all-songs">All Songs</a></li>',
    ]
    for group in groups:
        subtags = "".join(
            f'<li><a class="nav-subtag" href="#{tag_anchor(group.tag.id, sub_id)}">'
            f"{escape(label)}</a></li>"
            for sub_id, label, _ in group.subgroups
        )
        items.append(
            f'<li><a class="nav-tag" href="#{tag_anchor(group.tag.id)}">'
            f"{escape(group.tag.label)}</a>"
            + (f'<ul class="nav-subtags">{subtags}</ul>' if subtags else "")
            + "</li>"
        )
    return '<ul class="nav">\n' + "\n".join(items) + "\n</ul>"


def tag_index_html(groups):
    """Full index: every tag/subtag with the songs it contains."""
    sections = []
    for group in groups:
        parts = [song_list(group.songs)] if group.songs else []
        for sub_id, label, songs in group.subgroups:
            parts.append(
                collapsible(
                    tag_anchor(group.tag.id, sub_id), "h3", label, song_list(songs), "subtag-index"
                )
            )
        sections.append(
            collapsible(
                tag_anchor(group.tag.id), "h2", group.tag.label, "\n".join(parts), "tag-index"
            )
        )
    return "\n".join(sections)


def song_meta_html(song):
    items = []
    if song.autor:
        items.append(f'<span class="meta-item">Autor: {escape(song.autor)}</span>')
    if song.capo:
        items.append(f'<span class="meta-item">Capo: {escape(song.capo)}</span>')
    if song.link:
        items.append(
            f'<a class="meta-item" href="{escape(song.link)}" target="_blank" rel="noopener">Link</a>'
        )
    return f'<p class="song-meta">{"".join(items)}</p>' if items else ""


def song_html(song, controls):
    # --chars (widest line) lets CSS size the lyrics so every line fits the screen.
    # data-title / data-autor: plain values for the session list and search.
    autor = f' data-autor="{escape(song.autor)}"' if song.autor else ""
    return (
        f'<article class="song" id="{song.anchor}" data-title="{escape(song.title)}"{autor} '
        f'style="--chars: {lyrics_columns(song.body)}">\n'
        f"<h3>{escape(song_label(song))}</h3>\n"
        f"{song_meta_html(song)}\n"
        f"{controls}\n"
        f"{lyrics_html(song.body)}\n"
        "</article>"
    )


def render_book(songs, groups, web_dir):
    web = Path(web_dir)

    def read(name):
        return (web / name).read_text(encoding="utf-8")

    # core.js first (it defines helpers the feature scripts use), then the rest.
    scripts = [web / "js" / "core.js"] + sorted(
        p for p in (web / "js").glob("*.js") if p.name != "core.js"
    )
    controls = read("song-controls.html").strip()

    return fill_template(
        read("template.html"),
        {
            "css": read("styles.css"),
            "scripts": "\n".join(
                f"<script>\n{p.read_text(encoding='utf-8')}</script>" for p in scripts
            ),
            "nav": nav_html(groups),
            "tag_index": tag_index_html(groups),
            "all_songs": collapsible(
                "all-songs", "h2", "All Songs", song_list(songs), "tag-index", open_=True
            ),
            "songs": "\n".join(song_html(song, controls) for song in songs),
        },
    )
