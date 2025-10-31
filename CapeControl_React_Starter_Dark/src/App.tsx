
import { Outlet, Link, useLocation } from 'react-router-dom'
export default function App(){
  const loc = useLocation()
  return (
    <div className="min-h-screen bg-bg text-text">
      <header className="sticky top-0 z-10 border-b border-border bg-surface/80 backdrop-blur">
        <div className="container-cc flex h-14 items-center justify-between">
          <Link to="/" className="font-bold">CapeControl</Link>
          <nav className="flex gap-6 text-sm text-text-muted">
            <Link to="/">Home</Link><Link to="/marketplace">Marketplace</Link>
            <Link to="/pricing">Pricing</Link><Link to="/faq">FAQ</Link>
          </nav>
        </div>
      </header>
      <main className="container-cc py-8"><Outlet/></main>
      <footer className="container-cc pb-8 pt-6 text-xs text-text-muted">
        <hr className="div mb-4"/><div className="flex items-center justify-between">
          <span>© 2025 CapeControl. All rights reserved.</span><span className="hidden sm:block">Route: {loc.pathname}</span>
        </div>
      </footer>
    </div>
  )
}
