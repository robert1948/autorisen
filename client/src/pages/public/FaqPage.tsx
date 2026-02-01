import { Link } from "react-router-dom";

import PublicTopNav from "../../components/nav/PublicTopNav";
import Footer from "../../components/Footer";

const FAQS = [
  {
    q: "Do I need technical skills to get value?",
    a: "No. We start by mapping one real workflow and automating the busywork safely—no rebuild required.",
  },
  {
    q: "Will I have to change all my tools?",
    a: "Not at all. CapeControl is designed to layer on top of your current tools and processes.",
  },
  {
    q: "Is our data secure and auditable?",
    a: "Yes. Workflows are built with role-based access and audit trails so you can see what happened and why.",
  },
];

export default function FaqPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col font-sans">
      <PublicTopNav />

      <main className="flex-1 px-6 py-10">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-2xl font-semibold">FAQ</h1>

        <div className="mt-8 space-y-4">
          {FAQS.map((item) => (
            <div
              key={item.q}
              className="rounded-2xl border border-white/10 bg-white/5 p-5"
            >
              <div className="text-sm font-semibold">{item.q}</div>
              <div className="mt-2 text-sm text-white/70">{item.a}</div>
            </div>
          ))}
        </div>

          <div className="mt-10 flex flex-wrap gap-3">
          <Link
            to="/register"
            className="rounded-full bg-white text-black px-5 py-2 text-sm font-semibold hover:bg-white/90"
          >
            Get started
          </Link>
          <Link
            to="/contact"
            className="rounded-full border border-white/15 px-5 py-2 text-sm font-semibold text-white hover:bg-white/5"
          >
            Talk to our team
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
