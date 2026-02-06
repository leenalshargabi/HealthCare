// Toggle Read More / Less
document.querySelectorAll(".more-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const card = btn.closest(".news-card");
        const fullText = card.querySelector(".full-text");
        const summary = card.querySelector(".summary");

        if (fullText.style.display === "block") {
            fullText.style.display = "none";
            summary.style.display = "block";
            btn.innerText = "Read More";
        } else {
            fullText.style.display = "block";
            summary.style.display = "none";
            btn.innerText = "Read Less";
        }
    });
});
