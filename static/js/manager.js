function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}

function showSection(sectionId) {
    document.querySelectorAll(".section").forEach(sec => sec.classList.add("hidden"));
    document.getElementById(sectionId).classList.remove("hidden");
}