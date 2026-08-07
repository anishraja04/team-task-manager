import { useEffect, useState } from 'react'
import { tasksApi } from '../api'

// all the options for status and priority
const STATUSES = ['todo', 'in_progress', 'review', 'done']
const PRIORITIES = ['low', 'medium', 'high', 'urgent']

export default function TaskFormModal({ projects = [], members = [], task, onClose, onSaved }) {
  // if we are editing a task then prefill the form with its values
  const [form, setForm] = useState({
    title: task?.title || '',
    description: task?.description || '',
    project: task?.project || projects[0]?.id || '',
    assignee: task?.assignee || '',
    status: task?.status || 'todo',
    priority: task?.priority || 'medium',
    due_date: task?.due_date || '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  // small helper to update one field of the form
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  // if projects list is empty (like from project detail page) keep the current one
  const projectOptions = projects.length ? projects : [{ id: form.project, name: form.project_name }]

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (task) {
        await tasksApi.update(task.id, form)
      } else {
        await tasksApi.create(form)
      }
      onSaved()
    } catch (err) {
      const d = err.response?.data
      // show the field errors from the backend if any
      setError(
        d
          ? Object.entries(d).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; ')
          : 'Failed to save task.'
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{task ? 'Edit Task' : 'New Task'}</h2>
        {error && <div className="error-box">{error}</div>}
        <form onSubmit={submit}>
          <div className="field">
            <label>Title</label>
            <input value={form.title} onChange={set('title')} required />
          </div>
          <div className="field">
            <label>Description</label>
            <textarea rows={3} value={form.description} onChange={set('description')} />
          </div>
          <div className="field">
            <label>Project</label>
            <select value={form.project} onChange={set('project')} required>
              <option value="">Select project</option>
              {projectOptions.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Assignee</label>
            <select value={form.assignee} onChange={set('assignee')}>
              <option value="">Unassigned</option>
              {members?.map((m) => (
                <option key={m.user.id} value={m.user.id}>{m.user.name || m.user.email}</option>
              ))}
            </select>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <div className="field" style={{ flex: 1 }}>
              <label>Status</label>
              <select value={form.status} onChange={set('status')}>
                {STATUSES.map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
              </select>
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label>Priority</label>
              <select value={form.priority} onChange={set('priority')}>
                {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>
          <div className="field">
            <label>Due date</label>
            <input type="date" value={form.due_date} onChange={set('due_date')} />
          </div>
          <div className="actions">
            <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
            <button className="btn btn-primary" disabled={busy}>{busy ? 'Saving…' : 'Save'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}
