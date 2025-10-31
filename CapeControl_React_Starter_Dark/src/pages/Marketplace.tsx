
import { Link } from 'react-router-dom'
import Card from '@/components/Card'
export default function Marketplace(){
  return (<div className="space-y-4">
    <h2 className="text-xl font-semibold">Marketplace — Discover CapeControl Agents</h2>
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Card title="Ops Copilot" subtitle="Automate weekly digests and checks">
        <div className="flex justify-end"><Link to="/pricing" className="btn btn-secondary">View Pricing →</Link></div>
      </Card>
      <Card title="Energy Insights" subtitle="Query meter data in natural language."/>
      <Card title="Finance Q&A" subtitle="Ask about transactions, balances, trends."/>
    </div>
  </div>)
}
