import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Layout() {
  const { user, logout } = useAuth()

  const navLink = ({ isActive }) => (isActive ? 'active' : '')

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="logo">✓</span> TaskFlow
        </div>
        <nav className="nav">
          <NavLink to="/" end className={navLink}>Dashboard</NavLink>
          <NavLink to="/projects" className={navLink}>Projects</NavLink>
          <NavLink to="/tasks" className={navLink}>Tasks</NavLink>
        </nav>
        <div className="user-box">
          <div className="name">{user?.name || user?.email}</div>
          <div className="role">{user?.role}</div>
          <button className="btn btn-outline btn-sm logout" onClick={logout}>Log out</button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
