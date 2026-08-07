import { useEffect, useState } from 'react'
import { projectsApi, tasksApi } from '../api'
import TaskFormModal from '../components/TaskFormModal.jsx'
import { useAuth } from '../context/AuthContext.jsx'

const STATUS_LABELS = { todo: 'To Do', in_progress: 'In Progress', review: 'In Review', done: 'Done' }

export default function Tasks() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState([])
  const [projects, setProjects] = useState([])
  const [filter, setFilter] = useState({ project: '', status: '', assignee: 'all' })
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)

  const loadTasks = () => {
    const params = {}
    if (filter.project) params.project = filter.project
    tasksApi.list(params).then(({ data }) => setTasks(data.results ?? data))
  }

  useEffect(() => {
    projectsApi.list().then(({ data }) => setProjects(data.results ?? data))
  }, [])

  useEffect(loadTasks, [filter.project])

  const filtered = tasks.filter((t) => {
    if (filter.status && t.status !== filter.status) return false
    if (filter.assignee === 'mine' && t.assignee !== user?.id) return false
    if (filter.assignee === 'unassigned' && t.assignee) return false
    return true
  })

  const updateStatus = async (task, status) => {
    try {
      await tasksApi.update(task.id, { status })
      loadTasks()
    } catch (err) {
      alert(err.response?.data?.detail || 'Cannot update status.')
    }
  }

  const deleteTask = async (id) => {
    if (!window.confirm('Delete this task?')) return
    await tasksApi.remove(id)
    loadTasks()
  }

  const memberByProject = (projectId) =>
    projects.find((p) => p.id === projectId)?.members || []

  return (
    <div>
      <div className="toolbar">
        <h1 className="section-title" style={{ marginBottom: 0 }}>Tasks</h1>
        <button className="btn btn-primary" onClick={() => { setEditing(null); setShowModal(true) }}>+ New Task</button>
      </div>

      <div className="toolbar">
        <div className="field">
          <label>Project</label>
          <select value={filter.project} onChange={(e) => setFilter({ ...filter, project: e.target.value })}>
            <option value="">All projects</option>
            {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Status</label>
          <select value={filter.status} onChange={(e) => setFilter({ ...filter, status: e.target.value })}>
            <option value="">All statuses</option>
            {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Assignee</label>
          <select value={filter.assignee} onChange={(e) => setFilter({ ...filter, assignee: e.target.value })}>
            <option value="all">Everyone</option>
            <option value="mine">Assigned to me</option>
            <option value="unassigned">Unassigned</option>
          </select>
        </div>
      </div>

      <div className="card">
        {filtered.length === 0 ? (
          <p className="empty">No tasks match your filters.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Title</th><th>Project</th><th>Assignee</th><th>Status</th><th>Priority</th><th>Due</th><th></th></tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.id}>
                  <td style={{ fontWeight: 500 }}>{t.title}</td>
                  <td>{t.project_name}</td>
                  <td>{t.assignee_detail?.name || t.assignee_detail?.email || '—'}</td>
                  <td>
                    <select value={t.status} onChange={(e) => updateStatus(t, e.target.value)}>
                      {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                    </select>
                  </td>
                  <td><span className={`badge priority-${t.priority}`}>{t.priority}</span></td>
                  <td>
                    {t.due_date ? (
                      <span className={t.is_overdue ? 'badge overdue' : ''}>{t.due_date}</span>
                    ) : '—'}
                  </td>
                  <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                    <button className="btn btn-outline btn-sm" style={{ marginRight: 6 }} onClick={() => { setEditing(t); setShowModal(true) }}>Edit</button>
                    <button className="btn btn-danger btn-sm" onClick={() => deleteTask(t.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <TaskFormModal
          projects={projects}
          members={editing ? memberByProject(editing.project) : (projects.find((p) => p.id === filter.project)?.members || [])}
          task={editing}
          onClose={() => setShowModal(false)}
          onSaved={() => { setShowModal(false); setEditing(null); loadTasks() }}
        />
      )}
    </div>
  )
}
