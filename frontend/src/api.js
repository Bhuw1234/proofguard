const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function simulate(sql) {
  const res = await fetch(`${API_URL}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sql }),
  });
  return res.json();
}

export async function approve(simulationId, note) {
  const res = await fetch(`${API_URL}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ simulation_id: simulationId, note }),
  });
  return res.json();
}

export async function reject(simulationId, note) {
  const res = await fetch(`${API_URL}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ simulation_id: simulationId, note }),
  });
  return res.json();
}

export async function fetchAudit() {
  const res = await fetch(`${API_URL}/audit`);
  return res.json();
}

export async function fetchExamples() {
  const res = await fetch(`${API_URL}/examples`);
  return res.json();
}
