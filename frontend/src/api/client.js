// In development we use the Vite proxy (/api). In production set VITE_API_URL
// to your backend URL (e.g. https://mindclear-api.onrender.com).
const BASE = (import.meta.env.VITE_API_URL ?? '/api').replace(/\/$/, '')

const SESSION_KEY = 'mindclear_session_id'

function generateId() {
  if (globalThis.crypto?.randomUUID) return crypto.randomUUID()
  return Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join('')
}

// Anonymous per-visitor id: scopes tasks to this browser. Not authentication.
export function getSessionId() {
  let id = null
  try {
    id = localStorage.getItem(SESSION_KEY)
    if (!id) {
      id = generateId()
      localStorage.setItem(SESSION_KEY, id)
    }
  } catch (_) {
    id = id || generateId()
  }
  return id
}

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Session-ID': getSessionId(),
      ...options.headers,
    },
  })
  if (!res.ok) {
    const err = new Error(res.statusText || 'Request failed')
    err.status = res.status
    try {
      err.detail = (await res.json())?.detail
    } catch (_) {}
    throw err
  }
  if (res.status === 204) return null
  return res.json()
}

export { request, BASE }
