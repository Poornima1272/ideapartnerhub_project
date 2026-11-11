document.addEventListener("DOMContentLoaded", () => {
  const menu = document.getElementById("menu");
  const panel = document.querySelector(".panel");
  if (menu && panel) {
    menu.addEventListener("click", () => {
      const isOpen = panel.classList.toggle("open");
      menu.setAttribute("aria-expanded", isOpen);
    });
  }
});
