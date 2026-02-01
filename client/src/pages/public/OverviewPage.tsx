import { Link } from "react-router-dom";

import PublicTopNav from "../../components/nav/PublicTopNav";
import Footer from "../../components/Footer";

export default function OverviewPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col font-sans">
      <PublicTopNav />

      <main className="flex-1 px-6 pb-16">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-[#1e1b4b] border border-blue-900/50 text-blue-200 text-xs font-medium mb-8 shadow-sm">
            Overview
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold leading-tight">
            Calm, workflow-first AI for small business operations.
          </h1>

          <p className="mt-5 text-white/70 leading-relaxed">
            CapeControl helps you map one real process—then automate the repetitive steps without
            forcing a brand-new system. Start with the workflow you already run today, and add
            structure, handoffs, and audit trails as you grow.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="text-sm font-semibold">Map</div>
              <div className="mt-2 text-sm text-white/70">
                Turn the way you work into a clear, repeatable flow.
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="text-sm font-semibold">Automate</div>
              <div className="mt-2 text-sm text-white/70">
                Use AI agents for handoffs, follow-ups, and routine updates.
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="text-sm font-semibold">Govern</div>
              <div className="mt-2 text-sm text-white/70">
                Keep visibility with roles, logs, and safe defaults.
              </div>
            </div>
          </div>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              to="/register"
              className="rounded-full bg-white text-black px-5 py-2 text-sm font-semibold hover:bg-white/90"
            >
              Create free account
            </Link>
            <Link
              to="/contact"
              className="rounded-full border border-white/15 px-5 py-2 text-sm font-semibold text-white hover:bg-white/5"
            >
              Talk to our team
            </Link>
            <Link
              to="/trail"
              className="rounded-full border border-white/15 px-5 py-2 text-sm font-semibold text-white hover:bg-white/5"
            >
              See the curiosity trail
            </Link>
          </div>
        </div>
      </main>

      <div className="px-6 py-6">
        <Footer onOpenSupport={() => {}} />
      </div>
    </div>
  );
}
