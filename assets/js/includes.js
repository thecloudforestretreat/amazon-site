async function loadIncludes() {
  const header = document.getElementById("siteHeader");
  const footer = document.getElementById("siteFooter");

  if (header) {
    const res = await fetch("/assets/includes/header.html", { cache: "no-store" });
    header.innerHTML = await res.text();
  }

  if (footer) {
    const res = await fetch("/assets/includes/footer.html", { cache: "no-store" });
    footer.innerHTML = await res.text();
  }

  initMenu();
}

function initMenu() {
  const toggle = document.querySelector(".navToggle");
  const mobileMenu = document.getElementById("mobileMenu");

  if (!toggle || !mobileMenu) return;

  toggle.addEventListener("click", () => {
    const expanded = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!expanded));
    mobileMenu.hidden = expanded;
    document.body.classList.toggle("menuOpen", !expanded);
  });
}

document.addEventListener("DOMContentLoaded", loadIncludes);
