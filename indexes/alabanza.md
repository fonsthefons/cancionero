# Alabanza

## Primer ciclo

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.alabanza, "primer_ciclo")
SORT title ASC
```

## Segundo ciclo

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.alabanza, "segundo_ciclo")
SORT title ASC
```

## Tercer ciclo

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.alabanza, "tercer_ciclo")
SORT title ASC
```

## Cuarto ciclo

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.alabanza, "cuarto_ciclo")
SORT title ASC
```
