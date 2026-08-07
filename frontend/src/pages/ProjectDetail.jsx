import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { authApi, projectsApi, tasksApi } from '../api'
import TaskFormModal from '../components/TaskFormModal.jsx'
import { useAuth } from '../context/AuthContext.jsx'

const STATUS_LABELS = { todo: 'To Do', in_progress: 'In Progress', review: 'In Review', done: 'Done' }

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [project, setProject] = useState(null)
  const [tasks, setTasks] = useState([])
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [showMemberModal, setShowMemberModal] = useState(false)
  const [memberQuery, setMemberQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [memberRole, setMemberRole] = useState('member')
  const [error, setError] = useState('')

  const load = () => {
    projectsApi.get(id).then(({ data }) => setProject(data))
    tasksApi.list({ project: id }).then(({ data }) => setTasks(data.results ?? data))
  }

  useEffect(load, [id])

  if (!project) return <div className="loading">Loading project…</div>

  const amAdmin = project.owner?.id === user?.id || project.members?.some((m) => m.user?.id === user?.id && m.role === 'admin')

  const searchUsers = async (q) => {
    setMemberQuery(q)
    if (!q.trim()) {
      setSearchResults([])
      return
    }
    const { data } = await authApi.searchUsers(q)
    setSearchResults(data.results ?? data)
  }

  const addMember = async (e) => {
    e.preventDefault()
    setError('')
    if (!selectedUser) {
      setError('Search and select a user first.')
      return
    }
    try {
      await projectsApi.addMember(id, { user_id: selectedUser.id, role: memberRole })
      setShowMemberModal(false)
      setMemberQuery('')
      setSearchResults([])
      setSelectedUser(null)
      load()
    } catch (err) {
      const d = err.response?.data
      setError(d ? (d.user_id?.[0] || d.detail || 'Failed to add member.') : 'Failed to add member.')
    }
  }

  const removeMember = async (mpk) => {
    if (!window.confirm('Remove this member?')) return
    try {
      await projectsApi.removeMember(id, mpk)
      load()
    } catch (err) {
      alert(err.response?.data?.detail || 'Could not remove member.')
    }
  }

  const deleteTask = async (tid) => {
    if (!window.confirm('Delete this task?')) return
    await tasksApi.remove(tid)
    load()
  }

  const updateStatus = async (task, status) => {
    try {
      await tasksApi.update(task.id, { status })
      load()
    } catch (err) {
      alert(err.response?.data?.detail || 'Cannot update status.')
    }
  }

  return (
    <div>
      <div className="toolbar">
        <div style={{ flex: 1 }}>
          <h1 className="section-title" style={{ marginBottom: 4 }}>{project.name}</h1>
          <p style={{ color: 'var(--text-soft)', marginBottom: 0 }}>{project.description || 'No description'}</p>
        </div>
        <button className="btn btn-outline" onClick={() => navigate('/projects')}>← Back</button>
      </div>

      <div className="stats">
        <div className="stat primary"><div className="num">{project.task_count}</div><div className="label">Total tasks</div></div>
        <div className="stat done"><div className="num">{project.completed_tasks}</div><div className="label">Completed</div></div>
        <div className="stat danger"><div className="num">{project.overdue_tasks}</div><div className="label">Overdue</div></div>
        <div className="stat"><div className="num">{project.members?.length}</div><div className="label">Members</div></div>
      </div>

      <div className="toolbar">
        <h2 className="section-title" style={{ marginBottom: 0 }}>Team</h2>
        {amAdmin && <button className="btn btn-outline btn-sm" onClick={() => setShowMemberModal(true)}>+ Add member</button>}
      </div>
      <div className="card" style={{ marginBottom: 24 }}>
        {project.members?.length === 0 ? (
          <p className="empty">No members yet.</p>
        ) : (
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Role</th>{amAdmin && <th></th>}</tr></thead>
            <tbody>
              {project.members?.map((m) => (
                <tr key={m.id}>
                  <td>{m.user?.name || m.user?.email}</td>
                  <td>{m.user?.email}</td>
                  <td>
                    <span className={`badge role-${m.role}`}>
                      {m.role}{m.user?.id === project.owner?.id ? ' (owner)' : ''}
                    </span>
                  </td>
                  {amAdmin && (
                    <td style={{ textAlign: 'right' }}>
                      {m.user?.id !== project.owner?.id && (
                        <button className="btn btn-danger btn-sm" onClick={() => removeMember(m.id)}>Remove</button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="toolbar">
        <h2 className="section-title" style={{ marginBottom: 0 }}>Tasks</h2>
        {amAdmin && <button className="btn btn-primary btn-sm" onClick={() => setShowTaskModal(true)}>+ New task</button>}
      </div>
      <div className="card">
        {tasks.length === 0 ? (
          <p className="empty">No tasks in this project yet.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Title</th><th>Assignee</th><th>Status</th><th>Priority</th><th>Due</th>{amAdmin && <th></th>}</tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id}>
                  <td style={{ fontWeight: 500 }}>{t.title}</td>
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
                  {amAdmin && (
                    <td style={{ textAlign: 'right' }}>
                      <button className="btn btn-danger btn-sm" onClick={() => deleteTask(t.id)}>Delete</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showTaskModal && (
        <TaskFormModal
          projects={[project]}
          members={project.members || []}
          onClose={() => setShowTaskModal(false)}
          onSaved={() => { setShowTaskModal(false); load() }}
        />
      )}

      {showMemberModal && (
        <div className="modal-backdrop" onClick={() => setShowMemberModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add member</h2>
            {error && <div className="error-box">{error}</div>}
            <form onSubmit={addMember}>
              {!selectedUser ? (
                <div className="field">
                  <label>Search user (email, name, or username)</label>
                  <input
                    value={memberQuery}
                    onChange={(e) => searchUsers(e.target.value)}
                    placeholder="Type to search registered users"
                    autoFocus
                  />
                  {searchResults.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      {searchResults.map((u) => (
                        <div
                          key={u.id}
                          onClick={() => { setSelectedUser(u); setSearchResults([]); setError('') }}
                          style={{ padding: '10px 12px', borderRadius: 8, background: 'rgba(99,102,241,0.12)', marginBottom: 6, cursor: 'pointer' }}
                        >
                          <strong>{u.name || u.email}</strong>
                          <div style={{ color: 'var(--text-soft)', fontSize: '0.85rem' }}>{u.email}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="field">
                  <label>Selected user</label>
                  <div style={{ padding: '10px 12px', borderRadius: 8, background: 'rgba(99,102,241,0.12)' }}>
                    <strong>{selectedUser.name || selectedUser.email}</strong>
                    <div style={{ color: 'var(--text-soft)', fontSize: '0.85rem' }}>{selectedUser.email}</div>
                  </div>
                  <button type="button" className="btn btn-outline btn-sm" style={{ marginTop: 8 }} onClick={() => setSelectedUser(null)}>
                    Change
                  </button>
                </div>
              )}
              <div className="field">
                <label>Role</label>
                <select value={memberRole} onChange={(e) => setMemberRole(e.target.value)}>
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="actions">
                <button type="button" className="btn btn-outline" onClick={() => setShowMemberModal(false)}>Cancel</button>
                <button className="btn btn-primary" disabled={!selectedUser}>Add</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
