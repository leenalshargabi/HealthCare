function goBack() {
    window.history.back();
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".availability").forEach(badge => {
        const random = Math.random();
        if (random > 0.5) {
            badge.classList.remove("available");
            badge.classList.add("busy");
            badge.innerText = "Busy";
        }
    });

    const hero = document.querySelector(".hero");
    if (hero) {
        hero.style.opacity = "0";
        hero.style.transform = "translateY(30px)";
        setTimeout(() => {
            hero.style.transition = "all .7s ease";
            hero.style.opacity = "1";
            hero.style.transform = "translateY(0)";
        }, 200);
    }
});

\const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
        }
    });
}, observerOptions);

document.querySelectorAll(".doctor").forEach(doc => {
    observer.observe(doc);
});