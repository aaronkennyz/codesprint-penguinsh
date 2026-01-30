export function ensureSW() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(()=>{});
  }
}

export function setSyncBadge(text, level="ok") {
  const el = document.querySelector("[data-sync]");
  if (!el) return;
  el.textContent = text;
  el.className = `badge ${level}`;
}

export function toast(msg) {
  let t = document.querySelector("#toast");
  if (!t) {
    t = document.createElement("div");
    t.id = "toast";
    t.style.position="fixed"; t.style.left="12px"; t.style.right="12px";
    t.style.bottom="12px"; t.style.padding="12px";
    t.style.background="#111a2e"; t.style.border="1px solid #22304f";
    t.style.borderRadius="12px"; t.style.zIndex="9999";
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.display="block";
  setTimeout(()=>t.style.display="none", 2200);
}
