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

// PAGINATION SYSTEM

document.addEventListener("DOMContentLoaded", function () {

  const doctors = document.querySelectorAll(".doctor-item");
  const pagination = document.getElementById("pagination");

  const perPage = 6;
  let currentPage = 1;

  function showPage(page) {
    currentPage = page;

    doctors.forEach((doc, index) => {
      doc.style.display =
        index >= (page - 1) * perPage && index < page * perPage
          ? "block"
          : "none";
    });

    renderPagination();
  }

  function renderPagination() {
    pagination.innerHTML = "";

    const totalPages = Math.ceil(doctors.length / perPage);

    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("button");
      btn.innerText = i;

      if (i === currentPage) btn.classList.add("active");

      btn.addEventListener("click", () => showPage(i));
      pagination.appendChild(btn);
    }
  }

  showPage(1);
});

document.querySelectorAll(".availability").forEach(badge => {
    const random = Math.random();

    if(random > 0.5){
        badge.classList.remove("available");
        badge.classList.add("busy");
        badge.innerText = "Busy";
    }
});
