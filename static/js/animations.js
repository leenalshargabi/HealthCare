document.querySelectorAll(".stats div").forEach(card => {
  card.addEventListener("mouseenter", () => {
    card.style.transform = "scale(1.1)";
  });
  card.addEventListener("mouseleave", () => {
    card.style.transform = "scale(1)";
  });
});

window.addEventListener("scroll", () => {
  document.querySelectorAll(".slide-up").forEach(el => {
    const pos = el.getBoundingClientRect().top;
    if (pos < window.innerHeight - 100) {
      el.style.opacity = 1;
    }
  });
});

document.querySelectorAll(".card").forEach(card => {
  card.addEventListener("mouseenter", () => {
    card.style.transform = "translateY(-15px) scale(1.02)";
  });
  card.addEventListener("mouseleave", () => {
    card.style.transform = "translateY(0) scale(1)";
  });
});

