import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
    const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col font-sans">
      {/* Header */}
            <header className="px-6 py-6">
                <div className="relative">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            {/* Logo Placeholder */}
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/20">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                                </svg>
                            </div>
                            <span className="text-xl font-bold tracking-tight">CapeControl</span>
                        </div>

                        <button
                            type="button"
                            className="md:hidden rounded-xl border border-white/10 bg-white/5 px-3 py-2"
                            aria-label="Open menu"
                            aria-expanded={menuOpen}
                            aria-controls="mobile-menu"
                            onClick={() => setMenuOpen((v) => !v)}
                        >
                            ☰
                        </button>
                    </div>

                    {menuOpen && (
                        <>
                            <button
                                type="button"
                                className="fixed inset-0 z-40 bg-black/30 md:hidden"
                                aria-label="Close menu"
                                onClick={() => setMenuOpen(false)}
                            />
                            <div
                                id="mobile-menu"
                                className="absolute right-0 top-full mt-2 w-56 rounded-xl bg-neutral-900/95 border border-white/10 shadow-xl z-50 md:hidden"
                            >
                                <nav className="flex flex-col p-2 text-sm">
                                    <Link className="rounded-lg px-3 py-2 hover:bg-white/10" to="/" onClick={() => setMenuOpen(false)}>Home</Link>
                                    <Link className="rounded-lg px-3 py-2 hover:bg-white/10" to="/dashboard" onClick={() => setMenuOpen(false)}>Dashboard</Link>
                                    <Link className="rounded-lg px-3 py-2 hover:bg-white/10" to="/marketplace" onClick={() => setMenuOpen(false)}>Marketplace</Link>
                                    <Link className="rounded-lg px-3 py-2 hover:bg-white/10" to="/pricing" onClick={() => setMenuOpen(false)}>Pricing</Link>
                                    <Link className="rounded-lg px-3 py-2 hover:bg-white/10" to="/faq" onClick={() => setMenuOpen(false)}>FAQ</Link>
                                </nav>
                            </div>
                        </>
                    )}
                </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center max-w-md mx-auto mt-4">
        
        {/* Badge */}
        <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-[#1e1b4b] border border-blue-900/50 text-blue-200 text-xs font-medium mb-8 shadow-sm">
            Built for small business ops
        </div>

        {/* Headline */}
        <h1 className="text-[2.5rem] leading-[1.1] font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-white/70">
            AI that learns how your business runs— then quietly removes the busywork.
        </h1>

        {/* Description */}
        <p className="text-gray-400 text-sm leading-relaxed mb-12">
            If you're the founder or operations lead, you're probably the one holding everything together: spreadsheets, emails, follow-ups, and approvals. CapeControl listens first, maps how your day really works, then deploys AI-powered workflows that reduce manual tasks without forcing you into a rigid new system.
        </p>

        {/* Actions */}
        <div className="w-full space-y-4">
            <button className="w-full py-4 px-6 rounded-full bg-gradient-to-r from-[#4f46e5] to-[#7c3aed] hover:from-[#4338ca] hover:to-[#6d28d9] text-white font-semibold shadow-lg shadow-indigo-900/30 transition-all transform hover:scale-[1.02]">
                Start a workflow-mapping session
            </button>
            
            <button className="w-full py-4 px-6 rounded-full border border-white/10 hover:bg-white/5 text-white font-medium transition-all">
                Talk to our team
            </button>
        </div>

        {/* Link */}
        <Link to="/workflow" className="mt-10 text-blue-400 text-sm font-medium hover:text-blue-300 transition-colors flex items-center gap-1">
            See a real workflow <span aria-hidden="true">→</span>
        </Link>

      </main>

      {/* Footer Status */}
      <footer className="px-6 py-8 mt-auto">
        <div className="flex gap-3 text-[10px] font-mono uppercase tracking-wider font-semibold">
            <span className="px-2 py-1 rounded bg-[#14532d]/40 text-emerald-400 border border-emerald-900/50">healthy</span>
            <span className="px-2 py-1 rounded bg-gray-800/50 text-gray-500 border border-gray-800">api dev</span>
            <span className="px-2 py-1 rounded bg-gray-800/50 text-gray-500 border border-gray-800">prod</span>
        </div>
      </footer>
    </div>
  );
}
