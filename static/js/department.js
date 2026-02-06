// smooth hover animation for doctor cards
const cards = document.querySelectorAll(".doctor-card");

cards.forEach(card => {
    card.addEventListener("mouseenter", () => {
        card.style.transform = "scale(1.05)";
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "scale(1)";
    });
});


// smooth scroll return button
function goBack() {
    window.history.back();
}


// fade animation when scrolling
const elements = document.querySelectorAll(".doctor-card");

window.addEventListener("scroll", () => {
    elements.forEach(el => {
        const position = el.getBoundingClientRect().top;
        if(position < window.innerHeight - 100){
            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
        }
    });
});
