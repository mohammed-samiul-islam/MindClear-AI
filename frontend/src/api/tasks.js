import { request } from './client'

export function analyzeText(text) {
  return request('/analyze', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export function getTasks(params = {}) {
  const sp = new URLSearchParams()
  if (params.category != null) sp.set('category', params.category)
  if (params.priority != null) sp.set('priority', params.priority)
  if (params.completed != null) sp.set('completed', params.completed)
  if (params.conversion_id != null) sp.set('conversion_id', params.conversion_id)
  const q = sp.toString()
  return request(`/tasks${q ? `?${q}` : ''}`)
}

export function updateTask(id, data) {
  return request(`/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export function deleteTask(id) {
  return request(`/tasks/${id}`, { method: 'DELETE' })
}

export function getConversions() {
  return request('/conversions')
}
