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

export function createAgent(name, description, skills = ['base_chat']) {
  return request('/agents/create', {
    method: 'POST',
    body: JSON.stringify({ name, description, skills }),
  })
}

export function listAgents() {
  return request('/agents')
}

export function askAgent(agentId, message) {
  return request(`/agents/${agentId}/ask`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export function getAgentHistory(agentId) {
  return request(`/agents/${agentId}/history`)
}

export function listSkills() {
  return request('/skills')
}
