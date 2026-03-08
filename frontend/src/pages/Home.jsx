import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeText } from '../api/tasks'
import BrainDumpForm from '../components/BrainDumpForm'

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(text) {
    setError(null)
    setLoading(true)
    try {
      const res = await analyzeText(text)
      navigate('/dashboard', { state: { conversionId: res.conversion_id, tasks: res.tasks } })
    } catch (e) {
      setError(e.detail || e.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-2">Brain Dump</h1>
      <p className="text-slate-600 mb-4">
        Paste your messy thoughts below. We’ll turn them into clear, structured tasks.
      </p>
      <BrainDumpForm onSubmit={handleSubmit} loading={loading} error={error} />
    </div>
  )
}
