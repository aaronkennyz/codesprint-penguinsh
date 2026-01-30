import { ensureSW } from "./ui.js";
import { syncLoop, syncOnce } from "./sync.js";

ensureSW();
window.addEventListener("online", () => syncOnce());
setInterval(() => syncLoop(), 25_000);
