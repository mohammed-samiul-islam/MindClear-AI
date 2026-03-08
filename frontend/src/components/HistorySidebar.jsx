export default function HistorySidebar({ conversions, selectedId, onSelect }) {
  if (!conversions.length) return null

  return (
    <aside className="w-full md:w-64 shrink-0 border border-slate-200 rounded-lg p-4 bg-white">
      <h2 className="font-semibold text-slate-800 mb-3">History</h2>
      <ul className="space-y-2">
        {conversions.map((c) => (
          <li key={c.id}>
            <button
              type="button"
              onClick={() => onSelect(selectedId === c.id ? null : c.id)}
              className={`w-full text-left text-sm px-2 py-1.5 rounded truncate ${
                selectedId === c.id ? 'bg-slate-200 font-medium' : 'hover:bg-slate-100'
              }`}
              title={c.raw_input}
            >
              {new Date(c.created_at).toLocaleString()} · {c.task_count} task{c.task_count !== 1 ? 's' : ''}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}
