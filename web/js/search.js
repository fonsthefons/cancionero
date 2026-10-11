// Search songs by title, author or lyrics. Wires up every `.search` box.
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

function renderSearchResults(container, results) {
    container.replaceChildren(...results.slice(0, MAX_SEARCH_RESULTS).map((song) => {
        const link = document.createElement("a");
        link.href = "#" + song.id;
        link.className = "search-result";
        link.textContent = song.title;
        return link;
    }));
}

document.querySelectorAll(".search").forEach((box) => {
    const input = box.querySelector("input");
    const results = box.querySelector(".search-results");
    input.addEventListener("input", () => renderSearchResults(results, searchSongs(input.value)));
});
