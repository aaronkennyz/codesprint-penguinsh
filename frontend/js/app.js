import { ensureSW } from "./ui.js";
import { syncLoop, syncOnce } from "./sync.js";

ensureSW();
window.addEventListener("online", () => syncOnce());
setInterval(() => syncLoop(), 25_000);

// Theme + back-to-top helpers
const THEME_KEY = "rr_theme";
const root = document.documentElement;
const savedTheme = localStorage.getItem(THEME_KEY);
if (savedTheme === "dark") root.dataset.theme = "dark";

function updateThemeLabel(btn) {
  if (!btn) return;
  const isDark = root.dataset.theme === "dark";
  btn.setAttribute("aria-pressed", String(isDark));
  btn.querySelector(".label").textContent = isDark ? "Dark" : "Light";
}

function mountThemeToggle() {
  const bar = document.querySelector(".topbar-inner");
  if (!bar || bar.querySelector("[data-theme-toggle]")) return;
  const target = bar.querySelector(".row") || bar;
  const btn = document.createElement("button");
  btn.className = "btn ghost theme-toggle";
  btn.type = "button";
  btn.setAttribute("data-theme-toggle", "1");
  btn.innerHTML = `<span class="dot"></span><span class="label">Light</span>`;
  btn.onclick = () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    if (next === "dark") root.dataset.theme = "dark";
    else delete root.dataset.theme;
    localStorage.setItem(THEME_KEY, next);
    updateThemeLabel(btn);
  };
  target.appendChild(btn);
  updateThemeLabel(btn);
}

function mountBackToTop() {
  if (document.querySelector("[data-back-top]")) return;
  const btn = document.createElement("button");
  btn.className = "btn back-top";
  btn.type = "button";
  btn.textContent = "Back to top";
  btn.setAttribute("data-back-top", "1");
  btn.onclick = () => window.scrollTo({ top: 0, behavior: "smooth" });
  document.body.appendChild(btn);
  const onScroll = () => {
    if (window.scrollY > 300) btn.classList.add("show");
    else btn.classList.remove("show");
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

mountThemeToggle();
mountBackToTop();
