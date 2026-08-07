import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi } from '../api'

export default function Projects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', description: '' })
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    projectsApi.list().then(({ data }) => setProjects(data.results ?? data)).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const create = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await projectsApi.create(form)
      setShowModal(false)
      setForm({ name: '', description: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.name?.[0] || 'Failed to create project.')
    }
  }

  return (
    <div>
      <div className="toolbar">
        <h1 className="section-title" style={{ marginBottom: 0 }}>Projects</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Project</button>
      </div>

      {loading ? (
        <div className="loading">Loading projects…</div>
      ) : projects.length === 0 ? (
        <div className="card">
          <p className="empty">No projects yet. Create your first project to get started.</p>
        </div>
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr><th>Name</th><th>Members</th><th>Tasks</th><th>Completed</th><th>Overdue</th><th>Owner</th></tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id}>
                  <td><Link to={`/projects/${p.id}`} style={{ fontWeight: 600 }}>{p.name}</Link></td>
                  <td>{p.members?.length}</td>
                  <td>{p.task_count}</td>
                  <td>{p.completed_tasks}</td>
                  <td>{p.overdue_tasks > 0 ? <span className="badge overdue">{p.overdue_tasks}</span> : p.overdue_tasks}</td>
                  <td>{p.owner?.name || p.owner?.email}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-backdrop" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>New Project</h2>
            {error && <div className="error-box">{error}</div>}
            <form onSubmit={create}>
              <div className="field">
                <label>Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="field">
                <label>Description</label>
                <textarea rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="actions">
                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancel</button>
                <button className="btn btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
