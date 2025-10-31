
import Card from '@/components/Card'; import { Link } from 'react-router-dom'
export default function Pricing(){
  return (<div className="space-y-4">
    <h2 className="text-xl font-semibold">Plans that Scale with Your Impact</h2>
    <div className="grid gap-4 md:grid-cols-3">
      <Card title="Starter — $0" subtitle="Onboarding guide, read-only data, sandbox tools"/>
      <Card title="Growth — $249/mo" subtitle="Unlimited seats, dashboards, Ops Copilot & runbooks"/>
      <Card title="Enterprise — Contact" subtitle="Dedicated env, custom adapters, SLAs">
        <div className="flex justify-end"><Link to="/faq" className="btn btn-primary">Login</Link></div>
      </Card>
    </div>
  </div>)
}
