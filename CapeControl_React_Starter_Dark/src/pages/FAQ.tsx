
import { Link } from 'react-router-dom'
export default function FAQ(){
  return (<div className="space-y-4">
    <h2 className="text-xl font-semibold">Support & FAQ</h2>
    <div className="space-y-3">
      <div className="card p-4"><div className="font-semibold">Does ChatKit require code changes?</div><p className="muted text-sm mt-1">No—CapeControl mints secure tokens server-side. You can embed ChatKit widgets anywhere.</p></div>
      <div className="card p-4"><div className="font-semibold">How do you keep conversations safe?</div><p className="muted text-sm mt-1">Threads are persisted with audit logs and per-tool guardrails.</p></div>
      <div className="card p-4"><div className="font-semibold">Can I monitor system health?</div><p className="muted text-sm mt-1">Yes, the platform exposes logs, web vitals, and smoke checks.</p></div>
    </div>
    <Link to="/" className="btn btn-secondary">Back to Home</Link>
  </div>)
}
