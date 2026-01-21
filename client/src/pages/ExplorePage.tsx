import { Link } from "react-router-dom";

const CARDS = [
  {
    title: "What is CapeControl?",
    to: "/docs/start-here",
    body: "A calm introduction — the quiet before power.",
  },
  {
    title: "The Curiosity Trail",
    to: "/docs/curiosity-trail",
    body: "Follow breadcrumbs. Keep the next step optional.",
  },
  {
    title: "Trust & safety",
    to: "/docs/trust-and-safety",
    body: "Boundaries that stay clear and reversible.",
  },
  {
    title: "Agents",
    to: "/docs/agents-101",
    body: "Focused helpers with explicit permissions.",
  },
  {
    title: "Marketplace",
    to: "/docs/marketplace-preview",
    body: "Explore before commitment (preview).",
  },
] as const;

export default function ExplorePage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-5xl px-6 py-16">
        <div className="space-y-4">
          <h1 className="text-3xl font-semibold tracking-tight">Explore quietly</h1>
          <p className="max-w-2xl text-slate-300">
            No account needed. Just follow the trail.
          </p>

          <div className="grid gap-4 pt-6 sm:grid-cols-2 lg:grid-cols-3">
            {CARDS.map((card) => (
              <Link
                key={card.to}
                to={card.to}
                className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 hover:bg-slate-900/55 transition"
              >
                <h2 className="text-lg font-medium">{card.title}</h2>
                <p className="mt-2 text-sm text-slate-300">{card.body}</p>
              </Link>
            ))}
          </div>

          <div className="flex flex-wrap gap-3 pt-8">
            <Link
              to="/auth/login"
              className="rounded-xl bg-white px-4 py-2 text-sm font-medium text-slate-950 hover:opacity-90"
            >
              Log in
            </Link>
            <Link
              to="/auth/register"
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-900"
            >
              Create account
            </Link>
            <Link
              to="/"
              className="rounded-xl border border-slate-800 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-900"
            >
              Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
