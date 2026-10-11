// Search songs by title, author or lyrics. Wires up every `.search` box:
//   - default (top bar): results are links that jump to the song;
//   - data-search="<action>" (e.g. the session box): results are buttons that
//     run that action with data-song="<song id>", and the box stays ready for
//     the next search.
// The index is built from the page itself, so song text is not duplicated.

const MAX_SEARCH_RESULTS = 50;

const searchIndex = [...document.querySelectorAll(".song")].map((song) => {
    const title = song.querySelector("h3").textContent;
    return {
        id: song.id,
        title,
        text: normalizeText(title + " " + song.querySelector(".lyrics").textContent),
    };
});

function searchSongs(query) {
    const q = normalizeText(query.trim());
    if (!q) return [];
    return searchIndex.filter((song) => song.text.includes(q));
}

function searchResultElement(song, action) {
    const item = document.createElement(action ? "button" : "a");
    item.className = "search-result";
    item.textContent = song.title;
    if (action) {
        item.dataset.action = action;
        item.dataset.song = song.id;
    } else {
        item.href = "#" + song.id;
    }
    return item;
}

document.querySelectorAll(".search").forEach((box) => {
    const input = box.querySelector("input");
    const results = box.querySelector(".search-results");
    const action = box.dataset.search; // undefined for plain "jump to song"

    function close() {
        results.hidden = true;
    }

    function update() {
        const query = input.value.trim();
        if (!query) return close();
        const found = searchSongs(query).slice(0, MAX_SEARCH_RESULTS);
        results.replaceChildren(...(found.length
            ? found.map((song) => searchResultElement(song, action))
            : [Object.assign(document.createElement("div"), {
                className: "search-empty",
                textContent: "No songs found",
            })]));
        results.hidden = false;
    }

    input.addEventListener("input", update);
    input.addEventListener("focus", update);
    input.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            event.stopPropagation(); // clear the search, don't close the menu
            input.value = "";
            close();
            input.blur();
        }
    });

    // Picking a result: clear the box. Jumping also puts the keyboard away;
    // adding keeps focus so the next song can be typed straight away.
    results.addEventListener("click", (event) => {
        if (!event.target.closest(".search-result")) return;
        input.value = "";
        close();
        if (action) input.focus();
        else input.blur();
    });

    document.addEventListener("click", (event) => {
        if (!box.contains(event.target)) close();
    });
});
