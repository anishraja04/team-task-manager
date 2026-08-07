import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { tasksApi } from '../api'

// map the status code with a nice label to show on the page
const STATUS_LABELS = {
  todo: 'To Do',
  in_progress: 'In Progress',
  review: 'In Review',
  done: 'Done',
}

const statusBadge = (s) => `badge ${s}`

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])

  // load the dashboard numbers and the recent tasks when the page opens
  useEffect(() => {
    tasksApi.dashboard().then(({ data }) => setStats(data))
    tasksApi.list().then(({ data }) => {
      const results = data.results ?? data
      setRecent(results.slice(0, 5))
    })
  }, [])

  if (!stats) return <div className="loading">Loading dashboard…</div>

  return (
    <div>
      <h1 className="section-title">Dashboard</h1>
      {/* these boxes show the overall counts of tasks */}
      <div className="stats">
        <div className="stat primary"><div className="num">{stats.total_tasks}</div><div className="label">Total tasks</div></div>
        <div className="stat"><div className="num">{stats.todo}</div><div className="label">To do</div></div>
        <div className="stat"><div className="num">{stats.in_progress}</div><div className="label">In progress</div></div>
        <div className="stat"><div className="num">{stats.review}</div><div className="label">In review</div></div>
        <div className="stat done"><div className="num">{stats.done}</div><div className="label">Completed</div></div>
        <div className="stat danger"><div className="num">{stats.overdue}</div><div className="label">Overdue</div></div>
        <div className="stat warn"><div className="num">{stats.my_tasks}</div><div className="label">My tasks</div></div>
        <div className="stat"><div className="num">{stats.project_count}</div><div className="label">Projects</div></div>
      </div>

      <h2 className="section-title">Recent tasks</h2>
      <div className="card">
        {recent.length === 0 ? (
          <p className="empty">
            No tasks yet. <Link to="/tasks">Create a task</Link>.
          </p>
        ) : (
          <table>
            <thead>
              <tr><th>Title</th><th>Project</th><th>Status</th><th>Priority</th><th>Due</th></tr>
            </thead>
            <tbody>
              {recent.map((t) => (
                <tr key={t.id}>
                  <td><Link to={`/projects/${t.project}`}>{t.title}</Link></td>
                  <td>{t.project_name}</td>
                  <td><span className={statusBadge(t.status)}>{STATUS_LABELS[t.status]}</span></td>
                  <td><span className={`badge priority-${t.priority}`}>{t.priority}</span></td>
                  <td>
                    {t.due_date ? (
                      // highlight in red if the task is overdue
                      <span className={t.is_overdue ? 'badge overdue' : ''}>{t.due_date}</span>
                    ) : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
