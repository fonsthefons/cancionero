# Misa

## Entrada

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "entrada")
SORT title ASC
```

## Gloria

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "gloria")
SORT title ASC
```

## Aleluya

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "aleluya")
SORT title ASC
```

## Ofertorio

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "ofertorio")
SORT title ASC
```

## Santo

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "santo")
SORT title ASC
```

## Cordero

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "cordero")
SORT title ASC
```

## Comunion

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "comunion")
SORT title ASC
```

## Salida

```dataview
TABLE WITHOUT ID file.link as "Hymn"
FROM "songs"
WHERE contains(song_tags.misa, "salida")
SORT title ASC
```
