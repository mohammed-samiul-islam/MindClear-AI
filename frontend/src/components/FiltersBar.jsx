export default function FiltersBar({ filters, setFilters }) {
  return (
    <div className="flex flex-wrap gap-3 items-center mb-4">
      <span className="text-slate-600 text-sm">Filter:</span>
      <select
        value={filters.category}
        onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value }))}
        className="border border-slate-300 rounded px-2 py-1 text-sm"
      >
        <option value="">All categories</option>
        <option value="Work">Work</option>
        <option value="Personal">Personal</option>
        <option value="Health">Health</option>
        <option value="Finance">Finance</option>
        <option value="Other">Other</option>
      </select>
      <select
        value={filters.priority}
        onChange={(e) => setFilters((f) => ({ ...f, priority: e.target.value }))}
        className="border border-slate-300 rounded px-2 py-1 text-sm"
      >
        <option value="">All priorities</option>
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
      </select>
      <select
        value={filters.completed}
        onChange={(e) => setFilters((f) => ({ ...f, completed: e.target.value }))}
        className="border border-slate-300 rounded px-2 py-1 text-sm"
      >
        <option value="">All</option>
        <option value="false">Not done</option>
        <option value="true">Done</option>
      </select>
    </div>
  )
}
