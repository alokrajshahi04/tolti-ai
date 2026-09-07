const API_BASE = "/api/v1";

export async function healthLive(): Promise<{ status: string }> {
  const r = await fetch(`${API_BASE}/health/live`);
  if (!r.ok) throw new Error("health live failed");
  return r.json();
}

export async function healthReady(): Promise<{ status: string }> {
  const r = await fetch(`${API_BASE}/health/ready`);
  if (!r.ok) throw new Error("health ready failed");
  return r.json();
}

export async function getRoomShell(
  roomId: string,
): Promise<{ id: string; name: string; status: string }> {
  const r = await fetch(
    `${API_BASE}/rooms/${encodeURIComponent(roomId)}/shell`,
  );
  if (!r.ok) throw new Error("room shell failed");
  return r.json();
}
