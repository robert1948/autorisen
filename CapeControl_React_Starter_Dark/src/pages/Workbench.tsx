
import { Link } from 'react-router-dom'
export default function Workbench(){
  return (<div className="grid gap-6 md:grid-cols-2">
    <div className="card p-4">
      <div className="font-semibold mb-2">Developer Workbench — Test and Iterate with Live Logs</div>
      <pre className="bg-[#111318] p-3 rounded-lg text-xs text-text-muted overflow-auto">
{`> load: agent 'OnboardingHelper'
> run: explain_spike --since 'yesterday 18:00'
[trace] tool: db.query (42 ms) | messages: 3 | status: OK
Answer: Traffic spike due to Friday campaign. No errors detected.`}
      </pre>
      <Link to="/dashboard" className="btn btn-secondary mt-3">View Analytics →</Link>
    </div>
    <div className="grid gap-4">
      <div className="card p-3"><div className="muted text-xs">Tip</div> Promote successful runs into recipes, then publish to marketplace.</div>
      <div className="card p-3"><div className="muted text-xs">Guardrails</div> Each tool call is tracked for audit visibility.</div>
    </div>
  </div>)
}
