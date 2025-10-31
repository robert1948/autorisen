
import { useState } from 'react'; import { useNavigate } from 'react-router-dom'
import ChatMock from '@/components/ChatMock'
export default function Guide(){
  const [progress,setProgress]=useState([false,false,false,false])
  const nav = useNavigate()
  const mark=(i:number)=>setProgress(p=>{const n=[...p]; if(i<n.length) n[i]=true; return n})
  const done = progress.every(Boolean)
  return (<div className="grid gap-6 md:grid-cols-2">
    <div className="space-y-3">
      <h2 className="text-xl font-semibold">CapeAI Guide — Onboarding Chat</h2>
      <ChatMock onChecklist={mark}/>
      <button onClick={()=>nav('/workbench')} disabled={!done}
        className={`btn ${done?'btn-primary':'btn-ghost opacity-60 cursor-not-allowed'}`}>Mark Done</button>
    </div>
    <div className="card p-4">
      <div className="font-semibold mb-2">Checklist</div>
      <ul className="space-y-2 text-sm">
        {['Invite core teammates','Connect data sources','Configure notifications','Launch first CapeAI run'].map((t,i)=>(
          <li key={i} className="flex items-center gap-2">
            <span className={`h-4 w-4 rounded-sm border ${progress[i]?'bg-accent-agents border-accent-agents':'border-border'}`}/>
            <span>{t}</span>
          </li>
        ))}
      </ul>
    </div>
  </div>)
}
