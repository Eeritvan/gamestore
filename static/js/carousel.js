let currentSlide = 0;
const slides = document.querySelectorAll(".gamecontent");
const progressBars = document.querySelectorAll(".progressbar");
let slideInterval;

function changeSlide(index) {
    slides.forEach((slide, i) => {
        slide.style.display = i === index ? "flex" : "none";
        slide.classList.toggle("active", i === index);
    });
    progressBars.forEach((bar, i) => {
      bar.style.animation = "none";
      bar.offsetHeight;
      if (i === index) {
        bar.style.animation = "";
        bar.style.animationPlayState = "running";
      } else {
        bar.style.animationPlayState = "paused";
        bar.style.width = "0";
      }
    });
    currentSlide = Number(index);
    resetTimer();
}

function nextSlide() {
  currentSlide = (currentSlide + 1) % slides.length;
  changeSlide(currentSlide);
}

function resetTimer() {
  clearInterval(slideInterval);
  slideInterval = setInterval(nextSlide, 12000);
  progressBars[currentSlide].style.width = "0";
}

window.addEventListener("load", function() {
  slides.forEach((slide, i) => slide.style.display = i === 0 ? "flex" : "none");
  changeSlide(currentSlide);
  document.querySelector(".selectbar").classList.add("active");
});

document.querySelectorAll(".singleselection").forEach((selection, index) => {
  selection.addEventListener("click", () => changeSlide(index));
});