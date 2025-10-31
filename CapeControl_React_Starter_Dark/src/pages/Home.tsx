
import { Link } from 'react-router-dom'
export default function Home(){
  return (<div className="space-y-6">
    <section>
      <h1 className="text-3xl font-bold">Where Intelligence Meets Impact — AI Accessible to Everyone.</h1>
      <p className="muted mt-2 max-w-2xl">Democratize AI with guided onboarding, operational insights, and developer-friendly agents.</p>
      <div className="mt-4 flex gap-3">
        <Link to="/guide" className="btn btn-primary">Start CapeAI Onboarding</Link>
        <a href="#how" className="btn btn-secondary">See How It Works →</a>
      </div>
    </section>
    <section id="how" className="grid gap-4 sm:grid-cols-3">
      <div className="card p-4"><div className="font-semibold mb-1">Guided Onboarding</div><p className="muted text-sm">CapeAI walks every tenant through setup and first automations.</p></div>
      <div className="card p-4"><div className="font-semibold mb-1">Operational Insights</div><p className="muted text-sm">Ask questions about usage or finance data and get auditable answers.</p></div>
      <div className="card p-4"><div className="font-semibold mb-1">Developers Welcome</div><p className="muted text-sm">Build agents with guardrails, quotas, and observability baked in.</p></div>
    </section>
  </div>)
}
