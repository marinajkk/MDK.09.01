const burger = document.querySelector(".burger");
const menu = document.querySelector(".menu");

if (burger && menu) {
  burger.addEventListener("click", () => {
    const open = menu.classList.toggle("open");
    burger.setAttribute("aria-expanded", open ? "true" : "false");
  });
}
