import { useState } from 'react'
import { updateTask, deleteTask } from '../api/tasks'

const priorityColors = {
  High: 'bg-red-100 text-red-800',
  Medium: 'bg-amber-100 text-amber-800',
  Low: 'bg-slate-100 text-slate-700',
}

export default function TaskCard({ task, onUpdate }) {
  const [deleting, setDeleting] = useState(false)

  async function toggleComplete() {
    try {
      await updateTask(task.id, { completed: !task.completed })
      onUpdate()
    } catch (_) {}
  }

  async function handleDelete() {
    if (!confirm('Delete this task?')) return
    setDeleting(true)
    try {
      await deleteTask(task.id)
      onUpdate()
    } catch (_) {
      setDeleting(false)
    }
  }

  const deadlineStr = task.deadline
    ? new Date(task.deadline).toLocaleDateString()
    : null

  return (
    <li
      className={`border rounded-lg px-4 py-3 flex items-start justify-between gap-2 ${
        task.completed ? 'bg-slate-100 border-slate-200' : 'bg-white border-slate-200'
      }`}
    >
      <div className="flex-1 min-w-0">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={toggleComplete}
            className="rounded border-slate-300"
          />
          <span className={task.completed ? 'line-through text-slate-500' : ''}>
            {task.task}
          </span>
        </label>
        <div className="flex flex-wrap gap-2 mt-2">
          <span
            className={`text-xs px-2 py-0.5 rounded ${priorityColors[task.priority] || priorityColors.Medium}`}
          >
            {task.priority}
          </span>
          <span className="text-xs text-slate-500">{task.category}</span>
          {deadlineStr && (
            <span className="text-xs text-slate-500">Due {deadlineStr}</span>
          )}
        </div>
      </div>
      <button
        type="button"
        onClick={handleDelete}
        disabled={deleting}
        className="text-red-600 hover:text-red-800 text-sm disabled:opacity-50"
      >
        Delete
      </button>
    </li>
  )
}
