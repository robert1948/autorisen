import { Link } from "react-router-dom";

import PublicTopNav from "../../components/nav/PublicTopNav";
import Footer from "../../components/Footer";

export default function MarketplacePublicPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col font-sans">
      <PublicTopNav />

      <main className="flex-1 px-6 pb-16">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-[#1e1b4b] border border-blue-900/50 text-blue-200 text-xs font-medium mb-8 shadow-sm">
            Marketplace
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold leading-tight">
            Discover agents you can trust.
          </h1>
          <p className="mt-5 text-white/70 leading-relaxed">
            Browse curated, workflow-focused agents—built to reduce busywork without turning your
            operation into a science project. The public marketplace is a preview; the full
            deployment experience lives inside the app.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="text-sm font-semibold">Operations assistants</div>
              <div className="mt-2 text-sm text-white/70">
                Routing, approvals, reminders, and next-step nudges.
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="text-sm font-semibold">Integrations</div>
              <div className="mt-2 text-sm text-white/70">
                Connect email, forms, calendars, and docs with guardrails.
              </div>
            </div>
          </div>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              to="/register"
              className="rounded-full bg-white text-black px-5 py-2 text-sm font-semibold hover:bg-white/90"
            >
              Get early access
            </Link>
            <Link
              to="/login"
              className="rounded-full border border-white/15 px-5 py-2 text-sm font-semibold text-white hover:bg-white/5"
            >
              Log in to the in-app marketplace
            </Link>
          </div>

          <div className="mt-6 text-xs text-white/50">
            Note: The in-app marketplace requires login.
          </div>
        </div>
      </main>

      <div className="px-6 py-6">
        <Footer onOpenSupport={() => {}} />
      </div>
    </div>
  );
}
