import { Outlet, Link } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-brand">
          <h1>Nonprofit CRM</h1>
        </div>
        <div className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/constituents">Constituents</Link>
          <Link to="/contributions">Contributions</Link>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
