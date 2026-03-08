import TaskCard from './TaskCard'

export default function TaskList({ tasks, onUpdate }) {
  if (!tasks.length) {
    return <p className="text-slate-500">No tasks yet. Add some from the Home page.</p>
  }
  return (
    <ul className="space-y-2 mt-4">
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} onUpdate={onUpdate} />
      ))}
    </ul>
  )
}
