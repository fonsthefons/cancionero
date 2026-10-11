"""Tag taxonomy (loaded from tags.yaml) and grouping of songs by tag."""

from dataclasses import dataclass, field

import yaml


@dataclass
class Tag:
    id: str
    label: str
    subtags: dict[str, str] = field(default_factory=dict)  # id -> label, in order

    @property
    def is_flat(self):
        return not self.subtags


@dataclass
class TagGroup:
    """Songs of one tag, ready to render: flat songs plus (subtag label, songs)."""

    tag: Tag
    songs: list
    subgroups: list[tuple[str, str, list]]  # (subtag id, subtag label, songs)


class Taxonomy:
    def __init__(self, tags):
        self.tags = {tag.id: tag for tag in tags}

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return cls(
            Tag(id=tag_id, label=spec["label"], subtags=dict(spec.get("subtags") or {}))
            for tag_id, spec in raw.items()
        )

    def validate(self, song_tags):
        """Return a list of error messages for a song's {tag: [subtags]} dict."""
        errors = []
        for tag_id, subtags in song_tags.items():
            tag = self.tags.get(tag_id)
            if tag is None:
                errors.append(f'unknown tag "{tag_id}" (allowed: {", ".join(self.tags)})')
            elif tag.is_flat and subtags:
                errors.append(f'"{tag_id}" has no subtags, use `{tag_id}: []`')
            elif not tag.is_flat and not subtags:
                errors.append(
                    f'"{tag_id}" needs at least one subtag ({", ".join(tag.subtags)})'
                )
            else:
                for subtag in subtags:
                    if subtag not in tag.subtags:
                        errors.append(
                            f'unknown subtag "{subtag}" under "{tag_id}" '
                            f'(allowed: {", ".join(tag.subtags)})'
                        )
        return errors

    def group(self, songs):
        """Group songs by tag/subtag, in taxonomy order, skipping empty groups."""
        groups = []
        for tag in self.tags.values():
            tagged = [song for song in songs if tag.id in song.tags]
            if not tagged:
                continue
            flat = [song for song in tagged if not song.tags[tag.id]]
            subgroups = []
            for subtag_id, label in tag.subtags.items():
                members = [song for song in tagged if subtag_id in song.tags[tag.id]]
                if members:
                    subgroups.append((subtag_id, label, members))
            groups.append(TagGroup(tag=tag, songs=flat, subgroups=subgroups))
        return groups
