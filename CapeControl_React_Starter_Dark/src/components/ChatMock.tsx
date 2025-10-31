
import { useEffect, useState } from 'react'
type Msg = { role:'assistant'|'user', text:string }
const seed:Msg[]=[
  {role:'assistant', text:'Welcome to CapeControl. Let’s set up your workspace.'},
  {role:'user', text:'Okay, what’s first?'},
  {role:'assistant', text:'Invite teammates and connect data sources. I’ll track progress.'},
]
export default function ChatMock({onChecklist}:{onChecklist?:(i:number)=>void}){
  const [msgs,setMsgs]=useState<Msg[]>([])
  useEffect(()=>{ let i=0; const id=setInterval(()=>{
      setMsgs(p=>[...p, seed[i]]); onChecklist&&onChecklist(i); i++; if(i>=seed.length) clearInterval(id)
  },700); return ()=>clearInterval(id)},[])
  return <div className="card p-4">
    <div className="muted text-xs mb-2">CapeAI</div>
    <div className="space-y-2">
      {msgs.map((m,i)=>(
        <div key={i} className={`max-w-[70%] rounded-lg px-3 py-2 text-sm ${m.role==='assistant'?'bg-[#2A2E36] text-white':'bg-accent-agents text-black ml-auto'}`}>{m.text}</div>
      ))}
    </div>
  </div>
}
