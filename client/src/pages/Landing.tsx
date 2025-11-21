import React from "react";

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
      {/* Header */}
      <header className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-2xl bg-gradient-to-tr from-pink-500 via-purple-500 to-sky-500 flex items-center justify-center text-xs font-bold">
            CC
          </div>
          <span className="font-semibold tracking-tight">CapeControl</span>
        </div>
        <span className="text-[11px] sm:text-xs text-slate-400">
          Early access
        </span>
      </header>

      {/* Main */}
      <main className="flex-1 flex items-center">
        <div className="relative w-full">
          {/* Subtle gradient artwork (desktop only) */}
          <div className="pointer-events-none hidden lg:block absolute inset-y-0 right-0">
            <div className="h-80 w-80 rounded-full bg-gradient-to-tr from-purple-500/40 via-sky-500/20 to-transparent blur-3xl translate-x-16 -translate-y-8" />
          </div>

          <section className="relative max-w-6xl mx-auto px-4 sm:px-8 py-10 md:py-16 flex flex-col lg:flex-row items-center gap-10 lg:gap-16">
            {/* Left: Hero */}
            <div className="flex-1 max-w-xl">
              <p className="text-[11px] sm:text-xs font-semibold tracking-[0.25em] text-sky-400 uppercase mb-4">
                CapeControl • AI Agents
              </p>
              <h1 className="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight mb-5">
                Transform complexity into opportunity with intelligent AI.
              </h1>
              <p className="text-sm sm:text-base text-slate-300 mb-8">
                CapeControl makes AI accessible, practical, and personal —
                for everyone. Start with a guided AI that learns your context
                and grows with your work.
              </p>

              <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                <a
                  href="/register"
                  className="inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-medium bg-gradient-to-r from-fuchsia-500 via-purple-500 to-sky-500 shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition"
                >
                  Join Early Access
                </a>
                <button
                  type="button"
                  className="inline-flex items-center gap-1 text-sm font-medium text-sky-400 hover:text-sky-300"
                >
                  <span>Learn more</span>
                  <span aria-hidden="true">→</span>
                </button>
              </div>
            </div>

            {/* Right: subtle card (desktop), hidden on very small screens if you like */}
            <div className="flex-1 w-full max-w-md lg:max-w-none flex justify-center lg:justify-end">
              <div className="relative w-full max-w-sm aspect-[4/5] rounded-3xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-sm p-5 flex flex-col justify-between shadow-2xl">
                <div className="text-xs text-slate-400 mb-3">
                  CapeAI preview
                </div>
                <div className="text-sm text-slate-200">
                  “Hi Robert, I’m your CapeAI guide. Ready to turn today’s
                  complexity into a clear plan?”
                </div>
                <div className="mt-4 flex items-center justify-between text-[11px] text-slate-500">
                  <span>Context-aware</span>
                  <span>Always-on</span>
                  <span>Private</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] sm:text-xs text-slate-500">
        <span>© {new Date().getFullYear()} CapeControl. All rights reserved.</span>
        <span>Built with CapeAI.</span>
      </footer>
    </div>
  );
};

export default LandingPage;
