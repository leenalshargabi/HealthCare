/* PARTICLES GENERATOR */

const particlesContainer = document.getElementById("particles");

for(let i = 0; i < 40; i++){
    const particle = document.createElement("div");
    particle.classList.add("particle");

    particle.style.left = Math.random() * 100 + "vw";
    particle.style.animationDuration = (6 + Math.random() * 8) + "s";
    particle.style.opacity = Math.random();

    particlesContainer.appendChild(particle);
}

/* PAGE TRANSITION */
document.querySelectorAll(".card").forEach(card => {
  card.addEventListener("click", function(e){
    e.preventDefault();
    const link = this.href;

    document.body.classList.add("fade-out");

    setTimeout(() => {
      window.location = link;
    }, 300);
  });
});
