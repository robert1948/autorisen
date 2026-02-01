import { Link } from "react-router-dom";

import PublicTopNav from "../components/nav/PublicTopNav";

export default function LandingMinimal() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col font-sans">
      <PublicTopNav />

      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center max-w-md mx-auto mt-4">
        <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-[#1e1b4b] border border-blue-900/50 text-blue-200 text-xs font-medium mb-8 shadow-sm">
          Built for small business ops
        </div>

        <h1 className="text-[2.5rem] leading-[1.1] font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-white/70">
          AI that learns how your business runs— then quietly removes the busywork.
        </h1>

        <p className="text-gray-400 text-sm leading-relaxed mb-12">
          If you&apos;re the founder or operations lead, you&apos;re probably the one holding everything
          together: spreadsheets, emails, follow-ups, and approvals. CapeControl listens first, maps
          how your day really works, then deploys AI-powered workflows that reduce manual tasks
          without forcing you into a rigid new system.
        </p>

        <div className="w-full space-y-4">
          <Link
            to="/register"
            className="block w-full py-4 px-6 rounded-full bg-gradient-to-r from-[#4f46e5] to-[#7c3aed] hover:from-[#4338ca] hover:to-[#6d28d9] text-white font-semibold shadow-lg shadow-indigo-900/30 transition-all transform hover:scale-[1.02]"
          >
            Start a workflow-mapping session
          </Link>

          <Link
            to="/contact"
            className="block w-full py-4 px-6 rounded-full border border-white/10 hover:bg-white/5 text-white font-medium transition-all"
          >
            Talk to our team
          </Link>
        </div>

        <Link
          to="/docs/curiosity-trail"
          className="mt-10 text-blue-400 text-sm font-medium hover:text-blue-300 transition-colors flex items-center gap-1"
        >
          See a real workflow <span aria-hidden="true">→</span>
        </Link>
      </main>
    </div>
  );
}
