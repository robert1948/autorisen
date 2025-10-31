
import { Link } from 'react-router-dom'
export default function Dashboard(){
  return (<div className="space-y-4">
    <h2 className="text-xl font-semibold">Admin Dashboard — Operational Intelligence</h2>
    <div className="grid gap-4 md:grid-cols-3">
      <div className="card p-4"><div className="font-semibold mb-2">Usage Summary</div><div className="muted text-sm">Sessions: 284 • Agents: 6 • Errors: 0</div></div>
      <div className="card p-4"><div className="font-semibold mb-2">Audit Log Feed</div><div className="muted text-sm">Latest: marketplace.launch by robert@ at 08:14</div></div>
      <div className="card p-4"><div className="font-semibold mb-2">System Health</div><div className="muted text-sm">All services operational</div></div>
    </div>
    <Link to="/marketplace" className="btn btn-secondary">Marketplace</Link>
  </div>)
}
