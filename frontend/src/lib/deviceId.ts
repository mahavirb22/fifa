/** Anonymous device ID — crypto.randomUUID with fallback, persisted in localStorage. */

const STORAGE_KEY = "matchday_device_id";

function generateId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Fallback for older browsers
  return `dev-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export function getDeviceId(): string {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    const id = generateId();
    localStorage.setItem(STORAGE_KEY, id);
    return id;
  } catch {
    // localStorage unavailable (private browsing, SSR)
    return generateId();
  }
}
