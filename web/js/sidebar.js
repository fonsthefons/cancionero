// Sliding table-of-contents sidebar.

const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");

function setSidebarOpen(open) {
    sidebar.classList.toggle("open", open);
    sidebarToggle.textContent = open ? ">" : "<";
}

onAction("toggle-sidebar", () => setSidebarOpen(!sidebar.classList.contains("open")));

// Close the sidebar after jumping to a song or section.
sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a")) setSidebarOpen(false);
});
