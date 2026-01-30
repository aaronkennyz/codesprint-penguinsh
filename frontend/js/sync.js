import { listOutbox, removeOutbox } from "./outbox.js";
import { safeApi } from "./api.js";
import { setSyncBadge } from "./ui.js";
import { refreshCaches } from "./rules.js";

let syncing = false;
let lastTry = 0;

const handlers = {
  "household:create": (p) => safeApi("/api/households", { method:"POST", body:p }),
  "person:create": (p) => safeApi("/api/people", { method:"POST", body:p }),
  "camp:create": (p) => safeApi("/api/camps", { method:"POST", body:p }),
  "encounter:start": (p) => safeApi("/api/encounters/start", { method:"POST", body:p }),
  "encounter:submit": (p) => safeApi(`/api/encounters/${p.encounter_id}/submit`, { method:"POST", body:p.body }),
  "reminder:create": (p) => safeApi("/api/reminders", { method:"POST", body:p }),
  "task:create": (p) => safeApi("/api/tasks", { method:"POST", body:p })
};

export async function syncOnce() {
  if (!navigator.onLine || syncing) return;
  syncing = true;
  setSyncBadge("⏳ Syncing…", "warn");
  try {
    const outbox = await listOutbox();
    for (const item of outbox.sort((a,b)=> (a.id-b.id))) {
      const fn = handlers[item.type];
      if (!fn) { await removeOutbox(item.id); continue; }

      const res = await fn(item.payload_json);
      if (res.ok) {
        await removeOutbox(item.id);
      } else {
        // backoff: stop after first error to avoid battery drain
        console.warn("sync error", res.error);
        break;
      }
    }
    await refreshCaches(); // pull deltas when possible
    setSyncBadge("✅ Synced", "ok");
  } finally {
    syncing = false;
  }
}

export async function syncLoop() {
  const now = Date.now();
  if (now - lastTry < 20_000) return;
  lastTry = now;
  await syncOnce();
}
