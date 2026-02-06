function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}

function showSection(sectionId) {
    document.querySelectorAll(".section").forEach(sec => sec.classList.add("hidden"));
    document.getElementById(sectionId).classList.remove("hidden");
}

// SIDEBAR TOGGLE
document.getElementById("menuBtn").onclick = function () {
    const sidebar = document.getElementById("sidebar");
    sidebar.style.display =
        sidebar.style.display === "none" ? "block" : "none";
};


// SEARCH USERS
document.getElementById("searchInput").addEventListener("keyup", function () {

    const name = this.value;

    fetch(`/api/search?name=${name}`)
        .then(res => res.json())
        .then(data => {

            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";

            data.forEach(user => {
                resultsDiv.innerHTML += `
                    <div class="card">
                        <h3>${user.name}</h3>
                        <p>Role: ${user.role}</p>
                        <p>Email: ${user.email}</p>
                    </div>
                `;
            });
        });
});


// FILTER USERS
function filterUsers(type) {

    fetch(`/api/filter?type=${type}`)
        .then(res => res.json())
        .then(data => {

            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";

            data.forEach(user => {
                resultsDiv.innerHTML += `
                    <div class="card">
                        <h3>${user.name}</h3>
                        <p>${user.role}</p>
                    </div>
                `;
            });
        });
}


// SIDEBAR ACTIONS
function showSection(section) {
    document.getElementById("results").innerHTML =
        `<h2>${section.toUpperCase()} section will appear here</h2>`;
}

function goToReports() {
    window.location.href = "/manager/report";
}