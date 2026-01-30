const KEY = "rh_token";
const META = "rh_meta";

export function setAuth(token, meta) {
  localStorage.setItem(KEY, token);
  localStorage.setItem(META, JSON.stringify(meta||{}));
}
export function getToken() { return localStorage.getItem(KEY); }
export function getMeta() {
  try { return JSON.parse(localStorage.getItem(META)||"{}"); } catch { return {}; }
}
export function clearToken() { localStorage.removeItem(KEY); localStorage.removeItem(META); }
