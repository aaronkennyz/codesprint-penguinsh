import { getToken, clearToken } from "./auth.js";

const API_BASE = "http://127.0.0.1:8000"; // same origin

export async function api(path, { method="GET", body=null, headers={} } = {}) {
  const token = getToken();
  const h = { "Content-Type": "application/json", ...headers };
  if (token) h["Authorization"] = `Bearer ${token}`;
  const res = await fetch(API_BASE + path, { method, headers: h, body: body ? JSON.stringify(body) : null });

  if (res.status === 401) { clearToken(); throw new Error("Unauthorized"); }
  if (!res.ok) {
    let msg = `${res.status}`;
    try {
      const j = await res.json();
      msg = j.detail || msg;
      if (typeof msg === "object") msg = JSON.stringify(msg);
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export async function safeApi(path, opts) {
  try { return { ok:true, data: await api(path, opts) }; }
  catch (e) { return { ok:false, error: String(e.message || e) }; }
}
