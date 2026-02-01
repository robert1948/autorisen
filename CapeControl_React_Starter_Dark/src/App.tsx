import React from 'react'
import { Outlet, useLocation } from 'react-router-dom'

export default function App(){
  const loc = useLocation()

  return (
    <div className="min-h-screen bg-bg text-text">
      <main className="container-cc py-8"><Outlet/></main>
      <footer className="container-cc pb-8 pt-6 text-xs text-text-muted">
        <hr className="div mb-4"/><div className="flex items-center justify-between">
          <span>© 2025 CapeControl. All rights reserved.</span><span className="hidden sm:block">Route: {loc.pathname}</span>
        </div>
      </footer>
    </div>
  )
}
