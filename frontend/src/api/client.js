// In development we use Vite proxy (/api). In production set VITE_API_URL to your backend URL.
const BASE = import.meta.env.VITE_API_URL ?? '/api'

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
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
