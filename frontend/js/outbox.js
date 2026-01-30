import { put, getAll, del } from "./idb.js";

export async function enqueue(type, payload) {
  await put("outbox", {
    type,
    payload_json: payload,
    created_at: new Date().toISOString(),
    attempts: 0,
    last_error: null,
    status: "PENDING"
  });
}

export async function listOutbox() {
  return await getAll("outbox");
}

export async function removeOutbox(id) {
  return await del("outbox", id);
}
