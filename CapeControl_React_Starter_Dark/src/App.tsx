import React, { useEffect, useMemo, useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'

export default function App(){
  const loc = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    // Always close the mobile menu when navigating.
    setMenuOpen(false)
  }, [loc.pathname])

  useEffect(() => {
    if (!menuOpen) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [menuOpen])

  const navLinks = useMemo(() => (
    [
      { to: '/', label: 'Home' },
      { to: '/dashboard', label: 'Dashboard' },
      { to: '/marketplace', label: 'Marketplace' },
      { to: '/pricing', label: 'Pricing' },
      { to: '/faq', label: 'FAQ' },
    ]
  ), [])

  return (
    <div className="min-h-screen bg-bg text-text">
      <header className="sticky top-0 z-10 border-b border-border bg-surface/80 backdrop-blur">
        <div className="container-cc flex h-14 items-center justify-between">
          <Link to="/" className="font-bold tracking-tight">CapeControl</Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6 text-sm text-text-muted">
            {navLinks.map((l) => (
              <Link key={l.to} to={l.to} className="hover:text-text">
                {l.label}
              </Link>
            ))}
          </nav>

          {/* Mobile hamburger */}
          <button
            type="button"
            className="md:hidden inline-flex items-center justify-center rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-muted hover:text-text"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            onClick={() => setMenuOpen((v) => !v)}
          >
            <span className="sr-only">Menu</span>
            <span className="font-medium">☰</span>
          </button>
        </div>

        {/* Mobile menu panel (stacked; reserves space; never overlaps page header) */}
        {menuOpen ? (
          <div id="mobile-nav" className="md:hidden border-t border-border bg-surface shadow-lg">
            <div className="container-cc py-3">
              <div className="grid gap-2 text-sm">
                {navLinks.map((l) => (
                  <Link
                    key={l.to}
                    to={l.to}
                    className="rounded-lg px-3 py-2 text-text-muted hover:bg-bg hover:text-text"
                    onClick={() => setMenuOpen(false)}
                  >
                    {l.label}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        ) : null}
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
