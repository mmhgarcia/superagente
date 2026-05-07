const BASE = ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Error ${res.status}`)
  }
  return res.json()
}

export function generateAgent(name, description) {
  return request('/generate_agent/', {
    method: 'POST',
    body: JSON.stringify({ name, description }),
  })
}
