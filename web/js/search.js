// Search songs by title, author or lyrics from the box in the top bar.
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

document.querySelectorAll(".search").forEach((box) => {
    const input = box.querySelector("input");
    const results = box.querySelector(".search-results");

    function close() {
        results.hidden = true;
    }

    function update() {
        const query = input.value.trim();
        if (!query) return close();
        const found = searchSongs(query).slice(0, MAX_SEARCH_RESULTS);
        results.replaceChildren(...(found.length
            ? found.map((song) => {
                const link = document.createElement("a");
                link.href = "#" + song.id;
                link.className = "search-result";
                link.textContent = song.title;
                return link;
            })
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
            input.value = "";
            close();
            input.blur();
        }
    });

    // Picking a result: jump there, clear the box and put the keyboard away.
    results.addEventListener("click", (event) => {
        if (!event.target.closest("a")) return;
        input.value = "";
        close();
        input.blur();
    });

    document.addEventListener("click", (event) => {
        if (!box.contains(event.target)) close();
    });
});
