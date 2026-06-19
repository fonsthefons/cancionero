# Tema

## Padre

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.tema, "padre")
SORT title ASC
```

## Cristo

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.tema, "cristo")
SORT title ASC
```

## Espiritu

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.tema, "espiritu")
SORT title ASC
```

## Santo

Theme topic (distinct from the Misa *Santo* mass part).

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.tema, "santo")
SORT title ASC
```

## Martir

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.tema, "martir")
SORT title ASC
```

## Virgen

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.tema, "virgen")
SORT title ASC
```
