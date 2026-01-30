import { get, put } from "./idb.js";
import { safeApi } from "./api.js";

export async function loadRules() {
  const cached = await get("cache_meta", "rules");
  if (cached?.value) return cached.value;
  const r = await fetch("/assets/rules.json").then(x=>x.json());
  await put("cache_meta", { key:"rules", value:r });
  return r;
}

// Pull deltas for assigned villages when online (small pages)
export async function refreshCaches() {
  if (!navigator.onLine) return;

  const meta = await get("cache_meta","sync") || { key:"sync", value:{} };
  const last = meta.value || {};

  // In this minimal scaffold we fetch by village in UI.
  // You can expand: for each assigned village -> fetch updated_since and cache.
  await put("cache_meta", { key:"sync", value:last });
}
