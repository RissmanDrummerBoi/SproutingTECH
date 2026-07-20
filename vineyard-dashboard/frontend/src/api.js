const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options) {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export function getBlocks() {
  return request("/blocks");
}

export function getBlock(id) {
  return request(`/blocks/${id}`);
}

export function getReadings(id, limit = 30) {
  return request(`/blocks/${id}/readings?limit=${limit}`);
}
