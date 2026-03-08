import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { getTasks, getConversions } from '../api/tasks'
import TaskList from '../components/TaskList'
import FiltersBar from '../components/FiltersBar'
import HistorySidebar from '../components/HistorySidebar'

export default function Dashboard() {
  const location = useLocation()
  const [tasks, setTasks] = useState(location.state?.tasks ?? [])
  const [conversions, setConversions] = useState([])
  const [filters, setFilters] = useState({ category: '', priority: '', completed: '' })
  const [conversionId, setConversionId] = useState(location.state?.conversionId ?? null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  async function loadConversions() {
    try {
      const res = await getConversions()
      setConversions(res.conversions || [])
    } catch (_) {}
  }

  async function loadTasks() {
    setLoading(true)
    setError(null)
    try {
      const params = {}
      if (filters.category) params.category = filters.category
      if (filters.priority) params.priority = filters.priority
      if (filters.completed !== '') params.completed = filters.completed === 'true'
      if (conversionId) params.conversion_id = conversionId
      const res = await getTasks(params)
      setTasks(res.tasks || [])
    } catch (e) {
      setError(e.detail || e.message || 'Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConversions()
  }, [])

  useEffect(() => {
    loadTasks()
  }, [filters, conversionId])

  function onTaskUpdated() {
    loadTasks()
    loadConversions()
  }

  return (
    <div className="flex flex-col md:flex-row gap-6">
      <div className="flex-1 min-w-0">
        <h1 className="text-2xl font-bold text-slate-800 mb-4">Tasks</h1>
        <FiltersBar filters={filters} setFilters={setFilters} />
        {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
        {loading ? (
          <p className="text-slate-500 mt-4">Loading…</p>
        ) : (
          <TaskList tasks={tasks} onUpdate={onTaskUpdated} />
        )}
      </div>
      <HistorySidebar
        conversions={conversions}
        selectedId={conversionId}
        onSelect={setConversionId}
      />
    </div>
  )
}
