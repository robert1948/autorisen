import { Link } from "react-router-dom";

import PublicTopNav from "../../components/nav/PublicTopNav";
import Footer from "../../components/Footer";

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col font-sans">
      <PublicTopNav />

      <main className="flex-1 px-6 py-10">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-2xl font-semibold">Pricing</h1>

        <p className="mt-4 text-white/70">
          Pricing is being finalised for the current beta. If you&apos;d like early access pricing,
          get in touch and we&apos;ll tailor a plan to your workflows.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="text-sm text-white/70">Starter</div>
            <div className="mt-2 text-3xl font-bold">$0</div>
            <ul className="mt-4 space-y-2 text-sm text-white/70">
              <li>One workflow-mapping session</li>
              <li>Single workflow assistant</li>
              <li>Basic reporting</li>
            </ul>
          </div>
          <div className="rounded-2xl border border-indigo-500/30 bg-indigo-500/10 p-5">
            <div className="text-sm text-indigo-200">Growth</div>
            <div className="mt-2 text-3xl font-bold">$249</div>
            <div className="text-sm text-white/60">per month</div>
            <ul className="mt-4 space-y-2 text-sm text-white/70">
              <li>Multiple workflows</li>
              <li>Team access + roles</li>
              <li>Ops insights</li>
            </ul>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="text-sm text-white/70">Enterprise</div>
            <div className="mt-2 text-3xl font-bold">Custom</div>
            <ul className="mt-4 space-y-2 text-sm text-white/70">
              <li>Dedicated environment</li>
              <li>Custom integrations</li>
              <li>Support + SLAs</li>
            </ul>
          </div>
        </div>

          <div className="mt-10 flex flex-wrap gap-3">
          <Link
            to="/register"
            className="rounded-full bg-white text-black px-5 py-2 text-sm font-semibold hover:bg-white/90"
          >
            Start free
          </Link>
          <Link
            to="/contact"
            className="rounded-full border border-white/15 px-5 py-2 text-sm font-semibold text-white hover:bg-white/5"
          >
            Talk to sales
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
