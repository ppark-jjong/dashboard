// nav-active.js
document.addEventListener("DOMContentLoaded", () => {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    if (
      (currentPath.includes("index.html") ||
        currentPath === "/" ||
        currentPath === "") &&
      link.getAttribute("href").includes("index.html")
    ) {
      link.classList.add("active");
    } else if (
      currentPath.includes("visualization.html") &&
      link.getAttribute("href").includes("visualization.html")
    ) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
});
